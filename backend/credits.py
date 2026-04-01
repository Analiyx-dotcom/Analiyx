"""Credit management utility for Analiyx platform"""
from fastapi import HTTPException
from bson import ObjectId
from datetime import datetime

# Credit costs per action
CREDIT_COSTS = {
    "ai_chat": 1,
    "ai_visibility": 5,
    "file_upload": 2,
}

async def check_and_deduct_credits(db, user_id: str, action: str) -> dict:
    """
    Check if user has enough credits for the action and deduct them.
    Returns dict with previous_credits, cost, remaining_credits.
    Raises HTTPException if insufficient credits.
    """
    cost = CREDIT_COSTS.get(action, 1)
    
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    current_credits = user.get("credits", 0)
    
    if current_credits < cost:
        raise HTTPException(
            status_code=403,
            detail=f"Insufficient credits. This action costs {cost} credit(s), but you have {current_credits}. Please upgrade your plan or contact support."
        )
    
    # Deduct credits atomically
    result = await db.users.update_one(
        {"_id": ObjectId(user_id), "credits": {"$gte": cost}},
        {
            "$inc": {"credits": -cost},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=403, detail="Insufficient credits. Please upgrade your plan.")
    
    new_credits = current_credits - cost
    
    # Log credit usage
    await db.credit_usage.insert_one({
        "user_id": ObjectId(user_id),
        "action": action,
        "cost": cost,
        "credits_before": current_credits,
        "credits_after": new_credits,
        "created_at": datetime.utcnow()
    })
    
    return {
        "previous_credits": current_credits,
        "cost": cost,
        "remaining_credits": new_credits
    }
