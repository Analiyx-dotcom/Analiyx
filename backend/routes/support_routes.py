"""Support ticket routes for clients"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from auth import get_current_user_id
from datetime import datetime
from bson import ObjectId

router = APIRouter(prefix="/api/support", tags=["Support"])

db = None

def set_database(database):
    global db
    db = database

class TicketCreate(BaseModel):
    subject: str
    message: str
    priority: str = "medium"

@router.post("/tickets")
async def create_ticket(ticket: TicketCreate, user_id: str = Depends(get_current_user_id)):
    """Create a support ticket"""
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    ticket_doc = {
        "user_id": ObjectId(user_id),
        "user_email": user["email"],
        "user_name": user["name"],
        "subject": ticket.subject,
        "message": ticket.message,
        "priority": ticket.priority,
        "status": "open",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    result = await db.support_tickets.insert_one(ticket_doc)
    
    return {
        "success": True,
        "ticket_id": str(result.inserted_id),
        "message": "Ticket created successfully. Our team will respond soon."
    }

@router.get("/tickets")
async def get_my_tickets(user_id: str = Depends(get_current_user_id)):
    """Get all tickets for current user"""
    tickets = await db.support_tickets.find(
        {"user_id": ObjectId(user_id)}
    ).sort("created_at", -1).to_list(100)
    
    return {
        "tickets": [{
            "id": str(t["_id"]),
            "subject": t["subject"],
            "message": t["message"],
            "priority": t["priority"],
            "status": t["status"],
            "created_at": t["created_at"].isoformat()
        } for t in tickets]
    }
