"""
Unified Integration Framework for Analiyx
Handles all data source integrations with consistent patterns
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

class IntegrationType(str, Enum):
    """Types of integrations"""
    OAUTH = "oauth"  # Google Ads, Meta Ads, Google Analytics
    API_KEY = "api_key"  # Zoho Books, HubSpot
    DATABASE = "database"  # PostgreSQL, MySQL, MongoDB
    FILE = "file"  # CSV, Excel (already implemented)
    SPREADSHEET = "spreadsheet"  # Google Sheets

class IntegrationStatus(str, Enum):
    """Connection status"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    PENDING = "pending"

class BaseIntegration(ABC):
    """Base class for all integrations"""
    
    def __init__(self, user_id: str, credentials: Dict[str, Any]):
        self.user_id = user_id
        self.credentials = credentials
        self.status = IntegrationStatus.DISCONNECTED
    
    @abstractmethod
    async def connect(self) -> Dict[str, Any]:
        """Establish connection to the data source"""
        pass
    
    @abstractmethod
    async def fetch_data(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Fetch data from the data source"""
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """Test if connection is valid"""
        pass
    
    @abstractmethod
    def get_required_credentials(self) -> List[str]:
        """Return list of required credential fields"""
        pass
    
    async def disconnect(self) -> bool:
        """Disconnect from data source"""
        self.status = IntegrationStatus.DISCONNECTED
        return True
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get current connection information"""
        return {
            "status": self.status.value,
            "user_id": self.user_id,
            "connected_at": datetime.utcnow().isoformat()
        }

class IntegrationRegistry:
    """Registry for all available integrations"""
    
    _integrations = {}
    
    @classmethod
    def register(cls, name: str, integration_class):
        """Register an integration"""
        cls._integrations[name] = integration_class
    
    @classmethod
    def get(cls, name: str):
        """Get integration class by name"""
        return cls._integrations.get(name)
    
    @classmethod
    def list_all(cls) -> List[str]:
        """List all registered integrations"""
        return list(cls._integrations.keys())

# Integration metadata
INTEGRATION_METADATA = {
    "google_ads": {
        "name": "Google Ads",
        "type": IntegrationType.OAUTH,
        "icon": "megaphone",
        "color": "#4285F4",
        "description": "Connect Google Ads to track campaign performance",
        "metrics": ["impressions", "clicks", "conversions", "cost", "ctr"],
        "scopes": ["https://www.googleapis.com/auth/adwords"]
    },
    "meta_ads": {
        "name": "Meta Ads",
        "type": IntegrationType.OAUTH,
        "icon": "facebook",
        "color": "#1877F2",
        "description": "Connect Facebook/Instagram Ads for performance tracking",
        "metrics": ["impressions", "clicks", "conversions", "spend", "reach"],
        "scopes": ["ads_read", "ads_management"]
    },
    "google_analytics": {
        "name": "Google Analytics",
        "type": IntegrationType.OAUTH,
        "icon": "bar-chart",
        "color": "#E37400",
        "description": "Track website traffic and user behavior",
        "metrics": ["sessions", "users", "pageviews", "bounce_rate"],
        "scopes": ["https://www.googleapis.com/auth/analytics.readonly"]
    },
    "google_sheets": {
        "name": "Google Sheets",
        "type": IntegrationType.OAUTH,
        "icon": "sheet",
        "color": "#0F9D58",
        "description": "Import data from Google Sheets",
        "metrics": ["rows", "columns", "sheets"],
        "scopes": ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    },
    "zoho_books": {
        "name": "Zoho Books",
        "type": IntegrationType.API_KEY,
        "icon": "book-open",
        "color": "#E42527",
        "description": "Connect Zoho Books for financial data",
        "metrics": ["revenue", "invoices", "expenses", "payments"],
        "required_fields": ["organization_id", "client_id", "client_secret"]
    },
    "shopify": {
        "name": "Shopify",
        "type": IntegrationType.API_KEY,
        "icon": "shopping-bag",
        "color": "#96BF48",
        "description": "Connect Shopify store for e-commerce data",
        "metrics": ["orders", "revenue", "customers", "products"],
        "required_fields": ["shop_url", "access_token"]
    },
    "hubspot": {
        "name": "HubSpot",
        "type": IntegrationType.API_KEY,
        "icon": "users",
        "color": "#FF7A59",
        "description": "Connect HubSpot CRM for customer data",
        "metrics": ["contacts", "deals", "companies", "revenue"],
        "required_fields": ["api_key"]
    },
    "salesforce": {
        "name": "Salesforce",
        "type": IntegrationType.OAUTH,
        "icon": "cloud",
        "color": "#00A1E0",
        "description": "Connect Salesforce CRM for sales data",
        "metrics": ["leads", "opportunities", "accounts", "revenue"],
        "scopes": ["api", "refresh_token"]
    },
    "postgresql": {
        "name": "PostgreSQL",
        "type": IntegrationType.DATABASE,
        "icon": "database",
        "color": "#336791",
        "description": "Connect PostgreSQL database",
        "metrics": ["tables", "rows", "queries"],
        "required_fields": ["host", "port", "database", "username", "password"]
    },
    "mysql": {
        "name": "MySQL",
        "type": IntegrationType.DATABASE,
        "icon": "database",
        "color": "#4479A1",
        "description": "Connect MySQL database",
        "metrics": ["tables", "rows", "queries"],
        "required_fields": ["host", "port", "database", "username", "password"]
    },
    "mongodb": {
        "name": "MongoDB",
        "type": IntegrationType.DATABASE,
        "icon": "database",
        "color": "#47A248",
        "description": "Connect MongoDB database",
        "metrics": ["collections", "documents", "queries"],
        "required_fields": ["connection_string"]
    },
    "ai_visibility": {
        "name": "AI Visibility",
        "type": IntegrationType.API_KEY,
        "icon": "brain",
        "color": "#8B5CF6",
        "description": "Track AI search visibility and rankings",
        "metrics": ["appearances", "rankings", "mentions", "visibility"],
        "required_fields": ["api_key", "domain"]
    }
}
