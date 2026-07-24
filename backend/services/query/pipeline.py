"""End-to-end analytics pipeline: question → plan → validate → execute → validate results → insights → chart."""

import logging
from typing import Dict, Any
from services.query.planner import QueryPlanner
from services.query.validator import SQLValidator
from services.query.executor import QueryExecutor
from services.query.result_validator import ResultValidator
from services.query.chart_recommender import ChartRecommender
from services.query.summary_generator import SummaryGenerator
from services.metadata.scanner import MetadataScanner

logger = logging.getLogger(__name__)


class AnalyticsPipeline:
    def __init__(self, db):
        self.db = db
        self.planner = QueryPlanner(db)
        self.executor = QueryExecutor(db)
        self.scanner = MetadataScanner(db)

    async def ask(self, datasource_id: str, user_id: str, question: str,
                  mode: str = "hybrid", include_insights: bool = True) -> Dict[str, Any]:
        plan = await self.planner.plan_query(datasource_id, user_id, question)
        sql = plan["sql"]
        db_type = plan["db_type"]

        tables_meta = await self.scanner.get_tables_flat(datasource_id, user_id)
        validation = SQLValidator.validate(sql, db_type)
        meta_validation = SQLValidator.validate_against_metadata(sql, tables_meta)
        repaired = False

        if not validation["valid"] or not meta_validation["valid"]:
            all_issues = validation["issues"] + meta_validation["issues"]
            try:
                sql = await self.planner.repair_sql(question, sql, all_issues, db_type, tables_meta)
                repaired = True
                validation = SQLValidator.validate(sql, db_type)
                meta_validation = SQLValidator.validate_against_metadata(sql, tables_meta)
            except Exception as e:
                logger.warning("SQL auto-repair failed: %s", e)

        if not validation["valid"] or not meta_validation["valid"]:
            return {
                "success": False,
                "question": question,
                "sql": sql,
                "explanation": plan.get("explanation", ""),
                "validation": {**validation, "metadata_issues": meta_validation["issues"]},
                "repaired": repaired,
                "error": "Generated SQL failed validation",
            }

        execution = await self.executor.execute(datasource_id, user_id, validation["sql"], mode=mode)

        result_validation = ResultValidator.validate(execution, question)

        chart = None
        insights = None
        if execution.get("success") and execution.get("rows"):
            chart = ChartRecommender.recommend(execution.get("columns", []), execution.get("rows", []))
            if include_insights:
                insights = await SummaryGenerator.generate(
                    question, validation["sql"], execution.get("columns", []), execution.get("rows", [])
                )

        return {
            "success": execution.get("success", False),
            "question": question,
            "sql": validation["sql"],
            "explanation": plan.get("explanation", ""),
            "relevant_tables": plan.get("relevant_tables", []),
            "validation": {
                "valid": True,
                "warnings": validation.get("warnings", []) + meta_validation.get("warnings", []),
            },
            "repaired": repaired,
            "execution": {
                "columns": execution.get("columns", []),
                "rows": execution.get("rows", []),
                "row_count": execution.get("row_count", 0),
                "execution_time_ms": execution.get("execution_time_ms", 0),
                "source": execution.get("source", "live"),
                "error": execution.get("error"),
            },
            "result_validation": result_validation,
            "chart": chart,
            "insights": insights,
            "mode": mode,
        }
