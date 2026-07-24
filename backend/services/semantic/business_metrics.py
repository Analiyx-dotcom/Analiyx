"""Standard business metric definitions, column mapping, and auto-glossary seeding."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

STANDARD_METRICS = {
    "Revenue": {"definition": "Total income generated from sales of goods or services.",
                "synonyms": ["revenue", "sales_amount", "income", "turnover", "gmv", "total_amount", "amount", "earnings"]},
    "Sales": {"definition": "Number or value of completed sales transactions.",
              "synonyms": ["sales", "sold", "deals", "transactions"]},
    "Orders": {"definition": "Count of customer orders placed.",
               "synonyms": ["orders", "order_count", "purchases", "checkouts"]},
    "Customers": {"definition": "Unique individuals or businesses that purchase products or services.",
                  "synonyms": ["customer", "customers", "client", "buyer", "subscriber"]},
    "Profit": {"definition": "Revenue minus costs and expenses.",
               "synonyms": ["profit", "net_profit", "gross_profit", "net_income"]},
    "Margin": {"definition": "Profit expressed as a percentage of revenue.",
               "synonyms": ["margin", "gross_margin", "profit_margin"]},
    "MRR": {"definition": "Monthly Recurring Revenue — predictable subscription revenue per month.",
            "synonyms": ["mrr", "monthly_recurring_revenue", "recurring_revenue"]},
    "ARR": {"definition": "Annual Recurring Revenue — MRR annualized (MRR x 12).",
            "synonyms": ["arr", "annual_recurring_revenue"]},
    "Inventory": {"definition": "Quantity of goods available for sale.",
                  "synonyms": ["inventory", "stock", "quantity_on_hand", "stock_level", "qty"]},
    "Products": {"definition": "Items or services offered for sale.",
                 "synonyms": ["product", "products", "item", "sku", "variant", "catalog"]},
    "Marketing Spend": {"definition": "Total amount spent on marketing and advertising.",
                        "synonyms": ["spend", "ad_spend", "marketing_spend", "budget", "cost"]},
    "ROAS": {"definition": "Return On Ad Spend — revenue generated per unit of ad spend.",
             "synonyms": ["roas", "return_on_ad_spend"]},
    "CAC": {"definition": "Customer Acquisition Cost — total acquisition spend divided by new customers.",
            "synonyms": ["cac", "acquisition_cost", "customer_acquisition_cost"]},
    "LTV": {"definition": "Customer Lifetime Value — total revenue expected from a customer over their lifetime.",
            "synonyms": ["ltv", "clv", "lifetime_value", "customer_lifetime_value"]},
    "Conversion Rate": {"definition": "Percentage of visitors or leads that complete a desired action.",
                        "synonyms": ["conversion_rate", "cvr", "conversions"]},
    "Sessions": {"definition": "Number of visits to a website or app within a time period.",
                 "synonyms": ["sessions", "visits", "traffic"]},
    "Bounce Rate": {"definition": "Percentage of sessions where the visitor left without interaction.",
                    "synonyms": ["bounce_rate", "bounces"]},
    "Average Order Value": {"definition": "Average revenue per order (revenue / orders).",
                            "synonyms": ["aov", "average_order_value", "avg_order_value"]},
}


def match_business_terms(column_names: List[str]) -> Dict[str, List[str]]:
    """Map business metric names to matching column names."""
    matches: Dict[str, List[str]] = {}
    for col in column_names:
        col_l = str(col).lower()
        for metric, spec in STANDARD_METRICS.items():
            if any(syn == col_l or syn in col_l for syn in spec["synonyms"]):
                matches.setdefault(metric, []).append(str(col))
                break
    return matches


class BusinessMetricsService:
    def __init__(self, db):
        self.db = db

    async def infer_metrics(self, datasource_id: str, user_id: str) -> Dict[str, Any]:
        """Infer business metrics from scanned metadata and auto-seed the glossary."""
        meta = await self.db.metadata_schemas.find_one({"datasource_id": datasource_id, "user_id": user_id})
        if not meta:
            raise ValueError("No metadata found. Run a scan first.")

        inferred = []
        for schema in meta.get("metadata", {}).get("schemas", []):
            for tbl in schema.get("tables", []):
                col_names = [c["name"] for c in tbl.get("columns", [])]
                matches = match_business_terms(col_names)
                for metric, cols in matches.items():
                    inferred.append({
                        "metric": metric,
                        "definition": STANDARD_METRICS[metric]["definition"],
                        "schema": schema["name"],
                        "table": tbl["name"],
                        "columns": cols,
                    })

        result = {
            "datasource_id": datasource_id,
            "metrics": inferred,
            "count": len(inferred),
            "inferred_at": datetime.now(timezone.utc).isoformat(),
        }
        await self.db.business_metrics.update_one(
            {"datasource_id": datasource_id},
            {"$set": {**result, "user_id": user_id}},
            upsert=True,
        )

        seeded = await self.seed_glossary(user_id, inferred)
        result["glossary_terms_seeded"] = seeded
        return result

    async def seed_glossary(self, user_id: str, inferred: List[dict]) -> int:
        """Upsert glossary terms for inferred metrics (idempotent, never duplicates)."""
        seeded = 0
        by_metric: Dict[str, dict] = {}
        for item in inferred:
            m = by_metric.setdefault(item["metric"], {"tables": set(), "columns": set()})
            m["tables"].add(f"{item.get('schema', '')}.{item.get('table', '')}".strip("."))
            m["columns"].update(item.get("columns", []))

        for metric, info in by_metric.items():
            spec = STANDARD_METRICS[metric]
            existing = await self.db.business_glossary.find_one({"user_id": user_id, "term": metric})
            if existing:
                await self.db.business_glossary.update_one(
                    {"_id": existing["_id"]},
                    {"$addToSet": {
                        "related_tables": {"$each": sorted(info["tables"])},
                        "related_columns": {"$each": sorted(info["columns"])},
                    }, "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}},
                )
            else:
                await self.db.business_glossary.insert_one({
                    "_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "term": metric,
                    "definition": spec["definition"],
                    "synonyms": ", ".join(spec["synonyms"]),
                    "related_tables": sorted(info["tables"]),
                    "related_columns": sorted(info["columns"]),
                    "auto_generated": True,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                })
                seeded += 1
        return seeded

    async def get_metrics(self, datasource_id: str, user_id: str):
        return await self.db.business_metrics.find_one(
            {"datasource_id": datasource_id, "user_id": user_id}, {"_id": 0}
        )
