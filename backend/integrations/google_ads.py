"""
Google Ads Integration Implementation
"""

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import os
from typing import Dict, Any, List
from datetime import datetime, timedelta

class GoogleAdsIntegration:
    """Google Ads API Integration"""
    
    def __init__(self, credentials: Dict[str, Any]):
        self.credentials = credentials
        self.client = None
    
    def initialize_client(self):
        """Initialize Google Ads client"""
        config = {
            "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
            "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
            "refresh_token": self.credentials.get("refresh_token"),
            "use_proto_plus": True
        }
        
        self.client = GoogleAdsClient.load_from_dict(config)
    
    async def fetch_campaign_metrics(self, customer_id: str, days: int = 30) -> Dict[str, Any]:
        """Fetch campaign performance metrics"""
        
        if not self.client:
            self.initialize_client()
        
        ga_service = self.client.get_service("GoogleAdsService")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        query = f"""
            SELECT
              campaign.id,
              campaign.name,
              campaign.status,
              metrics.impressions,
              metrics.clicks,
              metrics.conversions,
              metrics.cost_micros,
              metrics.ctr,
              metrics.average_cpc,
              metrics.conversions_value
            FROM campaign
            WHERE segments.date >= '{start_date.strftime('%Y-%m-%d')}'
              AND segments.date <= '{end_date.strftime('%Y-%m-%d')}'
            ORDER BY metrics.impressions DESC
            LIMIT 100
        """
        
        try:
            response = ga_service.search(customer_id=customer_id, query=query)
            
            campaigns = []
            total_metrics = {
                "impressions": 0,
                "clicks": 0,
                "conversions": 0,
                "cost": 0,
                "ctr": 0,
                "avg_cpc": 0
            }
            
            for row in response:
                campaign_data = {
                    "id": row.campaign.id,
                    "name": row.campaign.name,
                    "status": row.campaign.status.name,
                    "impressions": row.metrics.impressions,
                    "clicks": row.metrics.clicks,
                    "conversions": row.metrics.conversions,
                    "cost": row.metrics.cost_micros / 1_000_000,  # Convert micros to currency
                    "ctr": round(row.metrics.ctr * 100, 2),
                    "avg_cpc": row.metrics.average_cpc / 1_000_000,
                    "conversion_value": row.metrics.conversions_value
                }
                
                campaigns.append(campaign_data)
                
                # Aggregate totals
                total_metrics["impressions"] += campaign_data["impressions"]
                total_metrics["clicks"] += campaign_data["clicks"]
                total_metrics["conversions"] += campaign_data["conversions"]
                total_metrics["cost"] += campaign_data["cost"]
            
            # Calculate average CTR
            if total_metrics["impressions"] > 0:
                total_metrics["ctr"] = round(
                    (total_metrics["clicks"] / total_metrics["impressions"]) * 100, 2
                )
            
            # Calculate average CPC
            if total_metrics["clicks"] > 0:
                total_metrics["avg_cpc"] = round(
                    total_metrics["cost"] / total_metrics["clicks"], 2
                )
            
            return {
                "success": True,
                "customer_id": customer_id,
                "period": f"{days} days",
                "total_metrics": total_metrics,
                "campaigns": campaigns,
                "fetched_at": datetime.now().isoformat()
            }
            
        except GoogleAdsException as ex:
            error_msg = f"Request failed with status {ex.error.code().name}"
            for error in ex.failure.errors:
                error_msg += f"\n\tError: {error.message}"
            
            return {
                "success": False,
                "error": error_msg
            }
    
    async def get_account_info(self, customer_id: str) -> Dict[str, Any]:
        """Get Google Ads account information"""
        
        if not self.client:
            self.initialize_client()
        
        ga_service = self.client.get_service("GoogleAdsService")
        
        query = """
            SELECT
              customer.id,
              customer.descriptive_name,
              customer.currency_code,
              customer.time_zone,
              customer.manager
            FROM customer
        """
        
        try:
            response = ga_service.search(customer_id=customer_id, query=query)
            
            for row in response:
                return {
                    "success": True,
                    "account_id": row.customer.id,
                    "account_name": row.customer.descriptive_name,
                    "currency": row.customer.currency_code,
                    "timezone": row.customer.time_zone,
                    "is_manager": row.customer.manager
                }
            
        except GoogleAdsException as ex:
            return {
                "success": False,
                "error": str(ex)
            }
    
    @staticmethod
    def get_oauth_url(state: str) -> str:
        """Generate OAuth authorization URL"""
        base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        params = {
            "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
            "redirect_uri": os.getenv("GOOGLE_ADS_REDIRECT_URI"),
            "scope": "https://www.googleapis.com/auth/adwords",
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent",
            "state": state
        }
        
        param_str = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{param_str}"
    
    @staticmethod
    async def exchange_code_for_token(code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        import httpx
        
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
            "redirect_uri": os.getenv("GOOGLE_ADS_REDIRECT_URI"),
            "grant_type": "authorization_code"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data)
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Token exchange failed: {response.text}")
