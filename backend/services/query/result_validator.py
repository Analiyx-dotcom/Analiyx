"""Post-execution result validation with confidence scoring."""

from typing import Dict, Any


class ResultValidator:
    @staticmethod
    def validate(result: Dict[str, Any], question: str = "") -> Dict[str, Any]:
        checks = []
        warnings = []
        confidence = 1.0

        if not result.get("success", True) or result.get("error"):
            return {
                "confidence": 0.0,
                "checks": [{"check": "execution", "passed": False, "detail": result.get("error", "Execution failed")}],
                "warnings": [],
                "needs_clarification": True,
                "clarification": "The query failed to execute. Please rephrase your question or check the datasource.",
            }
        checks.append({"check": "execution", "passed": True})

        columns = result.get("columns", []) or []
        rows = result.get("rows", []) or []
        row_count = result.get("row_count", len(rows))

        if row_count == 0:
            confidence -= 0.4
            warnings.append("Query returned no rows — data may not exist for this question, or filters may be too strict.")
            checks.append({"check": "non_empty_result", "passed": False})
        else:
            checks.append({"check": "non_empty_result", "passed": True})

        if not columns:
            confidence -= 0.3
            checks.append({"check": "columns_returned", "passed": False})
        else:
            checks.append({"check": "columns_returned", "passed": True})

        if rows and columns:
            null_heavy = []
            sample = rows[:200]
            for col in columns:
                nulls = sum(1 for r in sample if r.get(col) is None or r.get(col) == "")
                if nulls / len(sample) > 0.7:
                    null_heavy.append(col)
            if null_heavy:
                confidence -= min(0.1 * len(null_heavy), 0.25)
                warnings.append(f"Columns mostly empty: {', '.join(null_heavy[:5])}")
                checks.append({"check": "null_anomalies", "passed": False, "detail": null_heavy})
            else:
                checks.append({"check": "null_anomalies", "passed": True})

            agg_words = ("total", "sum", "count", "average", "avg", "how many", "how much")
            if question and any(w in question.lower() for w in agg_words):
                if row_count == 1 and len(columns) <= 3:
                    checks.append({"check": "aggregation_shape", "passed": True})
                elif row_count > 100:
                    confidence -= 0.1
                    warnings.append("Question looks like an aggregation but the result has many rows — verify grouping.")
                    checks.append({"check": "aggregation_shape", "passed": False})
                else:
                    checks.append({"check": "aggregation_shape", "passed": True})

        confidence = max(0.0, round(confidence, 2))
        needs_clarification = confidence < 0.5
        return {
            "confidence": confidence,
            "checks": checks,
            "warnings": warnings,
            "needs_clarification": needs_clarification,
            "clarification": (
                "I'm not fully confident in this result. Could you clarify the metric, time range, or table you mean?"
                if needs_clarification else None
            ),
        }
