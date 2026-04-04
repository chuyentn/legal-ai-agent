"""
Authentication endpoints
- Register, login, logout
- Token refresh
- Profile management
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import bcrypt
import secrets
import hashlib
from psycopg2.extras import RealDictCursor

from ..middleware.auth import (
    get_db,
    create_access_token,
    create_refresh_token,
    verify_token,
    get_current_user,
    get_current_active_user,
)

# FIX 8, FIX 9: Import security utilities
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from security_utils import rate_limiter, validate_password

# Webhook helper gửi lead sang Apps Script CRM
from ..core.webhook import send_lead_to_apps_script

router = APIRouter(prefix="/v1/auth", tags=["Authentication"])

# ============================================
# Models
# ============================================


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2)
    company_name: str = Field(..., min_length=2)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: Optional[dict] = None
    user_settings: Optional[dict] = None


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)


# ============================================
# Helper Functions
# ============================================


def hash_password(password: str) -> str:
    """Hash password with bcrypt"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def generate_api_key() -> tuple[str, str, str]:
    """Generate API key with hash and prefix"""
    api_key = f"lak_{secrets.token_hex(24)}"
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    key_prefix = api_key[:8]
    return api_key, key_hash, key_prefix


# ============================================
# Endpoints
# ============================================


@router.post("/register")
async def register(data: RegisterRequest):
    """
    Register new user and create company
    - Rate limit + validate password
    - Gửi thông tin sang Google Apps Script CRM
    """
    # Rate limiting (3 registration attempts / 10 phút / email)
    if not rate_limiter.check(f"register:{data.email}", max_req=3, window_sec=600):
        raise HTTPException(
            status_code=429,
            detail="Too many registration attempts. Please try again in 10 minutes.",
        )

    # Validate password strength
    validate_password(data.password)

    with get_db() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Check email tồn tại chưa
        cur.execute("SELECT id FROM users WHERE email = %s", (data.email,))
        if cur.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Tạo company
        company_slug = data.company_name.lower().replace(" ", "-")
        base_slug = company_slug
        counter = 1
        while True:
            cur.execute("SELECT id FROM companies WHERE slug = %s", (company_slug,))
            if not cur.fetchone():
                break
            company_slug = f"{base_slug}-{counter}"
            counter += 1

        cur.execute(
            """
            INSERT INTO companies (name, slug, plan, monthly_quota, used_quota)
            VALUES (%s, %s, 'trial', 100, 0)
            RETURNING id, name, slug, plan, monthly_quota, created_at
        """,
            (data.company_name, company_slug),
        )
        company = dict(cur.fetchone())

        # Tạo user
        password_hash = hash_password(data.password)
        cur.execute(
            """
            INSERT INTO users (company_id, role, full_name, email, password_hash, is_active)
            VALUES (%s, 'owner', %s, %s, %s, true)
            RETURNING id, company_id, role, full_name, email, avatar_url, created_at
        """,
            (company["id"], data.full_name, data.email, password_hash),
        )
        user = dict(cur.fetchone())

        # Tạo API key mặc định
        api_key, key_hash, key_prefix = generate_api_key()
        cur.execute(
            """
            INSERT INTO api_keys (company_id, name, key_hash, key_prefix, permissions, is_active)
            VALUES (%s, %s, %s, %s, ARRAY['read', 'ask', 'review', 'draft'], true)
            RETURNING id
        """,
            (company["id"], f"{data.company_name} - Default Key", key_hash, key_prefix),
        )
        api_key_id = cur.fetchone()["id"]

        conn.commit()

    # Save registration lead to internal CRM pipeline.
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO customer_leads (
                    source, full_name, company_name, email, status, converted_company_id, converted_user_id, converted_at, metadata
                ) VALUES (
                    'registration', %s, %s, %s, 'converted', %s, %s, now(), %s::jsonb
                )
                ON CONFLICT DO NOTHING
                """,
                (
                    data.full_name,
                    data.company_name,
                    str(data.email),
                    str(company["id"]),
                    str(user["id"]),
                    '{"auto_created": true}',
                ),
            )
            conn.commit()
    except Exception:
        pass

    # Gửi lead sang CRM (Apps Script) – không làm fail nếu lỗi
    try:
        await send_lead_to_apps_script(
            full_name=data.full_name,
            email=data.email,
            company_name=data.company_name,
            source="legal-ai-agent-app",
        )
    except Exception:
        pass

    # Tokens
    access_token = create_access_token(
        {"user_id": str(user["id"]), "email": user["email"]}
    )
    refresh_token = create_refresh_token({"user_id": str(user["id"])})

    return {
        "user": {
            "id": str(user["id"]),
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"],
            "company_id": str(user["company_id"]),
        },
        "company": {
            "id": str(company["id"]),
            "name": company["name"],
            "slug": company["slug"],
            "plan": company["plan"],
            "monthly_quota": company["monthly_quota"],
        },
        "api_key": api_key,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "message": "Registration successful! Save your API key - it cannot be retrieved later.",
    }


@router.post("/login")
async def login(data: LoginRequest):
    """
    Login with email and password (rate limited)
    """
    import logging

    # 5 attempts / phút / email
    if not rate_limiter.check(f"login:{data.email}", max_req=5, window_sec=60):
        raise HTTPException(
            status_code=429,
            detail="Too many login attempts. Please try again in 1 minute.",
        )

    from ..security_utils import sanitize_log

    logging.info(f"LOGIN ATTEMPT: email={sanitize_log(data.email)}")

    with get_db() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute(
            """
            SELECT u.id, u.company_id, u.email, u.full_name, u.role, 
                   u.password_hash, u.is_active, u.avatar_url,
                   c.name as company_name, c.plan, c.monthly_quota, c.used_quota
            FROM users u
            LEFT JOIN companies c ON c.id = u.company_id
            WHERE u.email = %s
        """,
            (data.email,),
        )
        user = cur.fetchone()

        logging.info(f"LOGIN USER FOUND: {user is not None}")

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive. Contact support.",
            )

        if not verify_password(data.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        cur.execute(
            "UPDATE users SET last_login_at = now() WHERE id = %s", (user["id"],)
        )
        conn.commit()

        try:
            from ..main import log_audit

            log_audit(str(user["company_id"]), str(user["id"]), "login", "auth")
        except Exception:
            pass

        access_token = create_access_token(
            {"user_id": str(user["id"]), "email": user["email"]}
        )
        refresh_token = create_refresh_token({"user_id": str(user["id"])})

        return {
            "user": {
                "id": str(user["id"]),
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user["role"],
                "company_id": str(user["company_id"]),
                "company_name": user["company_name"],
                "plan": user["plan"],
                "monthly_quota": user["monthly_quota"],
                "used_quota": user["used_quota"],
                "avatar_url": user["avatar_url"],
            },
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
        }


@router.post("/refresh")
async def refresh_token(data: RefreshTokenRequest):
    """Refresh access token using refresh token"""
    payload = verify_token(data.refresh_token, "refresh")
    user_id = payload.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    with get_db() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            "SELECT email FROM users WHERE id = %s AND is_active = true", (user_id,)
        )
        user = cur.fetchone()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

    access_token = create_access_token({"user_id": user_id, "email": user["email"]})

    return {
        "access_token": access_token,
        "token_type": "Bearer",
    }


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_active_user)):
    """Get current user info"""
    return {
        "id": str(current_user["id"]),
        "email": current_user["email"],
        "full_name": current_user["full_name"],
        "role": current_user["role"],
        "avatar_url": current_user["avatar_url"],
        "preferences": current_user["preferences"],
        "user_settings": current_user["user_settings"],
        "company": {
            "id": str(current_user["company_id"]),
            "name": current_user["company_name"],
            "plan": current_user["plan"],
            "monthly_quota": current_user["monthly_quota"],
            "used_quota": current_user["used_quota"],
        },
    }


@router.put("/me")
async def update_profile(
    data: UpdateProfileRequest, current_user: dict = Depends(get_current_active_user)
):
    """Update user profile"""
    update_fields = []
    params = []

    if data.full_name:
        update_fields.append("full_name = %s")
        params.append(data.full_name)
    if data.avatar_url:
        update_fields.append("avatar_url = %s")
        params.append(data.avatar_url)
    if data.preferences:
        update_fields.append("preferences = %s")
        params.append(data.preferences)
    if data.user_settings:
        update_fields.append("user_settings = %s")
        params.append(data.user_settings)

    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    params.append(current_user["id"])

    with get_db() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        query = (
            f"UPDATE users SET {', '.join(update_fields)}, "
            "updated_at = now() WHERE id = %s RETURNING *"
        )
        cur.execute(query, params)
        updated_user = dict(cur.fetchone())
        conn.commit()

    return {
        "message": "Profile updated successfully",
        "user": {
            "id": str(updated_user["id"]),
            "full_name": updated_user["full_name"],
            "avatar_url": updated_user["avatar_url"],
            "preferences": updated_user["preferences"],
            "user_settings": updated_user["user_settings"],
        },
    }


@router.post("/change-password")
async def change_password(
    data: ChangePasswordRequest, current_user: dict = Depends(get_current_active_user)
):
    """Change user password"""
    validate_password(data.new_password)

    with get_db() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute(
            "SELECT password_hash FROM users WHERE id = %s", (current_user["id"],)
        )
        result = cur.fetchone()

        if not result or not verify_password(
            data.old_password, result["password_hash"]
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        new_hash = hash_password(data.new_password)
        cur.execute(
            "UPDATE users SET password_hash = %s, updated_at = now() WHERE id = %s",
            (new_hash, current_user["id"]),
        )
        conn.commit()

    return {"message": "Password changed successfully"}


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_active_user)):
    """Logout"""
    return {"message": "Logged out successfully"}
