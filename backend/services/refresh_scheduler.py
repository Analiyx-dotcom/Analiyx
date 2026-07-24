"""Scheduled metadata refresh: 5m / 15m / 1h / 1d / manual intervals per datasource."""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

INTERVALS = {"5m": 300, "15m": 900, "1h": 3600, "1d": 86400}
_scheduler_task: Optional[asyncio.Task] = None


class RefreshScheduler:
    def __init__(self, db):
        self.db = db

    async def set_schedule(self, datasource_id: str, user_id: str, interval: str) -> dict:
        if interval != "manual" and interval not in INTERVALS:
            raise ValueError(f"Invalid interval. Use one of: manual, {', '.join(INTERVALS)}")
        ds = await self.db.external_datasources.find_one({"_id": datasource_id, "user_id": user_id})
        if not ds:
            raise ValueError("Datasource not found")
        now = datetime.now(timezone.utc)
        next_run = (now + timedelta(seconds=INTERVALS[interval])).isoformat() if interval != "manual" else None
        doc = {
            "datasource_id": datasource_id,
            "user_id": user_id,
            "interval": interval,
            "next_run": next_run,
            "updated_at": now.isoformat(),
        }
        await self.db.refresh_schedules.update_one(
            {"datasource_id": datasource_id}, {"$set": doc}, upsert=True
        )
        return doc

    async def list_schedules(self, user_id: str):
        cursor = self.db.refresh_schedules.find({"user_id": user_id}, {"_id": 0})
        return await cursor.to_list(100)

    async def trigger_refresh(self, datasource_id: str, user_id: str) -> dict:
        from services.background_tasks import BackgroundTaskManager
        mgr = BackgroundTaskManager(self.db)
        scan_job = await mgr.submit_scan(datasource_id, user_id)
        enrich_job = await mgr.submit_enrich(datasource_id, user_id)
        now = datetime.now(timezone.utc).isoformat()
        await self.db.refresh_schedules.update_one(
            {"datasource_id": datasource_id},
            {"$set": {"last_run": now, "last_run_status": "triggered"}},
        )
        return {"scan_job": scan_job, "enrich_job": enrich_job, "triggered_at": now}

    async def run_loop(self):
        logger.info("Refresh scheduler started")
        while True:
            try:
                await asyncio.sleep(60)
                now = datetime.now(timezone.utc)
                cursor = self.db.refresh_schedules.find({
                    "interval": {"$in": list(INTERVALS.keys())},
                    "next_run": {"$lte": now.isoformat()},
                })
                async for sched in cursor:
                    try:
                        await self.trigger_refresh(sched["datasource_id"], sched["user_id"])
                        next_run = (now + timedelta(seconds=INTERVALS[sched["interval"]])).isoformat()
                        await self.db.refresh_schedules.update_one(
                            {"datasource_id": sched["datasource_id"]},
                            {"$set": {"next_run": next_run}},
                        )
                        logger.info("Scheduled refresh triggered for %s", sched["datasource_id"])
                    except Exception as e:
                        logger.error("Scheduled refresh failed for %s: %s", sched.get("datasource_id"), e)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Scheduler loop error: %s", e)


def start_scheduler(db):
    global _scheduler_task
    if _scheduler_task is None or _scheduler_task.done():
        _scheduler_task = asyncio.create_task(RefreshScheduler(db).run_loop())
