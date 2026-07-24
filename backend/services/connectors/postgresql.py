import asyncpg
import time
import logging
from typing import List, Dict, Any, Optional
from .base import BaseConnector

logger = logging.getLogger(__name__)


class PostgreSQLConnector(BaseConnector):

    async def _get_conn(self):
        return await asyncpg.connect(
            host=self.config["host"],
            port=int(self.config.get("port", 5432)),
            user=self.config["username"],
            password=self.config["password"],
            database=self.config["database"],
            ssl=self.config.get("ssl", False) or None,
            timeout=15,
        )

    async def test_connection(self) -> dict:
        start = time.time()
        try:
            conn = await self._get_conn()
            await conn.execute("SELECT 1")
            latency = round((time.time() - start) * 1000, 2)
            version = await conn.fetchval("SELECT version()")
            await conn.close()
            return {"success": True, "message": f"Connected. {version}", "latency_ms": latency}
        except Exception as e:
            return {"success": False, "message": str(e), "latency_ms": round((time.time() - start) * 1000, 2)}

    async def get_schemas(self) -> List[str]:
        conn = await self._get_conn()
        try:
            rows = await conn.fetch(
                "SELECT schema_name FROM information_schema.schemata "
                "WHERE schema_name NOT IN ('pg_catalog','information_schema','pg_toast') ORDER BY schema_name"
            )
            return [r["schema_name"] for r in rows]
        finally:
            await conn.close()

    async def get_tables(self, schema: str) -> List[Dict[str, Any]]:
        conn = await self._get_conn()
        try:
            rows = await conn.fetch(
                """
                SELECT t.table_name, t.table_type,
                       COALESCE(s.n_live_tup, 0) AS row_estimate
                FROM information_schema.tables t
                LEFT JOIN pg_stat_user_tables s
                  ON s.schemaname = t.table_schema AND s.relname = t.table_name
                WHERE t.table_schema = $1
                ORDER BY t.table_name
                """,
                schema,
            )
            return [
                {
                    "name": r["table_name"],
                    "type": "view" if r["table_type"] == "VIEW" else "table",
                    "row_estimate": r["row_estimate"],
                }
                for r in rows
            ]
        finally:
            await conn.close()

    async def get_columns(self, schema: str, table: str) -> List[Dict[str, Any]]:
        conn = await self._get_conn()
        try:
            rows = await conn.fetch(
                """
                SELECT c.column_name, c.data_type, c.is_nullable,
                       c.column_default,
                       CASE WHEN pk.column_name IS NOT NULL THEN true ELSE false END AS is_primary
                FROM information_schema.columns c
                LEFT JOIN (
                    SELECT kcu.column_name
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                      ON tc.constraint_name = kcu.constraint_name
                    WHERE tc.table_schema = $1 AND tc.table_name = $2 AND tc.constraint_type = 'PRIMARY KEY'
                ) pk ON pk.column_name = c.column_name
                WHERE c.table_schema = $1 AND c.table_name = $2
                ORDER BY c.ordinal_position
                """,
                schema,
                table,
            )
            return [
                {
                    "name": r["column_name"],
                    "data_type": r["data_type"],
                    "nullable": r["is_nullable"] == "YES",
                    "is_primary": r["is_primary"],
                    "default": r["column_default"],
                }
                for r in rows
            ]
        finally:
            await conn.close()

    async def execute_query(self, sql: str, params: Optional[dict] = None, limit: int = 1000) -> Dict[str, Any]:
        conn = await self._get_conn()
        try:
            safe_sql = sql.rstrip("; \n")
            wrapped = f"SELECT * FROM ({safe_sql}) _q LIMIT {limit}"
            start = time.time()
            stmt = await conn.prepare(wrapped)
            columns = [a.name for a in stmt.get_attributes()]
            rows_raw = await stmt.fetch()
            execution_time = round((time.time() - start) * 1000, 2)
            rows = [dict(r) for r in rows_raw]
            # Serialize non-JSON types
            for row in rows:
                for k, v in row.items():
                    if not isinstance(v, (str, int, float, bool, type(None))):
                        row[k] = str(v)
            return {"columns": columns, "rows": rows, "row_count": len(rows), "execution_time_ms": execution_time}
        finally:
            await conn.close()

    async def get_sample_data(self, schema: str, table: str, limit: int = 100) -> Dict[str, Any]:
        sql = f'SELECT * FROM "{schema}"."{table}" LIMIT {limit}'
        return await self.execute_query(sql, limit=limit)

    async def get_row_count(self, schema: str, table: str) -> int:
        conn = await self._get_conn()
        try:
            count = await conn.fetchval(f'SELECT COUNT(*) FROM "{schema}"."{table}"')
            return count
        finally:
            await conn.close()

    async def get_column_stats(self, schema: str, table: str, column: str) -> Dict[str, Any]:
        conn = await self._get_conn()
        try:
            row = await conn.fetchrow(
                f"""
                SELECT
                    COUNT(*) AS total_rows,
                    COUNT("{column}") AS non_null_count,
                    COUNT(*) - COUNT("{column}") AS null_count,
                    COUNT(DISTINCT "{column}") AS distinct_count,
                    MIN("{column}"::text) AS min_value,
                    MAX("{column}"::text) AS max_value
                FROM "{schema}"."{table}"
                """
            )
            return {
                "total_rows": row["total_rows"],
                "non_null_count": row["non_null_count"],
                "null_count": row["null_count"],
                "distinct_count": row["distinct_count"],
                "min_value": row["min_value"],
                "max_value": row["max_value"],
                "null_percentage": round((row["null_count"] / max(row["total_rows"], 1)) * 100, 2),
            }
        finally:
            await conn.close()
