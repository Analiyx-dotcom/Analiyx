import os
import logging
from typing import Dict, Any, List
from emergentintegrations.llm.chat import LlmChat, UserMessage
from services.metadata.embeddings import EmbeddingService

logger = logging.getLogger(__name__)

EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY", "")


class SemanticSearch:
    """Semantic search over metadata using AI-powered understanding."""

    def __init__(self, db):
        self.db = db
        self.embedding_service = EmbeddingService(db)

    async def search(self, datasource_id: str, user_id: str, query: str, limit: int = 10) -> Dict[str, Any]:
        table_results = await self.embedding_service.search_tables(datasource_id, user_id, query, limit)

        glossary_results = await self._search_glossary(user_id, query)

        ai_interpretation = await self._interpret_query(query, table_results, glossary_results)

        return {
            "query": query,
            "tables": table_results,
            "glossary_matches": glossary_results,
            "ai_interpretation": ai_interpretation,
            "total_results": len(table_results),
        }

    async def _search_glossary(self, user_id: str, query: str) -> List[Dict[str, Any]]:
        query_words = query.lower().split()
        results = []
        cursor = self.db.business_glossary.find({"user_id": user_id}, {"_id": 0})
        async for term in cursor:
            term_text = f"{term.get('term', '')} {term.get('definition', '')} {term.get('synonyms', '')}".lower()
            score = sum(1 for w in query_words if w in term_text)
            if score > 0:
                term["relevance_score"] = score
                results.append(term)
        results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        return results[:5]

    async def _interpret_query(self, query: str, tables: list, glossary: list) -> str:
        if not tables:
            return "No matching tables found. Try scanning your datasource or refining your search."
        try:
            context_parts = []
            for t in tables[:5]:
                cols = ", ".join(t.get("columns", [])[:10])
                context_parts.append(f"- {t.get('schema', '')}.{t.get('table', '')}: {t.get('description', '')} (columns: {cols})")
            context = "\n".join(context_parts)

            chat = LlmChat(
                api_key=EMERGENT_KEY,
                session_id=f"search-interpret",
                system_message="You are a data analyst. Given a user's search query and matching database tables, briefly explain which tables are most relevant and why. Keep it to 2-3 sentences.",
            )
            chat.with_model("openai", "gpt-5.2")
            resp = await chat.send_message(UserMessage(text=f"Query: {query}\n\nMatching tables:\n{context}"))
            return resp.text.strip()
        except Exception as e:
            logger.warning("AI interpretation failed: %s", e)
            return f"Found {len(tables)} matching tables for your query."
