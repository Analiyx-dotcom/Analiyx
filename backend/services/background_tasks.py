import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

_running_tasks: dict = {}


class BackgroundTaskManager:
    """Manages async background jobs for metadata scanning, profiling, and enrichment."""

    def __init__(self, db):
        self.db = db

    async def submit_scan(self, datasource_id: str, user_id: str) -> str:
        from services.metadata.scanner import MetadataScanner
        job_id = f"scan-{datasource_id}"
        if job_id in _running_tasks and not _running_tasks[job_id].done():
            return job_id

        async def _run():
            await self.db.background_jobs.update_one(
                {"_id": job_id},
                {"$set": {"status": "running", "type": "scan", "datasource_id": datasource_id,
                          "user_id": user_id, "started_at": datetime.now(timezone.utc).isoformat()}},
                upsert=True,
            )
            try:
                scanner = MetadataScanner(self.db)
                result = scanner.scan_datasource(datasource_id, user_id)
                if asyncio.iscoroutine(result):
                    result = await result
                await self.db.background_jobs.update_one(
                    {"_id": job_id},
                    {"$set": {"status": "completed", "completed_at": datetime.now(timezone.utc).isoformat(),
                              "result_summary": {"total_tables": result.get("total_tables", 0)}}},
                )
            except Exception as e:
                logger.error("Background scan failed: %s", e)
                await self.db.background_jobs.update_one(
                    {"_id": job_id},
                    {"$set": {"status": "failed", "error": str(e),
                              "completed_at": datetime.now(timezone.utc).isoformat()}},
                )

        task = asyncio.create_task(_run())
        _running_tasks[job_id] = task
        return job_id

    async def submit_profile(self, datasource_id: str, user_id: str) -> str:
        from services.metadata.profiler import MetadataProfiler
        job_id = f"profile-{datasource_id}"
        if job_id in _running_tasks and not _running_tasks[job_id].done():
            return job_id

        async def _run():
            await self.db.background_jobs.update_one(
                {"_id": job_id},
                {"$set": {"status": "running", "type": "profile", "datasource_id": datasource_id,
                          "user_id": user_id, "started_at": datetime.now(timezone.utc).isoformat()}},
                upsert=True,
            )
            try:
                profiler = MetadataProfiler(self.db)
                results = await profiler.profile_datasource(datasource_id, user_id)
                await self.db.background_jobs.update_one(
                    {"_id": job_id},
                    {"$set": {"status": "completed", "completed_at": datetime.now(timezone.utc).isoformat(),
                              "result_summary": {"tables_profiled": len(results)}}},
                )
            except Exception as e:
                logger.error("Background profile failed: %s", e)
                await self.db.background_jobs.update_one(
                    {"_id": job_id},
                    {"$set": {"status": "failed", "error": str(e),
                              "completed_at": datetime.now(timezone.utc).isoformat()}},
                )

        task = asyncio.create_task(_run())
        _running_tasks[job_id] = task
        return job_id

    async def submit_enrich(self, datasource_id: str, user_id: str) -> str:
        from services.metadata.embeddings import EmbeddingService
        job_id = f"enrich-{datasource_id}"
        if job_id in _running_tasks and not _running_tasks[job_id].done():
            return job_id

        async def _run():
            await self.db.background_jobs.update_one(
                {"_id": job_id},
                {"$set": {"status": "running", "type": "enrich", "datasource_id": datasource_id,
                          "user_id": user_id, "started_at": datetime.now(timezone.utc).isoformat()}},
                upsert=True,
            )
            try:
                svc = EmbeddingService(self.db)
                count = await svc.generate_descriptions(datasource_id, user_id)
                await self.db.background_jobs.update_one(
                    {"_id": job_id},
                    {"$set": {"status": "completed", "completed_at": datetime.now(timezone.utc).isoformat(),
                              "result_summary": {"tables_enriched": count}}},
                )
            except Exception as e:
                logger.error("Background enrich failed: %s", e)
                await self.db.background_jobs.update_one(
                    {"_id": job_id},
                    {"$set": {"status": "failed", "error": str(e),
                              "completed_at": datetime.now(timezone.utc).isoformat()}},
                )

        task = asyncio.create_task(_run())
        _running_tasks[job_id] = task
        return job_id

    async def get_job_status(self, job_id: str) -> Optional[dict]:
        doc = await self.db.background_jobs.find_one({"_id": job_id})
        if doc:
            doc["id"] = doc.pop("_id")
        return doc

    async def list_jobs(self, user_id: str, limit: int = 20):
        cursor = self.db.background_jobs.find(
            {"user_id": user_id}, {"_id": 1, "type": 1, "status": 1, "started_at": 1, "completed_at": 1}
        ).sort("started_at", -1).limit(limit)
        results = []
        async for doc in cursor:
            doc["id"] = doc.pop("_id")
            results.append(doc)
        return results
