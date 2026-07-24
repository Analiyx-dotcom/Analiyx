import aiomysql
import time
import logging
from typing import List, Dict, Any, Optional
from .base import BaseConnector

logger = logging.getLogger(__name__)


class MySQLConnector(BaseConnector):

    async def _get_conn(self):
        return await aiomysql.connect(
            host=self.config["host"],
            port=int(self.config.get("port", 3306)),
            user=self.config["username"],
            password=self.config["password"],
            db=self.config["database"],
            connect_timeout=15,
        )

    async def test_connection(self) -> dict:
        start = time.time()
        try:
            conn = await self._get_conn()
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1")
                await cur.execute("SELECT VERSION()")
                version = (await cur.fetchone())[0]
            latency = round((time.time() - start) * 1000, 2)
            conn.close()
            return {"success": True, "message": f"Connected. MySQL {version}", "latency_ms": latency}
        except Exception as e:
            return {"success": False, "message": str(e), "latency_ms": round((time.time() - start) * 1000, 2)}

    async def get_schemas(self) -> List[str]:
        conn = await self._get_conn()
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT SCHEMA_NAME FROM information_schema.SCHEMATA "
                    "WHERE SCHEMA_NAME NOT IN ('information_schema','mysql','performance_schema','sys') ORDER BY SCHEMA_NAME"
                )
                rows = await cur.fetchall()
                return [r[0] for r in rows]
        finally:
            conn.close()

    async def get_tables(self, schema: str) -> List[Dict[str, Any]]:
        conn = await self._get_conn()
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT TABLE_NAME, TABLE_TYPE, TABLE_ROWS
                    FROM information_schema.TABLES
                    WHERE TABLE_SCHEMA = %s ORDER BY TABLE_NAME
                    """,
                    (schema,),
                )
                rows = await cur.fetchall()
                return [
                    {"name": r[0], "type": "view" if r[1] == "VIEW" else "table", "row_estimate": r[2] or 0}
                    for r in rows
                ]
        finally:
            conn.close()

    async def get_columns(self, schema: str, table: str) -> List[Dict[str, Any]]:
        conn = await self._get_conn()
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_KEY
                    FROM information_schema.COLUMNS
                    WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                    ORDER BY ORDINAL_POSITION
                    """,
                    (schema, table),
                )
                rows = await cur.fetchall()
                return [
                    {
                        "name": r[0],
                        "data_type": r[1],
                        "nullable": r[2] == "YES",
                        "is_primary": r[4] == "PRI",
                        "default": r[3],
                    }
                    for r in rows
                ]
        finally:
            conn.close()

    async def execute_query(self, sql: str, params: Optional[dict] = None, limit: int = 1000) -> Dict[str, Any]:
        conn = await self._get_conn()
        try:
            safe_sql = sql.rstrip("; \n")
            wrapped = f"SELECT * FROM ({safe_sql}) _q LIMIT {limit}"
            async with conn.cursor(aiomysql.DictCursor) as cur:
                start = time.time()
                await cur.execute(wrapped)
                rows = await cur.fetchall()
                execution_time = round((time.time() - start) * 1000, 2)
                columns = [d[0] for d in cur.description] if cur.description else []
            for row in rows:
                for k, v in row.items():
                    if not isinstance(v, (str, int, float, bool, type(None))):
                        row[k] = str(v)
            return {"columns": columns, "rows": list(rows), "row_count": len(rows), "execution_time_ms": execution_time}
        finally:
            conn.close()

    async def get_sample_data(self, schema: str, table: str, limit: int = 100) -> Dict[str, Any]:
        sql = f"SELECT * FROM `{schema}`.`{table}` LIMIT {limit}"
        return await self.execute_query(sql, limit=limit)

    async def get_row_count(self, schema: str, table: str) -> int:
        conn = await self._get_conn()
        try:
            async with conn.cursor() as cur:
                await cur.execute(f"SELECT COUNT(*) FROM `{schema}`.`{table}`")
                row = await cur.fetchone()
                return row[0]
        finally:
            conn.close()

    async def get_column_stats(self, schema: str, table: str, column: str) -> Dict[str, Any]:
        conn = await self._get_conn()
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    f"""
                    SELECT
                        COUNT(*) AS total_rows,
                        COUNT(`{column}`) AS non_null_count,
                        COUNT(*) - COUNT(`{column}`) AS null_count,
                        COUNT(DISTINCT `{column}`) AS distinct_count,
                        MIN(`{column}`) AS min_value,
                        MAX(`{column}`) AS max_value
                    FROM `{schema}`.`{table}`
                    """
                )
                r = await cur.fetchone()
                return {
                    "total_rows": r[0],
                    "non_null_count": r[1],
                    "null_count": r[2],
                    "distinct_count": r[3],
                    "min_value": str(r[4]) if r[4] is not None else None,
                    "max_value": str(r[5]) if r[5] is not None else None,
                    "null_percentage": round((r[2] / max(r[0], 1)) * 100, 2),
                }
        finally:
            conn.close()
