"""
Google Ads Integration Tests - Iteration 14
Tests for:
1. GET /api/google-ads/customers - Returns 400 when not connected
2. GET /api/google-ads/campaigns - Returns 400 when not connected
3. POST /api/nango/connect-session - Works for google-ads provider
4. POST /api/nango/save-connection - Stores google-ads connection in DB
5. GET /api/nango/connections - Returns saved connections
6. Credit deduction on AI chat (1 credit per query)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestGoogleAdsNotConnected:
    """Test Google Ads endpoints return proper error when not connected"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as test user and get token"""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "testuser@test.com",
            "password": "test1234"
        })
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        self.token = login_resp.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        # Clean up any existing google-ads connection for clean test
        requests.delete(f"{BASE_URL}/api/nango/connections/google-ads", headers=self.headers)
    
    def test_get_customers_returns_400_when_not_connected(self):
        """GET /api/google-ads/customers should return 400 with clear message when not connected"""
        resp = requests.get(f"{BASE_URL}/api/google-ads/customers", headers=self.headers)
        assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert "detail" in data
        assert "not connected" in data["detail"].lower(), f"Expected 'not connected' message, got: {data['detail']}"
    
    def test_get_campaigns_returns_400_when_not_connected(self):
        """GET /api/google-ads/campaigns should return 400 with clear message when not connected"""
        resp = requests.get(f"{BASE_URL}/api/google-ads/campaigns", headers=self.headers)
        assert resp.status_code == 400, f"Expected 400, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert "detail" in data
        assert "not connected" in data["detail"].lower(), f"Expected 'not connected' message, got: {data['detail']}"
    
    def test_get_customers_requires_auth(self):
        """GET /api/google-ads/customers should require authentication"""
        resp = requests.get(f"{BASE_URL}/api/google-ads/customers")
        assert resp.status_code in [401, 403], f"Expected 401 or 403, got {resp.status_code}"
    
    def test_get_campaigns_requires_auth(self):
        """GET /api/google-ads/campaigns should require authentication"""
        resp = requests.get(f"{BASE_URL}/api/google-ads/campaigns")
        assert resp.status_code in [401, 403], f"Expected 401 or 403, got {resp.status_code}"


class TestNangoConnectSessionGoogleAds:
    """Test Nango connect session works for google-ads provider"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as test user and get token"""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "testuser@test.com",
            "password": "test1234"
        })
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        self.token = login_resp.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_connect_session_for_google_ads(self):
        """POST /api/nango/connect-session should work for google-ads provider"""
        resp = requests.post(f"{BASE_URL}/api/nango/connect-session", 
                           headers=self.headers,
                           json={"allowed_integrations": ["google-ads"]})
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        # Check for token in response (Nango returns nested data)
        token = data.get("data", {}).get("token") or data.get("token")
        assert token is not None, f"Expected token in response, got: {data}"
        assert len(token) > 10, f"Token seems too short: {token}"


class TestNangoSaveGoogleAdsConnection:
    """Test saving google-ads connection in DB"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as test user and get token"""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "testuser@test.com",
            "password": "test1234"
        })
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        self.token = login_resp.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_save_google_ads_connection(self):
        """POST /api/nango/save-connection should store google-ads connection"""
        # First clean up any existing connection
        requests.delete(f"{BASE_URL}/api/nango/connections/google-ads", headers=self.headers)
        
        # Save a test connection
        test_connection_id = f"test-google-ads-conn-{os.urandom(4).hex()}"
        resp = requests.post(f"{BASE_URL}/api/nango/save-connection",
                           headers=self.headers,
                           json={
                               "integration_id": "google-ads",
                               "connection_id": test_connection_id
                           })
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        # Verify connection was saved by fetching connections
        get_resp = requests.get(f"{BASE_URL}/api/nango/connections", headers=self.headers)
        assert get_resp.status_code == 200
        connections = get_resp.json().get("connections", [])
        
        google_ads_conn = next((c for c in connections if c.get("integration_id") == "google-ads"), None)
        assert google_ads_conn is not None, f"google-ads connection not found in: {connections}"
        assert google_ads_conn.get("connection_id") == test_connection_id
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/nango/connections/google-ads", headers=self.headers)


class TestNangoGetConnections:
    """Test getting all Nango connections"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as test user and get token"""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "testuser@test.com",
            "password": "test1234"
        })
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        self.token = login_resp.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_connections_returns_list(self):
        """GET /api/nango/connections should return a list"""
        resp = requests.get(f"{BASE_URL}/api/nango/connections", headers=self.headers)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert "connections" in data
        assert isinstance(data["connections"], list)


class TestAIChatCreditDeduction:
    """Test AI chat deducts credits correctly"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as test user and get token"""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "testuser@test.com",
            "password": "test1234"
        })
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        self.token = login_resp.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_ai_chat_deducts_credits(self):
        """AI chat should deduct 1 credit per query"""
        # Get initial credits
        me_resp = requests.get(f"{BASE_URL}/api/auth/me", headers=self.headers)
        assert me_resp.status_code == 200
        initial_credits = me_resp.json().get("credits", 0)
        
        if initial_credits < 1:
            pytest.skip("User has no credits to test deduction")
        
        # Make an AI chat request
        chat_resp = requests.post(f"{BASE_URL}/api/ai/chat",
                                 headers=self.headers,
                                 json={"query": "What is 2+2?"})
        
        # Check credits after (should be deducted by 1)
        me_resp2 = requests.get(f"{BASE_URL}/api/auth/me", headers=self.headers)
        assert me_resp2.status_code == 200
        final_credits = me_resp2.json().get("credits", 0)
        
        # If chat succeeded, credits should be deducted
        if chat_resp.status_code == 200:
            assert final_credits == initial_credits - 1, f"Expected credits to decrease by 1. Initial: {initial_credits}, Final: {final_credits}"


class TestSettingsPageAPI:
    """Test Settings page API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as test user and get token"""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "testuser@test.com",
            "password": "test1234"
        })
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        self.token = login_resp.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_current_user(self):
        """GET /api/auth/me should return user profile"""
        resp = requests.get(f"{BASE_URL}/api/auth/me", headers=self.headers)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert "email" in data
        assert data["email"] == "testuser@test.com"


class TestExistingCredentials:
    """Verify existing test credentials work"""
    
    def test_admin_login(self):
        """Admin credentials should work"""
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "Admin@analiyx.com",
            "password": "1234"
        })
        assert resp.status_code == 200, f"Admin login failed: {resp.text}"
        data = resp.json()
        assert "token" in data
        assert data.get("user", {}).get("role") == "admin"
    
    def test_test_user_login(self):
        """Test user credentials should work"""
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "testuser@test.com",
            "password": "test1234"
        })
        assert resp.status_code == 200, f"Test user login failed: {resp.text}"
        data = resp.json()
        assert "token" in data
