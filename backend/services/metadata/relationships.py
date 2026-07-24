"""Detects PK/FK relationships, join paths, and fact/dimension classification from scanned metadata."""

import logging
from datetime import datetime, timezone
from typing import Dict, Any

logger = logging.getLogger(__name__)

NUMERIC_TYPES = ("int", "bigint", "smallint", "float", "double", "numeric", "decimal", "real", "money")


class RelationshipDetector:
    def __init__(self, db):
        self.db = db

    async def detect(self, datasource_id: str, user_id: str) -> Dict[str, Any]:
        meta = await self.db.metadata_schemas.find_one({"datasource_id": datasource_id, "user_id": user_id})
        if not meta:
            raise ValueError("No metadata found. Run a scan first.")

        tables = []
        for schema in meta.get("metadata", {}).get("schemas", []):
            for tbl in schema.get("tables", []):
                tables.append({"schema": schema["name"], "name": tbl["name"], "columns": tbl.get("columns", [])})

        table_names = {}
        for t in tables:
            base = t["name"].lower()
            table_names[base] = t
            if base.endswith("s"):
                table_names[base[:-1]] = t
            else:
                table_names[base + "s"] = t

        primary_keys = []
        foreign_keys = []
        for t in tables:
            for c in t["columns"]:
                if c.get("is_primary"):
                    primary_keys.append({"schema": t["schema"], "table": t["name"], "column": c["name"]})
                cname = c["name"].lower()
                if cname.endswith("_id") and not c.get("is_primary"):
                    ref_base = cname[:-3]
                    ref = table_names.get(ref_base)
                    if ref and ref["name"] != t["name"]:
                        foreign_keys.append({
                            "schema": t["schema"], "table": t["name"], "column": c["name"],
                            "references_schema": ref["schema"], "references_table": ref["name"],
                            "references_column": self._pk_of(ref) or "id",
                            "detected_by": "naming_convention",
                        })

        join_paths = [
            {
                "from": f"{fk['schema']}.{fk['table']}",
                "to": f"{fk['references_schema']}.{fk['references_table']}",
                "on": f"{fk['table']}.{fk['column']} = {fk['references_table']}.{fk['references_column']}",
            }
            for fk in foreign_keys
        ]

        referenced = {fk["references_table"].lower() for fk in foreign_keys}
        fk_counts = {}
        for fk in foreign_keys:
            fk_counts[fk["table"].lower()] = fk_counts.get(fk["table"].lower(), 0) + 1

        fact_tables, dimension_tables = [], []
        for t in tables:
            name_l = t["name"].lower()
            measure_count = sum(
                1 for c in t["columns"]
                if any(nt in str(c.get("data_type", "")).lower() for nt in NUMERIC_TYPES)
                and not c["name"].lower().endswith("_id") and c["name"].lower() != "id"
            )
            if fk_counts.get(name_l, 0) >= 2 and measure_count >= 1:
                fact_tables.append(f"{t['schema']}.{t['name']}")
            elif name_l in referenced:
                dimension_tables.append(f"{t['schema']}.{t['name']}")

        schema_type = "unknown"
        if len(fact_tables) == 1 and len(dimension_tables) >= 2:
            schema_type = "star"
        elif len(fact_tables) >= 1 and len(dimension_tables) >= 2:
            schema_type = "snowflake"
        elif not fact_tables and tables:
            schema_type = "flat"

        result = {
            "datasource_id": datasource_id,
            "primary_keys": primary_keys,
            "foreign_keys": foreign_keys,
            "join_paths": join_paths,
            "fact_tables": fact_tables,
            "dimension_tables": dimension_tables,
            "schema_type": schema_type,
            "detected_at": datetime.now(timezone.utc).isoformat(),
        }

        await self.db.metadata_relationships.update_one(
            {"datasource_id": datasource_id},
            {"$set": {**result, "user_id": user_id}},
            upsert=True,
        )
        logger.info("Detected %d FKs, %d join paths for datasource %s", len(foreign_keys), len(join_paths), datasource_id)
        return result

    @staticmethod
    def _pk_of(table: dict):
        for c in table.get("columns", []):
            if c.get("is_primary"):
                return c["name"]
        return None

    async def get(self, datasource_id: str, user_id: str):
        return await self.db.metadata_relationships.find_one(
            {"datasource_id": datasource_id, "user_id": user_id}, {"_id": 0}
        )
