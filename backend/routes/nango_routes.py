"""
Nango integration routes - Manages OAuth connections via Nango.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from auth import get_current_user_id
from nango_service import NangoService
from typing import Optional, List
import logging

router = APIRouter(prefix="/api/nango", tags=["Nango"])

db = None
nango: NangoService = None


def set_database(database):
    global db, nango
    db = database
    nango = NangoService(database)


# ---- Request Models ----

class SaveConnectionRequest(BaseModel):
    integration_id: str
    connection_id: str

class ProxyRequest(BaseModel):
    integration_id: str
    connection_id: str
    endpoint: str
    method: str = "GET"
    data: Optional[dict] = None

class ConnectSessionRequest(BaseModel):
    allowed_integrations: Optional[List[str]] = None


# ---- Endpoints ----

@router.post("/connect-session")
async def create_connect_session(req: ConnectSessionRequest, user_id: str = Depends(get_current_user_id)):
    """Create a Nango connect session token for the frontend SDK"""
    try:
        result = await nango.create_connect_session(user_id, req.allowed_integrations)
        return result
    except Exception as e:
        error_msg = str(e)
        logging.error(f"Nango connect session error: {error_msg}")
        # Surface Nango-specific errors clearly
        if "resource_capped" in error_msg or "connection limits" in error_msg.lower():
            raise HTTPException(status_code=429, detail="Nango connection limit reached. Please delete unused connections from your Nango Dashboard or upgrade your Nango plan.")
        raise HTTPException(status_code=500, detail=error_msg)


@router.post("/save-connection")
async def save_connection(req: SaveConnectionRequest, user_id: str = Depends(get_current_user_id)):
    """Save a Nango connection ID after successful OAuth"""
    result = await nango.save_connection(user_id, req.integration_id, req.connection_id)
    return result


@router.get("/connections")
async def get_connections(user_id: str = Depends(get_current_user_id)):
    """Get all Nango connections for the current user"""
    connections = await nango.get_all_connections(user_id)
    return {"connections": connections}


@router.delete("/connections/{integration_id}")
async def disconnect(integration_id: str, user_id: str = Depends(get_current_user_id)):
    """Disconnect a Nango integration"""
    deleted = await nango.delete_connection(user_id, integration_id)
    return {"success": True, "message": f"{integration_id} disconnected" if deleted else "Connection not found"}


@router.post("/proxy")
async def proxy_request(req: ProxyRequest, user_id: str = Depends(get_current_user_id)):
    """Make an authenticated proxy request through Nango"""
    try:
        if req.method.upper() == "GET":
            result = await nango.proxy_get(req.integration_id, req.connection_id, req.endpoint)
        else:
            result = await nango.proxy_post(req.integration_id, req.connection_id, req.endpoint, req.data)
        return result
    except Exception as e:
        logging.error(f"Nango proxy error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
