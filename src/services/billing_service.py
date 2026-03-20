import hmac
import hashlib
import json
import uuid
from typing import Dict, Any, Optional, Tuple

import httpx
from psycopg2.extras import RealDictCursor

from ..middleware.auth import get_db
from ..core.config import settings


def get_plan_config(plan_id: str) -> Dict[str, Any]:
    """
    Định nghĩa tạm các gói plan.
    Sau này có thể chuyển sang bảng plans trong DB.
    """
    plans: Dict[str, Dict[str, Any]] = {
        "trial": {"name": "Trial", "monthly_quota": 100, "price_usd": 0},
        "starter": {"name": "Starter", "monthly_quota": 1000, "price_usd": 9},
        "pro": {"name": "Pro", "monthly_quota": 5000, "price_usd": 29},
    }
    if plan_id not in plans:
        raise ValueError("Invalid plan_id")
    return plans[plan_id]


def update_company_plan(
    company_id: str, plan_id: str, tx_id: Optional[str] = None
) -> None:
    """
    Cập nhật plan & quota cho company sau khi thanh toán thành công.
    Reset used_quota về 0.
    """
    plan = get_plan_config(plan_id)
    with get_db() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            """
            UPDATE companies
            SET plan = %s::plan_type,
                monthly_quota = %s,
                used_quota = 0,
                updated_at = now()
            WHERE id = %s
        """,
            (plan_id, plan["monthly_quota"], company_id),
        )
        conn.commit()


# ==========================
# PayPal
# ==========================


async def create_paypal_order(company_id: str, plan_id: str) -> str:
    """
    Tạo PayPal order và trả về approval_url để frontend redirect.
    """
    if not (
        settings.paypal_client_id
        and settings.paypal_client_secret
        and settings.paypal_api_url
    ):
        raise RuntimeError("PayPal is not configured")

    plan = get_plan_config(plan_id)
    amount = plan["price_usd"]

    body = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "reference_id": f"{company_id}:{plan_id}",
                "amount": {
                    "currency_code": "USD",
                    "value": str(amount),
                },
            }
        ],
        "application_context": {
            "brand_name": "Legal AI Agent",
            "landing_page": "LOGIN",
            "user_action": "PAY_NOW",
        },
    }

    auth = (settings.paypal_client_id, settings.paypal_client_secret)

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(
            f"{settings.paypal_api_url}/v2/checkout/orders",
            auth=auth,
            json=body,
        )
        resp.raise_for_status()
        data = resp.json()

    links = data.get("links", [])
    approval_url: Optional[str] = None
    for link in links:
        if link.get("rel") == "approve":
            approval_url = link.get("href")
            break

    if not approval_url:
        raise RuntimeError("Cannot find PayPal approval URL")

    return approval_url


async def capture_paypal_order(order_id: str) -> Tuple[str, str]:
    """
    Capture order sau khi user approve trên PayPal.
    Trả về (company_id, plan_id) nếu thành công.
    """
    if not (
        settings.paypal_client_id
        and settings.paypal_client_secret
        and settings.paypal_api_url
    ):
        raise RuntimeError("PayPal is not configured")

    auth = (settings.paypal_client_id, settings.paypal_client_secret)

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(
            f"{settings.paypal_api_url}/v2/checkout/orders/{order_id}/capture",
            auth=auth,
        )
        resp.raise_for_status()
        data = resp.json()

    try:
        purchase_unit = data["purchase_units"][0]
        reference_id = purchase_unit.get("reference_id", "")
        company_id, plan_id = reference_id.split(":")
    except Exception:
        raise RuntimeError("Invalid PayPal capture payload")

    update_company_plan(company_id, plan_id, tx_id=order_id)
    return company_id, plan_id


# ==========================
# MoMo
# ==========================


def _momo_signature(payload: Dict[str, Any]) -> str:
    """
    Tạo signature cho MoMo theo format raw query string.
    """
    raw_items = [
        f"accessKey={settings.momo_access_key}",
        f"amount={payload['amount']}",
        f"extraData={payload['extraData']}",
        f"ipnUrl={payload['ipnUrl']}",
        f"orderId={payload['orderId']}",
        f"orderInfo={payload['orderInfo']}",
        f"partnerCode={settings.momo_partner_code}",
        f"redirectUrl={payload['redirectUrl']}",
        f"requestId={payload['requestId']}",
        f"requestType={payload['requestType']}",
    ]
    raw_string = "&".join(raw_items)
    h = hmac.new(
        settings.momo_secret_key.encode("utf-8"),
        raw_string.encode("utf-8"),
        hashlib.sha256,
    )
    return h.hexdigest()


async def create_momo_payment(
    company_id: str, plan_id: str, user_id: str
) -> str:
    """
    Tạo yêu cầu thanh toán MoMo, trả về payUrl để frontend redirect.
    """
    if not (
        settings.momo_partner_code
        and settings.momo_access_key
        and settings.momo_secret_key
        and settings.momo_endpoint
        and settings.app_base_url
    ):
        raise RuntimeError("MoMo is not configured")

    plan = get_plan_config(plan_id)
    amount = int(plan["price_usd"] * 25000)  # ví dụ: USD -> VND

    order_id = str(uuid.uuid4())
    request_id = str(uuid.uuid4())

    redirect_url = f"{settings.app_base_url}/billing/momo/return"
    ipn_url = f"{settings.app_base_url}/v1/billing/momo/callback"

    extra_data_obj = {"company_id": company_id, "plan_id": plan_id, "user_id": user_id}
    extra_data = json.dumps(extra_data_obj)

    payload: Dict[str, Any] = {
        "partnerCode": settings.momo_partner_code,
        "accessKey": settings.momo_access_key,
        "requestId": request_id,
        "amount": str(amount),
        "orderId": order_id,
        "orderInfo": f"Upgrade plan {plan_id} for company {company_id}",
        "redirectUrl": redirect_url,
        "ipnUrl": ipn_url,
        "extraData": extra_data,
        "requestType": "captureWallet",
        "lang": "vi",
    }

    signature = _momo_signature(payload)
    payload["signature"] = signature

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(str(settings.momo_endpoint), json=payload)
        resp.raise_for_status()
        data = resp.json()

    if data.get("resultCode") != 0:
        raise RuntimeError(f"MoMo error: {data.get('message')}")

    pay_url = data.get("payUrl")
    if not pay_url:
        raise RuntimeError("MoMo payUrl not found")

    return pay_url


def verify_momo_callback(params: Dict[str, Any]) -> Tuple[str, str]:
    """
    Xác minh callback của MoMo.
    Trả về (company_id, plan_id) nếu hợp lệ.
    Hiện tại đơn giản: tin vào extraData khi resultCode == 0.
    """
    if not settings.momo_secret_key:
        raise RuntimeError("MoMo is not configured")

    if str(params.get("resultCode")) != "0":
        raise RuntimeError("MoMo payment not successful")

    extra_data_raw = params.get("extraData") or "{}"
    try:
        extra_data = json.loads(extra_data_raw)
        company_id = extra_data["company_id"]
        plan_id = extra_data["plan_id"]
    except Exception:
        raise RuntimeError("Invalid MoMo extraData")

    update_company_plan(company_id, plan_id, tx_id=params.get("transId"))
    return company_id, plan_id
