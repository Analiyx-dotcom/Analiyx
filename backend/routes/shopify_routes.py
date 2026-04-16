"""
Shopify Routes — Dashboard data for Shopify store analytics.
Currently returns SAMPLE data. Developer needs to replace with actual Shopify Admin API calls.
See API_CONTRACTS.md for the exact response schema.
"""
from fastapi import APIRouter, Depends
from auth import get_current_user_id
from datetime import datetime, timezone, timedelta
import random

router = APIRouter(prefix="/api/shopify", tags=["Shopify"])

db = None

def set_database(database):
    global db
    db = database


def _generate_sample_data():
    """Generate realistic sample Shopify store data. Replace with actual Shopify Admin API calls."""
    days = []
    for i in range(30, 0, -1):
        d = datetime.now(timezone.utc) - timedelta(days=i)
        orders = random.randint(15, 85)
        revenue = round(orders * random.uniform(1200, 3800), 2)
        visitors = random.randint(800, 3500)
        add_to_cart = int(visitors * random.uniform(0.06, 0.14))
        conversion_rate = round(orders / visitors * 100, 2) if visitors else 0
        days.append({
            "date": d.strftime("%b %d"),
            "orders": orders,
            "revenue": revenue,
            "visitors": visitors,
            "add_to_cart": add_to_cart,
            "conversion_rate": conversion_rate,
        })

    top_products = [
        {"name": "Premium Wireless Earbuds", "sku": "SKU-001", "sold": 342, "revenue": 854658, "inventory": 128, "status": "active"},
        {"name": "Organic Cotton T-Shirt", "sku": "SKU-012", "sold": 289, "revenue": 432211, "inventory": 56, "status": "active"},
        {"name": "Smart Fitness Band Pro", "sku": "SKU-045", "sold": 178, "revenue": 623456, "inventory": 0, "status": "out_of_stock"},
        {"name": "Bamboo Water Bottle 1L", "sku": "SKU-023", "sold": 456, "revenue": 318920, "inventory": 312, "status": "active"},
        {"name": "Laptop Backpack - Urban", "sku": "SKU-067", "sold": 134, "revenue": 401466, "inventory": 89, "status": "active"},
        {"name": "Handmade Scented Candle Set", "sku": "SKU-089", "sold": 267, "revenue": 186900, "inventory": 15, "status": "low_stock"},
    ]

    recent_orders = [
        {"order_id": "#AN-4521", "customer": "Priya M.", "items": 3, "total": 4580, "status": "fulfilled", "date": "2026-04-14"},
        {"order_id": "#AN-4520", "customer": "Rahul K.", "items": 1, "total": 2499, "status": "processing", "date": "2026-04-14"},
        {"order_id": "#AN-4519", "customer": "Sneha R.", "items": 2, "total": 3250, "status": "fulfilled", "date": "2026-04-13"},
        {"order_id": "#AN-4518", "customer": "Arjun D.", "items": 5, "total": 8920, "status": "shipped", "date": "2026-04-13"},
        {"order_id": "#AN-4517", "customer": "Meera S.", "items": 1, "total": 1299, "status": "refunded", "date": "2026-04-12"},
        {"order_id": "#AN-4516", "customer": "Karthik V.", "items": 2, "total": 5670, "status": "fulfilled", "date": "2026-04-12"},
    ]

    traffic_sources = [
        {"source": "Organic Search", "visitors": 4200, "percentage": 35},
        {"source": "Direct", "visitors": 2880, "percentage": 24},
        {"source": "Social Media", "visitors": 2160, "percentage": 18},
        {"source": "Paid Ads", "visitors": 1560, "percentage": 13},
        {"source": "Email", "visitors": 840, "percentage": 7},
        {"source": "Referral", "visitors": 360, "percentage": 3},
    ]

    total_orders = sum(d["orders"] for d in days)
    total_revenue = sum(d["revenue"] for d in days)
    total_visitors = sum(d["visitors"] for d in days)
    avg_order_value = round(total_revenue / total_orders, 2) if total_orders else 0

    return {
        "is_sample_data": True,
        "store_name": "Analiyx Demo Store",
        "summary": {
            "total_orders": total_orders,
            "total_revenue": round(total_revenue, 2),
            "total_visitors": total_visitors,
            "avg_order_value": avg_order_value,
            "conversion_rate": round(total_orders / total_visitors * 100, 2) if total_visitors else 0,
            "returning_customer_rate": 34.2,
            "cart_abandonment_rate": 68.5,
        },
        "daily_performance": days,
        "top_products": top_products,
        "recent_orders": recent_orders,
        "traffic_sources": traffic_sources,
    }


@router.get("/report")
async def get_shopify_report(user_id: str = Depends(get_current_user_id)):
    """
    Get Shopify store performance report.
    TODO (Developer): Replace _generate_sample_data() with actual Shopify Admin API calls.
    Required: Shopify Access Token, Store Domain
    API: GET https://{store}.myshopify.com/admin/api/2024-10/orders.json
    Docs: https://shopify.dev/docs/api/admin-rest
    """
    return _generate_sample_data()
