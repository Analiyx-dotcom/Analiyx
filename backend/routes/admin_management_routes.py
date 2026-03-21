"""
Admin management routes for user control, subscription management, exports, and ticket management
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from auth import require_admin
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from bson import ObjectId
import io
import logging

router = APIRouter(prefix="/api/admin/manage", tags=["Admin Management"])

db = None

def set_database(database):
    global db
    db = database

class UserStatusUpdate(BaseModel):
    status: str  # "active", "disabled", "spam"

class TrialExtension(BaseModel):
    days: int = 7

class SubscriptionUpdate(BaseModel):
    duration_months: int  # 12 or 24

class CreditUpdate(BaseModel):
    credits: int
    action: str  # "add", "remove", "set"

class TicketReply(BaseModel):
    reply: str

@router.get("/users/details")
async def get_all_users_details(admin_user: dict = Depends(require_admin)):
    """Get detailed list of all users with subscriptions"""
    users = await db.users.find().sort("created_at", -1).to_list(1000)

    detailed_users = []
    for user in users:
        user_id = user["_id"]
        subscription = await db.subscriptions.find_one({"user_id": user_id})
        data_sources_count = await db.uploaded_files.count_documents({"user_id": user_id})
        data_sources_count += await db.integrations.count_documents({"user_id": user_id, "status": "connected"})

        detailed_users.append({
            "id": str(user_id),
            "name": user["name"],
            "email": user["email"],
            "plan": user.get("plan", "Trial"),
            "status": user.get("status", "active"),
            "role": user.get("role", "user"),
            "credits": user.get("credits", 0),
            "created_at": user["created_at"].isoformat(),
            "trial_ends_at": user.get("trial_ends_at").isoformat() if user.get("trial_ends_at") else None,
            "subscription_end_date": user.get("subscription_end_date").isoformat() if user.get("subscription_end_date") else (subscription.get("end_date").isoformat() if subscription and subscription.get("end_date") else None),
            "subscription_status": subscription.get("status") if subscription else "none",
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
    """Enable, disable, or mark user as spam"""
    valid_statuses = ["active", "disabled", "inactive", "spam"]
    if update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Use: {valid_statuses}")

    result = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"status": update.status, "updated_at": datetime.utcnow()}}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    status_msg = {
        "active": "activated",
        "disabled": "disabled",
        "inactive": "deactivated",
        "spam": "blocked as spam"
    }

    return {
        "success": True,
        "message": f"User account {status_msg.get(update.status, update.status)} successfully"
    }

@router.post("/users/{user_id}/extend-trial")
async def extend_trial(
    user_id: str,
    extension: TrialExtension,
    admin_user: dict = Depends(require_admin)
):
    """Extend user's trial period"""
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_end_date = datetime.utcnow() + timedelta(days=extension.days)
    current_end = user.get("trial_ends_at")
    if current_end and current_end > datetime.utcnow():
        new_end_date = current_end + timedelta(days=extension.days)

    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"trial_ends_at": new_end_date, "status": "active", "updated_at": datetime.utcnow()}}
    )

    subscription = await db.subscriptions.find_one({"user_id": ObjectId(user_id)})
    if subscription:
        await db.subscriptions.update_one(
            {"_id": subscription["_id"]},
            {"$set": {"end_date": new_end_date, "status": "active"}}
        )
    else:
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

@router.put("/users/{user_id}/subscription")
async def update_subscription_duration(
    user_id: str,
    update: SubscriptionUpdate,
    admin_user: dict = Depends(require_admin)
):
    """Admin can extend subscription duration (1 year or 2 years)"""
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    current_end = user.get("subscription_end_date")
    base_date = current_end if current_end and current_end > datetime.utcnow() else datetime.utcnow()
    new_end_date = base_date + timedelta(days=update.duration_months * 30)

    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {
            "subscription_end_date": new_end_date,
            "status": "active",
            "updated_at": datetime.utcnow()
        }}
    )

    return {
        "success": True,
        "message": f"Subscription extended by {update.duration_months} months",
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

@router.get("/users/export/{format}")
async def export_users(format: str, admin_user: dict = Depends(require_admin)):
    """Export registered users as Excel or PDF"""
    users = await db.users.find({}, {"password": 0}).sort("created_at", -1).to_list(10000)

    if format == "excel":
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Users"
        headers = ["Name", "Email", "Plan", "Status", "Role", "Credits", "Trial Ends", "Subscription End", "Created At"]
        ws.append(headers)
        for u in users:
            ws.append([
                u.get("name", ""),
                u.get("email", ""),
                u.get("plan", ""),
                u.get("status", ""),
                u.get("role", ""),
                u.get("credits", 0),
                u.get("trial_ends_at", "").isoformat() if u.get("trial_ends_at") else "",
                u.get("subscription_end_date", "").isoformat() if u.get("subscription_end_date") else "",
                u.get("created_at", "").isoformat() if u.get("created_at") else "",
            ])
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=analiyx_users.xlsx"}
        )

    elif format == "pdf":
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
        styles = getSampleStyleSheet()
        elements = []
        elements.append(Paragraph("Analiyx - Registered Users", styles["Title"]))
        elements.append(Spacer(1, 20))

        headers = ["Name", "Email", "Plan", "Status", "Credits", "Created At"]
        data = [headers]
        for u in users:
            data.append([
                u.get("name", "")[:20],
                u.get("email", "")[:30],
                u.get("plan", ""),
                u.get("status", ""),
                str(u.get("credits", 0)),
                u.get("created_at", "").strftime("%Y-%m-%d") if u.get("created_at") else "",
            ])

        table = Table(data)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#7c3aed")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f4f6")]),
        ]))
        elements.append(table)
        doc.build(elements)
        buffer.seek(0)
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=analiyx_users.pdf"}
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Use 'excel' or 'pdf'")

# ===== TICKET MANAGEMENT =====

@router.get("/tickets")
async def get_all_tickets(admin_user: dict = Depends(require_admin)):
    """Admin: Get all support tickets from all users"""
    tickets = await db.support_tickets.find().sort("created_at", -1).to_list(500)

    return {
        "tickets": [{
            "id": str(t["_id"]),
            "user_id": str(t.get("user_id", "")),
            "user_email": t.get("user_email", ""),
            "user_name": t.get("user_name", ""),
            "subject": t.get("subject", ""),
            "message": t.get("message", ""),
            "priority": t.get("priority", "medium"),
            "status": t.get("status", "open"),
            "replies": t.get("replies", []),
            "created_at": t["created_at"].isoformat() if t.get("created_at") else "",
            "updated_at": t.get("updated_at", t.get("created_at", "")).isoformat() if t.get("updated_at") or t.get("created_at") else ""
        } for t in tickets]
    }

@router.post("/tickets/{ticket_id}/reply")
async def reply_to_ticket(
    ticket_id: str,
    reply: TicketReply,
    admin_user: dict = Depends(require_admin)
):
    """Admin: Reply to a support ticket"""
    ticket = await db.support_tickets.find_one({"_id": ObjectId(ticket_id)})
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    reply_doc = {
        "from": "admin",
        "message": reply.reply,
        "replied_at": datetime.utcnow().isoformat()
    }

    await db.support_tickets.update_one(
        {"_id": ObjectId(ticket_id)},
        {
            "$push": {"replies": reply_doc},
            "$set": {"status": "replied", "updated_at": datetime.utcnow()}
        }
    )

    return {"success": True, "message": "Reply sent successfully"}

@router.put("/tickets/{ticket_id}/status")
async def update_ticket_status(
    ticket_id: str,
    admin_user: dict = Depends(require_admin)
):
    """Admin: Close a ticket"""
    await db.support_tickets.update_one(
        {"_id": ObjectId(ticket_id)},
        {"$set": {"status": "closed", "updated_at": datetime.utcnow()}}
    )
    return {"success": True, "message": "Ticket closed"}

@router.get("/users/{user_id}/activity")
async def get_user_activity(
    user_id: str,
    admin_user: dict = Depends(require_admin)
):
    """Get user activity logs"""
    files = await db.uploaded_files.find(
        {"user_id": ObjectId(user_id)}
    ).sort("uploaded_at", -1).to_list(50)

    integrations = await db.integrations.find(
        {"user_id": ObjectId(user_id)}
    ).sort("connected_at", -1).to_list(50)

    return {
        "user_id": user_id,
        "uploaded_files": len(files),
        "connected_integrations": len(integrations),
        "recent_files": [
            {"filename": f["filename"], "uploaded_at": f["uploaded_at"].isoformat()}
            for f in files[:5]
        ],
        "connected_sources": [
            {"name": i["integration_name"], "connected_at": i["connected_at"].isoformat()}
            for i in integrations
        ]
    }
