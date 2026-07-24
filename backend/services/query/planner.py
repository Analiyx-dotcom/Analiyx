import os
import logging
from typing import Dict, Any
from emergentintegrations.llm.chat import LlmChat, UserMessage
from services.metadata.embeddings import EmbeddingService

logger = logging.getLogger(__name__)

EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY", "")


class QueryPlanner:
    """Converts natural language questions into SQL queries using semantic metadata context."""

    def __init__(self, db):
        self.db = db
        self.embedding_service = EmbeddingService(db)

    async def plan_query(self, datasource_id: str, user_id: str, question: str) -> Dict[str, Any]:
        relevant_tables = await self.embedding_service.search_tables(datasource_id, user_id, question, limit=5)

        ds = await self.db.external_datasources.find_one({"_id": datasource_id, "user_id": user_id})
        if not ds:
            raise ValueError("Datasource not found")
        db_type = ds["db_type"]

        context = self._build_context(relevant_tables, db_type)

        glossary_terms = await self._get_relevant_glossary(user_id, question)
        if glossary_terms:
            context += "\n\nBusiness Glossary:\n"
            for gt in glossary_terms:
                context += f"- {gt['term']}: {gt['definition']}\n"

        sql, explanation = await self._generate_sql(question, context, db_type)

        return {
            "question": question,
            "sql": sql,
            "explanation": explanation,
            "relevant_tables": [
                {"schema": t.get("schema"), "table": t.get("table"), "description": t.get("description", "")}
                for t in relevant_tables
            ],
            "db_type": db_type,
            "datasource_id": datasource_id,
        }

    def _build_context(self, tables: list, db_type: str) -> str:
        lines = [f"Database type: {db_type}\n\nAvailable tables:"]
        for t in tables:
            cols = t.get("columns", [])
            col_types = t.get("column_types", {})
            col_strs = []
            for c in cols:
                dtype = col_types.get(c, "unknown")
                col_strs.append(f"{c} ({dtype})")
            lines.append(f"\n{t.get('schema', 'public')}.{t.get('table', '')}:")
            lines.append(f"  Description: {t.get('description', 'N/A')}")
            lines.append(f"  Columns: {', '.join(col_strs)}")
        return "\n".join(lines)

    async def _get_relevant_glossary(self, user_id: str, question: str):
        words = question.lower().split()
        results = []
        cursor = self.db.business_glossary.find({"user_id": user_id})
        async for term in cursor:
            term_lower = term.get("term", "").lower()
            if any(w in term_lower or term_lower in w for w in words):
                results.append(term)
        return results[:5]

    async def _generate_sql(self, question: str, context: str, db_type: str):
        try:
            dialect = "PostgreSQL" if db_type == "postgresql" else "MySQL"
            chat = LlmChat(
                api_key=EMERGENT_KEY,
                session_id="query-planner",
                system_message=(
                    f"You are an expert {dialect} SQL query writer. Given database schema context and a natural language question, "
                    f"generate a valid {dialect} SQL query.\n\n"
                    "Rules:\n"
                    "1. Only use tables and columns from the provided schema context\n"
                    "2. Write read-only SELECT queries only\n"
                    "3. Use proper quoting for identifiers\n"
                    "4. Add LIMIT 1000 if no limit specified\n"
                    "5. Respond with ONLY the SQL query on the first line, then '---' separator, then a brief explanation\n"
                    "6. Do not wrap SQL in code blocks or backticks"
                ),
            )
            chat.with_model("openai", "gpt-5.2")

            prompt = f"Schema context:\n{context}\n\nQuestion: {question}"
            response = await chat.send_message(UserMessage(text=prompt))
            text = response.text.strip()

            if "---" in text:
                parts = text.split("---", 1)
                sql = parts[0].strip()
                explanation = parts[1].strip()
            else:
                lines = text.split("\n")
                sql_lines = []
                explanation_lines = []
                in_explanation = False
                for line in lines:
                    if line.lower().startswith("explanation") or line.lower().startswith("this query"):
                        in_explanation = True
                    if in_explanation:
                        explanation_lines.append(line)
                    else:
                        sql_lines.append(line)
                sql = "\n".join(sql_lines).strip()
                explanation = "\n".join(explanation_lines).strip() or "Query generated from your question."

            sql = sql.strip("`").strip()
            if sql.startswith("sql\n"):
                sql = sql[4:]

            return sql, explanation
        except Exception as e:
            logger.error("SQL generation failed: %s", e)
            raise ValueError(f"Failed to generate SQL: {e}")
