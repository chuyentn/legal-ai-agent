"""
Storage Connectors API (User self-service)
Allow company admin to manage their own Google Drive/Supabase connector
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from pydantic import BaseModel
from psycopg2.extras import RealDictCursor
import json
from ..middleware.auth import get_current_user, get_db

router = APIRouter(prefix="/v1/storage/connectors", tags=["storage-connectors"])

class GoogleDriveConnectorPayload(BaseModel):
    service_account_json: Dict[str, Any]
    root_folder_id: Optional[str] = None
    auto_backup: bool = True
    realtime_sync: bool = True
    is_default: bool = True
    is_active: bool = True

@router.get("/me")
async def get_my_storage_connectors(current_user: Dict = Depends(get_current_user)):
    """List storage connectors for current user's company."""
    company_id = current_user["company_id"]
    with get_db() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            """
            SELECT id, provider, is_active, is_default, config, created_at, updated_at
            FROM company_storage_connections
            WHERE company_id = %s
            ORDER BY is_default DESC, updated_at DESC
            """,
            (company_id,),
        )
        rows = cur.fetchall()
    connectors = []
    for row in rows:
        item = dict(row)
        config = item.get("config") or {}
        item["id"] = str(item["id"])
        item["has_service_account"] = bool(config.get("service_account_json"))
        item["root_folder_id"] = config.get("root_folder_id")
        item["auto_backup"] = bool(config.get("auto_backup", True))
        item["realtime_sync"] = bool(config.get("realtime_sync", True))
        item.pop("config", None)
        if item.get("created_at"):
            item["created_at"] = item["created_at"].isoformat()
        if item.get("updated_at"):
            item["updated_at"] = item["updated_at"].isoformat()
        connectors.append(item)
    return {"connectors": connectors}

@router.post("/google-drive")
async def upsert_my_google_drive_connector(
    payload: GoogleDriveConnectorPayload,
    current_user: Dict = Depends(get_current_user),
):
    """Upsert Google Drive connector for current user's company."""
    company_id = current_user["company_id"]
    config = {
        "service_account_json": payload.service_account_json,
        "root_folder_id": payload.root_folder_id,
        "auto_backup": payload.auto_backup,
        "realtime_sync": payload.realtime_sync,
    }
    with get_db() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        if payload.is_default:
            cur.execute(
                """
                UPDATE company_storage_connections
                SET is_default = false, updated_at = now()
                WHERE company_id = %s
                """,
                (company_id,),
            )
        cur.execute(
            """
            INSERT INTO company_storage_connections (
                company_id, provider, is_active, is_default, config, created_at, updated_at
            )
            VALUES (%s, 'google_drive', %s, %s, %s::jsonb, now(), now())
            ON CONFLICT (company_id, provider)
            DO UPDATE SET
                is_active = EXCLUDED.is_active,
                is_default = EXCLUDED.is_default,
                config = EXCLUDED.config,
                updated_at = now()
            RETURNING id, provider, is_active, is_default, created_at, updated_at
            """,
            (
                company_id,
                payload.is_active,
                payload.is_default,
                json.dumps(config, ensure_ascii=False),
            ),
        )
        connector = dict(cur.fetchone())
        conn.commit()
    connector["id"] = str(connector["id"])
    if connector.get("created_at"):
        connector["created_at"] = connector["created_at"].isoformat()
    if connector.get("updated_at"):
        connector["updated_at"] = connector["updated_at"].isoformat()
    connector["provider"] = "google_drive"
    connector["message"] = "Google Drive connector đã được cấu hình cho công ty của bạn"
    return connector

@router.delete("/{connector_id}")
async def delete_my_storage_connector(connector_id: str, current_user: Dict = Depends(get_current_user)):
    """Delete a storage connector for current user's company."""
    company_id = current_user["company_id"]
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            DELETE FROM company_storage_connections
            WHERE id = %s AND company_id = %s
            """,
            (connector_id, company_id),
        )
        conn.commit()
    return {"message": "Connector deleted"}
