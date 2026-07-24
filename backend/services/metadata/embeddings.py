import os
import logging
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)

EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY", "")


class EmbeddingService:
    """Generates semantic descriptions for metadata using GPT-5.2 and stores them for search."""

    def __init__(self, db):
        self.db = db

    def _build_table_text(self, schema: str, table_info: dict) -> str:
        cols = table_info.get("columns", [])
        col_lines = []
        for c in cols:
            pk = " [PK]" if c.get("is_primary") else ""
            null = " NULL" if c.get("nullable") else " NOT NULL"
            col_lines.append(f"  - {c['name']} ({c['data_type']}{pk}{null})")
        return f"Table: {schema}.{table_info['name']}\nType: {table_info.get('type', 'table')}\nColumns:\n" + "\n".join(col_lines)

    async def generate_descriptions(self, datasource_id: str, user_id: str) -> int:
        meta = await self.db.metadata_schemas.find_one({"datasource_id": datasource_id, "user_id": user_id})
        if not meta:
            raise ValueError("No metadata. Run a scan first.")

        count = 0
        for schema in meta.get("metadata", {}).get("schemas", []):
            for tbl in schema.get("tables", []):
                table_text = self._build_table_text(schema["name"], tbl)
                description = await self._generate_description(table_text)
                search_text = f"{schema['name']}.{tbl['name']} {description} " + " ".join(
                    c["name"] for c in tbl.get("columns", [])
                )
                text_hash = hashlib.md5(search_text.encode()).hexdigest()

                await self.db.metadata_embeddings.update_one(
                    {"datasource_id": datasource_id, "schema": schema["name"], "table": tbl["name"]},
                    {
                        "$set": {
                            "datasource_id": datasource_id,
                            "user_id": user_id,
                            "schema": schema["name"],
                            "table": tbl["name"],
                            "description": description,
                            "search_text": search_text.lower(),
                            "text_hash": text_hash,
                            "columns": [c["name"] for c in tbl.get("columns", [])],
                            "column_types": {c["name"]: c["data_type"] for c in tbl.get("columns", [])},
                            "updated_at": datetime.now(timezone.utc).isoformat(),
                        }
                    },
                    upsert=True,
                )
                count += 1
        logger.info("Generated descriptions for %d tables in datasource %s", count, datasource_id)
        return count

    async def _generate_description(self, table_text: str) -> str:
        try:
            chat = LlmChat(
                api_key=EMERGENT_KEY,
                session_id=f"embed-{hashlib.md5(table_text.encode()).hexdigest()[:8]}",
                system_message=(
                    "You are a data analyst. Given a database table schema, write a concise 1-2 sentence "
                    "business description of what this table stores and its likely purpose. "
                    "Focus on business meaning, not technical details."
                ),
            )
            chat.with_model("openai", "gpt-5.2")
            response = await chat.send_message(UserMessage(text=table_text))
            return str(response).strip()
        except Exception as e:
            logger.warning("Failed to generate description: %s", e)
            return ""

    async def search_tables(self, datasource_id: str, user_id: str, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Text-based semantic search over metadata descriptions."""
        query_lower = query.lower()
        query_words = query_lower.split()

        await self.db.metadata_embeddings.create_index([("search_text", "text")])

        results = await self.db.metadata_embeddings.find(
            {
                "datasource_id": datasource_id,
                "user_id": user_id,
                "$text": {"$search": query},
            },
            {"score": {"$meta": "textScore"}, "_id": 0},
        ).sort([("score", {"$meta": "textScore"})]).limit(limit).to_list(limit)

        if not results:
            all_tables = await self.db.metadata_embeddings.find(
                {"datasource_id": datasource_id, "user_id": user_id}, {"_id": 0}
            ).to_list(500)
            scored = []
            for t in all_tables:
                text = t.get("search_text", "")
                score = sum(1 for w in query_words if w in text)
                if score > 0:
                    t["score"] = score
                    scored.append(t)
            scored.sort(key=lambda x: x["score"], reverse=True)
            results = scored[:limit]

        return results
