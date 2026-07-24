"""AI insight generation: executive summary, KPIs, trends, anomalies, recommendations."""

import os
import json
import logging
from typing import Dict, Any, List
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)

EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY", "")


class SummaryGenerator:
    @staticmethod
    async def generate(question: str, sql: str, columns: List[str], rows: List[dict]) -> Dict[str, Any]:
        sample = rows[:30]
        try:
            chat = LlmChat(
                api_key=EMERGENT_KEY,
                session_id="insight-gen",
                system_message=(
                    "You are a senior business analyst. Given a question, the SQL used, and result data, "
                    "generate business insights. Respond with ONLY valid JSON (no code fences) in this exact shape:\n"
                    '{"executive_summary": "2-3 sentence summary", '
                    '"kpis": [{"label": "...", "value": "..."}], '
                    '"trends": ["..."], "anomalies": ["..."], '
                    '"recommendations": ["..."], "key_takeaways": ["..."]}\n'
                    "Keep arrays to max 4 items each. Base everything strictly on the data provided — never invent numbers."
                ),
            )
            chat.with_model("openai", "gpt-5.2")
            prompt = (
                f"Question: {question}\nSQL: {sql}\nColumns: {columns}\n"
                f"Result sample ({len(sample)} of {len(rows)} rows):\n{json.dumps(sample, default=str)[:6000]}"
            )
            resp = await chat.send_message(UserMessage(text=prompt))
            text = str(resp).strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            insights = json.loads(text.strip())
            insights["generated"] = True
            return insights
        except Exception as e:
            logger.warning("Insight generation failed: %s", e)
            return {
                "generated": False,
                "executive_summary": f"Query returned {len(rows)} rows across {len(columns)} columns.",
                "kpis": [], "trends": [], "anomalies": [], "recommendations": [], "key_takeaways": [],
            }
