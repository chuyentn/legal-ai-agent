import os
import httpx
import logging

logger = logging.getLogger(__name__)

WEBHOOK_URL = os.getenv("GOOGLE_APPS_SCRIPT_WEBHOOK_URL")


async def send_lead_to_apps_script(
    full_name: str,
    email: str,
    company_name: str = "",
    source: str = "legal-ai-agent-app",
):
    """
    Gửi thông tin user mới sang Google Apps Script (CRM).
    Không làm hỏng flow đăng ký nếu webhook lỗi.
    """
    if not WEBHOOK_URL:
        logger.warning(
            "GOOGLE_APPS_SCRIPT_WEBHOOK_URL not set; skip CRM sync."
        )
        return

    payload = {
        "name": full_name,
        "email": email,
        "company_name": company_name,
        "source": source,
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(WEBHOOK_URL, json=payload)
            if resp.status_code >= 400:
                logger.warning(
                    "CRM webhook error %s: %s",
                    resp.status_code,
                    resp.text,
                )
    except Exception as e:
        logger.exception("Failed to send CRM webhook: %s", e)
