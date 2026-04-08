"""
Google Ads integration routes - Fetches campaign data via Nango proxy.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from auth import get_current_user_id
from nango_service import NangoService
from bson import ObjectId
import httpx
import os
import logging

router = APIRouter(prefix="/api/google-ads", tags=["Google Ads"])

db = None
nango: NangoService = None


def set_database(database):
    global db, nango
    db = database
    nango = NangoService(database)


async def _get_connection(user_id: str):
    """Get the user's google-ads Nango connection"""
    conn = await nango.get_connection(user_id, "google-ads")
    if not conn or not conn.get("connection_id"):
        raise HTTPException(status_code=400, detail="Google Ads not connected. Please connect via Data Sources.")
    return conn


async def _proxy_gaql(connection_id: str, customer_id: str, query: str):
    """Execute a GAQL query via Nango proxy to Google Ads API"""
    secret = os.environ.get("NANGO_SECRET_KEY")
    host = os.environ.get("NANGO_HOST", "https://api.nango.dev")
    dev_token = os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN", "")

    headers = {
        "Authorization": f"Bearer {secret}",
        "Connection-Id": connection_id,
        "Provider-Config-Key": "google-ads",
        "Content-Type": "application/json",
        "Base-Url-Override": "https://googleads.googleapis.com",
        "nango-proxy-developer-token": dev_token,
    }

    url = f"{host}/proxy/v20/customers/{customer_id}/googleAds:searchStream"

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, headers=headers, json={"query": query})
        if resp.status_code != 200:
            error_text = resp.text[:500]
            logging.error(f"Google Ads GAQL failed ({resp.status_code}): {error_text}")
            # Check for specific errors
            if "DEVELOPER_TOKEN_NOT_APPROVED" in error_text:
                raise HTTPException(
                    status_code=403,
                    detail="Your Google Ads developer token is not approved. Please apply for Basic or Standard Access at Google Ads API Center (ads.google.com/aw/apicenter) to use production data."
                )
            return None
        return resp.json()


async def _get_accessible_customers(connection_id: str):
    """List accessible customer IDs for the connected Google Ads account"""
    secret = os.environ.get("NANGO_SECRET_KEY")
    host = os.environ.get("NANGO_HOST", "https://api.nango.dev")
    dev_token = os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN", "")

    headers = {
        "Authorization": f"Bearer {secret}",
        "Connection-Id": connection_id,
        "Provider-Config-Key": "google-ads",
        "Base-Url-Override": "https://googleads.googleapis.com",
        "nango-proxy-developer-token": dev_token,
    }

    url = f"{host}/proxy/v20/customers:listAccessibleCustomers"

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url, headers=headers)
        if resp.status_code != 200:
            logging.error(f"Google Ads listAccessibleCustomers failed: {resp.status_code} {resp.text[:300]}")
            return []
        data = resp.json()
        # Returns {"resourceNames": ["customers/1234567890", ...]}
        names = data.get("resourceNames", [])
        return [n.split("/")[-1] for n in names]


# ---- Endpoints ----

@router.get("/customers")
async def get_customers(user_id: str = Depends(get_current_user_id)):
    """Get list of accessible Google Ads customer IDs"""
    conn = await _get_connection(user_id)
    customers = await _get_accessible_customers(conn["connection_id"])
    return {"customers": customers}


@router.get("/campaigns")
async def get_campaigns(customer_id: Optional[str] = None, user_id: str = Depends(get_current_user_id)):
    """Fetch campaigns with performance metrics for the last 30 days"""
    conn = await _get_connection(user_id)
    connection_id = conn["connection_id"]

    # If no customer_id provided, fetch the first accessible one
    if not customer_id:
        customers = await _get_accessible_customers(connection_id)
        if not customers:
            raise HTTPException(status_code=404, detail="No Google Ads accounts found for this connection.")
        customer_id = customers[0]

    query = """
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.advertising_channel_type,
            campaign_budget.amount_micros,
            metrics.impressions,
            metrics.clicks,
            metrics.ctr,
            metrics.average_cpc,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value
        FROM campaign
        WHERE campaign.status != 'REMOVED'
            AND segments.date DURING LAST_30_DAYS
    """

    try:
        raw = await _proxy_gaql(connection_id, customer_id, query)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Google Ads campaigns error: {e}")
        raise HTTPException(status_code=502, detail="Failed to fetch campaign data from Google Ads.")

    if raw is None:
        raise HTTPException(status_code=502, detail="Failed to fetch campaign data from Google Ads.")

    # Parse the response (searchStream returns a list of result batches)
    campaigns = []
    total_impressions = 0
    total_clicks = 0
    total_cost = 0.0
    total_conversions = 0.0

    results = []
    if isinstance(raw, list):
        for batch in raw:
            results.extend(batch.get("results", []))
    elif isinstance(raw, dict):
        results = raw.get("results", [])

    for row in results:
        camp = row.get("campaign", {})
        metrics = row.get("metrics", {})
        budget = row.get("campaignBudget", {})

        impressions = int(metrics.get("impressions", 0))
        clicks = int(metrics.get("clicks", 0))
        cost_micros = int(metrics.get("costMicros", 0))
        cost = cost_micros / 1_000_000
        ctr = float(metrics.get("ctr", 0))
        avg_cpc_micros = int(metrics.get("averageCpc", 0))
        avg_cpc = avg_cpc_micros / 1_000_000
        conversions = float(metrics.get("conversions", 0))
        conv_value = float(metrics.get("conversionsValue", 0))
        budget_amount = int(budget.get("amountMicros", 0)) / 1_000_000

        total_impressions += impressions
        total_clicks += clicks
        total_cost += cost
        total_conversions += conversions

        campaigns.append({
            "id": camp.get("id"),
            "name": camp.get("name", "Unknown"),
            "status": camp.get("status", "UNKNOWN"),
            "channel_type": camp.get("advertisingChannelType", "UNKNOWN"),
            "daily_budget": round(budget_amount, 2),
            "impressions": impressions,
            "clicks": clicks,
            "ctr": round(ctr * 100, 2),
            "avg_cpc": round(avg_cpc, 2),
            "cost": round(cost, 2),
            "conversions": round(conversions, 1),
            "conversion_value": round(conv_value, 2),
        })

    total_ctr = round((total_clicks / total_impressions * 100) if total_impressions > 0 else 0, 2)

    return {
        "customer_id": customer_id,
        "campaigns": campaigns,
        "summary": {
            "total_campaigns": len(campaigns),
            "total_impressions": total_impressions,
            "total_clicks": total_clicks,
            "total_ctr": total_ctr,
            "total_cost": round(total_cost, 2),
            "total_conversions": round(total_conversions, 1),
        },
    }
