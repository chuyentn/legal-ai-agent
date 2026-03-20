import os
from functools import lru_cache
from pydantic import BaseSettings, AnyHttpUrl


class Settings(BaseSettings):
    # Core
    environment: str = os.getenv("ENVIRONMENT", "production")

    # Database
    database_url: str = os.getenv("DATABASE_URL", "")

    # JWT / app secrets (đã dùng trong middleware.auth)
    jwt_secret: str = os.getenv("JWT_SECRET", os.getenv("SECRET_KEY", "change_me"))
    jwt_algorithm: str = "HS256"

    # PayPal Live
    paypal_client_id: str = os.getenv("PAYPAL_CLIENT_ID", "")
    paypal_client_secret: str = os.getenv("PAYPAL_CLIENT_SECRET", "")
    paypal_api_url: AnyHttpUrl | None = (
        AnyHttpUrl(os.getenv("PAYPAL_API_URL"))
        if os.getenv("PAYPAL_API_URL")
        else None
    )

    # MoMo
    momo_partner_code: str = os.getenv("MOMO_PARTNER_CODE", "")
    momo_access_key: str = os.getenv("MOMO_ACCESS_KEY", "")
    momo_secret_key: str = os.getenv("MOMO_SECRET_KEY", "")
    momo_endpoint: AnyHttpUrl | None = (
        AnyHttpUrl(os.getenv("MOMO_ENDPOINT"))
        if os.getenv("MOMO_ENDPOINT")
        else None
    )

    # App URL (dùng cho return_url, webhook)
    app_base_url: AnyHttpUrl | None = (
        AnyHttpUrl(os.getenv("APP_BASE_URL"))
        if os.getenv("APP_BASE_URL")
        else None
    )

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
