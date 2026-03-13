"""Cashfree payment integration routes"""
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from auth import get_current_user_id
from datetime import datetime
from bson import ObjectId
from cashfree_pg.api_client import Cashfree
from cashfree_pg.models.create_order_request import CreateOrderRequest
from cashfree_pg.models.customer_details import CustomerDetails
from cashfree_pg.models.order_meta import OrderMeta
import os
import uuid
import json
import logging

router = APIRouter(prefix="/api/payments", tags=["Payments"])

db = None

PLANS = {
    "Starter": {"amount": 2999, "credits": 100, "name": "Starter"},
    "Business Pro": {"amount": 7999, "credits": 1000, "name": "Business Pro"},
}

def set_database(database):
    global db
    db = database

def init_cashfree():
    """Initialize and return Cashfree client"""
    client_id = os.environ.get("CASHFREE_CLIENT_ID")
    client_secret = os.environ.get("CASHFREE_CLIENT_SECRET")
    env = os.environ.get("CASHFREE_ENVIRONMENT", "SANDBOX")
    cf_env = Cashfree.PRODUCTION if env == "PRODUCTION" else Cashfree.SANDBOX
    return Cashfree(cf_env, client_id, client_secret)

class CreatePaymentRequest(BaseModel):
    plan: str
    return_url: str = ""

@router.post("/create-order")
async def create_payment_order(req: CreatePaymentRequest, user_id: str = Depends(get_current_user_id)):
    """Create a Cashfree payment order for plan upgrade"""
    if req.plan not in PLANS:
        raise HTTPException(status_code=400, detail=f"Invalid plan. Choose from: {list(PLANS.keys())}")
    
    plan = PLANS[req.plan]
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    init_cashfree()
    
    order_id = f"analiyx_{user_id[:8]}_{uuid.uuid4().hex[:8]}"
    
    customer_details = CustomerDetails(
        customer_id=user_id[:50],
        customer_phone="9999999999",
        customer_email=user["email"],
        customer_name=user.get("name", "User")
    )
    
    frontend_url = os.environ.get("FRONTEND_URL", req.return_url or "https://insights-hub-44.preview.emergentagent.com")
    
    order_meta = OrderMeta(
        return_url=f"{frontend_url}/dashboard?payment_status=success&order_id={order_id}"
    )
    
    create_order_request = CreateOrderRequest(
        order_amount=float(plan["amount"]),
        order_currency="INR",
        order_id=order_id,
        customer_details=customer_details,
        order_meta=order_meta,
        order_note=f"Analiyx {plan['name']} Plan Subscription"
    )
    
    try:
        cf = init_cashfree()
        api_response = cf.PGCreateOrder(
            x_api_version="2025-01-01",
            create_order_request=create_order_request
        )
        
        if api_response and api_response.data:
            # Save order in DB
            order_doc = {
                "order_id": order_id,
                "cf_order_id": api_response.data.cf_order_id,
                "user_id": ObjectId(user_id),
                "plan": req.plan,
                "amount": plan["amount"],
                "currency": "INR",
                "status": "CREATED",
                "payment_session_id": api_response.data.payment_session_id,
                "created_at": datetime.utcnow()
            }
            await db.payment_orders.insert_one(order_doc)
            
            return {
                "success": True,
                "order_id": order_id,
                "cf_order_id": api_response.data.cf_order_id,
                "payment_session_id": api_response.data.payment_session_id,
                "order_amount": plan["amount"],
                "order_currency": "INR"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create payment order")
    except Exception as e:
        logging.error(f"Cashfree order creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Payment order creation failed: {str(e)}")

@router.get("/order-status/{order_id}")
async def get_order_status(order_id: str, user_id: str = Depends(get_current_user_id)):
    """Check payment order status"""
    
    try:
        cf = init_cashfree()
        api_response = cf.PGFetchOrder(
            x_api_version="2025-01-01",
            order_id=order_id
        )
        
        if api_response and api_response.data:
            # Update order in DB
            order_status = api_response.data.order_status
            await db.payment_orders.update_one(
                {"order_id": order_id},
                {"$set": {"status": order_status, "updated_at": datetime.utcnow()}}
            )
            
            # If payment is successful, upgrade user
            if order_status == "PAID":
                order = await db.payment_orders.find_one({"order_id": order_id})
                if order:
                    plan_name = order["plan"]
                    plan_credits = PLANS.get(plan_name, {}).get("credits", 100)
                    await db.users.update_one(
                        {"_id": order["user_id"]},
                        {"$set": {
                            "plan": plan_name,
                            "status": "active",
                            "updated_at": datetime.utcnow()
                        }, "$inc": {"credits": plan_credits}}
                    )
            
            return {
                "order_id": order_id,
                "order_status": order_status,
                "order_amount": api_response.data.order_amount,
                "order_currency": api_response.data.order_currency
            }
        else:
            raise HTTPException(status_code=404, detail="Order not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook")
async def payment_webhook(request: Request):
    """Handle Cashfree payment webhook"""
    try:
        raw_body = await request.body()
        webhook_data = json.loads(raw_body.decode('utf-8'))
        
        event_type = webhook_data.get('type')
        
        if event_type == 'PAYMENT_SUCCESS_WEBHOOK':
            payment_data = webhook_data.get('data', {})
            order_data = payment_data.get('order', {})
            order_id = order_data.get('order_id')
            
            if order_id:
                order = await db.payment_orders.find_one({"order_id": order_id})
                if order:
                    await db.payment_orders.update_one(
                        {"order_id": order_id},
                        {"$set": {"status": "PAID", "webhook_data": webhook_data, "updated_at": datetime.utcnow()}}
                    )
                    
                    plan_name = order["plan"]
                    plan_credits = PLANS.get(plan_name, {}).get("credits", 100)
                    await db.users.update_one(
                        {"_id": order["user_id"]},
                        {"$set": {"plan": plan_name, "status": "active"}, "$inc": {"credits": plan_credits}}
                    )
        
        return JSONResponse(status_code=200, content={"status": "received"})
    except Exception as e:
        logging.error(f"Webhook error: {str(e)}")
        return JSONResponse(status_code=200, content={"error": str(e)})
