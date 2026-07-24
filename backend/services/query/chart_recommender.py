"""Rule-based chart recommendation from query result shape and column types."""

import re
from typing import Dict, Any, List

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")


class ChartRecommender:
    @staticmethod
    def _column_kind(values: list) -> str:
        vals = [v for v in values if v is not None and v != ""][:50]
        if not vals:
            return "empty"
        if all(isinstance(v, bool) for v in vals):
            return "categorical"
        if all(isinstance(v, (int, float)) for v in vals):
            return "numeric"
        str_vals = [str(v) for v in vals]
        if sum(1 for s in str_vals if DATE_RE.match(s)) / len(str_vals) >= 0.8:
            return "temporal"
        numeric_like = sum(1 for s in str_vals if re.match(r"^-?[\d,]+(\.\d+)?$", s))
        if numeric_like / len(str_vals) >= 0.9:
            return "numeric"
        return "categorical"

    @classmethod
    def recommend(cls, columns: List[str], rows: List[dict]) -> Dict[str, Any]:
        if not columns or not rows:
            return {"recommended_chart": "table", "alternatives": [], "reason": "No data to visualize.",
                    "x_axis": None, "y_axis": None}

        kinds = {c: cls._column_kind([r.get(c) for r in rows]) for c in columns}
        temporal = [c for c, k in kinds.items() if k == "temporal"]
        numeric = [c for c, k in kinds.items() if k == "numeric"]
        categorical = [c for c, k in kinds.items() if k == "categorical"]

        if len(rows) == 1 and len(numeric) >= 1 and not temporal and not categorical:
            return {"recommended_chart": "kpi", "alternatives": ["table"],
                    "reason": "Single aggregated value — best shown as a KPI card.",
                    "x_axis": None, "y_axis": numeric[0], "column_kinds": kinds}

        if temporal and numeric:
            return {"recommended_chart": "line", "alternatives": ["area", "bar"],
                    "reason": "Time series data — line chart shows trends over time.",
                    "x_axis": temporal[0], "y_axis": numeric[0],
                    "series": numeric[:5], "column_kinds": kinds}

        if categorical and numeric:
            cardinality = len({str(r.get(categorical[0])) for r in rows})
            if len(categorical) >= 2 and numeric:
                return {"recommended_chart": "heatmap", "alternatives": ["bar", "table"],
                        "reason": "Two categorical dimensions with a measure — heatmap shows the matrix.",
                        "x_axis": categorical[0], "y_axis": categorical[1], "value": numeric[0], "column_kinds": kinds}
            if cardinality <= 6:
                return {"recommended_chart": "pie", "alternatives": ["bar", "treemap"],
                        "reason": f"Few categories ({cardinality}) — pie chart shows composition.",
                        "x_axis": categorical[0], "y_axis": numeric[0], "column_kinds": kinds}
            if cardinality <= 50:
                return {"recommended_chart": "bar", "alternatives": ["treemap", "table"],
                        "reason": f"{cardinality} categories with a measure — bar chart compares values.",
                        "x_axis": categorical[0], "y_axis": numeric[0], "column_kinds": kinds}
            return {"recommended_chart": "table", "alternatives": ["bar"],
                    "reason": "Too many categories for a chart — table is clearest.",
                    "x_axis": categorical[0], "y_axis": numeric[0], "column_kinds": kinds}

        if len(numeric) >= 2:
            return {"recommended_chart": "scatter", "alternatives": ["line", "table"],
                    "reason": "Two numeric measures — scatter plot reveals correlation.",
                    "x_axis": numeric[0], "y_axis": numeric[1], "column_kinds": kinds}

        if temporal and not numeric:
            return {"recommended_chart": "bar", "alternatives": ["table"],
                    "reason": "Temporal data without measures — bar chart of counts.",
                    "x_axis": temporal[0], "y_axis": None, "column_kinds": kinds}

        return {"recommended_chart": "table", "alternatives": [],
                "reason": "Data shape does not map to a standard chart — showing table.",
                "x_axis": columns[0] if columns else None, "y_axis": None, "column_kinds": kinds}
