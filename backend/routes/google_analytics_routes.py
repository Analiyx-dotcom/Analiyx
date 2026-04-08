"""
Google Analytics integration routes - Fetches GA4 report data via Nango proxy.
Uses GA4 Data API: https://analyticsdata.googleapis.com
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from auth import get_current_user_id
from nango_service import NangoService
from bson import ObjectId
from datetime import datetime, timedelta
import httpx
import os
import logging

router = APIRouter(prefix="/api/google-analytics", tags=["Google Analytics"])

db = None
nango: NangoService = None


def set_database(database):
    global db, nango
    db = database
    nango = NangoService(database)


async def _get_connection(user_id: str):
    """Get the user's google-analytics Nango connection"""
    conn = await nango.get_connection(user_id, "google-analytics")
    if not conn or not conn.get("connection_id"):
        raise HTTPException(status_code=400, detail="Google Analytics not connected. Please connect via Data Sources.")
    return conn


async def _nango_proxy(connection_id: str, method: str, path: str, data: dict = None, base_url_override: str = None):
    """Make a Nango proxy request with optional base URL override"""
    secret = os.environ.get("NANGO_SECRET_KEY")
    host = os.environ.get("NANGO_HOST", "https://api.nango.dev")

    headers = {
        "Authorization": f"Bearer {secret}",
        "Connection-Id": connection_id,
        "Provider-Config-Key": "google-analytics",
        "Content-Type": "application/json",
    }
    if base_url_override:
        headers["Base-Url-Override"] = base_url_override

    url = f"{host}/proxy{path}"

    async with httpx.AsyncClient(timeout=30) as client:
        if method == "GET":
            resp = await client.get(url, headers=headers)
        else:
            resp = await client.post(url, headers=headers, json=data)

        if resp.status_code != 200:
            logging.error(f"GA proxy {method} {path} failed ({resp.status_code}): {resp.text[:500]}")
            return None
        return resp.json()


@router.get("/properties")
async def get_properties(user_id: str = Depends(get_current_user_id)):
    """List available GA4 properties via Admin API"""
    conn = await _get_connection(user_id)
    cid = conn["connection_id"]

    # Use GA4 Admin API to list account summaries
    data = await _nango_proxy(
        cid, "GET", "/v1beta/accountSummaries",
        base_url_override="https://analyticsadmin.googleapis.com"
    )

    if not data:
        # Admin API may need extra scopes — return empty with instruction
        return {"properties": [], "note": "Could not list properties. You may need to enter your GA4 Property ID manually. Find it in Google Analytics > Admin > Property Settings."}

    properties = []
    for acct in data.get("accountSummaries", []):
        acct_name = acct.get("displayName", "Unknown Account")
        for prop in acct.get("propertySummaries", []):
            prop_id = prop.get("property", "").replace("properties/", "")
            properties.append({
                "property_id": prop_id,
                "name": prop.get("displayName", "Unknown Property"),
                "account_name": acct_name,
            })

    # Save the first property ID for the user
    if properties:
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"ga_property_id": properties[0]["property_id"]}}
        )

    return {"properties": properties}


@router.post("/set-property")
async def set_property(data: dict, user_id: str = Depends(get_current_user_id)):
    """Manually set the GA4 property ID for the user"""
    prop_id = data.get("property_id", "").strip()
    if not prop_id:
        raise HTTPException(status_code=400, detail="Property ID is required")
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"ga_property_id": prop_id}}
    )
    return {"success": True, "property_id": prop_id}


@router.get("/report")
async def get_report(property_id: Optional[str] = None, days: int = 30, user_id: str = Depends(get_current_user_id)):
    """Fetch GA4 daily metrics report for charts"""
    conn = await _get_connection(user_id)
    cid = conn["connection_id"]

    # If no property_id, try user's saved one or auto-discover
    if not property_id:
        user = await db.users.find_one({"_id": ObjectId(user_id)}, {"ga_property_id": 1})
        property_id = user.get("ga_property_id") if user else None

    if not property_id:
        # Auto-discover
        props_data = await _nango_proxy(
            cid, "GET", "/v1beta/accountSummaries",
            base_url_override="https://analyticsadmin.googleapis.com"
        )
        if props_data:
            for acct in props_data.get("accountSummaries", []):
                for prop in acct.get("propertySummaries", []):
                    property_id = prop.get("property", "").replace("properties/", "")
                    break
                if property_id:
                    break

    if not property_id:
        raise HTTPException(status_code=404, detail="No GA4 property found. Please check your Google Analytics account.")

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Fetch daily metrics
    report_body = {
        "dateRanges": [{
            "startDate": start_date.strftime("%Y-%m-%d"),
            "endDate": end_date.strftime("%Y-%m-%d"),
        }],
        "dimensions": [{"name": "date"}],
        "metrics": [
            {"name": "sessions"},
            {"name": "activeUsers"},
            {"name": "screenPageViews"},
            {"name": "bounceRate"},
            {"name": "averageSessionDuration"},
            {"name": "newUsers"},
        ],
        "orderBys": [{"dimension": {"dimensionName": "date"}}],
        "limit": "365",
    }

    daily_data = await _nango_proxy(
        cid, "POST", f"/v1beta/properties/{property_id}:runReport",
        data=report_body,
        base_url_override="https://analyticsdata.googleapis.com"
    )

    # Fetch top pages
    pages_body = {
        "dateRanges": [{
            "startDate": start_date.strftime("%Y-%m-%d"),
            "endDate": end_date.strftime("%Y-%m-%d"),
        }],
        "dimensions": [{"name": "pagePath"}],
        "metrics": [
            {"name": "screenPageViews"},
            {"name": "activeUsers"},
            {"name": "bounceRate"},
        ],
        "orderBys": [{"metric": {"metricName": "screenPageViews"}, "desc": True}],
        "limit": "10",
    }

    pages_data = await _nango_proxy(
        cid, "POST", f"/v1beta/properties/{property_id}:runReport",
        data=pages_body,
        base_url_override="https://analyticsdata.googleapis.com"
    )

    # Fetch traffic sources
    sources_body = {
        "dateRanges": [{
            "startDate": start_date.strftime("%Y-%m-%d"),
            "endDate": end_date.strftime("%Y-%m-%d"),
        }],
        "dimensions": [{"name": "sessionDefaultChannelGroup"}],
        "metrics": [
            {"name": "sessions"},
            {"name": "activeUsers"},
        ],
        "orderBys": [{"metric": {"metricName": "sessions"}, "desc": True}],
        "limit": "10",
    }

    sources_data = await _nango_proxy(
        cid, "POST", f"/v1beta/properties/{property_id}:runReport",
        data=sources_body,
        base_url_override="https://analyticsdata.googleapis.com"
    )

    # Parse daily data into chart format
    daily_chart = []
    total_sessions = 0
    total_users = 0
    total_pageviews = 0
    total_new_users = 0

    if daily_data and daily_data.get("rows"):
        for row in daily_data["rows"]:
            date_str = row["dimensionValues"][0]["value"]  # "20250101"
            formatted_date = f"{date_str[4:6]}/{date_str[6:8]}"
            mv = row["metricValues"]
            sessions = int(mv[0]["value"])
            users = int(mv[1]["value"])
            pageviews = int(mv[2]["value"])
            bounce_rate = round(float(mv[3]["value"]) * 100, 1) if mv[3]["value"] else 0
            avg_duration = round(float(mv[4]["value"]), 1) if mv[4]["value"] else 0
            new_users = int(mv[5]["value"])

            total_sessions += sessions
            total_users += users
            total_pageviews += pageviews
            total_new_users += new_users

            daily_chart.append({
                "date": formatted_date,
                "sessions": sessions,
                "users": users,
                "pageviews": pageviews,
                "bounce_rate": bounce_rate,
                "avg_duration": avg_duration,
                "new_users": new_users,
            })

    # Parse top pages
    top_pages = []
    if pages_data and pages_data.get("rows"):
        for row in pages_data["rows"]:
            top_pages.append({
                "page": row["dimensionValues"][0]["value"],
                "pageviews": int(row["metricValues"][0]["value"]),
                "users": int(row["metricValues"][1]["value"]),
                "bounce_rate": round(float(row["metricValues"][2]["value"]) * 100, 1),
            })

    # Parse traffic sources
    traffic_sources = []
    if sources_data and sources_data.get("rows"):
        for row in sources_data["rows"]:
            traffic_sources.append({
                "source": row["dimensionValues"][0]["value"],
                "sessions": int(row["metricValues"][0]["value"]),
                "users": int(row["metricValues"][1]["value"]),
            })

    avg_bounce = round(sum(d["bounce_rate"] for d in daily_chart) / len(daily_chart), 1) if daily_chart else 0

    return {
        "property_id": property_id,
        "period": f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}",
        "summary": {
            "total_sessions": total_sessions,
            "total_users": total_users,
            "total_pageviews": total_pageviews,
            "total_new_users": total_new_users,
            "avg_bounce_rate": avg_bounce,
        },
        "daily_chart": daily_chart,
        "top_pages": top_pages,
        "traffic_sources": traffic_sources,
    }
