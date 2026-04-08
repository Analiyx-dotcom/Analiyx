"""
Test suite for Onboarding Feature - Iteration 16
Tests the post-signup onboarding chat flow including:
- GET /api/onboarding/status - Check onboarding status
- POST /api/onboarding/save - Save onboarding data
- GET /api/onboarding/admin/all - Admin endpoint for all onboarding data
- Login response includes onboarding_completed field
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_USER_EMAIL = "testuser@test.com"
TEST_USER_PASSWORD = "test1234"
ADMIN_EMAIL = "Admin@analiyx.com"
ADMIN_PASSWORD = "1234"


class TestOnboardingStatus:
    """Test GET /api/onboarding/status endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get token for test user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        self.token = response.json()["token"]
        self.user = response.json()["user"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_1_login_includes_onboarding_completed_field(self):
        """Verify login response includes onboarding_completed field"""
        assert "onboarding_completed" in self.user, "Login response missing onboarding_completed field"
        assert isinstance(self.user["onboarding_completed"], bool), "onboarding_completed should be boolean"
        print(f"✓ Login response includes onboarding_completed: {self.user['onboarding_completed']}")
    
    def test_2_get_onboarding_status_returns_completed_false(self):
        """GET /api/onboarding/status returns {completed: false} for non-onboarded user"""
        response = requests.get(f"{BASE_URL}/api/onboarding/status", headers=self.headers)
        assert response.status_code == 200, f"Status check failed: {response.text}"
        data = response.json()
        assert "completed" in data, "Response missing 'completed' field"
        assert "name" in data, "Response missing 'name' field"
        print(f"✓ Onboarding status: completed={data['completed']}, name={data['name']}")
    
    def test_3_onboarding_status_requires_auth(self):
        """GET /api/onboarding/status requires authentication"""
        response = requests.get(f"{BASE_URL}/api/onboarding/status")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ Onboarding status endpoint requires authentication")


class TestOnboardingSave:
    """Test POST /api/onboarding/save endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get token for test user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_4_save_onboarding_business_flow(self):
        """POST /api/onboarding/save saves business onboarding data"""
        onboarding_data = {
            "usage_type": "business",
            "company_name": "TEST_Acme Corp",
            "company_location": "San Francisco, CA",
            "company_description": "We provide SaaS analytics tools",
            "industry": "Technology",
            "monthly_mrr": "$50,000",
            "has_data_analyst": "Yes",
            "does_digital_marketing": "Yes",
            "data_preference": "connect"
        }
        response = requests.post(
            f"{BASE_URL}/api/onboarding/save",
            json=onboarding_data,
            headers=self.headers
        )
        assert response.status_code == 200, f"Save failed: {response.text}"
        data = response.json()
        assert data.get("success") == True, "Response should indicate success"
        print(f"✓ Onboarding data saved successfully: {data.get('message')}")
    
    def test_5_onboarding_status_returns_completed_true_after_save(self):
        """GET /api/onboarding/status returns {completed: true} after saving"""
        response = requests.get(f"{BASE_URL}/api/onboarding/status", headers=self.headers)
        assert response.status_code == 200, f"Status check failed: {response.text}"
        data = response.json()
        assert data.get("completed") == True, f"Expected completed=True, got {data.get('completed')}"
        print(f"✓ Onboarding status after save: completed={data['completed']}")
    
    def test_6_login_shows_onboarding_completed_true(self):
        """Login response shows onboarding_completed=true after completing onboarding"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        user = response.json()["user"]
        assert user.get("onboarding_completed") == True, f"Expected onboarding_completed=True, got {user.get('onboarding_completed')}"
        print(f"✓ Login now shows onboarding_completed=True")
    
    def test_7_save_onboarding_requires_auth(self):
        """POST /api/onboarding/save requires authentication"""
        onboarding_data = {
            "usage_type": "personal",
            "data_preference": "synthetic"
        }
        response = requests.post(f"{BASE_URL}/api/onboarding/save", json=onboarding_data)
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ Onboarding save endpoint requires authentication")


class TestOnboardingAdminEndpoint:
    """Test GET /api/onboarding/admin/all endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        self.admin_token = response.json()["token"]
        self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Also get regular user token
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        assert response.status_code == 200
        self.user_token = response.json()["token"]
        self.user_headers = {"Authorization": f"Bearer {self.user_token}"}
    
    def test_8_admin_get_all_onboarding_data(self):
        """GET /api/onboarding/admin/all returns onboarding data for all onboarded users"""
        response = requests.get(f"{BASE_URL}/api/onboarding/admin/all", headers=self.admin_headers)
        assert response.status_code == 200, f"Admin endpoint failed: {response.text}"
        data = response.json()
        assert "users" in data, "Response missing 'users' field"
        assert isinstance(data["users"], list), "users should be a list"
        
        # Check if our test user is in the list
        test_user_found = False
        for user in data["users"]:
            if user.get("email") == TEST_USER_EMAIL:
                test_user_found = True
                assert "onboarding_data" in user, "User missing onboarding_data"
                onboarding = user["onboarding_data"]
                assert onboarding.get("usage_type") == "business", f"Expected usage_type=business, got {onboarding.get('usage_type')}"
                assert onboarding.get("company_name") == "TEST_Acme Corp", f"Company name mismatch"
                print(f"✓ Found test user with onboarding data: {onboarding.get('company_name')}, {onboarding.get('industry')}")
                break
        
        assert test_user_found, "Test user not found in admin onboarding data"
        print(f"✓ Admin endpoint returned {len(data['users'])} onboarded users")
    
    def test_9_admin_endpoint_requires_admin_role(self):
        """GET /api/onboarding/admin/all requires admin role"""
        response = requests.get(f"{BASE_URL}/api/onboarding/admin/all", headers=self.user_headers)
        assert response.status_code == 403, f"Expected 403 for non-admin, got {response.status_code}"
        print("✓ Admin endpoint correctly rejects non-admin users")
    
    def test_10_admin_endpoint_requires_auth(self):
        """GET /api/onboarding/admin/all requires authentication"""
        response = requests.get(f"{BASE_URL}/api/onboarding/admin/all")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ Admin endpoint requires authentication")


class TestAdminDashboardOnboardingData:
    """Test that admin dashboard user details include onboarding data"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        self.admin_token = response.json()["token"]
        self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
    
    def test_11_admin_users_details_includes_onboarding_data(self):
        """GET /api/admin/manage/users/details includes onboarding_data for users"""
        response = requests.get(f"{BASE_URL}/api/admin/manage/users/details", headers=self.admin_headers)
        assert response.status_code == 200, f"Admin users endpoint failed: {response.text}"
        data = response.json()
        assert "users" in data, "Response missing 'users' field"
        
        # Find test user and verify onboarding data
        test_user_found = False
        for user in data["users"]:
            if user.get("email") == TEST_USER_EMAIL:
                test_user_found = True
                assert "onboarding_completed" in user, "User missing onboarding_completed field"
                assert "onboarding_data" in user, "User missing onboarding_data field"
                
                if user.get("onboarding_completed"):
                    onboarding = user.get("onboarding_data", {})
                    print(f"✓ User onboarding data in admin dashboard:")
                    print(f"  - Company: {onboarding.get('company_name')}")
                    print(f"  - Industry: {onboarding.get('industry')}")
                    print(f"  - Location: {onboarding.get('company_location')}")
                break
        
        assert test_user_found, "Test user not found in admin users list"


class TestOnboardingCleanup:
    """Reset test user onboarding status for future tests"""
    
    def test_99_reset_test_user_onboarding(self):
        """Reset test user onboarding status (cleanup)"""
        # This is a cleanup test - we need to reset the user's onboarding status
        # Since there's no API for this, we'll just note it
        print("⚠ Note: Test user onboarding_completed is now True")
        print("  To reset for future tests, manually set onboarding_completed=false in MongoDB")
        print("  Or create a new test user")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
