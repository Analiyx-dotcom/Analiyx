"""Workspace management routes"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from auth import get_current_user_id
from datetime import datetime
from bson import ObjectId
from typing import List, Optional

router = APIRouter(prefix="/api/workspaces", tags=["Workspaces"])

db = None

def set_database(database):
    global db
    db = database

class WorkspaceCreate(BaseModel):
    name: str
    data_sources: List[str] = []

@router.post("/create")
async def create_workspace(workspace: WorkspaceCreate, user_id: str = Depends(get_current_user_id)):
    """Create a new workspace"""
    existing = await db.workspaces.count_documents({"user_id": ObjectId(user_id)})
    
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    plan = user.get("plan", "Starter") if user else "Starter"
    trial_active = user and user.get("trial_ends_at") and user["trial_ends_at"] > datetime.utcnow()
    max_workspaces = 999 if trial_active else {"Starter": 2, "Business Pro": 10, "Enterprise": 999}.get(plan, 2)
    
    if existing >= max_workspaces:
        raise HTTPException(status_code=400, detail=f"Workspace limit reached ({max_workspaces}) for your {plan} plan. Please upgrade.")
    
    ws_doc = {
        "user_id": ObjectId(user_id),
        "name": workspace.name,
        "data_sources": workspace.data_sources,
        "status": "active",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    result = await db.workspaces.insert_one(ws_doc)
    
    return {
        "success": True,
        "workspace_id": str(result.inserted_id),
        "name": workspace.name,
        "message": f"Workspace '{workspace.name}' created successfully!"
    }

@router.get("/list")
async def list_workspaces(user_id: str = Depends(get_current_user_id)):
    """List all workspaces for user"""
    workspaces = await db.workspaces.find(
        {"user_id": ObjectId(user_id)}
    ).sort("created_at", -1).to_list(50)
    
    return {
        "workspaces": [{
            "id": str(ws["_id"]),
            "name": ws["name"],
            "data_sources": ws.get("data_sources", []),
            "status": ws.get("status", "active"),
            "created_at": ws["created_at"].isoformat()
        } for ws in workspaces]
    }

@router.delete("/{workspace_id}")
async def delete_workspace(workspace_id: str, user_id: str = Depends(get_current_user_id)):
    """Delete a workspace"""
    result = await db.workspaces.delete_one({
        "_id": ObjectId(workspace_id),
        "user_id": ObjectId(user_id)
    })
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return {"success": True, "message": "Workspace deleted"}
