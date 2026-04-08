"""
Onboarding routes - Handles the post-signup onboarding chat flow.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from auth import get_current_user_id
from bson import ObjectId
from datetime import datetime, timezone
import logging

router = APIRouter(prefix="/api/onboarding", tags=["Onboarding"])

db = None

def set_database(database):
    global db
    db = database


class OnboardingData(BaseModel):
    usage_type: str  # "personal" or "business"
    company_name: Optional[str] = None
    company_location: Optional[str] = None
    company_description: Optional[str] = None
    industry: Optional[str] = None
    monthly_mrr: Optional[str] = None
    has_data_analyst: Optional[str] = None
    does_digital_marketing: Optional[str] = None
    data_preference: str  # "connect" or "synthetic"


@router.get("/status")
async def get_onboarding_status(user_id: str = Depends(get_current_user_id)):
    """Check if user has completed onboarding"""
    user = await db.users.find_one(
        {"_id": ObjectId(user_id)},
        {"onboarding_completed": 1, "name": 1}
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "completed": user.get("onboarding_completed", False),
        "name": user.get("name", "")
    }


@router.post("/save")
async def save_onboarding(data: OnboardingData, user_id: str = Depends(get_current_user_id)):
    """Save onboarding data and mark as completed"""
    onboarding_doc = data.model_dump()
    onboarding_doc["completed_at"] = datetime.now(timezone.utc).isoformat()

    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {
            "$set": {
                "onboarding_completed": True,
                "onboarding_data": onboarding_doc,
            }
        }
    )
    logging.info(f"Onboarding completed for user {user_id}")
    return {"success": True, "message": "Onboarding completed"}


@router.get("/admin/all")
async def get_all_onboarding_data(user_id: str = Depends(get_current_user_id)):
    """Admin: Get onboarding data for all users"""
    user = await db.users.find_one({"_id": ObjectId(user_id)}, {"role": 1, "email": 1})
    if not user or (user.get("role") != "admin" and user.get("email", "").lower() != "admin@analiyx.com"):
        raise HTTPException(status_code=403, detail="Admin access required")

    users = await db.users.find(
        {"onboarding_completed": True},
        {"_id": 0, "name": 1, "email": 1, "phone": 1, "onboarding_data": 1, "created_at": 1}
    ).to_list(500)

    return {"users": users}
