import logging
from datetime import datetime, timezone
from typing import Dict, Any, List
from services.connectors.factory import ConnectorFactory

logger = logging.getLogger(__name__)


class MetadataProfiler:
    """Profiles external database tables: row counts, column statistics, data quality."""

    def __init__(self, db):
        self.db = db

    async def profile_table(self, datasource_id: str, user_id: str, schema: str, table: str) -> Dict[str, Any]:
        ds = await self.db.external_datasources.find_one({"_id": datasource_id, "user_id": user_id})
        if not ds:
            raise ValueError("Datasource not found")

        connector = ConnectorFactory.create(ds["db_type"], ds["connection"])
        row_count = await connector.get_row_count(schema, table)
        columns = await connector.get_columns(schema, table)

        column_profiles = []
        for col in columns:
            try:
                stats = await connector.get_column_stats(schema, table, col["name"])
                stats["column_name"] = col["name"]
                stats["data_type"] = col["data_type"]
                column_profiles.append(stats)
            except Exception as e:
                logger.warning("Failed to profile column %s.%s.%s: %s", schema, table, col["name"], e)
                column_profiles.append({
                    "column_name": col["name"],
                    "data_type": col["data_type"],
                    "error": str(e),
                })

        profile = {
            "datasource_id": datasource_id,
            "schema": schema,
            "table": table,
            "row_count": row_count,
            "column_count": len(columns),
            "columns": column_profiles,
            "profiled_at": datetime.now(timezone.utc).isoformat(),
        }

        await self.db.metadata_profiles.update_one(
            {"datasource_id": datasource_id, "schema": schema, "table": table},
            {"$set": {**profile, "user_id": user_id}},
            upsert=True,
        )

        logger.info("Profiled %s.%s: %d rows, %d columns", schema, table, row_count, len(columns))
        return profile

    async def profile_datasource(self, datasource_id: str, user_id: str) -> List[Dict[str, Any]]:
        """Profile all tables in a datasource (uses cached metadata scan)."""
        meta = await self.db.metadata_schemas.find_one({"datasource_id": datasource_id, "user_id": user_id})
        if not meta:
            raise ValueError("No metadata found. Run a scan first.")

        profiles = []
        for schema in meta.get("metadata", {}).get("schemas", []):
            for tbl in schema.get("tables", []):
                try:
                    p = await self.profile_table(datasource_id, user_id, schema["name"], tbl["name"])
                    profiles.append(p)
                except Exception as e:
                    logger.warning("Failed to profile %s.%s: %s", schema["name"], tbl["name"], e)
        return profiles

    async def get_profile(self, datasource_id: str, schema: str, table: str) -> Dict[str, Any]:
        doc = await self.db.metadata_profiles.find_one(
            {"datasource_id": datasource_id, "schema": schema, "table": table}, {"_id": 0}
        )
        return doc

    async def get_all_profiles(self, datasource_id: str) -> List[Dict[str, Any]]:
        cursor = self.db.metadata_profiles.find({"datasource_id": datasource_id}, {"_id": 0})
        return await cursor.to_list(500)
