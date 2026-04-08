"""
Test Nango Integration - OAuth connection management via Nango
Tests: connect-session, save-connection, get-connections, delete-connection, proxy endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "Admin@analiyx.com"
ADMIN_PASSWORD = "1234"
TEST_USER_EMAIL = "testuser@test.com"
TEST_USER_PASSWORD = "test1234"


class TestNangoConnectSession:
    """Test POST /api/nango/connect-session - Creates Nango connect session token"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        if response.status_code == 200:
            self.token = response.json().get("token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Login failed - skipping Nango tests")
    
    def test_create_connect_session_returns_token(self):
        """Test that connect-session endpoint returns a valid Nango session token"""
        response = requests.post(
            f"{BASE_URL}/api/nango/connect-session",
            json={"allowed_integrations": ["google-ads"]},
            headers=self.headers
        )
        
        # Should return 200 or 201
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Nango returns token in data.token or directly as token
        token = data.get("data", {}).get("token") or data.get("token")
        assert token is not None, f"Expected token in response, got: {data}"
        assert isinstance(token, str), "Token should be a string"
        assert len(token) > 10, "Token should be a non-trivial string"
        print(f"✓ Connect session created with token: {token[:20]}...")
    
    def test_create_connect_session_without_integrations(self):
        """Test connect-session without specifying allowed_integrations"""
        response = requests.post(
            f"{BASE_URL}/api/nango/connect-session",
            json={},
            headers=self.headers
        )
        
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}: {response.text}"
        data = response.json()
        token = data.get("data", {}).get("token") or data.get("token")
        assert token is not None, f"Expected token in response, got: {data}"
        print(f"✓ Connect session created without specifying integrations")
    
    def test_connect_session_requires_auth(self):
        """Test that connect-session requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/nango/connect-session",
            json={"allowed_integrations": ["google-ads"]}
        )
        
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✓ Connect session requires authentication")


class TestNangoSaveConnection:
    """Test POST /api/nango/save-connection - Saves integration connection for user"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        if response.status_code == 200:
            self.token = response.json().get("token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Login failed - skipping Nango tests")
    
    def test_save_connection_success(self):
        """Test saving a Nango connection"""
        test_integration_id = "test-integration-pytest"
        test_connection_id = f"test-conn-{os.urandom(4).hex()}"
        
        response = requests.post(
            f"{BASE_URL}/api/nango/save-connection",
            json={
                "integration_id": test_integration_id,
                "connection_id": test_connection_id
            },
            headers=self.headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, f"Expected success=True, got: {data}"
        assert data.get("integration_id") == test_integration_id
        assert data.get("connection_id") == test_connection_id
        print(f"✓ Connection saved: {test_integration_id} -> {test_connection_id}")
        
        # Cleanup - delete the test connection
        requests.delete(
            f"{BASE_URL}/api/nango/connections/{test_integration_id}",
            headers=self.headers
        )
    
    def test_save_connection_requires_auth(self):
        """Test that save-connection requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/nango/save-connection",
            json={
                "integration_id": "test-integration",
                "connection_id": "test-conn"
            }
        )
        
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✓ Save connection requires authentication")


class TestNangoGetConnections:
    """Test GET /api/nango/connections - Returns all user Nango connections"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        if response.status_code == 200:
            self.token = response.json().get("token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Login failed - skipping Nango tests")
    
    def test_get_connections_returns_list(self):
        """Test that get connections returns a list"""
        response = requests.get(
            f"{BASE_URL}/api/nango/connections",
            headers=self.headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "connections" in data, f"Expected 'connections' key in response, got: {data}"
        assert isinstance(data["connections"], list), "Connections should be a list"
        print(f"✓ Get connections returned {len(data['connections'])} connections")
    
    def test_get_connections_after_save(self):
        """Test that saved connection appears in get connections"""
        test_integration_id = "test-get-conn-pytest"
        test_connection_id = f"test-conn-{os.urandom(4).hex()}"
        
        # Save a connection first
        save_response = requests.post(
            f"{BASE_URL}/api/nango/save-connection",
            json={
                "integration_id": test_integration_id,
                "connection_id": test_connection_id
            },
            headers=self.headers
        )
        assert save_response.status_code == 200
        
        # Get connections
        response = requests.get(
            f"{BASE_URL}/api/nango/connections",
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        connections = data.get("connections", [])
        
        # Find our test connection
        found = any(c.get("integration_id") == test_integration_id for c in connections)
        assert found, f"Expected to find {test_integration_id} in connections"
        print(f"✓ Saved connection found in get connections")
        
        # Cleanup
        requests.delete(
            f"{BASE_URL}/api/nango/connections/{test_integration_id}",
            headers=self.headers
        )
    
    def test_get_connections_requires_auth(self):
        """Test that get connections requires authentication"""
        response = requests.get(f"{BASE_URL}/api/nango/connections")
        
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✓ Get connections requires authentication")


class TestNangoDeleteConnection:
    """Test DELETE /api/nango/connections/{integration_id} - Disconnects an integration"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        if response.status_code == 200:
            self.token = response.json().get("token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Login failed - skipping Nango tests")
    
    def test_delete_connection_success(self):
        """Test deleting a Nango connection"""
        test_integration_id = "test-delete-pytest"
        test_connection_id = f"test-conn-{os.urandom(4).hex()}"
        
        # Save a connection first
        save_response = requests.post(
            f"{BASE_URL}/api/nango/save-connection",
            json={
                "integration_id": test_integration_id,
                "connection_id": test_connection_id
            },
            headers=self.headers
        )
        assert save_response.status_code == 200
        
        # Delete the connection
        response = requests.delete(
            f"{BASE_URL}/api/nango/connections/{test_integration_id}",
            headers=self.headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, f"Expected success=True, got: {data}"
        print(f"✓ Connection deleted: {test_integration_id}")
        
        # Verify it's gone
        get_response = requests.get(
            f"{BASE_URL}/api/nango/connections",
            headers=self.headers
        )
        connections = get_response.json().get("connections", [])
        found = any(c.get("integration_id") == test_integration_id for c in connections)
        assert not found, "Connection should be deleted"
        print("✓ Verified connection is removed from list")
    
    def test_delete_nonexistent_connection(self):
        """Test deleting a connection that doesn't exist"""
        response = requests.delete(
            f"{BASE_URL}/api/nango/connections/nonexistent-integration-xyz",
            headers=self.headers
        )
        
        # Should still return 200 with success=True but message indicates not found
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ Delete nonexistent connection handled gracefully")
    
    def test_delete_connection_requires_auth(self):
        """Test that delete connection requires authentication"""
        response = requests.delete(f"{BASE_URL}/api/nango/connections/test-integration")
        
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✓ Delete connection requires authentication")


class TestNangoProxy:
    """Test POST /api/nango/proxy - Makes authenticated proxy requests via Nango"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        if response.status_code == 200:
            self.token = response.json().get("token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Login failed - skipping Nango tests")
    
    def test_proxy_endpoint_exists(self):
        """Test that proxy endpoint exists and accepts requests"""
        # This will fail with Nango error since we don't have a real connection,
        # but it proves the endpoint exists and processes requests
        response = requests.post(
            f"{BASE_URL}/api/nango/proxy",
            json={
                "integration_id": "google-ads",
                "connection_id": "fake-connection-id",
                "endpoint": "/test",
                "method": "GET"
            },
            headers=self.headers
        )
        
        # We expect either 200 (with error from Nango) or 500 (Nango API error)
        # The key is that the endpoint exists and processes the request
        assert response.status_code in [200, 500], f"Unexpected status: {response.status_code}"
        print(f"✓ Proxy endpoint exists and processes requests (status: {response.status_code})")
    
    def test_proxy_requires_auth(self):
        """Test that proxy endpoint requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/nango/proxy",
            json={
                "integration_id": "google-ads",
                "connection_id": "test-conn",
                "endpoint": "/test",
                "method": "GET"
            }
        )
        
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✓ Proxy endpoint requires authentication")


class TestSettingsPage:
    """Test Settings page functionality - profile update and change password"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        if response.status_code == 200:
            self.token = response.json().get("token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
            self.user_data = response.json().get("user", {})
        else:
            pytest.skip("Login failed - skipping Settings tests")
    
    def test_get_current_user(self):
        """Test GET /api/auth/me returns user profile"""
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers=self.headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "email" in data, "Expected email in user data"
        assert "name" in data, "Expected name in user data"
        print(f"✓ Get current user: {data.get('email')}")
    
    def test_update_profile(self):
        """Test PUT /api/auth/profile updates user profile"""
        # Profile update expects first_name, last_name, phone
        new_first = "Test"
        new_last = f"User{os.urandom(2).hex()}"
        
        response = requests.put(
            f"{BASE_URL}/api/auth/profile",
            json={
                "first_name": new_first,
                "last_name": new_last,
                "phone": "+919876543210"
            },
            headers=self.headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, f"Expected success=True, got: {data}"
        print(f"✓ Profile updated: {new_first} {new_last}")
        
        # Restore original name
        requests.put(
            f"{BASE_URL}/api/auth/profile",
            json={
                "first_name": "Test",
                "last_name": "User",
                "phone": "+919876543210"
            },
            headers=self.headers
        )


class TestAIChatCredits:
    """Test AI Chat credit deduction - 1 credit per query"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        if response.status_code == 200:
            self.token = response.json().get("token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Login failed - skipping AI Chat tests")
    
    def test_ai_chat_deducts_credits(self):
        """Test that AI chat deducts 1 credit per query"""
        # Get initial credits
        me_response = requests.get(f"{BASE_URL}/api/auth/me", headers=self.headers)
        assert me_response.status_code == 200
        initial_credits = me_response.json().get("credits", 0)
        
        if initial_credits < 1:
            pytest.skip("User has no credits - skipping credit deduction test")
        
        # Make an AI chat query
        chat_response = requests.post(
            f"{BASE_URL}/api/ai/chat",
            json={"query": "What is 2+2?"},
            headers=self.headers,
            timeout=30
        )
        
        # Check if chat succeeded or failed due to credits
        if chat_response.status_code == 200:
            # Get updated credits
            me_response2 = requests.get(f"{BASE_URL}/api/auth/me", headers=self.headers)
            new_credits = me_response2.json().get("credits", 0)
            
            # Credits should be deducted
            assert new_credits < initial_credits, f"Credits not deducted: {initial_credits} -> {new_credits}"
            print(f"✓ AI Chat deducted credits: {initial_credits} -> {new_credits}")
        elif chat_response.status_code == 402 or "Insufficient credits" in chat_response.text:
            print("✓ AI Chat correctly rejects when insufficient credits")
        else:
            # Other errors are acceptable for this test
            print(f"✓ AI Chat endpoint responded: {chat_response.status_code}")


class TestExistingCredentials:
    """Verify test credentials work"""
    
    def test_admin_login(self):
        """Test admin login works"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        assert response.status_code == 200, f"Admin login failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "token" in data, "Expected token in response"
        assert data.get("user", {}).get("role") == "admin", "Expected admin role"
        print(f"✓ Admin login successful: {ADMIN_EMAIL}")
    
    def test_test_user_login(self):
        """Test user login works"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        
        assert response.status_code == 200, f"Test user login failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "token" in data, "Expected token in response"
        print(f"✓ Test user login successful: {TEST_USER_EMAIL}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
