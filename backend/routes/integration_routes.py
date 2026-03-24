"""
OAuth integrations for Google Ads, Google Analytics, and Meta Ads.
Simple connect/disconnect flow for clients.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from auth import get_current_user_id
from datetime import datetime
from bson import ObjectId
import os
import httpx
import logging
import urllib.parse

router = APIRouter(prefix="/api/integrations", tags=["Integrations"])

db = None

def set_database(database):
    global db
    db = database

# ==================== AUTH URLs ====================

@router.get("/connect/google_ads")
async def connect_google_ads(user_id: str = Depends(get_current_user_id)):
    """Generate Google Ads OAuth URL for client to connect"""
    client_id = os.environ.get("GOOGLE_ADS_CLIENT_ID")
    redirect_uri = os.environ.get("GOOGLE_ADS_REDIRECT_URI")
    if not client_id or not redirect_uri:
        raise HTTPException(status_code=500, detail="Google Ads not configured")

    scope = "https://www.googleapis.com/auth/adwords"
    state = f"google_ads_{user_id}"

    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={client_id}"
        f"&redirect_uri={urllib.parse.quote(redirect_uri, safe='')}"
        f"&response_type=code"
        f"&scope={urllib.parse.quote(scope, safe='')}"
        f"&access_type=offline"
        f"&state={state}"
        f"&prompt=consent"
    )

    return {"auth_url": auth_url, "service": "Google Ads"}

@router.get("/connect/google_analytics")
async def connect_google_analytics(user_id: str = Depends(get_current_user_id)):
    """Generate Google Analytics OAuth URL for client to connect"""
    client_id = os.environ.get("GOOGLE_ADS_CLIENT_ID")
    redirect_uri = os.environ.get("GOOGLE_ANALYTICS_REDIRECT_URI")
    if not client_id or not redirect_uri:
        raise HTTPException(status_code=500, detail="Google Analytics not configured")

    scope = "https://www.googleapis.com/auth/analytics.readonly"
    state = f"google_analytics_{user_id}"

    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={client_id}"
        f"&redirect_uri={urllib.parse.quote(redirect_uri, safe='')}"
        f"&response_type=code"
        f"&scope={urllib.parse.quote(scope, safe='')}"
        f"&access_type=offline"
        f"&state={state}"
        f"&prompt=consent"
    )

    return {"auth_url": auth_url, "service": "Google Analytics"}

@router.get("/connect/meta_ads")
async def connect_meta_ads(user_id: str = Depends(get_current_user_id)):
    """Generate Meta Ads OAuth URL for client to connect"""
    app_id = os.environ.get("META_APP_ID")
    redirect_uri = os.environ.get("META_REDIRECT_URI")
    if not app_id or not redirect_uri:
        raise HTTPException(status_code=500, detail="Meta Ads not configured")

    scope = "ads_management,ads_read,read_insights"
    state = f"meta_ads_{user_id}"

    auth_url = (
        f"https://www.facebook.com/v19.0/dialog/oauth?"
        f"client_id={app_id}"
        f"&redirect_uri={urllib.parse.quote(redirect_uri, safe='')}"
        f"&response_type=code"
        f"&scope={urllib.parse.quote(scope, safe='')}"
        f"&state={state}"
    )

    return {"auth_url": auth_url, "service": "Meta Ads"}

@router.get("/connect/google_sheets")
async def connect_google_sheets(user_id: str = Depends(get_current_user_id)):
    """Generate Google Sheets OAuth URL for client to connect"""
    client_id = os.environ.get("GOOGLE_ADS_CLIENT_ID")
    redirect_uri = os.environ.get("GOOGLE_SHEETS_REDIRECT_URI", os.environ.get("GOOGLE_ADS_REDIRECT_URI", "").replace("google_ads", "google_sheets"))
    if not client_id:
        raise HTTPException(status_code=500, detail="Google Sheets not configured")

    scope = "https://www.googleapis.com/auth/spreadsheets.readonly https://www.googleapis.com/auth/drive.readonly"
    state = f"google_sheets_{user_id}"

    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={client_id}"
        f"&redirect_uri={urllib.parse.quote(redirect_uri, safe='')}"
        f"&response_type=code"
        f"&scope={urllib.parse.quote(scope, safe='')}"
        f"&access_type=offline"
        f"&state={state}"
        f"&prompt=consent"
    )

    return {"auth_url": auth_url, "service": "Google Sheets"}

# ==================== OAUTH CALLBACKS ====================

@router.get("/oauth/callback/google_ads")
async def google_ads_callback(code: str = None, state: str = None, error: str = None):
    """Handle Google Ads OAuth callback"""
    if error:
        return RedirectResponse(url=f"/dashboard?integration=google_ads&status=error&message={error}")

    if not code or not state:
        return RedirectResponse(url="/dashboard?integration=google_ads&status=error&message=missing_params")

    try:
        user_id = state.replace("google_ads_", "")
        tokens = await exchange_google_code(code, os.environ.get("GOOGLE_ADS_REDIRECT_URI"))

        await db.integrations.update_one(
            {"user_id": ObjectId(user_id), "service": "google_ads"},
            {"$set": {
                "user_id": ObjectId(user_id),
                "service": "google_ads",
                "service_name": "Google Ads",
                "access_token": tokens.get("access_token"),
                "refresh_token": tokens.get("refresh_token"),
                "token_expiry": tokens.get("expires_in"),
                "status": "connected",
                "connected_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }},
            upsert=True
        )

        return RedirectResponse(url="/dashboard?integration=google_ads&status=success")
    except Exception as e:
        logging.error(f"Google Ads callback error: {str(e)}")
        return RedirectResponse(url=f"/dashboard?integration=google_ads&status=error&message={str(e)}")

@router.get("/oauth/callback/google_analytics")
async def google_analytics_callback(code: str = None, state: str = None, error: str = None):
    """Handle Google Analytics OAuth callback"""
    if error:
        return RedirectResponse(url=f"/dashboard?integration=google_analytics&status=error&message={error}")

    if not code or not state:
        return RedirectResponse(url="/dashboard?integration=google_analytics&status=error&message=missing_params")

    try:
        user_id = state.replace("google_analytics_", "")
        tokens = await exchange_google_code(code, os.environ.get("GOOGLE_ANALYTICS_REDIRECT_URI"))

        await db.integrations.update_one(
            {"user_id": ObjectId(user_id), "service": "google_analytics"},
            {"$set": {
                "user_id": ObjectId(user_id),
                "service": "google_analytics",
                "service_name": "Google Analytics",
                "access_token": tokens.get("access_token"),
                "refresh_token": tokens.get("refresh_token"),
                "token_expiry": tokens.get("expires_in"),
                "status": "connected",
                "connected_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }},
            upsert=True
        )

        return RedirectResponse(url="/dashboard?integration=google_analytics&status=success")
    except Exception as e:
        logging.error(f"Google Analytics callback error: {str(e)}")
        return RedirectResponse(url=f"/dashboard?integration=google_analytics&status=error&message={str(e)}")

@router.get("/oauth/callback/meta_ads")
async def meta_ads_callback(code: str = None, state: str = None, error: str = None):
    """Handle Meta Ads OAuth callback"""
    if error:
        return RedirectResponse(url=f"/dashboard?integration=meta_ads&status=error&message={error}")

    if not code or not state:
        return RedirectResponse(url="/dashboard?integration=meta_ads&status=error&message=missing_params")

    try:
        user_id = state.replace("meta_ads_", "")
        tokens = await exchange_meta_code(code)

        await db.integrations.update_one(
            {"user_id": ObjectId(user_id), "service": "meta_ads"},
            {"$set": {
                "user_id": ObjectId(user_id),
                "service": "meta_ads",
                "service_name": "Meta Ads",
                "access_token": tokens.get("access_token"),
                "token_expiry": tokens.get("expires_in"),
                "status": "connected",
                "connected_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }},
            upsert=True
        )

        return RedirectResponse(url="/dashboard?integration=meta_ads&status=success")
    except Exception as e:
        logging.error(f"Meta Ads callback error: {str(e)}")
        return RedirectResponse(url=f"/dashboard?integration=meta_ads&status=error&message={str(e)}")

@router.get("/oauth/callback/google_sheets")
async def google_sheets_callback(code: str = None, state: str = None, error: str = None):
    """Handle Google Sheets OAuth callback"""
    if error:
        return RedirectResponse(url=f"/dashboard?integration=google_sheets&status=error&message={error}")
    if not code or not state:
        return RedirectResponse(url="/dashboard?integration=google_sheets&status=error&message=missing_params")

    try:
        user_id = state.replace("google_sheets_", "")
        redirect_uri = os.environ.get("GOOGLE_SHEETS_REDIRECT_URI", os.environ.get("GOOGLE_ADS_REDIRECT_URI", "").replace("google_ads", "google_sheets"))
        tokens = await exchange_google_code(code, redirect_uri)

        await db.integrations.update_one(
            {"user_id": ObjectId(user_id), "service": "google_sheets"},
            {"$set": {
                "user_id": ObjectId(user_id),
                "service": "google_sheets",
                "service_name": "Google Sheets",
                "access_token": tokens.get("access_token"),
                "refresh_token": tokens.get("refresh_token"),
                "token_expiry": tokens.get("expires_in"),
                "status": "connected",
                "connected_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }},
            upsert=True
        )
        return RedirectResponse(url="/dashboard?integration=google_sheets&status=success")
    except Exception as e:
        logging.error(f"Google Sheets callback error: {str(e)}")
        return RedirectResponse(url=f"/dashboard?integration=google_sheets&status=error&message={str(e)}")

# ==================== TOKEN EXCHANGE ====================

async def exchange_google_code(code: str, redirect_uri: str) -> dict:
    """Exchange Google OAuth authorization code for tokens"""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": os.environ.get("GOOGLE_ADS_CLIENT_ID"),
                "client_secret": os.environ.get("GOOGLE_ADS_CLIENT_SECRET"),
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code"
            }
        )
        if resp.status_code != 200:
            raise Exception(f"Token exchange failed: {resp.text}")
        return resp.json()

async def exchange_meta_code(code: str) -> dict:
    """Exchange Meta OAuth authorization code for access token"""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://graph.facebook.com/v19.0/oauth/access_token",
            params={
                "client_id": os.environ.get("META_APP_ID"),
                "client_secret": os.environ.get("META_APP_SECRET"),
                "redirect_uri": os.environ.get("META_REDIRECT_URI"),
                "code": code
            }
        )
        if resp.status_code != 200:
            raise Exception(f"Token exchange failed: {resp.text}")
        return resp.json()

# ==================== STATUS & DISCONNECT ====================

@router.get("/status")
async def get_integration_status(user_id: str = Depends(get_current_user_id)):
    """Get all integration statuses for the current user"""
    integrations = await db.integrations.find(
        {"user_id": ObjectId(user_id)},
        {"_id": 0, "access_token": 0, "refresh_token": 0, "token_expiry": 0}
    ).to_list(20)

    status = {}
    for i in integrations:
        status[i["service"]] = {
            "connected": i.get("status") == "connected",
            "service_name": i.get("service_name", i["service"]),
            "connected_at": i.get("connected_at").isoformat() if i.get("connected_at") else None
        }

    return {"integrations": status}

@router.delete("/disconnect/{service}")
async def disconnect_integration(service: str, user_id: str = Depends(get_current_user_id)):
    """Disconnect an integration"""
    valid_services = ["google_ads", "google_analytics", "meta_ads", "google_sheets"]
    if service not in valid_services:
        raise HTTPException(status_code=400, detail=f"Invalid service. Use: {valid_services}")

    result = await db.integrations.delete_one(
        {"user_id": ObjectId(user_id), "service": service}
    )

    return {
        "success": True,
        "message": f"{service.replace('_', ' ').title()} disconnected" if result.deleted_count > 0 else "Integration not found"
    }
