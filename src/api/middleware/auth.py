"""
Authentication middleware for Legal AI Agent
- JWT token verification
- User and company context injection
"""
from fastapi import HTTPException, Header, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict
import jwt
import os
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

# Import security utilities
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from security_utils import (
    validate_jwt_secret, sanitize_log, rate_limiter, validate_password,
    ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, create_jwt_with_jti
)

# JWT Configuration - FIX 1: Validate JWT secret
JWT_SECRET = validate_jwt_secret()
JWT_ALGORITHM = "HS256"

def _normalize_db_host(raw_host: str) -> str:
    host = (raw_host or "").strip()
    if not host:
        return "localhost"
    if "://" in host:
        parsed = urlparse(host)
        if parsed.hostname:
            return parsed.hostname
    if "/" in host:
        return host.split("/")[0]
    return host


def _build_database_url_with_ssl(url: str, sslmode: str) -> str:
    parsed = urlparse(url)
    query_params = dict(parse_qsl(parsed.query, keep_blank_values=True))
    if "sslmode" not in query_params and sslmode:
        query_params["sslmode"] = sslmode
    return urlunparse(parsed._replace(query=urlencode(query_params)))


def _build_db_connect_args():
    sslmode = os.getenv("DB_SSL_MODE", "require")
    database_url = (os.getenv("DATABASE_URL") or "").strip()
    if database_url:
        return {
            "dsn": _build_database_url_with_ssl(database_url, sslmode),
            "kwargs": {},
        }

    return {
        "dsn": None,
        "kwargs": {
            "host": _normalize_db_host(os.getenv("SUPABASE_DB_HOST", "localhost")),
            "port": int(os.getenv("SUPABASE_DB_PORT", "5432")),
            "dbname": os.getenv("DB_NAME", "postgres"),
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("SUPABASE_DB_PASSWORD", ""),
            "sslmode": sslmode,
        },
    }


DB_CONNECT = _build_db_connect_args()

@contextmanager
def get_db():
    """Database connection context manager"""
    if DB_CONNECT["dsn"]:
        conn = psycopg2.connect(DB_CONNECT["dsn"], **DB_CONNECT["kwargs"])
    else:
        conn = psycopg2.connect(**DB_CONNECT["kwargs"])
    try:
        yield conn
    finally:
        conn.close()

security = HTTPBearer(auto_error=False)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token - FIX 14: Reduced lifetime (15 min) + JTI"""
    return create_jwt_with_jti(data, "access")

def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token - FIX 14: Reduced lifetime (7 days) + JTI"""
    return create_jwt_with_jti(data, "refresh")

def verify_token(token: str, token_type: str = "access") -> Dict:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token type. Expected {token_type}"
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """Get current authenticated user from JWT token"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    payload = verify_token(token, "access")
    user_id = payload.get("user_id")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Fetch user from database
    with get_db() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT u.id, u.company_id, u.role, u.full_name, u.email, 
                   u.avatar_url, u.preferences, u.user_settings, u.is_active,
                   c.name as company_name, c.plan, c.monthly_quota, c.used_quota
            FROM users u
            LEFT JOIN companies c ON c.id = u.company_id
            WHERE u.id = %s AND u.is_active = true
        """, (user_id,))
        user = cur.fetchone()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Update last login
        cur.execute("UPDATE users SET last_login_at = now() WHERE id = %s", (user_id,))
        conn.commit()
        
        return dict(user)

async def get_current_active_user(current_user: Dict = Depends(get_current_user)) -> Dict:
    """Ensure user is active"""
    if not current_user.get("is_active"):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def require_role(required_role: str):
    """Dependency to check user role (owner, admin, member, viewer)"""
    async def role_checker(current_user: Dict = Depends(get_current_user)):
        role_hierarchy = {"viewer": 0, "member": 1, "admin": 2, "owner": 3}
        user_level = role_hierarchy.get(current_user["role"], 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {required_role}"
            )
        return current_user
    return role_checker

async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict]:
    """Get user if authenticated, otherwise None (for public endpoints)"""
    if not credentials:
        return None
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
