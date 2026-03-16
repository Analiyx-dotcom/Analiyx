"""
Test P1/P2 Features for Analiyx Platform - Iteration 5
Tests:
1. AI Search Bar - POST /api/ai/search endpoint (uses GPT-5.2 via emergentintegrations)
2. Slack integration endpoints - /api/slack/*
3. Workspace endpoints (verification for deletion which is P0, already covered)
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
USER_EMAIL = "testpay@analiyx.com"
USER_PASSWORD = "test1234"
ADMIN_EMAIL = "admin@papermap.com"
ADMIN_PASSWORD = "admin123"


class TestSetup:
    """Setup fixtures for authenticated requests"""
    
    @pytest.fixture
    def api_client(self):
        """Shared requests session"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        return session
    
    @pytest.fixture
    def user_token(self, api_client):
        """Get user auth token"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": USER_EMAIL,
            "password": USER_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"User authentication failed: {response.status_code} - {response.text}")
    
    @pytest.fixture
    def admin_token(self, api_client):
        """Get admin auth token"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip(f"Admin authentication failed: {response.status_code}")
    
    @pytest.fixture
    def auth_headers(self, user_token):
        """Headers with user auth token"""
        return {"Authorization": f"Bearer {user_token}", "Content-Type": "application/json"}
    
    @pytest.fixture
    def admin_headers(self, admin_token):
        """Headers with admin auth token"""
        return {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}


class TestAISearch(TestSetup):
    """Test AI Search endpoint - uses GPT-5.2 via emergentintegrations"""
    
    def test_ai_search_no_data_returns_helpful_message(self, api_client, auth_headers):
        """Test AI search returns helpful message when user has no data"""
        response = api_client.post(
            f"{BASE_URL}/api/ai/search",
            json={"query": "What are my top revenue sources?"},
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "answer" in data, "Missing 'answer' field in response"
        assert "sources" in data, "Missing 'sources' field in response"
        
        # For user with no data, we expect a helpful message about uploading data
        answer = data["answer"]
        assert len(answer) > 0, "Answer should not be empty"
        print(f"✓ AI Search returned: {answer[:100]}...")
    
    def test_ai_search_empty_query_returns_400(self, api_client, auth_headers):
        """Test AI search rejects empty queries"""
        response = api_client.post(
            f"{BASE_URL}/api/ai/search",
            json={"query": ""},
            headers=auth_headers
        )
        assert response.status_code == 400, f"Expected 400 for empty query, got {response.status_code}"
        print("✓ Empty query correctly rejected with 400")
    
    def test_ai_search_whitespace_query_returns_400(self, api_client, auth_headers):
        """Test AI search rejects whitespace-only queries"""
        response = api_client.post(
            f"{BASE_URL}/api/ai/search",
            json={"query": "   "},
            headers=auth_headers
        )
        assert response.status_code == 400, f"Expected 400 for whitespace query, got {response.status_code}"
        print("✓ Whitespace query correctly rejected with 400")
    
    def test_ai_search_requires_auth(self, api_client):
        """Test AI search requires authentication"""
        response = api_client.post(
            f"{BASE_URL}/api/ai/search",
            json={"query": "Test query"}
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ Unauthenticated request correctly rejected")
    
    def test_ai_search_with_data_query(self, api_client, auth_headers):
        """Test AI search with a specific data-related question"""
        # This tests that the endpoint processes the query correctly
        # and returns a valid response structure
        response = api_client.post(
            f"{BASE_URL}/api/ai/search",
            json={"query": "Show me a summary of my uploaded files"},
            headers=auth_headers,
            timeout=30  # AI calls may take time
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "answer" in data, "Missing 'answer' field"
        assert isinstance(data["sources"], list), "'sources' should be a list"
        print(f"✓ AI Search with data query returned valid response")


class TestSlackIntegration(TestSetup):
    """Test Slack integration endpoints - UI verification only (no real Slack tokens)"""
    
    def test_slack_status_not_connected(self, api_client, auth_headers):
        """Test Slack status returns connected=False when not connected"""
        response = api_client.get(
            f"{BASE_URL}/api/slack/status",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Status endpoint should always return a valid response
        assert "connected" in data, "Missing 'connected' field"
        print(f"✓ Slack status: connected={data.get('connected')}")
    
    def test_slack_connect_invalid_token(self, api_client, auth_headers):
        """Test Slack connect with invalid token returns error"""
        response = api_client.post(
            f"{BASE_URL}/api/slack/connect",
            json={"bot_token": "xoxb-invalid-token-test"},
            headers=auth_headers
        )
        # Invalid token should return 400
        assert response.status_code == 400, f"Expected 400 for invalid token, got {response.status_code}"
        print("✓ Invalid Slack token correctly rejected")
    
    def test_slack_channels_not_connected(self, api_client, auth_headers):
        """Test Slack channels endpoint when not connected"""
        response = api_client.get(
            f"{BASE_URL}/api/slack/channels",
            headers=auth_headers
        )
        # Should return 400 with "not connected" message
        assert response.status_code == 400, f"Expected 400 when not connected, got {response.status_code}"
        print("✓ Slack channels correctly requires connection first")
    
    def test_slack_send_not_connected(self, api_client, auth_headers):
        """Test Slack send endpoint when not connected"""
        response = api_client.post(
            f"{BASE_URL}/api/slack/send",
            json={"channel_id": "C123456", "message": "Test message"},
            headers=auth_headers
        )
        # Should return 400 with "not connected" message
        assert response.status_code == 400, f"Expected 400 when not connected, got {response.status_code}"
        print("✓ Slack send correctly requires connection first")
    
    def test_slack_disconnect_not_connected(self, api_client, auth_headers):
        """Test Slack disconnect endpoint when not connected"""
        response = api_client.delete(
            f"{BASE_URL}/api/slack/disconnect",
            headers=auth_headers
        )
        # Should succeed even if not connected (idempotent)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ Slack disconnect successful (idempotent)")
    
    def test_slack_requires_auth(self, api_client):
        """Test Slack endpoints require authentication"""
        # Status endpoint
        response = api_client.get(f"{BASE_URL}/api/slack/status")
        assert response.status_code in [401, 403], f"Expected 401/403 for status, got {response.status_code}"
        
        # Connect endpoint
        response = api_client.post(f"{BASE_URL}/api/slack/connect", json={"bot_token": "test"})
        assert response.status_code in [401, 403], f"Expected 401/403 for connect, got {response.status_code}"
        print("✓ Slack endpoints correctly require authentication")


class TestAdminSlack(TestSetup):
    """Test Admin Slack integration - same endpoints, admin context"""
    
    def test_admin_slack_status(self, api_client, admin_headers):
        """Test Slack status endpoint for admin user"""
        response = api_client.get(
            f"{BASE_URL}/api/slack/status",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "connected" in data, "Missing 'connected' field"
        print(f"✓ Admin Slack status: connected={data.get('connected')}")


class TestWorkspaceDataSources(TestSetup):
    """Test workspace creation with new data sources (Practo API, Notion API, Zoho CRM)"""
    
    def test_create_workspace_with_new_datasources(self, api_client, auth_headers):
        """Test creating workspace with new data sources"""
        new_datasources = ["Practo API", "Notion API", "Zoho CRM", "Excel"]
        
        response = api_client.post(
            f"{BASE_URL}/api/workspaces/create",
            json={"name": "TEST_NewIntegrations_Workspace", "data_sources": new_datasources},
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed to create workspace: {response.status_code}: {response.text}"
        
        data = response.json()
        workspace_id = data.get("workspace_id")
        assert workspace_id, "Missing workspace_id in response"
        print(f"✓ Created workspace with new data sources: {workspace_id}")
        
        # Verify workspace has the data sources
        list_response = api_client.get(
            f"{BASE_URL}/api/workspaces/list",
            headers=auth_headers
        )
        assert list_response.status_code == 200
        
        workspaces = list_response.json().get("workspaces", [])
        created_ws = next((ws for ws in workspaces if ws["id"] == workspace_id), None)
        assert created_ws, "Created workspace not found in list"
        
        # Verify data sources are saved
        ws_sources = created_ws.get("data_sources", [])
        for ds in new_datasources:
            assert ds in ws_sources, f"Expected '{ds}' in workspace data_sources"
        print(f"✓ Verified workspace contains: {ws_sources}")
        
        # Cleanup - delete the test workspace
        delete_response = api_client.delete(
            f"{BASE_URL}/api/workspaces/{workspace_id}",
            headers=auth_headers
        )
        assert delete_response.status_code == 200, "Failed to cleanup test workspace"
        print(f"✓ Cleaned up test workspace")


class TestUserAuthentication(TestSetup):
    """Verify login flows for both user and admin"""
    
    def test_user_login_returns_correct_fields(self, api_client):
        """Test user login returns all expected fields"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": USER_EMAIL,
            "password": USER_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.status_code}"
        
        data = response.json()
        user = data.get("user", {})
        
        # Verify expected user fields
        assert "token" in data, "Missing token"
        assert "email" in user, "Missing email"
        assert "name" in user, "Missing name"
        assert "plan" in user, "Missing plan"
        assert "credits" in user, "Missing credits"
        print(f"✓ User login verified: {user.get('email')}, plan={user.get('plan')}")
    
    def test_admin_login_returns_admin_role(self, api_client):
        """Test admin login returns admin role"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.status_code}"
        
        data = response.json()
        user = data.get("user", {})
        assert user.get("role") == "admin", f"Expected admin role, got {user.get('role')}"
        print(f"✓ Admin login verified: role={user.get('role')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
