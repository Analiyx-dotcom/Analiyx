"""Razorpay payment integration routes"""
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from auth import get_current_user_id
from datetime import datetime, timedelta
from bson import ObjectId
import razorpay
import os
import json
import logging
import hmac
import hashlib

router = APIRouter(prefix="/api/payments", tags=["Payments"])

db = None

PLANS = {
    "Starter": {"amount": 6000, "credits": 100, "name": "Starter", "duration_months": 12},
    "Business Pro": {"amount": 9000, "credits": 1000, "name": "Business Pro", "duration_months": 12},
}

def set_database(database):
    global db
    db = database

def get_razorpay_client():
    key_id = os.environ.get("RAZORPAY_KEY_ID")
    key_secret = os.environ.get("RAZORPAY_KEY_SECRET")
    if not key_id or not key_secret:
        raise HTTPException(status_code=500, detail="Razorpay keys not configured")
    return razorpay.Client(auth=(key_id, key_secret))

class CreatePaymentRequest(BaseModel):
    plan: str
    coupon_code: Optional[str] = None

@router.post("/create-order")
async def create_payment_order(req: CreatePaymentRequest, user_id: str = Depends(get_current_user_id)):
    """Create a Razorpay payment order for plan upgrade"""
    if req.plan not in PLANS:
        raise HTTPException(status_code=400, detail=f"Invalid plan. Choose from: {list(PLANS.keys())}")

    plan = PLANS[req.plan]
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Calculate amount with optional coupon
    final_amount = plan["amount"]
    discount_percentage = 0
    coupon_code = None

    if req.coupon_code:
        coupon = await db.coupons.find_one({"code": req.coupon_code.upper(), "is_active": True})
        if not coupon:
            raise HTTPException(status_code=400, detail="Invalid or expired coupon code")
        discount_percentage = coupon["discount_percentage"]
        coupon_code = coupon["code"]
        discount = (final_amount * discount_percentage) // 100
        final_amount = final_amount - discount

    if final_amount < 1:
        final_amount = 1  # Razorpay requires minimum 1 INR

    client = get_razorpay_client()

    try:
        order_data = {
            "amount": final_amount * 100,  # Razorpay expects paise
            "currency": "INR",
            "payment_capture": 1,
            "notes": {
                "plan": req.plan,
                "user_id": user_id,
                "user_email": user["email"],
                "coupon_code": coupon_code or "",
                "discount_percentage": str(discount_percentage)
            }
        }
        razorpay_order = client.order.create(data=order_data)

        # Save order in DB
        order_doc = {
            "order_id": razorpay_order["id"],
            "user_id": ObjectId(user_id),
            "plan": req.plan,
            "original_amount": plan["amount"],
            "discount_percentage": discount_percentage,
            "coupon_code": coupon_code,
            "amount": final_amount,
            "currency": "INR",
            "status": "created",
            "duration_months": plan["duration_months"],
            "created_at": datetime.utcnow()
        }
        await db.payment_orders.insert_one(order_doc)

        # Increment coupon usage count
        if coupon_code:
            await db.coupons.update_one({"code": coupon_code}, {"$inc": {"usage_count": 1}})

        return {
            "success": True,
            "order_id": razorpay_order["id"],
            "amount": final_amount * 100,
            "original_amount": plan["amount"] * 100,
            "discount_percentage": discount_percentage,
            "currency": "INR",
            "key_id": os.environ.get("RAZORPAY_KEY_ID"),
            "user_name": user.get("name", "User"),
            "user_email": user["email"],
            "plan_name": plan["name"]
        }
    except Exception as e:
        logging.error(f"Razorpay order creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Payment order creation failed: {str(e)}")

class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

@router.post("/verify-payment")
async def verify_payment(req: VerifyPaymentRequest, user_id: str = Depends(get_current_user_id)):
    """Verify Razorpay payment signature and upgrade user plan"""
    client = get_razorpay_client()

    try:
        # Verify signature
        params_dict = {
            "razorpay_order_id": req.razorpay_order_id,
            "razorpay_payment_id": req.razorpay_payment_id,
            "razorpay_signature": req.razorpay_signature
        }
        client.utility.verify_payment_signature(params_dict)
    except razorpay.errors.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Payment verification failed. Invalid signature.")

    # Payment verified - upgrade user
    order = await db.payment_orders.find_one({"order_id": req.razorpay_order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    plan_name = order["plan"]
    plan = PLANS.get(plan_name, {})
    duration_months = plan.get("duration_months", 12)
    subscription_end = datetime.utcnow() + timedelta(days=duration_months * 30)

    # Update order status
    await db.payment_orders.update_one(
        {"order_id": req.razorpay_order_id},
        {"$set": {
            "status": "PAID",
            "payment_id": req.razorpay_payment_id,
            "signature": req.razorpay_signature,
            "updated_at": datetime.utcnow()
        }}
    )

    # Upgrade user plan
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {
            "plan": plan_name,
            "status": "active",
            "subscription_end_date": subscription_end,
            "updated_at": datetime.utcnow()
        }, "$inc": {"credits": plan.get("credits", 100)}}
    )

    # Send payment confirmation email
    try:
        from email_service import send_payment_confirmation
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            send_payment_confirmation(
                user["email"], user.get("name", "User"),
                plan_name, order.get("amount", 0),
                subscription_end.strftime("%d %b %Y")
            )
    except Exception:
        pass

    return {
        "success": True,
        "message": f"Payment verified. Plan upgraded to {plan_name}.",
        "plan": plan_name,
        "subscription_end_date": subscription_end.isoformat()
    }


@router.post("/validate-coupon")
async def validate_coupon(req: dict, user_id: str = Depends(get_current_user_id)):
    """Validate a coupon code and return discount info"""
    code = req.get("code", "").strip().upper()
    plan = req.get("plan", "")
    if not code:
        raise HTTPException(status_code=400, detail="Coupon code is required")
    if plan not in PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan")

    coupon = await db.coupons.find_one({"code": code, "is_active": True})
    if not coupon:
        raise HTTPException(status_code=400, detail="Invalid or expired coupon code")

    plan_amount = PLANS[plan]["amount"]
    discount = (plan_amount * coupon["discount_percentage"]) // 100
    final_amount = max(plan_amount - discount, 1)

    return {
        "valid": True,
        "code": coupon["code"],
        "discount_percentage": coupon["discount_percentage"],
        "original_amount": plan_amount,
        "discount_amount": discount,
        "final_amount": final_amount
    }


@router.get("/order-status/{order_id}")
async def get_order_status(order_id: str, user_id: str = Depends(get_current_user_id)):
    """Check payment order status"""
    order = await db.payment_orders.find_one({"order_id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return {
        "order_id": order_id,
        "order_status": order.get("status", "unknown"),
        "plan": order.get("plan"),
        "amount": order.get("amount")
    }

@router.post("/webhook")
async def payment_webhook(request: Request):
    """Handle Razorpay payment webhook"""
    try:
        raw_body = await request.body()
        webhook_data = json.loads(raw_body.decode("utf-8"))
        event = webhook_data.get("event")

        if event == "payment.captured":
            payment = webhook_data.get("payload", {}).get("payment", {}).get("entity", {})
            order_id = payment.get("order_id")
            if order_id:
                order = await db.payment_orders.find_one({"order_id": order_id})
                if order and order.get("status") != "PAID":
                    plan_name = order["plan"]
                    plan = PLANS.get(plan_name, {})
                    duration_months = plan.get("duration_months", 12)
                    subscription_end = datetime.utcnow() + timedelta(days=duration_months * 30)

                    await db.payment_orders.update_one(
                        {"order_id": order_id},
                        {"$set": {"status": "PAID", "webhook_data": webhook_data, "updated_at": datetime.utcnow()}}
                    )
                    await db.users.update_one(
                        {"_id": order["user_id"]},
                        {"$set": {
                            "plan": plan_name,
                            "status": "active",
                            "subscription_end_date": subscription_end
                        }, "$inc": {"credits": plan.get("credits", 100)}}
                    )

        return JSONResponse(status_code=200, content={"status": "received"})
    except Exception as e:
        logging.error(f"Webhook error: {str(e)}")
        return JSONResponse(status_code=200, content={"error": str(e)})
