"""
Platform logging middleware - FIXED version
Logs all API requests to platform_logs table
Uses background task to avoid Starlette body consumption bug
"""
from fastapi import Request, Response
from starlette.background import BackgroundTask
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from contextlib import contextmanager
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse
import jwt

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

JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "your-super-secret-jwt-key-change-in-production")

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

def extract_user_from_request(request: Request) -> tuple:
    """Extract company_id and user_id from request (Bearer token or API key)"""
    company_id = None
    user_id = None
    
    # Try Bearer token first
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        try:
            token = auth_header.split(" ", 1)[1]
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            user_id = payload.get("user_id")
            
            if user_id:
                with get_db() as conn:
                    cur = conn.cursor(cursor_factory=RealDictCursor)
                    cur.execute("SELECT company_id FROM users WHERE id = %s", (user_id,))
                    result = cur.fetchone()
                    if result:
                        company_id = result["company_id"]
        except:
            pass
    
    # Try API key
    api_key = request.headers.get("x-api-key")
    if api_key and not company_id:
        try:
            import hashlib
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            key_prefix = api_key[:8]
            
            with get_db() as conn:
                cur = conn.cursor(cursor_factory=RealDictCursor)
                cur.execute("""
                    SELECT company_id FROM api_keys
                    WHERE key_prefix = %s AND key_hash = %s AND is_active = true
                """, (key_prefix, key_hash))
                result = cur.fetchone()
                if result:
                    company_id = result["company_id"]
        except:
            pass
    
    return company_id, user_id

def log_request_sync(log_data: dict):
    """Sync database insert - called as background task"""
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO platform_logs (
                    company_id, user_id, endpoint, method, status_code,
                    response_time_ms, input_tokens, output_tokens, ip_address
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                log_data.get("company_id"),
                log_data.get("user_id"),
                log_data.get("endpoint"),
                log_data.get("method"),
                log_data.get("status_code"),
                log_data.get("response_time_ms"),
                log_data.get("input_tokens", 0),
                log_data.get("output_tokens", 0),
                log_data.get("ip_address")
            ))
            conn.commit()
    except Exception as e:
        # Silent fail - logging should never break the API
        print(f"Failed to log request: {e}")

class PlatformLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all API requests to platform_logs table
    FIXED: Uses background task to avoid body consumption bug
    """
    
    def __init__(self, app: ASGIApp, exclude_paths: list = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/health", "/docs", "/openapi.json", "/static"]
    
    async def dispatch(self, request: Request, call_next):
        # Skip excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # Skip non-API paths
        if not request.url.path.startswith("/v1/"):
            return await call_next(request)
        
        # Record start time
        start_time = time.time()
        
        # Extract user context (before processing request)
        company_id, user_id = extract_user_from_request(request)
        
        # Get client IP
        ip_address = request.client.host if request.client else None
        
        # Process request - DON'T consume the body
        response = await call_next(request)
        
        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Prepare log data
        log_data = {
            "company_id": company_id,
            "user_id": user_id,
            "endpoint": request.url.path,
            "method": request.method,
            "status_code": response.status_code,
            "response_time_ms": response_time_ms,
            "ip_address": ip_address,
            "input_tokens": 0,
            "output_tokens": 0
        }
        
        # Add background task to log (doesn't block response)
        # This is the FIX: use background_task parameter instead of asyncio.create_task
        # This way Starlette handles it properly without body consumption issues
        response.background = BackgroundTask(log_request_sync, log_data)
        
        return response
