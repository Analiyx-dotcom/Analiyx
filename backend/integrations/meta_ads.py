"""
Meta Ads (Facebook) Integration Implementation
"""

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adsinsights import AdsInsights
import os
from typing import Dict, Any, List
from datetime import datetime, timedelta

class MetaAdsIntegration:
    """Meta Ads (Facebook/Instagram) Integration"""
    
    def __init__(self, credentials: Dict[str, Any]):
        self.credentials = credentials
        self.api = None
    
    def initialize_api(self):
        """Initialize Facebook Ads API"""
        access_token = self.credentials.get("access_token") or os.getenv("META_ACCESS_TOKEN")
        app_id = os.getenv("META_APP_ID")
        app_secret = os.getenv("META_APP_SECRET")
        
        FacebookAdsApi.init(
            app_id=app_id,
            app_secret=app_secret,
            access_token=access_token
        )
        
        self.api = FacebookAdsApi.get_default_api()
    
    async def fetch_campaign_metrics(self, ad_account_id: str, days: int = 30) -> Dict[str, Any]:
        """Fetch Meta Ads campaign performance"""
        
        if not self.api:
            self.initialize_api()
        
        # Ensure account ID has correct format
        if not ad_account_id.startswith('act_'):
            ad_account_id = f'act_{ad_account_id}'
        
        account = AdAccount(ad_account_id)
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Define fields to fetch
        fields = [
            AdsInsights.Field.campaign_id,
            AdsInsights.Field.campaign_name,
            AdsInsights.Field.impressions,
            AdsInsights.Field.clicks,
            AdsInsights.Field.spend,
            AdsInsights.Field.reach,
            AdsInsights.Field.ctr,
            AdsInsights.Field.cpc,
            AdsInsights.Field.cpp,
            AdsInsights.Field.actions,
        ]
        
        params = {
            'time_range': {
                'since': start_date.strftime('%Y-%m-%d'),
                'until': end_date.strftime('%Y-%m-%d')
            },
            'level': 'campaign',
            'breakdowns': []
        }
        
        try:
            insights = account.get_insights(fields=fields, params=params)
            
            campaigns = []
            total_metrics = {
                "impressions": 0,
                "clicks": 0,
                "spend": 0,
                "reach": 0,
                "conversions": 0,
                "ctr": 0,
                "cpc": 0
            }
            
            for insight in insights:
                # Extract conversion data
                conversions = 0
                if 'actions' in insight:
                    for action in insight['actions']:
                        if action['action_type'] in ['purchase', 'lead', 'complete_registration']:
                            conversions += int(action['value'])
                
                campaign_data = {
                    "id": insight.get('campaign_id', ''),
                    "name": insight.get('campaign_name', ''),
                    "impressions": int(insight.get('impressions', 0)),
                    "clicks": int(insight.get('clicks', 0)),
                    "spend": float(insight.get('spend', 0)),
                    "reach": int(insight.get('reach', 0)),
                    "conversions": conversions,
                    "ctr": float(insight.get('ctr', 0)),
                    "cpc": float(insight.get('cpc', 0))
                }
                
                campaigns.append(campaign_data)
                
                # Aggregate totals
                total_metrics["impressions"] += campaign_data["impressions"]
                total_metrics["clicks"] += campaign_data["clicks"]
                total_metrics["spend"] += campaign_data["spend"]
                total_metrics["reach"] += campaign_data["reach"]
                total_metrics["conversions"] += campaign_data["conversions"]
            
            # Calculate average CTR and CPC
            if total_metrics["impressions"] > 0:
                total_metrics["ctr"] = round(
                    (total_metrics["clicks"] / total_metrics["impressions"]) * 100, 2
                )
            
            if total_metrics["clicks"] > 0:
                total_metrics["cpc"] = round(
                    total_metrics["spend"] / total_metrics["clicks"], 2
                )
            
            return {
                "success": True,
                "ad_account_id": ad_account_id,
                "period": f"{days} days",
                "total_metrics": total_metrics,
                "campaigns": campaigns,
                "fetched_at": datetime.now().isoformat()
            }
            
        except Exception as ex:
            return {
                "success": False,
                "error": str(ex)
            }
    
    async def get_account_info(self, ad_account_id: str) -> Dict[str, Any]:
        """Get Meta Ads account information"""
        
        if not self.api:
            self.initialize_api()
        
        if not ad_account_id.startswith('act_'):
            ad_account_id = f'act_{ad_account_id}'
        
        try:
            account = AdAccount(ad_account_id)
            account_data = account.api_get(fields=[
                'name',
                'currency',
                'timezone_name',
                'account_status',
                'amount_spent'
            ])
            
            return {
                "success": True,
                "account_id": ad_account_id,
                "account_name": account_data.get('name'),
                "currency": account_data.get('currency'),
                "timezone": account_data.get('timezone_name'),
                "status": account_data.get('account_status'),
                "total_spent": float(account_data.get('amount_spent', 0)) / 100
            }
            
        except Exception as ex:
            return {
                "success": False,
                "error": str(ex)
            }
    
    @staticmethod
    def get_oauth_url(state: str) -> str:
        """Generate Facebook OAuth authorization URL"""
        base_url = "https://www.facebook.com/v18.0/dialog/oauth"
        params = {
            "client_id": os.getenv("META_APP_ID"),
            "redirect_uri": os.getenv("META_REDIRECT_URI"),
            "scope": "ads_read,ads_management,business_management",
            "response_type": "code",
            "state": state
        }
        
        param_str = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{param_str}"
    
    @staticmethod
    async def exchange_code_for_token(code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        import httpx
        
        token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
        params = {
            "client_id": os.getenv("META_APP_ID"),
            "client_secret": os.getenv("META_APP_SECRET"),
            "redirect_uri": os.getenv("META_REDIRECT_URI"),
            "code": code
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(token_url, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Token exchange failed: {response.text}")
    
    async def get_ad_accounts(self) -> List[Dict[str, Any]]:
        """Get list of all ad accounts accessible with current token"""
        
        if not self.api:
            self.initialize_api()
        
        try:
            from facebook_business.adobjects.user import User
            
            me = User(fbid='me')
            ad_accounts = me.get_ad_accounts(fields=['name', 'id', 'currency'])
            
            accounts = []
            for account in ad_accounts:
                accounts.append({
                    "id": account['id'],
                    "name": account['name'],
                    "currency": account.get('currency', 'USD')
                })
            
            return accounts
            
        except Exception as ex:
            return []
