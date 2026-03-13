"""Slack integration routes - Connect Slack, list channels, send reports"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from auth import get_current_user_id
from datetime import datetime
from bson import ObjectId
from typing import Optional
import logging

router = APIRouter(prefix="/api/slack", tags=["Slack"])

db = None

def set_database(database):
    global db
    db = database

class SlackConnectRequest(BaseModel):
    bot_token: str

class SlackSendRequest(BaseModel):
    channel_id: str
    message: str
    report_type: Optional[str] = "general"

@router.post("/connect")
async def connect_slack(req: SlackConnectRequest, user_id: str = Depends(get_current_user_id)):
    """Connect user's Slack workspace using bot token"""
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError

    try:
        client = WebClient(token=req.bot_token)
        auth = client.auth_test()

        # Store the connection in DB
        await db.slack_connections.update_one(
            {"user_id": ObjectId(user_id)},
            {"$set": {
                "user_id": ObjectId(user_id),
                "bot_token": req.bot_token,
                "team_id": auth["team_id"],
                "team_name": auth["team"],
                "bot_user_id": auth["user_id"],
                "status": "connected",
                "connected_at": datetime.utcnow()
            }},
            upsert=True
        )

        return {
            "success": True,
            "team_name": auth["team"],
            "bot_user_id": auth["user_id"],
            "message": f"Connected to {auth['team']} workspace!"
        }
    except SlackApiError as e:
        raise HTTPException(status_code=400, detail=f"Slack authentication failed: {e.response['error']}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Connection failed: {str(e)}")

@router.get("/status")
async def get_slack_status(user_id: str = Depends(get_current_user_id)):
    """Check if user has Slack connected"""
    connection = await db.slack_connections.find_one(
        {"user_id": ObjectId(user_id)},
        {"_id": 0, "bot_token": 0}
    )
    if not connection:
        return {"connected": False}

    connection.pop("user_id", None)
    if "connected_at" in connection:
        connection["connected_at"] = connection["connected_at"].isoformat()
    return {"connected": True, **connection}

@router.get("/channels")
async def list_channels(user_id: str = Depends(get_current_user_id)):
    """List available Slack channels"""
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError

    connection = await db.slack_connections.find_one({"user_id": ObjectId(user_id)})
    if not connection:
        raise HTTPException(status_code=400, detail="Slack not connected. Please connect first.")

    try:
        client = WebClient(token=connection["bot_token"])
        result = client.conversations_list(types="public_channel,private_channel", limit=100)

        channels = [{
            "id": ch["id"],
            "name": ch["name"],
            "is_private": ch.get("is_private", False),
            "num_members": ch.get("num_members", 0)
        } for ch in result.get("channels", []) if not ch.get("is_archived")]

        return {"channels": channels}
    except SlackApiError as e:
        raise HTTPException(status_code=400, detail=f"Failed to list channels: {e.response['error']}")

@router.post("/send")
async def send_to_slack(req: SlackSendRequest, user_id: str = Depends(get_current_user_id)):
    """Send a message or report to a Slack channel"""
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError

    connection = await db.slack_connections.find_one({"user_id": ObjectId(user_id)})
    if not connection:
        raise HTTPException(status_code=400, detail="Slack not connected.")

    try:
        client = WebClient(token=connection["bot_token"])
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        user_name = user.get("name", "User") if user else "User"

        client.chat_postMessage(
            channel=req.channel_id,
            text=req.message,
            blocks=[
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": f"Analiyx Report from {user_name}"}
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": req.message}
                },
                {"type": "divider"},
                {
                    "type": "context",
                    "elements": [{"type": "mrkdwn", "text": f"Shared via *Analiyx* | {datetime.utcnow().strftime('%b %d, %Y %H:%M UTC')}"}]
                }
            ]
        )

        # Log the share
        await db.slack_shares.insert_one({
            "user_id": ObjectId(user_id),
            "channel_id": req.channel_id,
            "report_type": req.report_type,
            "created_at": datetime.utcnow()
        })

        return {"success": True, "message": "Report sent to Slack channel!"}
    except SlackApiError as e:
        raise HTTPException(status_code=400, detail=f"Failed to send: {e.response['error']}")

@router.delete("/disconnect")
async def disconnect_slack(user_id: str = Depends(get_current_user_id)):
    """Disconnect Slack workspace"""
    await db.slack_connections.delete_one({"user_id": ObjectId(user_id)})
    return {"success": True, "message": "Slack disconnected."}
