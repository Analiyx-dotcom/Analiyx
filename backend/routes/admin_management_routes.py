"""
Admin management routes for user control, subscription management, and trial extensions
"""

from fastapi import APIRouter, HTTPException, Depends
from auth import require_admin
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from bson import ObjectId

router = APIRouter(prefix="/api/admin/manage", tags=["Admin Management"])

# Database will be injected
db = None

def set_database(database):
    global db
    db = database

class UserStatusUpdate(BaseModel):
    status: str  # "active" or "inactive"

class TrialExtension(BaseModel):
    days: int = 7

class CreditUpdate(BaseModel):
    credits: int
    action: str  # "add", "remove", "set"

@router.get("/users/details")
async def get_all_users_details(admin_user: dict = Depends(require_admin)):
    """Get detailed list of all users with subscriptions"""
    
    users = await db.users.find().sort("created_at", -1).to_list(1000)
    
    detailed_users = []
    for user in users:
        user_id = user["_id"]
        
        # Get subscription info
        subscription = await db.subscriptions.find_one({"user_id": user_id})
        
        # Get data sources count
        data_sources_count = await db.uploaded_files.count_documents({"user_id": user_id})
        data_sources_count += await db.integrations.count_documents({"user_id": user_id, "status": "connected"})
        
        detailed_users.append({
            "id": str(user_id),
            "name": user["name"],
            "email": user["email"],
            "plan": user.get("plan", "Starter"),
            "status": user.get("status", "active"),
            "role": user.get("role", "user"),
            "credits": user.get("credits", 0),
            "created_at": user["created_at"].isoformat(),
            "subscription_status": subscription.get("status") if subscription else "none",
            "subscription_end_date": subscription.get("end_date").isoformat() if subscription and subscription.get("end_date") else None,
            "data_sources_count": data_sources_count,
            "last_login": user.get("updated_at", user["created_at"]).isoformat()
        })
    
    return {"users": detailed_users, "total": len(detailed_users)}

@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: str,
    update: UserStatusUpdate,
    admin_user: dict = Depends(require_admin)
):
    """Enable or disable a user account"""
    
    result = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"status": update.status, "updated_at": datetime.utcnow()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "success": True,
        "message": f"User account {'enabled' if update.status == 'active' else 'disabled'} successfully"
    }

@router.post("/users/{user_id}/extend-trial")
async def extend_trial(
    user_id: str,
    extension: TrialExtension,
    admin_user: dict = Depends(require_admin)
):
    """Extend user's trial period"""
    
    # Get or create subscription
    subscription = await db.subscriptions.find_one({"user_id": ObjectId(user_id)})
    
    new_end_date = datetime.utcnow() + timedelta(days=extension.days)
    
    # Update user's trial_ends_at
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    current_end = user.get("trial_ends_at")
    if current_end and current_end > datetime.utcnow():
        new_end_date = current_end + timedelta(days=extension.days)
    
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"trial_ends_at": new_end_date, "status": "active", "updated_at": datetime.utcnow()}}
    )
    
    if subscription:
        # Update existing subscription
        result = await db.subscriptions.update_one(
            {"_id": subscription["_id"]},
            {
                "$set": {
                    "end_date": new_end_date,
                    "status": "active"
                }
            }
        )
    else:
        # Create new trial subscription
        await db.subscriptions.insert_one({
            "user_id": ObjectId(user_id),
            "plan": "Trial",
            "status": "active",
            "amount": 0,
            "start_date": datetime.utcnow(),
            "end_date": new_end_date,
            "created_at": datetime.utcnow()
        })
    
    return {
        "success": True,
        "message": f"Trial extended by {extension.days} days",
        "new_end_date": new_end_date.isoformat()
    }

@router.put("/users/{user_id}/credits")
async def manage_user_credits(
    user_id: str,
    update: CreditUpdate,
    admin_user: dict = Depends(require_admin)
):
    """Add, remove, or set user credits"""
    
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    current_credits = user.get("credits", 0)
    
    if update.action == "add":
        new_credits = current_credits + update.credits
    elif update.action == "remove":
        new_credits = max(0, current_credits - update.credits)
    elif update.action == "set":
        new_credits = update.credits
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'add', 'remove', or 'set'")
    
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"credits": new_credits, "updated_at": datetime.utcnow()}}
    )
    
    return {
        "success": True,
        "message": f"Credits {update.action}ed successfully",
        "previous_credits": current_credits,
        "new_credits": new_credits
    }

@router.get("/users/{user_id}/activity")
async def get_user_activity(
    user_id: str,
    admin_user: dict = Depends(require_admin)
):
    """Get user activity logs"""
    
    # Get uploaded files
    files = await db.uploaded_files.find(
        {"user_id": ObjectId(user_id)}
    ).sort("uploaded_at", -1).to_list(50)
    
    # Get integrations
    integrations = await db.integrations.find(
        {"user_id": ObjectId(user_id)}
    ).sort("connected_at", -1).to_list(50)
    
    return {
        "user_id": user_id,
        "uploaded_files": len(files),
        "connected_integrations": len(integrations),
        "recent_files": [
            {
                "filename": f["filename"],
                "uploaded_at": f["uploaded_at"].isoformat()
            } for f in files[:5]
        ],
        "connected_sources": [
            {
                "name": i["integration_name"],
                "connected_at": i["connected_at"].isoformat()
            } for i in integrations
        ]
    }
