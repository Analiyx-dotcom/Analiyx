from fastapi import APIRouter, HTTPException, Depends
from auth import get_current_user_id
from integrations.base import INTEGRATION_METADATA, IntegrationType
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime
from bson import ObjectId

router = APIRouter(prefix="/api/integrations", tags=["Integrations"])

# Database will be injected
db = None

def set_database(database):
    global db
    db = database

class IntegrationConnectionRequest(BaseModel):
    integration_name: str
    credentials: Dict[str, Any]
    config: Optional[Dict[str, Any]] = {}

class IntegrationResponse(BaseModel):
    id: str
    integration_name: str
    status: str
    connected_at: str
    last_sync: Optional[str] = None
    metrics_count: int = 0

@router.get("/available")
async def get_available_integrations():
    """Get list of all available integrations"""
    integrations = []
    for key, metadata in INTEGRATION_METADATA.items():
        integrations.append({
            "id": key,
            "name": metadata["name"],
            "type": metadata["type"],
            "icon": metadata["icon"],
            "color": metadata["color"],
            "description": metadata["description"],
            "metrics": metadata["metrics"],
            "requires_oauth": metadata["type"] == IntegrationType.OAUTH,
            "required_fields": metadata.get("required_fields", [])
        })
    return {"integrations": integrations}

@router.get("/connected")
async def get_connected_integrations(user_id: str = Depends(get_current_user_id)):
    """Get user's connected integrations"""
    connections = await db.integrations.find({
        "user_id": ObjectId(user_id),
        "status": {"$in": ["connected", "active"]}
    }).to_list(100)
    
    formatted = []
    for conn in connections:
        formatted.append({
            "id": str(conn["_id"]),
            "integration_name": conn["integration_name"],
            "status": conn["status"],
            "connected_at": conn["connected_at"].isoformat(),
            "last_sync": conn.get("last_sync", {}).get("timestamp", None),
            "metrics_count": conn.get("metrics_count", 0)
        })
    
    return {"connections": formatted}

@router.post("/connect/{integration_name}")
async def connect_integration(
    integration_name: str,
    request: IntegrationConnectionRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Connect a new integration"""
    
    if integration_name not in INTEGRATION_METADATA:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    metadata = INTEGRATION_METADATA[integration_name]
    
    # Validate required fields for API_KEY and DATABASE types
    if metadata["type"] in [IntegrationType.API_KEY, IntegrationType.DATABASE]:
        required_fields = metadata.get("required_fields", [])
        missing_fields = [f for f in required_fields if f not in request.credentials]
        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required fields: {', '.join(missing_fields)}"
            )
    
    # Store connection
    connection_doc = {
        "user_id": ObjectId(user_id),
        "integration_name": integration_name,
        "integration_type": metadata["type"],
        "credentials": request.credentials,  # Should be encrypted in production
        "config": request.config,
        "status": "pending",
        "connected_at": datetime.utcnow(),
        "last_sync": None,
        "metrics_count": 0
    }
    
    result = await db.integrations.insert_one(connection_doc)
    
    # Test connection based on integration type
    try:
        if integration_name == "postgresql":
            await test_postgresql_connection(request.credentials)
        elif integration_name == "mysql":
            await test_mysql_connection(request.credentials)
        elif integration_name == "mongodb":
            await test_mongodb_connection(request.credentials)
        elif integration_name in ["shopify", "zoho_books", "hubspot"]:
            await test_api_key_integration(integration_name, request.credentials)
        
        # Update status to connected
        await db.integrations.update_one(
            {"_id": result.inserted_id},
            {"$set": {"status": "connected"}}
        )
        status = "connected"
    except Exception as e:
        await db.integrations.update_one(
            {"_id": result.inserted_id},
            {"$set": {"status": "error", "error_message": str(e)}}
        )
        raise HTTPException(status_code=400, detail=f"Connection failed: {str(e)}")
    
    return {
        "success": True,
        "connection_id": str(result.inserted_id),
        "status": status,
        "message": f"Successfully connected to {metadata['name']}"
    }

@router.delete("/disconnect/{connection_id}")
async def disconnect_integration(
    connection_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Disconnect an integration"""
    result = await db.integrations.delete_one({
        "_id": ObjectId(connection_id),
        "user_id": ObjectId(user_id)
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    return {"success": True, "message": "Integration disconnected"}

@router.get("/oauth/authorize/{integration_name}")
async def get_oauth_authorization_url(
    integration_name: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get OAuth authorization URL for integrations that require it"""
    
    if integration_name not in INTEGRATION_METADATA:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    metadata = INTEGRATION_METADATA[integration_name]
    
    if metadata["type"] != IntegrationType.OAUTH:
        raise HTTPException(
            status_code=400,
            detail="This integration does not use OAuth"
        )
    
    # Generate OAuth URLs based on integration
    auth_urls = {
        "google_ads": f"https://accounts.google.com/o/oauth2/v2/auth?client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&scope={'+'.join(metadata['scopes'])}&response_type=code&access_type=offline",
        "google_analytics": f"https://accounts.google.com/o/oauth2/v2/auth?client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&scope={'+'.join(metadata['scopes'])}&response_type=code&access_type=offline",
        "google_sheets": f"https://accounts.google.com/o/oauth2/v2/auth?client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&scope={'+'.join(metadata['scopes'])}&response_type=code&access_type=offline",
        "meta_ads": "https://www.facebook.com/v12.0/dialog/oauth?client_id=YOUR_APP_ID&redirect_uri=YOUR_REDIRECT_URI&scope=ads_read,ads_management",
        "salesforce": "https://login.salesforce.com/services/oauth2/authorize?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&scope=api%20refresh_token"
    }
    
    return {
        "authorization_url": auth_urls.get(integration_name, ""),
        "state": user_id,  # Use for CSRF protection
        "integration_name": integration_name
    }

# Helper functions for testing connections
async def test_postgresql_connection(credentials: Dict[str, Any]):
    """Test PostgreSQL connection"""
    import asyncpg
    conn = await asyncpg.connect(
        host=credentials.get("host"),
        port=credentials.get("port", 5432),
        database=credentials.get("database"),
        user=credentials.get("username"),
        password=credentials.get("password")
    )
    await conn.close()

async def test_mysql_connection(credentials: Dict[str, Any]):
    """Test MySQL connection"""
    import aiomysql
    conn = await aiomysql.connect(
        host=credentials.get("host"),
        port=credentials.get("port", 3306),
        db=credentials.get("database"),
        user=credentials.get("username"),
        password=credentials.get("password")
    )
    conn.close()

async def test_mongodb_connection(credentials: Dict[str, Any]):
    """Test MongoDB connection"""
    from motor.motor_asyncio import AsyncIOMotorClient
    client = AsyncIOMotorClient(credentials.get("connection_string"))
    await client.server_info()
    client.close()

async def test_api_key_integration(integration_name: str, credentials: Dict[str, Any]):
    """Test API key based integrations"""
    import httpx
    
    test_endpoints = {
        "shopify": f"https://{credentials.get('shop_url')}/admin/api/2024-01/shop.json",
        "hubspot": "https://api.hubapi.com/contacts/v1/lists/all/contacts/all",
        "zoho_books": "https://www.zohoapis.com/books/v3/organizations"
    }
    
    headers = {}
    if integration_name == "shopify":
        headers = {"X-Shopify-Access-Token": credentials.get("access_token")}
    elif integration_name == "hubspot":
        headers = {"Authorization": f"Bearer {credentials.get('api_key')}"}
    elif integration_name == "zoho_books":
        headers = {"Authorization": f"Zoho-oauthtoken {credentials.get('access_token')}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            test_endpoints.get(integration_name, ""),
            headers=headers
        )
        if response.status_code not in [200, 201]:
            raise Exception(f"API test failed with status {response.status_code}")
