"""Routes for managing external database connections (PostgreSQL, MySQL)."""

import uuid
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from auth import get_verified_user_id
from services.connectors.factory import ConnectorFactory

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/datasources", tags=["datasources"])

db = None


def set_database(database):
    global db
    db = database


class DatasourceCreateRequest(BaseModel):
    name: str
    db_type: str  # "postgresql" or "mysql"
    host: str
    port: int = 5432
    database: str
    username: str
    password: str
    ssl: bool = False
    description: str = ""


class DatasourceUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


@router.post("/connect")
async def connect_datasource(req: DatasourceCreateRequest, user_id: str = Depends(get_verified_user_id)):
    if req.db_type not in ConnectorFactory.supported_types():
        raise HTTPException(400, f"Unsupported type. Supported: {ConnectorFactory.supported_types()}")

    config = {
        "host": req.host,
        "port": req.port,
        "database": req.database,
        "username": req.username,
        "password": req.password,
        "ssl": req.ssl,
    }

    connector = ConnectorFactory.create(req.db_type, config)
    test_result = await connector.test_connection()
    if not test_result["success"]:
        raise HTTPException(400, f"Connection failed: {test_result['message']}")

    ds_id = str(uuid.uuid4())
    doc = {
        "_id": ds_id,
        "user_id": user_id,
        "name": req.name,
        "db_type": req.db_type,
        "connection": config,
        "description": req.description,
        "status": "connected",
        "scan_status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_tested": datetime.now(timezone.utc).isoformat(),
        "test_latency_ms": test_result["latency_ms"],
    }
    await db.external_datasources.insert_one(doc)

    return {
        "id": ds_id,
        "name": req.name,
        "db_type": req.db_type,
        "status": "connected",
        "message": test_result["message"],
        "latency_ms": test_result["latency_ms"],
    }


@router.post("/{ds_id}/test")
async def test_datasource(ds_id: str, user_id: str = Depends(get_verified_user_id)):
    ds = await db.external_datasources.find_one({"_id": ds_id, "user_id": user_id})
    if not ds:
        raise HTTPException(404, "Datasource not found")

    connector = ConnectorFactory.create(ds["db_type"], ds["connection"])
    result = await connector.test_connection()

    status = "connected" if result["success"] else "error"
    await db.external_datasources.update_one(
        {"_id": ds_id},
        {"$set": {"status": status, "last_tested": datetime.now(timezone.utc).isoformat(),
                  "test_latency_ms": result["latency_ms"]}},
    )
    return result


@router.get("/supported-types")
async def supported_types():
    return {"types": ConnectorFactory.supported_types()}


@router.get("/")
async def list_datasources(user_id: str = Depends(get_verified_user_id)):
    cursor = db.external_datasources.find(
        {"user_id": user_id},
        {"connection.password": 0},
    ).sort("created_at", -1)
    results = []
    async for doc in cursor:
        doc["id"] = doc.pop("_id")
        conn = doc.get("connection", {})
        conn.pop("password", None)
        results.append(doc)
    return {"datasources": results}


@router.get("/{ds_id}")
async def get_datasource(ds_id: str, user_id: str = Depends(get_verified_user_id)):
    doc = await db.external_datasources.find_one({"_id": ds_id, "user_id": user_id})
    if not doc:
        raise HTTPException(404, "Datasource not found")
    doc["id"] = doc.pop("_id")
    doc.get("connection", {}).pop("password", None)
    return doc


@router.put("/{ds_id}")
async def update_datasource(ds_id: str, req: DatasourceUpdateRequest, user_id: str = Depends(get_verified_user_id)):
    updates = {k: v for k, v in req.model_dump(exclude_none=True).items()}
    if not updates:
        raise HTTPException(400, "No updates provided")
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    result = await db.external_datasources.update_one({"_id": ds_id, "user_id": user_id}, {"$set": updates})
    if result.matched_count == 0:
        raise HTTPException(404, "Datasource not found")
    return {"success": True}


@router.delete("/{ds_id}")
async def delete_datasource(ds_id: str, user_id: str = Depends(get_verified_user_id)):
    result = await db.external_datasources.delete_one({"_id": ds_id, "user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Datasource not found")
    await db.metadata_schemas.delete_many({"datasource_id": ds_id})
    await db.metadata_profiles.delete_many({"datasource_id": ds_id})
    await db.metadata_embeddings.delete_many({"datasource_id": ds_id})
    return {"success": True, "message": "Datasource and all related metadata deleted"}
