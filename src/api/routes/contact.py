"""
Public contact/lead endpoint.
Forwards website lead requests to Google Apps Script webhook (if configured).
"""
from datetime import datetime, timezone
import json
import os

import httpx
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

from ..middleware.auth import get_db

router = APIRouter(prefix="/v1/contact", tags=["contact"])


class ContactLeadRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=120)
    law_firm: str = Field(..., min_length=2, max_length=180)
    email: EmailStr
    phone: str = Field(..., min_length=7, max_length=40)
    ai_level: str = Field(..., min_length=2, max_length=80)
    needs: List[str] = Field(default_factory=list)
    detail: Optional[str] = Field(default="", max_length=4000)
    source: str = Field(default="legal-ai-landing")


@router.post("/lead")
async def submit_contact_lead(payload: ContactLeadRequest, request: Request):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO customer_leads (
                    source, full_name, company_name, email, phone, ai_level, needs, detail, status, metadata
                ) VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s, 'new', %s::jsonb)
                """,
                (
                    payload.source,
                    payload.full_name,
                    payload.law_firm,
                    str(payload.email),
                    payload.phone,
                    payload.ai_level,
                    json.dumps(payload.needs, ensure_ascii=False),
                    payload.detail or "",
                    json.dumps(
                        {
                            "origin": request.headers.get("origin") or "",
                            "referer": request.headers.get("referer") or "",
                            "user_agent": request.headers.get("user-agent", ""),
                            "client_ip": request.client.host if request.client else "",
                        },
                        ensure_ascii=False,
                    ),
                ),
            )
            conn.commit()
    except Exception:
        # Internal lead storage should not block public lead capture.
        pass

    webhook_url = (os.getenv("GOOGLE_APPS_SCRIPT_WEBHOOK_URL") or "").strip()
    if not webhook_url:
        raise HTTPException(
            status_code=503,
            detail="Lead webhook chưa được cấu hình. Vui lòng liên hệ quản trị hệ thống.",
        )

    event = {
        "event": "contact_lead",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": payload.source,
        "full_name": payload.full_name,
        "law_firm": payload.law_firm,
        "email": str(payload.email),
        "phone": payload.phone,
        "ai_level": payload.ai_level,
        "needs": payload.needs,
        "detail": payload.detail or "",
        "page_url": request.headers.get("origin") or request.headers.get("referer") or "",
        "user_agent": request.headers.get("user-agent", ""),
        "client_ip": request.client.host if request.client else "",
    }

    timeout = httpx.Timeout(15.0, connect=10.0)
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(webhook_url, json=event)
            if resp.status_code >= 400:
                fallback_payload = {"payload": json.dumps(event, ensure_ascii=False)}
                resp = await client.post(webhook_url, data=fallback_payload)

            if resp.status_code >= 400:
                raise HTTPException(
                    status_code=502,
                    detail=f"Webhook rejected request (status {resp.status_code}).",
                )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Không gửi được lead tới webhook: {exc}")

    return {"ok": True, "message": "Lead đã được gửi thành công."}
