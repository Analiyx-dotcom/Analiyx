"""
Meta Ads Routes — Dashboard data for Facebook/Instagram Ads.
Currently returns SAMPLE data. Developer needs to replace with actual Meta Marketing API calls.
See API_CONTRACTS.md for the exact response schema.
"""
from fastapi import APIRouter, HTTPException, Depends
from auth import get_current_user_id
from datetime import datetime, timezone, timedelta
import random

router = APIRouter(prefix="/api/meta-ads", tags=["Meta Ads"])

db = None

def set_database(database):
    global db
    db = database


def _generate_sample_data():
    """Generate realistic sample Meta Ads data. Replace this with actual Meta API calls."""
    days = []
    for i in range(30, 0, -1):
        d = datetime.now(timezone.utc) - timedelta(days=i)
        impressions = random.randint(8000, 25000)
        reach = int(impressions * random.uniform(0.6, 0.85))
        clicks = int(impressions * random.uniform(0.015, 0.04))
        spend = round(random.uniform(800, 3500), 2)
        conversions = int(clicks * random.uniform(0.02, 0.08))
        days.append({
            "date": d.strftime("%b %d"),
            "impressions": impressions,
            "reach": reach,
            "clicks": clicks,
            "spend": spend,
            "conversions": conversions,
        })

    campaigns = [
        {"name": "Brand Awareness - Instagram", "status": "ACTIVE", "objective": "BRAND_AWARENESS", "impressions": 185420, "reach": 142300, "clicks": 4215, "spend": 28500, "ctr": 2.27, "cpc": 6.76},
        {"name": "Lead Gen - Facebook", "status": "ACTIVE", "objective": "LEAD_GENERATION", "impressions": 92100, "reach": 71800, "clicks": 2840, "spend": 19200, "ctr": 3.08, "cpc": 6.76},
        {"name": "Retargeting - Carousel", "status": "ACTIVE", "objective": "CONVERSIONS", "impressions": 54300, "reach": 38200, "clicks": 1920, "spend": 14600, "ctr": 3.54, "cpc": 7.60},
        {"name": "Video Views - Reels", "status": "PAUSED", "objective": "VIDEO_VIEWS", "impressions": 210500, "reach": 178900, "clicks": 3100, "spend": 12800, "ctr": 1.47, "cpc": 4.13},
        {"name": "Website Traffic - Stories", "status": "ACTIVE", "objective": "LINK_CLICKS", "impressions": 67800, "reach": 52100, "clicks": 2450, "spend": 9800, "ctr": 3.61, "cpc": 4.00},
    ]

    total_impressions = sum(c["impressions"] for c in campaigns)
    total_reach = sum(c["reach"] for c in campaigns)
    total_clicks = sum(c["clicks"] for c in campaigns)
    total_spend = sum(c["spend"] for c in campaigns)
    total_conversions = sum(days[i]["conversions"] for i in range(len(days)))

    age_breakdown = [
        {"age_group": "18-24", "impressions": 125000, "clicks": 3800, "spend": 18500},
        {"age_group": "25-34", "impressions": 198000, "clicks": 6200, "spend": 28400},
        {"age_group": "35-44", "impressions": 142000, "clicks": 3100, "spend": 19200},
        {"age_group": "45-54", "impressions": 89000, "clicks": 1400, "spend": 11500},
        {"age_group": "55+", "impressions": 56000, "clicks": 520, "spend": 7300},
    ]

    platform_breakdown = [
        {"platform": "Facebook", "value": 58},
        {"platform": "Instagram", "value": 35},
        {"platform": "Audience Network", "value": 5},
        {"platform": "Messenger", "value": 2},
    ]

    return {
        "is_sample_data": True,
        "summary": {
            "total_impressions": total_impressions,
            "total_reach": total_reach,
            "total_clicks": total_clicks,
            "total_spend": total_spend,
            "total_conversions": total_conversions,
            "avg_ctr": round(total_clicks / total_impressions * 100, 2) if total_impressions else 0,
            "avg_cpc": round(total_spend / total_clicks, 2) if total_clicks else 0,
            "avg_cpm": round(total_spend / total_impressions * 1000, 2) if total_impressions else 0,
        },
        "daily_performance": days,
        "campaigns": campaigns,
        "age_breakdown": age_breakdown,
        "platform_breakdown": platform_breakdown,
    }


@router.get("/report")
async def get_meta_ads_report(user_id: str = Depends(get_current_user_id)):
    """
    Get Meta Ads performance report.
    TODO (Developer): Replace _generate_sample_data() with actual Meta Marketing API call.
    Required: Meta Access Token, Ad Account ID
    API: GET https://graph.facebook.com/v21.0/act_{ad_account_id}/insights
    """
    return _generate_sample_data()
