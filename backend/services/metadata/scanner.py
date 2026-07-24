import logging
from datetime import datetime, timezone
from typing import Dict, Any
from services.connectors.factory import ConnectorFactory

logger = logging.getLogger(__name__)


class MetadataScanner:
    """Scans external databases to extract schema, table, and column metadata."""

    def __init__(self, db):
        self.db = db

    async def scan_datasource(self, datasource_id: str, user_id: str) -> Dict[str, Any]:
        ds = await self.db.external_datasources.find_one({"_id": datasource_id, "user_id": user_id})
        if not ds:
            raise ValueError("Datasource not found")

        connector = ConnectorFactory.create(ds["db_type"], ds["connection"])
        schemas_list = await connector.get_schemas()

        scan_result = {"datasource_id": datasource_id, "schemas": [], "total_tables": 0, "total_columns": 0}

        for schema_name in schemas_list:
            tables = await connector.get_tables(schema_name)
            schema_data = {"name": schema_name, "tables": []}

            for tbl in tables:
                columns = await connector.get_columns(schema_name, tbl["name"])
                table_data = {
                    "name": tbl["name"],
                    "type": tbl["type"],
                    "row_estimate": tbl.get("row_estimate", 0),
                    "columns": columns,
                    "column_count": len(columns),
                }
                schema_data["tables"].append(table_data)
                scan_result["total_columns"] += len(columns)

            scan_result["total_tables"] += len(tables)
            scan_result["schemas"].append(schema_data)

        now = datetime.now(timezone.utc).isoformat()
        await self.db.metadata_schemas.update_one(
            {"datasource_id": datasource_id},
            {
                "$set": {
                    "datasource_id": datasource_id,
                    "user_id": user_id,
                    "metadata": scan_result,
                    "scanned_at": now,
                    "status": "completed",
                }
            },
            upsert=True,
        )

        await self.db.external_datasources.update_one(
            {"_id": datasource_id},
            {"$set": {"last_scanned": now, "scan_status": "completed"}},
        )

        logger.info("Metadata scan completed for datasource %s: %d schemas, %d tables, %d columns",
                     datasource_id, len(schemas_list), scan_result["total_tables"], scan_result["total_columns"])
        return scan_result

    async def get_metadata(self, datasource_id: str, user_id: str) -> Dict[str, Any]:
        doc = await self.db.metadata_schemas.find_one(
            {"datasource_id": datasource_id, "user_id": user_id}, {"_id": 0}
        )
        return doc

    async def get_tables_flat(self, datasource_id: str, user_id: str):
        doc = await self.db.metadata_schemas.find_one(
            {"datasource_id": datasource_id, "user_id": user_id}
        )
        if not doc:
            return []
        tables = []
        for schema in doc.get("metadata", {}).get("schemas", []):
            for tbl in schema.get("tables", []):
                tables.append({
                    "schema": schema["name"],
                    "table": tbl["name"],
                    "type": tbl["type"],
                    "row_estimate": tbl.get("row_estimate", 0),
                    "column_count": tbl.get("column_count", 0),
                    "columns": tbl.get("columns", []),
                })
        return tables
