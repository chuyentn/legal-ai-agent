"""
Billing & Payments endpoints
- PayPal checkout & capture
- MoMo checkout & callback
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from typing import Dict, Any

from ..middleware.auth import get_current_active_user
from ..services.billing_service import (
    create_paypal_order,
    capture_paypal_order,
    create_momo_payment,
    verify_momo_callback,
)

router = APIRouter(prefix="/v1/billing", tags=["Billing"])


class CreateCheckoutRequest(BaseModel):
    plan_id: str = Field(..., description="trial | starter | pro")


class PayPalCaptureRequest(BaseModel):
    order_id: str


@router.post("/paypal/checkout")
async def paypal_checkout(
    body: CreateCheckoutRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
):
    """
    Tạo PayPal order, trả về approval_url để frontend redirect.
    """
    try:
        url = await create_paypal_order(
            company_id=str(current_user["company_id"]),
            plan_id=body.plan_id,
        )
        return {"approval_url": url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/paypal/capture")
async def paypal_capture(
    body: PayPalCaptureRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
):
    """
    Capture PayPal order sau khi user đã approve.
    Frontend gọi endpoint này với order_id từ PayPal.
    """
    try:
        company_id, plan_id = await capture_paypal_order(body.order_id)
        return {
            "status": "success",
            "company_id": company_id,
            "plan_id": plan_id,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/momo/checkout")
async def momo_checkout(
    body: CreateCheckoutRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
):
    """
    Tạo yêu cầu thanh toán MoMo, trả về payUrl để frontend redirect.
    """
    try:
        pay_url = await create_momo_payment(
            company_id=str(current_user["company_id"]),
            plan_id=body.plan_id,
            user_id=str(current_user["id"]),
        )
        return {"payUrl": pay_url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/momo/callback")
async def momo_callback(request: Request):
    """
    Endpoint nhận callback từ MoMo (ipnUrl).
    MoMo có thể gửi JSON hoặc form-urlencoded.
    """
    try:
        if request.headers.get("content-type", "").startswith("application/json"):
            params = await request.json()
        else:
            form = await request.form()
            params = dict(form)

        company_id, plan_id = verify_momo_callback(params)
        return {"status": "success", "company_id": company_id, "plan_id": plan_id}
    except Exception as e:
        return {"status": "error", "message": str(e)}
