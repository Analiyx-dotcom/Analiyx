"""Routes for query planning, validation, and execution (Live/Cached/Hybrid)."""

import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from auth import get_verified_user_id
from services.query.planner import QueryPlanner
from services.query.validator import SQLValidator
from services.query.executor import QueryExecutor
from services.cache.redis_cache import RedisCache

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/query", tags=["query"])

db = None


def set_database(database):
    global db
    db = database


class PlanRequest(BaseModel):
    datasource_id: str
    question: str


class ValidateRequest(BaseModel):
    sql: str
    db_type: str = "postgresql"


class ExecuteRequest(BaseModel):
    datasource_id: str
    sql: str
    mode: str = "hybrid"  # "live" | "cached" | "hybrid"
    cache_ttl: int = 300


@router.post("/plan")
async def plan_query(req: PlanRequest, user_id: str = Depends(get_verified_user_id)):
    try:
        planner = QueryPlanner(db)
        result = await planner.plan_query(req.datasource_id, user_id, req.question)
        return result
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error("Query planning failed: %s", e)
        raise HTTPException(500, f"Planning failed: {e}")


@router.post("/validate")
async def validate_query(req: ValidateRequest):
    result = SQLValidator.validate(req.sql, req.db_type)
    return result


@router.post("/execute")
async def execute_query(req: ExecuteRequest, user_id: str = Depends(get_verified_user_id)):
    executor = QueryExecutor(db)
    result = await executor.execute(
        datasource_id=req.datasource_id,
        user_id=user_id,
        sql=req.sql,
        mode=req.mode,
        cache_ttl=req.cache_ttl,
    )
    if not result.get("success"):
        raise HTTPException(400, result.get("error", "Execution failed"))
    return result


@router.get("/history")
async def query_history(datasource_id: Optional[str] = None, limit: int = 50,
                        user_id: str = Depends(get_verified_user_id)):
    executor = QueryExecutor(db)
    history = await executor.get_history(user_id, datasource_id, limit)
    return {"history": history, "count": len(history)}


@router.post("/cache/clear/{datasource_id}")
async def clear_cache(datasource_id: str, user_id: str = Depends(get_verified_user_id)):
    executor = QueryExecutor(db)
    try:
        result = await executor.clear_cache(datasource_id, user_id)
        return result
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.get("/cache/stats")
async def cache_stats():
    cache = RedisCache()
    stats = await cache.get_stats()
    return stats
