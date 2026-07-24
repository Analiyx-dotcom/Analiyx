import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from services.connectors.factory import ConnectorFactory
from services.query.validator import SQLValidator
from services.cache.redis_cache import RedisCache

logger = logging.getLogger(__name__)


class QueryExecutor:
    """Executes SQL queries on external databases with Live/Cached/Hybrid modes."""

    def __init__(self, db):
        self.db = db
        self.cache = RedisCache()

    @staticmethod
    def _query_hash(datasource_id: str, sql: str) -> str:
        return hashlib.md5(f"{datasource_id}:{sql.strip()}".encode()).hexdigest()

    async def execute(
        self,
        datasource_id: str,
        user_id: str,
        sql: str,
        mode: str = "hybrid",
        cache_ttl: int = 300,
    ) -> Dict[str, Any]:
        """
        Execute a query.
        Modes:
          - live: Always hit the external DB
          - cached: Only return cached results (fail if not cached)
          - hybrid: Return cache if fresh, else hit DB and cache
        """
        validation = SQLValidator.validate(sql)
        if not validation["valid"]:
            return {"success": False, "error": "Validation failed", "issues": validation["issues"]}

        clean_sql = validation["sql"]
        q_hash = self._query_hash(datasource_id, clean_sql)

        if mode in ("cached", "hybrid"):
            cached = await self.cache.get(f"query:{q_hash}")
            if cached:
                logger.info("Cache HIT for query %s", q_hash[:8])
                result = json.loads(cached)
                result["source"] = "cache"
                return result

        if mode == "cached":
            return {"success": False, "error": "No cached result available", "source": "cache"}

        ds = await self.db.external_datasources.find_one({"_id": datasource_id, "user_id": user_id})
        if not ds:
            return {"success": False, "error": "Datasource not found"}

        connector = ConnectorFactory.create(ds["db_type"], ds["connection"])

        try:
            result = await connector.execute_query(clean_sql)
            result["success"] = True
            result["source"] = "live"
            result["query_hash"] = q_hash

            if mode in ("live", "hybrid"):
                await self.cache.set(f"query:{q_hash}", json.dumps(result, default=str), ttl=cache_ttl)

            await self._save_history(datasource_id, user_id, clean_sql, result)
            return result

        except Exception as e:
            logger.error("Query execution failed: %s", e)
            return {"success": False, "error": str(e), "source": "live"}

    async def _save_history(self, datasource_id: str, user_id: str, sql: str, result: dict):
        await self.db.query_history.insert_one({
            "datasource_id": datasource_id,
            "user_id": user_id,
            "sql": sql,
            "row_count": result.get("row_count", 0),
            "execution_time_ms": result.get("execution_time_ms", 0),
            "source": result.get("source", "unknown"),
            "executed_at": datetime.now(timezone.utc).isoformat(),
        })

    async def get_history(self, user_id: str, datasource_id: Optional[str] = None, limit: int = 50):
        query = {"user_id": user_id}
        if datasource_id:
            query["datasource_id"] = datasource_id
        cursor = self.db.query_history.find(query, {"_id": 0}).sort("executed_at", -1).limit(limit)
        return await cursor.to_list(limit)

    async def clear_cache(self, datasource_id: str, user_id: str):
        ds = await self.db.external_datasources.find_one({"_id": datasource_id, "user_id": user_id})
        if not ds:
            raise ValueError("Datasource not found")
        count = await self.cache.clear_pattern(f"query:*")
        return {"cleared": count}
