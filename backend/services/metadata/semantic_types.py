"""Semantic type and business category detection for columns."""

import re

VALUE_PATTERNS = [
    ("email", re.compile(r"^[\w.+-]+@[\w-]+\.[\w.]+$")),
    ("uuid", re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)),
    ("percentage", re.compile(r"^-?\d+(\.\d+)?\s?%$")),
    ("currency", re.compile(r"^[$€£₹]\s?-?[\d,]+(\.\d+)?$")),
    ("zip", re.compile(r"^\d{5}(-\d{4})?$")),
    ("phone", re.compile(r"^\+?[\d\s()./-]{7,17}$")),
    ("date", re.compile(r"^\d{4}-\d{2}-\d{2}")),
    ("time", re.compile(r"^\d{2}:\d{2}(:\d{2})?$")),
]

NAME_RULES = [
    (("email", "e_mail"), "email"),
    (("phone", "mobile", "telephone"), "phone"),
    (("uuid", "guid"), "uuid"),
    (("zip", "postal", "pincode", "pin_code"), "zip"),
    (("country",), "country"),
    (("state", "province"), "state"),
    (("city", "town"), "city"),
    (("percent", "pct", "_rate", "ratio"), "percentage"),
    (("price", "amount", "cost", "revenue", "total", "subtotal", "fee", "spend", "salary"), "currency"),
    (("date", "created", "updated", "timestamp", "_at", "_on", "birthday", "dob"), "date"),
    (("time",), "time"),
    (("is_", "has_", "flag", "active", "enabled", "deleted", "verified"), "boolean"),
]

BUSINESS_CATEGORIES = {
    "revenue": ["revenue", "turnover", "income", "gmv", "sales_amount", "earnings"],
    "sales": ["sales", "sold", "deal"],
    "margin": ["margin", "profit", "gross_profit", "net_profit"],
    "tax": ["tax", "vat", "gst"],
    "discount": ["discount", "coupon", "promo", "rebate"],
    "inventory": ["inventory", "stock", "quantity", "qty", "on_hand"],
    "payments": ["payment", "paid", "transaction", "refund", "charge"],
    "orders": ["order", "purchase", "checkout", "cart", "fulfillment"],
    "invoices": ["invoice", "billing", "bill"],
    "customer": ["customer", "client", "buyer", "subscriber", "account_name"],
    "product": ["product", "item", "sku", "variant", "catalog"],
    "marketing": ["campaign", "ad_", "spend", "impression", "click", "roas", "cac", "ctr", "conversion"],
    "geographic": ["country", "state", "city", "zip", "postal", "region", "location", "address"],
}

DTYPE_MAP = [
    (("bool",), "boolean"),
    (("timestamp", "datetime"), "date"),
    (("date",), "date"),
    (("time",), "time"),
    (("int", "bigint", "smallint", "float", "double", "numeric", "decimal", "real", "money"), "numeric"),
]


def detect_semantic_type(name: str, data_type: str = "", samples: list = None) -> dict:
    """Detect semantic type + business category from column name, dtype, and sample values."""
    n = str(name).lower()
    dt = str(data_type).lower()
    semantic = None
    is_identifier = False

    if n == "id" or n.endswith("_id") or n.endswith("_key") or n == "pk":
        semantic = "identifier"
        is_identifier = True

    if not semantic:
        for keywords, stype in NAME_RULES:
            if any(k in n for k in keywords):
                semantic = stype
                break

    if not semantic and samples:
        str_samples = [str(s).strip() for s in samples if s is not None and str(s).strip()][:20]
        if str_samples:
            for stype, pattern in VALUE_PATTERNS:
                matches = sum(1 for s in str_samples if pattern.match(s))
                if matches / len(str_samples) >= 0.8:
                    semantic = stype
                    break

    if not semantic:
        for keywords, stype in DTYPE_MAP:
            if any(k in dt for k in keywords):
                semantic = stype
                break

    if not semantic:
        semantic = "text" if ("char" in dt or "text" in dt or "object" in dt or "str" in dt or not dt) else "unknown"

    business_category = None
    for category, keywords in BUSINESS_CATEGORIES.items():
        if any(k in n for k in keywords):
            business_category = category
            break

    return {"semantic_type": semantic, "business_category": business_category, "is_identifier": is_identifier}


def compute_quality_score(row_count: int, column_profiles: list, duplicate_rows: int = 0) -> dict:
    """Compute a 0-100 data quality score from column profiles."""
    if not column_profiles:
        return {"score": 0, "issues": ["No columns profiled"]}
    issues = []
    penalty = 0.0

    null_pcts = []
    error_cols = 0
    for cp in column_profiles:
        if cp.get("error"):
            error_cols += 1
            continue
        nulls = cp.get("null_count", 0) or 0
        if row_count > 0:
            null_pcts.append(nulls / row_count * 100)

    avg_null_pct = sum(null_pcts) / len(null_pcts) if null_pcts else 0
    if avg_null_pct > 0:
        penalty += min(avg_null_pct * 0.6, 40)
        if avg_null_pct > 20:
            issues.append(f"High missing values ({avg_null_pct:.1f}% average)")

    if error_cols:
        penalty += min(error_cols * 5, 20)
        issues.append(f"{error_cols} columns could not be profiled")

    if row_count > 0 and duplicate_rows > 0:
        dup_pct = duplicate_rows / row_count * 100
        penalty += min(dup_pct * 0.5, 20)
        if dup_pct > 5:
            issues.append(f"{dup_pct:.1f}% duplicate rows")

    if row_count == 0:
        penalty = 100
        issues.append("Table is empty")

    return {"score": max(0, round(100 - penalty, 1)), "issues": issues, "avg_null_pct": round(avg_null_pct, 2)}
