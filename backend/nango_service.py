"""
Nango Service - Reusable utility for managing OAuth integrations via Nango.
Handles: OAuth connection flow, authenticated API proxy calls, connection storage.
"""
import os
import httpx
import logging
from datetime import datetime
from bson import ObjectId

logger = logging.getLogger(__name__)


class NangoService:
    """Reusable Nango integration service"""

    def __init__(self, db):
        self.db = db
        self.secret_key = os.environ.get("NANGO_SECRET_KEY")
        self.host = os.environ.get("NANGO_HOST", "https://api.nango.dev")
        self._headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }

    # ---- Connect Session ----

    async def create_connect_session(self, user_id: str, allowed_integrations: list = None) -> dict:
        """
        Create a Nango Connect session token for the frontend SDK.
        The end_user is mapped to our internal user_id.
        Includes OAuth scope overrides for integrations that need them.
        """
        payload = {
            "end_user": {
                "id": user_id,
                "display_name": None,
            },
            "integrations_config_defaults": {
                "google-analytics": {
                    "oauth_scopes_override": [
                        "https://www.googleapis.com/auth/analytics.readonly",
                        "https://www.googleapis.com/auth/analytics",
                    ]
                },
                "google-ads": {
                    "oauth_scopes_override": [
                        "https://www.googleapis.com/auth/adwords",
                    ]
                },
            },
        }
        if allowed_integrations:
            payload["allowed_integrations"] = allowed_integrations

        # Optionally enrich display_name from DB
        user = await self.db.users.find_one({"_id": ObjectId(user_id)}, {"name": 1})
        if user:
            payload["end_user"]["display_name"] = user.get("name", user_id)

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{self.host}/connect/sessions",
                headers=self._headers,
                json=payload,
            )
            if resp.status_code not in (200, 201):
                logger.error(f"Nango create session failed: {resp.status_code} {resp.text}")
                raise Exception(f"Nango session creation failed: {resp.text}")
            return resp.json()

    # ---- Connection Management ----

    async def save_connection(self, user_id: str, integration_id: str, connection_id: str) -> dict:
        """Save a Nango connection ID for a user-integration pair"""
        doc = {
            "user_id": ObjectId(user_id),
            "integration_id": integration_id,
            "connection_id": connection_id,
            "provider": integration_id,
            "status": "connected",
            "connected_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        await self.db.nango_connections.update_one(
            {"user_id": ObjectId(user_id), "integration_id": integration_id},
            {"$set": doc},
            upsert=True,
        )
        return {"success": True, "integration_id": integration_id, "connection_id": connection_id}

    async def get_connection(self, user_id: str, integration_id: str) -> dict:
        """Get a stored Nango connection for a user"""
        conn = await self.db.nango_connections.find_one(
            {"user_id": ObjectId(user_id), "integration_id": integration_id},
            {"_id": 0, "user_id": 0},
        )
        return conn

    async def get_all_connections(self, user_id: str) -> list:
        """Get all Nango connections for a user"""
        conns = await self.db.nango_connections.find(
            {"user_id": ObjectId(user_id)},
            {"_id": 0, "user_id": 0},
        ).to_list(50)
        for c in conns:
            if "connected_at" in c and c["connected_at"]:
                c["connected_at"] = c["connected_at"].isoformat()
            if "updated_at" in c and c["updated_at"]:
                c["updated_at"] = c["updated_at"].isoformat()
        return conns

    async def delete_connection(self, user_id: str, integration_id: str) -> bool:
        """Remove a stored Nango connection"""
        result = await self.db.nango_connections.delete_one(
            {"user_id": ObjectId(user_id), "integration_id": integration_id}
        )
        # Also delete from Nango server
        conn = await self.db.nango_connections.find_one(
            {"user_id": ObjectId(user_id), "integration_id": integration_id}
        )
        if conn and conn.get("connection_id"):
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    await client.delete(
                        f"{self.host}/connection/{conn['connection_id']}",
                        headers=self._headers,
                        params={"provider_config_key": integration_id},
                    )
            except Exception as e:
                logger.warning(f"Failed to delete Nango remote connection: {e}")
        return result.deleted_count > 0

    # ---- Proxy Requests ----

    async def proxy_get(self, integration_id: str, connection_id: str, endpoint: str, params: dict = None) -> dict:
        """Make an authenticated GET request through Nango's proxy"""
        headers = {
            **self._headers,
            "Connection-Id": connection_id,
            "Provider-Config-Key": integration_id,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{self.host}/proxy{endpoint}",
                headers=headers,
                params=params,
            )
            return {"status": resp.status_code, "data": resp.json() if resp.status_code == 200 else resp.text}

    async def proxy_post(self, integration_id: str, connection_id: str, endpoint: str, data: dict = None) -> dict:
        """Make an authenticated POST request through Nango's proxy"""
        headers = {
            **self._headers,
            "Connection-Id": connection_id,
            "Provider-Config-Key": integration_id,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self.host}/proxy{endpoint}",
                headers=headers,
                json=data,
            )
            return {"status": resp.status_code, "data": resp.json() if resp.status_code == 200 else resp.text}
