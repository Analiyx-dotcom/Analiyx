"""
Test P0 Fixes for Analiyx Platform - Iteration 4
Tests:
1. Cashfree payment gateway - /api/payments/create-order endpoint
2. Workspace deletion - DELETE /api/workspaces/{id}
3. Admin dashboard tabs with data
"""
import pytest
import requests
import os

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


class TestCashfreePayment(TestSetup):
    """Test Cashfree payment gateway create-order endpoint"""
    
    def test_create_order_starter_plan(self, api_client, auth_headers):
        """Test payment order creation for Starter plan"""
        response = api_client.post(
            f"{BASE_URL}/api/payments/create-order",
            json={"plan": "Starter", "return_url": "https://ai-analytics-engine-4.preview.emergentagent.com"},
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Verify response structure
        assert data.get("success") == True, "Expected success=True"
        assert "order_id" in data, "Missing order_id in response"
        assert "cf_order_id" in data, "Missing cf_order_id in response"
        assert "payment_session_id" in data, "Missing payment_session_id in response"
        assert "order_amount" in data, "Missing order_amount in response"
        assert data["order_currency"] == "INR", "Expected currency to be INR"
        
        # Verify payment_session_id is not empty
        assert len(data["payment_session_id"]) > 10, "payment_session_id should be a valid string"
        print(f"✓ Starter plan order created: order_id={data['order_id']}, payment_session_id={data['payment_session_id'][:20]}...")
    
    def test_create_order_business_pro_plan(self, api_client, auth_headers):
        """Test payment order creation for Business Pro plan"""
        response = api_client.post(
            f"{BASE_URL}/api/payments/create-order",
            json={"plan": "Business Pro", "return_url": "https://ai-analytics-engine-4.preview.emergentagent.com"},
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True
        assert "payment_session_id" in data
        assert len(data["payment_session_id"]) > 10
        print(f"✓ Business Pro order created: order_id={data['order_id']}")
    
    def test_create_order_invalid_plan(self, api_client, auth_headers):
        """Test payment order creation with invalid plan returns 400"""
        response = api_client.post(
            f"{BASE_URL}/api/payments/create-order",
            json={"plan": "InvalidPlan", "return_url": "https://ai-analytics-engine-4.preview.emergentagent.com"},
            headers=auth_headers
        )
        assert response.status_code == 400, f"Expected 400 for invalid plan, got {response.status_code}"
        print("✓ Invalid plan correctly rejected with 400")
    
    def test_create_order_requires_auth(self, api_client):
        """Test payment order creation requires authentication"""
        response = api_client.post(
            f"{BASE_URL}/api/payments/create-order",
            json={"plan": "Starter"}
        )
        assert response.status_code == 401 or response.status_code == 403, f"Expected 401/403, got {response.status_code}"
        print("✓ Unauthenticated request correctly rejected")


class TestWorkspaceDeletion(TestSetup):
    """Test workspace deletion endpoint"""
    
    def test_create_and_delete_workspace(self, api_client, auth_headers):
        """Test full workspace lifecycle: create then delete"""
        # First create a workspace
        create_response = api_client.post(
            f"{BASE_URL}/api/workspaces/create",
            json={"name": "TEST_DeleteTest_Workspace", "data_sources": ["Excel", "CSV"]},
            headers=auth_headers
        )
        assert create_response.status_code == 200, f"Failed to create workspace: {create_response.status_code}"
        
        workspace_id = create_response.json().get("workspace_id")
        assert workspace_id, "Missing workspace_id in create response"
        print(f"✓ Created test workspace: {workspace_id}")
        
        # Now delete it
        delete_response = api_client.delete(
            f"{BASE_URL}/api/workspaces/{workspace_id}",
            headers=auth_headers
        )
        assert delete_response.status_code == 200, f"Expected 200, got {delete_response.status_code}: {delete_response.text}"
        
        data = delete_response.json()
        assert data.get("success") == True, "Expected success=True in delete response"
        print(f"✓ Workspace deleted successfully")
        
        # Verify workspace no longer exists by listing
        list_response = api_client.get(
            f"{BASE_URL}/api/workspaces/list",
            headers=auth_headers
        )
        workspaces = list_response.json().get("workspaces", [])
        ws_ids = [ws["id"] for ws in workspaces]
        assert workspace_id not in ws_ids, "Deleted workspace should not appear in list"
        print(f"✓ Verified workspace removed from list")
    
    def test_delete_nonexistent_workspace(self, api_client, auth_headers):
        """Test deleting non-existent workspace returns 404"""
        fake_id = "507f1f77bcf86cd799439011"  # Valid ObjectId format but doesn't exist
        response = api_client.delete(
            f"{BASE_URL}/api/workspaces/{fake_id}",
            headers=auth_headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Non-existent workspace correctly returns 404")
    
    def test_delete_requires_auth(self, api_client):
        """Test workspace deletion requires authentication"""
        fake_id = "507f1f77bcf86cd799439011"
        response = api_client.delete(f"{BASE_URL}/api/workspaces/{fake_id}")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ Unauthenticated delete correctly rejected")


class TestAdminDashboard(TestSetup):
    """Test Admin Dashboard API endpoints for all tabs"""
    
    def test_admin_stats_dashboard_tab(self, api_client, admin_headers):
        """Test admin stats endpoint (Dashboard tab)"""
        response = api_client.get(
            f"{BASE_URL}/api/admin/stats",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # Verify expected fields
        assert "total_users" in data, "Missing total_users"
        assert "active_subscriptions" in data, "Missing active_subscriptions"
        assert "monthly_revenue" in data, "Missing monthly_revenue"
        assert "data_sources" in data, "Missing data_sources"
        print(f"✓ Admin stats: {data['total_users']} users, ₹{data['monthly_revenue']} revenue")
    
    def test_admin_users_tab(self, api_client, admin_headers):
        """Test admin users list endpoint (Users tab)"""
        response = api_client.get(
            f"{BASE_URL}/api/admin/manage/users/details",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "users" in data, "Missing users array"
        assert isinstance(data["users"], list), "users should be a list"
        
        # Verify user data structure
        if len(data["users"]) > 0:
            user = data["users"][0]
            assert "id" in user or "_id" in user, "User missing id"
            assert "email" in user, "User missing email"
            assert "plan" in user, "User missing plan"
        print(f"✓ Admin users list: {len(data['users'])} users returned")
    
    def test_admin_revenue_chart(self, api_client, admin_headers):
        """Test admin revenue chart endpoint (Revenue tab)"""
        response = api_client.get(
            f"{BASE_URL}/api/admin/charts/revenue",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "data" in data, "Missing data array"
        print(f"✓ Admin revenue chart data retrieved")
    
    def test_admin_user_growth_chart(self, api_client, admin_headers):
        """Test admin user growth chart endpoint"""
        response = api_client.get(
            f"{BASE_URL}/api/admin/charts/user-growth",
            headers=admin_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "data" in data, "Missing data array"
        print(f"✓ Admin user growth chart data retrieved")


class TestUserLogin(TestSetup):
    """Test user login functionality"""
    
    def test_user_login_success(self, api_client):
        """Test user login returns token and user info"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": USER_EMAIL,
            "password": USER_PASSWORD
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "token" in data, "Missing token in response"
        assert "user" in data, "Missing user in response"
        assert data["user"]["email"] == USER_EMAIL, f"Expected email {USER_EMAIL}"
        assert data["user"].get("role") == "user", "Expected role=user"
        print(f"✓ User login successful: {data['user']['email']}")
    
    def test_admin_login_success(self, api_client):
        """Test admin login returns token with admin role"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "token" in data, "Missing token"
        assert data["user"].get("role") == "admin", "Expected role=admin"
        print(f"✓ Admin login successful: role={data['user']['role']}")


class TestWorkspaceList(TestSetup):
    """Test workspace listing"""
    
    def test_list_workspaces(self, api_client, auth_headers):
        """Test listing user workspaces"""
        response = api_client.get(
            f"{BASE_URL}/api/workspaces/list",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "workspaces" in data, "Missing workspaces array"
        print(f"✓ Workspaces list: {len(data['workspaces'])} workspaces")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
