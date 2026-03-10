from fastapi import APIRouter, HTTPException, Depends
from auth import get_current_user_id
from integrations.base import INTEGRATION_METADATA, IntegrationType
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime
from bson import ObjectId
import os

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
    
    # Generate OAuth URLs using integration classes
    auth_url = ""
    
    if integration_name == "google_ads":
        from integrations.google_ads import GoogleAdsIntegration
        auth_url = GoogleAdsIntegration.get_oauth_url(state=user_id)
    
    elif integration_name == "meta_ads":
        from integrations.meta_ads import MetaAdsIntegration
        auth_url = MetaAdsIntegration.get_oauth_url(state=user_id)
    
    elif integration_name in ["google_analytics", "google_sheets"]:
        # Similar to Google Ads OAuth
        scopes = "+".join(metadata['scopes'])
        base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        auth_url = f"{base_url}?client_id={os.getenv('GOOGLE_ADS_CLIENT_ID')}&redirect_uri={os.getenv('GOOGLE_ADS_REDIRECT_URI')}&scope={scopes}&response_type=code&access_type=offline&prompt=consent&state={user_id}"
    
    elif integration_name == "salesforce":
        client_id = os.getenv("SALESFORCE_CLIENT_ID", "YOUR_CLIENT_ID")
        redirect_uri = os.getenv("SALESFORCE_REDIRECT_URI", "YOUR_REDIRECT_URI")
        auth_url = f"https://login.salesforce.com/services/oauth2/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope=api%20refresh_token&state={user_id}"
    
    return {
        "authorization_url": auth_url,
        "state": user_id,
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

@router.get("/oauth/callback/google_ads")
async def google_ads_oauth_callback(code: str, state: str):
    """Handle Google Ads OAuth callback"""
    from integrations.google_ads import GoogleAdsIntegration
    
    try:
        # Exchange code for tokens
        tokens = await GoogleAdsIntegration.exchange_code_for_token(code)
        
        # Store tokens in database for the user
        user_id = state  # state parameter contains user_id
        
        connection_doc = {
            "user_id": ObjectId(user_id),
            "integration_name": "google_ads",
            "integration_type": "oauth",
            "credentials": {
                "access_token": tokens.get("access_token"),
                "refresh_token": tokens.get("refresh_token"),
                "expires_in": tokens.get("expires_in")
            },
            "status": "connected",
            "connected_at": datetime.utcnow()
        }
        
        await db.integrations.insert_one(connection_doc)
        
        # Redirect to success page
        return {
            "success": True,
            "message": "Google Ads connected successfully!",
            "redirect_url": "/dashboard?integration=google_ads&status=success"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "redirect_url": "/dashboard?integration=google_ads&status=error"
        }

@router.get("/oauth/callback/meta_ads")
async def meta_ads_oauth_callback(code: str, state: str):
    """Handle Meta Ads OAuth callback"""
    from integrations.meta_ads import MetaAdsIntegration
    
    try:
        # Exchange code for tokens
        tokens = await MetaAdsIntegration.exchange_code_for_token(code)
        
        # Store tokens in database for the user
        user_id = state
        
        connection_doc = {
            "user_id": ObjectId(user_id),
            "integration_name": "meta_ads",
            "integration_type": "oauth",
            "credentials": {
                "access_token": tokens.get("access_token"),
                "expires_in": tokens.get("expires_in")
            },
            "status": "connected",
            "connected_at": datetime.utcnow()
        }
        
        await db.integrations.insert_one(connection_doc)
        
        return {
            "success": True,
            "message": "Meta Ads connected successfully!",
            "redirect_url": "/dashboard?integration=meta_ads&status=success"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "redirect_url": "/dashboard?integration=meta_ads&status=error"
        }

@router.post("/fetch-data/{integration_name}")
async def fetch_integration_data(
    integration_name: str,
    user_id: str = Depends(get_current_user_id)
):
    """Fetch data from connected integration"""
    
    # Get user's connection
    connection = await db.integrations.find_one({
        "user_id": ObjectId(user_id),
        "integration_name": integration_name,
        "status": "connected"
    })
    
    if not connection:
        raise HTTPException(status_code=404, detail="Integration not connected")
    
    try:
        if integration_name == "google_ads":
            from integrations.google_ads import GoogleAdsIntegration
            
            integration = GoogleAdsIntegration(connection["credentials"])
            
            # Get customer ID from user input or stored config
            customer_id = connection.get("config", {}).get("customer_id")
            if not customer_id:
                raise HTTPException(
                    status_code=400, 
                    detail="Google Ads Customer ID not configured"
                )
            
            data = await integration.fetch_campaign_metrics(customer_id)
            
        elif integration_name == "meta_ads":
            from integrations.meta_ads import MetaAdsIntegration
            
            integration = MetaAdsIntegration(connection["credentials"])
            
            # Get ad account ID
            ad_account_id = connection.get("config", {}).get("ad_account_id")
            if not ad_account_id:
                raise HTTPException(
                    status_code=400,
                    detail="Meta Ads Account ID not configured"
                )
            
            data = await integration.fetch_campaign_metrics(ad_account_id)
        
        else:
            raise HTTPException(status_code=400, detail="Integration not supported yet")
        
        # Store fetched data
        await db.integration_data.insert_one({
            "user_id": ObjectId(user_id),
            "integration_name": integration_name,
            "data": data,
            "fetched_at": datetime.utcnow()
        })
        
        # Update last sync
        await db.integrations.update_one(
            {"_id": connection["_id"]},
            {"$set": {"last_sync": {"timestamp": datetime.utcnow(), "status": "success"}}}
        )
        
        return data
        
    except Exception as e:
        # Update last sync with error
        await db.integrations.update_one(
            {"_id": connection["_id"]},
            {"$set": {"last_sync": {"timestamp": datetime.utcnow(), "status": "error", "error": str(e)}}}
        )
        raise HTTPException(status_code=500, detail=f"Failed to fetch data: {str(e)}")
