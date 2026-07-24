import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class BusinessGlossary:
    """Manages business glossary terms mapped to technical metadata."""

    def __init__(self, db):
        self.db = db

    async def add_term(self, user_id: str, term: str, definition: str,
                       synonyms: str = "", related_tables: Optional[List[str]] = None,
                       related_columns: Optional[List[str]] = None) -> Dict[str, Any]:
        term_id = str(uuid.uuid4())
        doc = {
            "_id": term_id,
            "user_id": user_id,
            "term": term,
            "definition": definition,
            "synonyms": synonyms,
            "related_tables": related_tables or [],
            "related_columns": related_columns or [],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        await self.db.business_glossary.insert_one(doc)
        doc.pop("_id")
        doc["id"] = term_id
        return doc

    async def update_term(self, term_id: str, user_id: str, updates: dict) -> Dict[str, Any]:
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        allowed = {"term", "definition", "synonyms", "related_tables", "related_columns", "updated_at"}
        safe_updates = {k: v for k, v in updates.items() if k in allowed}
        result = await self.db.business_glossary.update_one(
            {"_id": term_id, "user_id": user_id}, {"$set": safe_updates}
        )
        if result.matched_count == 0:
            raise ValueError("Term not found")
        doc = await self.db.business_glossary.find_one({"_id": term_id})
        doc["id"] = doc.pop("_id")
        return doc

    async def delete_term(self, term_id: str, user_id: str) -> bool:
        result = await self.db.business_glossary.delete_one({"_id": term_id, "user_id": user_id})
        return result.deleted_count > 0

    async def list_terms(self, user_id: str, search: str = "") -> List[Dict[str, Any]]:
        query = {"user_id": user_id}
        if search:
            query["$or"] = [
                {"term": {"$regex": search, "$options": "i"}},
                {"definition": {"$regex": search, "$options": "i"}},
                {"synonyms": {"$regex": search, "$options": "i"}},
            ]
        cursor = self.db.business_glossary.find(query).sort("term", 1)
        results = []
        async for doc in cursor:
            doc["id"] = doc.pop("_id")
            results.append(doc)
        return results

    async def get_term(self, term_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        doc = await self.db.business_glossary.find_one({"_id": term_id, "user_id": user_id})
        if doc:
            doc["id"] = doc.pop("_id")
        return doc
