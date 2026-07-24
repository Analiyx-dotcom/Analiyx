"""Routes for metadata scanning, profiling, enrichment, relationships, metrics, search, and refresh."""

import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from auth import get_verified_user_id
from services.metadata.scanner import MetadataScanner
from services.metadata.profiler import MetadataProfiler
from services.metadata.embeddings import EmbeddingService
from services.metadata.relationships import RelationshipDetector
from services.semantic.business_metrics import BusinessMetricsService
from services.semantic.search import SemanticSearch
from services.background_tasks import BackgroundTaskManager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/metadata", tags=["metadata"])

db = None


def set_database(database):
    global db
    db = database


@router.post("/scan/{datasource_id}")
async def scan_metadata(datasource_id: str, background: bool = False,
                        user_id: str = Depends(get_verified_user_id)):
    if background:
        mgr = BackgroundTaskManager(db)
        job_id = await mgr.submit_scan(datasource_id, user_id)
        return {"job_id": job_id, "status": "submitted", "message": "Scan running in background"}

    try:
        scanner = MetadataScanner(db)
        result = await scanner.scan_datasource(datasource_id, user_id)
        return {"status": "completed", "metadata": result}
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        logger.error("Scan failed: %s", e)
        raise HTTPException(500, f"Scan failed: {e}")


@router.get("/jobs")
async def list_jobs(user_id: str = Depends(get_verified_user_id)):
    mgr = BackgroundTaskManager(db)
    jobs = await mgr.list_jobs(user_id)
    return {"jobs": jobs}


@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str, user_id: str = Depends(get_verified_user_id)):
    mgr = BackgroundTaskManager(db)
    job = await mgr.get_job_status(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return job


class MetadataSearchRequest(BaseModel):
    datasource_id: str
    query: str
    limit: int = 10


@router.post("/search")
async def metadata_search(req: MetadataSearchRequest, user_id: str = Depends(get_verified_user_id)):
    try:
        search = SemanticSearch(db)
        return await search.search(req.datasource_id, user_id, req.query, req.limit)
    except Exception as e:
        logger.error("Metadata search failed: %s", e)
        raise HTTPException(500, f"Search failed: {e}")


@router.post("/refresh/{datasource_id}")
async def refresh_metadata(datasource_id: str, user_id: str = Depends(get_verified_user_id)):
    """Full metadata refresh: rescan schema, then relationships, metrics, and background AI enrichment."""
    try:
        scanner = MetadataScanner(db)
        scan_result = await scanner.scan_datasource(datasource_id, user_id)
        relationships = await RelationshipDetector(db).detect(datasource_id, user_id)
        metrics = await BusinessMetricsService(db).infer_metrics(datasource_id, user_id)
        mgr = BackgroundTaskManager(db)
        enrich_job = await mgr.submit_enrich(datasource_id, user_id)
        return {
            "status": "completed",
            "tables_scanned": scan_result.get("total_tables", 0),
            "foreign_keys_detected": len(relationships.get("foreign_keys", [])),
            "metrics_inferred": metrics.get("count", 0),
            "glossary_terms_seeded": metrics.get("glossary_terms_seeded", 0),
            "enrich_job": enrich_job,
        }
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        logger.error("Metadata refresh failed: %s", e)
        raise HTTPException(500, f"Refresh failed: {e}")


@router.post("/relationships/{datasource_id}")
async def detect_relationships(datasource_id: str, user_id: str = Depends(get_verified_user_id)):
    try:
        return await RelationshipDetector(db).detect(datasource_id, user_id)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.get("/relationships/{datasource_id}")
async def get_relationships(datasource_id: str, user_id: str = Depends(get_verified_user_id)):
    rel = await RelationshipDetector(db).get(datasource_id, user_id)
    if not rel:
        raise HTTPException(404, "No relationships detected yet. Run detection first.")
    return rel


@router.post("/metrics/{datasource_id}")
async def infer_metrics(datasource_id: str, user_id: str = Depends(get_verified_user_id)):
    try:
        return await BusinessMetricsService(db).infer_metrics(datasource_id, user_id)
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.get("/metrics/{datasource_id}")
async def get_metrics(datasource_id: str, user_id: str = Depends(get_verified_user_id)):
    metrics = await BusinessMetricsService(db).get_metrics(datasource_id, user_id)
    if not metrics:
        raise HTTPException(404, "No metrics inferred yet. Run inference first.")
    return metrics


@router.get("/{datasource_id}")
async def get_metadata(datasource_id: str, user_id: str = Depends(get_verified_user_id)):
    scanner = MetadataScanner(db)
    meta = await scanner.get_metadata(datasource_id, user_id)
    if not meta:
        raise HTTPException(404, "No metadata found. Run a scan first.")
    return meta


@router.get("/{datasource_id}/tables")
async def get_tables(datasource_id: str, user_id: str = Depends(get_verified_user_id)):
    scanner = MetadataScanner(db)
    tables = await scanner.get_tables_flat(datasource_id, user_id)
    return {"tables": tables, "count": len(tables)}


@router.post("/profile/{datasource_id}")
async def profile_datasource(datasource_id: str, background: bool = False,
                              user_id: str = Depends(get_verified_user_id)):
    if background:
        mgr = BackgroundTaskManager(db)
        job_id = await mgr.submit_profile(datasource_id, user_id)
        return {"job_id": job_id, "status": "submitted", "message": "Profiling running in background"}

    try:
        profiler = MetadataProfiler(db)
        results = await profiler.profile_datasource(datasource_id, user_id)
        return {"status": "completed", "profiles": results, "count": len(results)}
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        logger.error("Profile failed: %s", e)
        raise HTTPException(500, f"Profile failed: {e}")


@router.get("/profile/{datasource_id}")
async def get_profiles(datasource_id: str, user_id: str = Depends(get_verified_user_id)):
    profiler = MetadataProfiler(db)
    profiles = await profiler.get_all_profiles(datasource_id)
    return {"profiles": profiles, "count": len(profiles)}


@router.get("/profile/{datasource_id}/{schema}/{table}")
async def get_table_profile(datasource_id: str, schema: str, table: str,
                            user_id: str = Depends(get_verified_user_id)):
    profiler = MetadataProfiler(db)
    profile = await profiler.get_profile(datasource_id, schema, table)
    if not profile:
        raise HTTPException(404, "Profile not found. Run profiling first.")
    return profile


@router.post("/enrich/{datasource_id}")
async def enrich_metadata(datasource_id: str, background: bool = True,
                          user_id: str = Depends(get_verified_user_id)):
    if background:
        mgr = BackgroundTaskManager(db)
        job_id = await mgr.submit_enrich(datasource_id, user_id)
        return {"job_id": job_id, "status": "submitted", "message": "AI enrichment running in background"}

    try:
        svc = EmbeddingService(db)
        count = await svc.generate_descriptions(datasource_id, user_id)
        return {"status": "completed", "tables_enriched": count}
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        logger.error("Enrich failed: %s", e)
        raise HTTPException(500, f"Enrichment failed: {e}")
