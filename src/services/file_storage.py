"""
File Storage Service.

Supports per-tenant connectors:
- Supabase Storage
- Google Drive (service account + folder isolation)

Production policy:
- Local disk fallback is disabled by default in production.
"""
import asyncio
import io
import json
import os
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Optional

import httpx
import psycopg2
from psycopg2.extras import RealDictCursor
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://chiokotzjtjwfodryfdt.supabase.co")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
BUCKET = "documents"
LOCAL_UPLOAD_DIR = Path("/tmp/legal-ai-agent-uploads/documents")
DATABASE_URL = os.getenv("DATABASE_URL")
DEFAULT_STORAGE_PROVIDER = (os.getenv("DEFAULT_STORAGE_PROVIDER") or "supabase").strip().lower()

_MIME_MAP = {
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".doc": "application/msword",
    ".pdf": "application/pdf",
    ".txt": "text/plain",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
}


def _is_true(raw: Optional[str], default: bool = False) -> bool:
    if raw is None:
        return default
    return str(raw).strip().lower() in {"1", "true", "yes", "y", "on"}


def _is_production() -> bool:
    env = (os.getenv("ENVIRONMENT") or os.getenv("APP_ENV") or "development").strip().lower()
    return env in {"production", "prod"}


def _allow_local_fallback() -> bool:
    # In production: disabled by default unless explicitly forced on.
    if _is_production():
        return _is_true(os.getenv("ALLOW_LOCAL_STORAGE_FALLBACK"), default=False)
    return _is_true(os.getenv("ALLOW_LOCAL_STORAGE_FALLBACK"), default=True)


@contextmanager
def _get_db():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set")
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    try:
        yield conn
    finally:
        conn.close()


def _get_company_storage_connection(company_id: str) -> Optional[Dict[str, Any]]:
    if not DATABASE_URL:
        return None
    try:
        with _get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT provider, is_active, is_default, config
                FROM company_storage_connections
                WHERE company_id = %s AND is_active = true
                ORDER BY is_default DESC, updated_at DESC, created_at DESC
                LIMIT 1
                """,
                (company_id,),
            )
            row = cur.fetchone()
            return dict(row) if row else None
    except Exception:
        return None


def _content_type(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    return _MIME_MAP.get(ext, "application/octet-stream")


def _auth_headers() -> dict:
    """Build auth headers — supports both JWT (eyJ...) and new sb_ key formats"""
    headers = {"apikey": SUPABASE_SERVICE_KEY}
    if SUPABASE_SERVICE_KEY.startswith("eyJ"):
        headers["Authorization"] = f"Bearer {SUPABASE_SERVICE_KEY}"
    else:
        headers["Authorization"] = f"Bearer {SUPABASE_SERVICE_KEY}"
    return headers


def _build_google_drive_service(service_account_json: Any):
    info = service_account_json
    if isinstance(service_account_json, str):
        info = json.loads(service_account_json)
    if not isinstance(info, dict):
        raise ValueError("service_account_json must be a JSON object")

    creds = service_account.Credentials.from_service_account_info(
        info,
        scopes=["https://www.googleapis.com/auth/drive"],
    )
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def _ensure_google_drive_company_folder(service, company_id: str, root_folder_id: Optional[str]) -> Optional[str]:
    # Folder isolation: each tenant gets its own deterministic folder.
    folder_name = f"company-{company_id}"
    safe_folder_name = folder_name.replace("'", "\\'")

    query_parts = [
        "mimeType='application/vnd.google-apps.folder'",
        f"name='{safe_folder_name}'",
        "trashed=false",
    ]
    if root_folder_id:
        query_parts.append(f"'{root_folder_id}' in parents")

    query = " and ".join(query_parts)
    result = service.files().list(
        q=query,
        fields="files(id,name)",
        pageSize=1,
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute()
    files = result.get("files", [])
    if files:
        return files[0]["id"]

    metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    if root_folder_id:
        metadata["parents"] = [root_folder_id]

    created = service.files().create(
        body=metadata,
        fields="id",
        supportsAllDrives=True,
    ).execute()
    return created.get("id")


def _parse_storage_path(storage_path: str) -> tuple[str, str]:
    if storage_path.startswith("gdrive://"):
        return "google_drive", storage_path.replace("gdrive://", "", 1)
    return "supabase", storage_path


def _upload_google_drive_sync(file_bytes: bytes, company_id: str, filename: str, config: Dict[str, Any]) -> dict:
    ct = _content_type(filename)
    service_account_json = config.get("service_account_json")
    if not service_account_json:
        raise RuntimeError("Google Drive connector missing service_account_json")

    root_folder_id = config.get("root_folder_id")
    service = _build_google_drive_service(service_account_json)
    company_folder_id = _ensure_google_drive_company_folder(service, company_id, root_folder_id)

    unique_filename = f"{uuid.uuid4()}_{filename}"
    media = MediaIoBaseUpload(io.BytesIO(file_bytes), mimetype=ct, resumable=False)
    file_metadata = {"name": unique_filename}
    if company_folder_id:
        file_metadata["parents"] = [company_folder_id]

    created = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id,name,webViewLink",
        supportsAllDrives=True,
    ).execute()

    return {
        "storage_path": f"gdrive://{created['id']}",
        "provider": "google_drive",
        "content_type": ct,
        "file_id": created["id"],
        "folder_id": company_folder_id,
    }


def _download_google_drive_sync(storage_id: str, config: Dict[str, Any]) -> bytes:
    service_account_json = config.get("service_account_json")
    if not service_account_json:
        raise RuntimeError("Google Drive connector missing service_account_json")

    service = _build_google_drive_service(service_account_json)
    request = service.files().get_media(fileId=storage_id, supportsAllDrives=True)
    output = io.BytesIO()
    downloader = MediaIoBaseDownload(output, request)

    done = False
    while not done:
        _, done = downloader.next_chunk()
    output.seek(0)
    return output.read()


def _delete_google_drive_sync(storage_id: str, config: Dict[str, Any]) -> bool:
    service_account_json = config.get("service_account_json")
    if not service_account_json:
        return False

    service = _build_google_drive_service(service_account_json)
    service.files().delete(fileId=storage_id, supportsAllDrives=True).execute()
    return True


def _get_effective_connector(company_id: str) -> Dict[str, Any]:
    conn = _get_company_storage_connection(company_id)
    if conn and conn.get("provider"):
        return conn
    return {
        "provider": DEFAULT_STORAGE_PROVIDER,
        "config": {},
        "is_active": True,
        "is_default": True,
    }


def _raise_storage_error(detail: str) -> None:
    print(f"Storage unavailable: {detail}")
    raise RuntimeError("Storage service temporarily unavailable")


async def upload_file(file_bytes: bytes, company_id: str, filename: str) -> dict:
    """Upload file to tenant connector. Returns {storage_path, provider, content_type}."""
    unique_name = f"{company_id}/{uuid.uuid4()}_{filename}"
    ct = _content_type(filename)

    connector = _get_effective_connector(company_id)
    provider = (connector.get("provider") or "supabase").lower()

    if provider == "google_drive":
        try:
            return await asyncio.to_thread(
                _upload_google_drive_sync,
                file_bytes,
                company_id,
                filename,
                connector.get("config") or {},
            )
        except Exception as e:
            print(f"Google Drive upload error: {e}")
            if _is_production():
                _raise_storage_error("Google Drive upload failed in production")

    if provider == "supabase" and SUPABASE_SERVICE_KEY:
        # Upload to Supabase Storage
        url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{unique_name}"
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    url,
                    content=file_bytes,
                    headers={
                        **_auth_headers(),
                        "Content-Type": ct
                    }
                )
                if resp.status_code in (200, 201):
                    return {"storage_path": unique_name, "provider": "supabase", "content_type": ct}
                else:
                    print(f"Supabase upload failed: {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"Supabase upload error: {e}")

        if _is_production():
            _raise_storage_error("Supabase upload failed in production")

    if not _allow_local_fallback():
        _raise_storage_error("Local fallback disabled by environment policy")

    # Local fallback (non-production by default)
    local_path = LOCAL_UPLOAD_DIR / unique_name
    local_path.parent.mkdir(parents=True, exist_ok=True)
    local_path.write_bytes(file_bytes)
    return {"storage_path": str(local_path), "provider": "local", "content_type": ct}


async def download_file(storage_path: str, company_id: Optional[str] = None) -> bytes:
    """Download file from storage path. For Google Drive, company_id is required."""
    provider, storage_id = _parse_storage_path(storage_path)

    if provider == "google_drive":
        if not company_id:
            _raise_storage_error("company_id required for Google Drive download")
        connector = _get_effective_connector(company_id)
        if (connector.get("provider") or "").lower() != "google_drive":
            _raise_storage_error("Google Drive connector not configured for company")
        return await asyncio.to_thread(
            _download_google_drive_sync,
            storage_id,
            connector.get("config") or {},
        )

    if SUPABASE_SERVICE_KEY and not storage_path.startswith("/"):
        url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{storage_path}"
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    url, 
                    headers=_auth_headers()
                )
                if resp.status_code == 200:
                    return resp.content
                else:
                    print(f"Supabase download failed: {resp.status_code}")
        except Exception as e:
            print(f"Supabase download error: {e}")

        if _is_production():
            _raise_storage_error("Supabase download failed in production")

    if not _allow_local_fallback():
        _raise_storage_error("Local fallback disabled by environment policy")

    # Local fallback (legacy)
    return Path(storage_path).read_bytes()


async def get_download_url(storage_path: str, expires_in: int = 3600, company_id: Optional[str] = None) -> str:
    """Get download URL. For Google Drive we return a stable ID URL if configured."""
    provider, storage_id = _parse_storage_path(storage_path)

    if provider == "google_drive":
        if not company_id:
            _raise_storage_error("company_id required for Google Drive URL")
        connector = _get_effective_connector(company_id)
        if (connector.get("provider") or "").lower() != "google_drive":
            _raise_storage_error("Google Drive connector not configured for company")
        return f"https://drive.google.com/file/d/{storage_id}/view"

    if SUPABASE_SERVICE_KEY and not storage_path.startswith("/"):
        url = f"{SUPABASE_URL}/storage/v1/object/sign/{BUCKET}/{storage_path}"
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    url, 
                    json={"expiresIn": expires_in},
                    headers=_auth_headers()
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return f"{SUPABASE_URL}/storage/v1{data['signedURL']}"
                else:
                    print(f"Supabase signed URL failed: {resp.status_code}")
        except Exception as e:
            print(f"Supabase signed URL error: {e}")

        if _is_production():
            _raise_storage_error("Supabase signed URL failed in production")

    if not _allow_local_fallback():
        _raise_storage_error("Local fallback disabled by environment policy")

    # Return local path for fallback
    return f"/uploads/{storage_path}"


async def delete_file(storage_path: str, company_id: Optional[str] = None) -> bool:
    """Delete file from storage."""
    provider, storage_id = _parse_storage_path(storage_path)

    if provider == "google_drive":
        if not company_id:
            return False
        connector = _get_effective_connector(company_id)
        if (connector.get("provider") or "").lower() != "google_drive":
            return False
        try:
            return await asyncio.to_thread(
                _delete_google_drive_sync,
                storage_id,
                connector.get("config") or {},
            )
        except Exception:
            return False

    if SUPABASE_SERVICE_KEY and not storage_path.startswith("/"):
        url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{storage_path}"
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.delete(
                    url,
                    headers=_auth_headers()
                )
                return resp.status_code == 200
        except Exception as e:
            print(f"Supabase delete error: {e}")
            return False

        if _is_production():
            return False

    if not _allow_local_fallback():
        return False

    # Local fallback
    try:
        Path(storage_path).unlink(missing_ok=True)
        return True
    except Exception:
        return False


async def test_google_drive_connector(company_id: str) -> dict:
    """Validate current tenant Google Drive connector and folder isolation."""
    connector = _get_effective_connector(company_id)
    provider = (connector.get("provider") or "").lower()
    if provider != "google_drive":
        return {"ok": False, "error": "Google Drive connector not active"}

    config = connector.get("config") or {}
    try:
        service = await asyncio.to_thread(_build_google_drive_service, config.get("service_account_json"))
        folder_id = await asyncio.to_thread(
            _ensure_google_drive_company_folder,
            service,
            company_id,
            config.get("root_folder_id"),
        )
        return {"ok": True, "provider": "google_drive", "company_folder_id": folder_id}
    except Exception as e:
        return {"ok": False, "error": str(e)}
