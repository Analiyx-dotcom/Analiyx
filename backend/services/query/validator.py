import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

FORBIDDEN_KEYWORDS = [
    "DROP", "DELETE", "TRUNCATE", "ALTER", "CREATE", "INSERT",
    "UPDATE", "GRANT", "REVOKE", "EXEC", "EXECUTE", "MERGE",
    "CALL", "REPLACE INTO",
]


class SQLValidator:
    """Validates SQL queries for safety before execution."""

    @staticmethod
    def validate(sql: str, db_type: str = "postgresql") -> Dict[str, Any]:
        issues = []
        warnings = []
        sql_upper = sql.upper().strip()

        if not sql_upper.startswith("SELECT") and not sql_upper.startswith("WITH"):
            issues.append("Only SELECT and WITH (CTE) queries are allowed")

        for kw in FORBIDDEN_KEYWORDS:
            pattern = r"\b" + kw + r"\b"
            if re.search(pattern, sql_upper):
                issues.append(f"Forbidden keyword detected: {kw}")

        if ";" in sql.rstrip("; \n"):
            mid_semicolons = sql.rstrip("; \n")
            if ";" in mid_semicolons:
                issues.append("Multiple statements detected (semicolon in query body)")

        if not re.search(r"\bLIMIT\b", sql_upper):
            warnings.append("No LIMIT clause — results may be large")

        if re.search(r"\bSELECT\s+\*\b", sql_upper):
            warnings.append("SELECT * may return many columns; consider specifying columns")

        if sql_upper.count("JOIN") > 4:
            warnings.append("Query has many JOINs — may be slow")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "sql": sql.rstrip("; \n"),
        }
