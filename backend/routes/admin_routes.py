from fastapi import APIRouter, HTTPException, Depends, Query
from models import AdminStats, ChartDataPoint, RevenueDataPoint, UserResponse
from auth import get_current_user_id, require_admin
from datetime import datetime, timedelta
from typing import List
from bson import ObjectId
import calendar

router = APIRouter(prefix="/api/admin", tags=["Admin"])

# Database will be injected
db = None

def set_database(database):
    global db
    db = database

@router.get("/stats", response_model=AdminStats)
async def get_admin_stats(admin_user: dict = Depends(require_admin)):
    """Get dashboard statistics"""
    # Total users
    total_users = await db.users.count_documents({})
    
    # Active subscriptions
    active_subscriptions = await db.subscriptions.count_documents({"status": "active"})
    
    # Monthly revenue (sum of active subscriptions)
    pipeline = [
        {"$match": {"status": "active"}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ]
    revenue_result = await db.subscriptions.aggregate(pipeline).to_list(1)
    monthly_revenue = revenue_result[0]["total"] if revenue_result else 0
    
    # Total data sources
    data_sources = await db.data_sources.count_documents({})
    
    return AdminStats(
        total_users=total_users,
        active_subscriptions=active_subscriptions,
        monthly_revenue=monthly_revenue,
        data_sources=data_sources
    )

@router.get("/users")
async def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    admin_user: dict = Depends(require_admin)
):
    """Get all users (paginated)"""
    skip = (page - 1) * limit
    
    # Get users
    users_cursor = db.users.find().sort("created_at", -1).skip(skip).limit(limit)
    users = await users_cursor.to_list(length=limit)
    
    # Get total count
    total = await db.users.count_documents({})
    
    # Format users
    formatted_users = []
    for user in users:
        formatted_users.append({
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"],
            "plan": user["plan"],
            "status": user["status"],
            "joined": user["created_at"].strftime("%Y-%m-%d")
        })
    
    return {
        "users": formatted_users,
        "total": total,
        "page": page,
        "total_pages": (total + limit - 1) // limit
    }

@router.get("/charts/user-growth")
async def get_user_growth(admin_user: dict = Depends(require_admin)):
    """Get user growth data for the last 7 months"""
    # Calculate date range (last 7 months)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=210)  # Approximately 7 months
    
    # Aggregate users by month
    pipeline = [
        {
            "$match": {
                "created_at": {"$gte": start_date, "$lte": end_date}
            }
        },
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$created_at"},
                    "month": {"$month": "$created_at"}
                },
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"_id.year": 1, "_id.month": 1}}
    ]
    
    result = await db.users.aggregate(pipeline).to_list(None)
    
    # Format data
    data = []
    cumulative_count = 0
    for item in result:
        month_name = calendar.month_abbr[item["_id"]["month"]]
        cumulative_count += item["count"]
        data.append({
            "month": month_name,
            "users": cumulative_count
        })
    
    # Fill in missing months if needed
    if len(data) < 7:
        # Generate last 7 months
        months_data = []
        for i in range(6, -1, -1):
            month_date = end_date - timedelta(days=30 * i)
            month_name = calendar.month_abbr[month_date.month]
            
            # Find if we have data for this month
            found = False
            for d in data:
                if d["month"] == month_name:
                    months_data.append(d)
                    found = True
                    break
            
            if not found:
                # Use previous count or 0
                prev_count = months_data[-1]["users"] if months_data else 0
                months_data.append({"month": month_name, "users": prev_count})
        
        data = months_data
    
    return {"data": data[-7:]}

@router.get("/charts/revenue")
async def get_revenue_trend(admin_user: dict = Depends(require_admin)):
    """Get revenue trend data for the last 7 months"""
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=210)
    
    # Aggregate revenue by month
    pipeline = [
        {
            "$match": {
                "created_at": {"$gte": start_date, "$lte": end_date},
                "status": "active"
            }
        },
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$created_at"},
                    "month": {"$month": "$created_at"}
                },
                "total": {"$sum": "$amount"}
            }
        },
        {"$sort": {"_id.year": 1, "_id.month": 1}}
    ]
    
    result = await db.subscriptions.aggregate(pipeline).to_list(None)
    
    # Format data
    data = []
    cumulative_revenue = 0
    for item in result:
        month_name = calendar.month_abbr[item["_id"]["month"]]
        cumulative_revenue += item["total"]
        data.append({
            "month": month_name,
            "amount": cumulative_revenue
        })
    
    # Generate last 7 months with data or defaults
    months_data = []
    for i in range(6, -1, -1):
        month_date = end_date - timedelta(days=30 * i)
        month_name = calendar.month_abbr[month_date.month]
        
        found = False
        for d in data:
            if d["month"] == month_name:
                months_data.append(d)
                found = True
                break
        
        if not found:
            prev_amount = months_data[-1]["amount"] if months_data else 28000
            months_data.append({"month": month_name, "amount": prev_amount})
    
    return {"data": months_data[-7:]}