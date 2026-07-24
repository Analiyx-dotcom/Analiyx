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

        if re.search(r"\bCROSS\s+JOIN\b", sql_upper):
            issues.append("Cartesian join detected (CROSS JOIN)")
        if re.search(r"\bFROM\s+[\w.\"]+\s*,\s*[\w.\"]+", sql_upper):
            issues.append("Cartesian join risk: comma-separated tables in FROM — use explicit JOIN ... ON")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "sql": sql.rstrip("; \n"),
        }

    @staticmethod
    def validate_against_metadata(sql: str, tables: list) -> Dict[str, Any]:
        """Detect hallucinated tables/columns by checking SQL identifiers against scanned metadata."""
        issues = []
        warnings = []
        if not tables:
            return {"valid": True, "issues": [], "warnings": ["No metadata available to validate against"]}

        known_tables = {}
        known_columns = set()
        schemas = set()
        for t in tables:
            tname = t["table"].lower()
            schema = (t.get("schema") or "public").lower()
            schemas.add(schema)
            known_tables[tname] = t
            known_tables[f"{schema}.{tname}"] = t
            for c in t.get("columns", []):
                cname = c["name"] if isinstance(c, dict) else c
                known_columns.add(cname.lower())

        alias_to_table = {}
        for m in re.finditer(
            r"\b(?:FROM|JOIN)\s+\"?([\w.]+)\"?(?:\s+(?:AS\s+)?(?!ON\b|WHERE\b|JOIN\b|GROUP\b|ORDER\b|LEFT\b|RIGHT\b|INNER\b|OUTER\b|CROSS\b|ON\b|USING\b|LIMIT\b)([a-zA-Z_]\w*))?",
            sql, re.IGNORECASE,
        ):
            ref = m.group(1).lower()
            base = ref.split(".")[-1]
            if ref not in known_tables and base not in known_tables:
                issues.append(f"Unknown table referenced: {m.group(1)} (possible hallucination)")
            alias = m.group(2)
            if alias:
                alias_to_table[alias.lower()] = base

        for m in re.finditer(r"\b([a-zA-Z_]\w*)\.\"?([a-zA-Z_]\w*)\"?", sql):
            left, right = m.group(1).lower(), m.group(2).lower()
            if left in schemas or right in known_tables:
                continue
            if left in alias_to_table or left in known_tables:
                if right not in known_columns and right != "*":
                    issues.append(f"Unknown column referenced: {m.group(1)}.{m.group(2)} (possible hallucination)")

        return {"valid": len(issues) == 0, "issues": issues, "warnings": warnings}
