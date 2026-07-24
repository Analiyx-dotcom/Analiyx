"""Live analytics engine routes: datasource status, manual refresh, refresh schedules."""

import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from auth import get_verified_user_id
from services.refresh_scheduler import RefreshScheduler
from services.cache.redis_cache import RedisCache
from services.connectors.factory import ConnectorFactory

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/live", tags=["live"])

db = None


def set_database(database):
    global db
    db = database


class RefreshRequest(BaseModel):
    datasource_id: str


class ScheduleRequest(BaseModel):
    datasource_id: str
    interval: str  # manual | 5m | 15m | 1h | 1d


@router.get("/status")
async def live_status(check: bool = False, user_id: str = Depends(get_verified_user_id)):
    datasources = await db.external_datasources.find({"user_id": user_id}).to_list(100)
    schedules = {s["datasource_id"]: s for s in await RefreshScheduler(db).list_schedules(user_id)}
    cache_stats = await RedisCache().get_stats()

    items = []
    for ds in datasources:
        item = {
            "id": ds["_id"],
            "name": ds.get("name"),
            "db_type": ds.get("db_type"),
            "last_scanned": ds.get("last_scanned"),
            "scan_status": ds.get("scan_status"),
            "schedule": schedules.get(ds["_id"], {"interval": "manual"}),
        }
        if check:
            try:
                connector = ConnectorFactory.create(ds["db_type"], ds["connection"])
                item["health"] = await connector.test_connection()
            except Exception as e:
                item["health"] = {"success": False, "message": str(e)}
        items.append(item)

    return {"datasources": items, "cache": cache_stats, "count": len(items)}


@router.post("/refresh")
async def live_refresh(req: RefreshRequest, user_id: str = Depends(get_verified_user_id)):
    ds = await db.external_datasources.find_one({"_id": req.datasource_id, "user_id": user_id})
    if not ds:
        raise HTTPException(404, "Datasource not found")
    result = await RefreshScheduler(db).trigger_refresh(req.datasource_id, user_id)
    return {"status": "triggered", **result}


@router.post("/schedule")
async def set_schedule(req: ScheduleRequest, user_id: str = Depends(get_verified_user_id)):
    try:
        sched = await RefreshScheduler(db).set_schedule(req.datasource_id, user_id, req.interval)
        return sched
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/schedules")
async def list_schedules(user_id: str = Depends(get_verified_user_id)):
    schedules = await RefreshScheduler(db).list_schedules(user_id)
    return {"schedules": schedules}
