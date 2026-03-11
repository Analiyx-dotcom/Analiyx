"""
Comprehensive API Tests for Analiyx Analytics Platform
Tests: Auth, Admin, User Management, Data Sources
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@papermap.com"
ADMIN_PASSWORD = "admin123"
TEST_USER_EMAIL = "testuser@analiyx.com"
TEST_USER_PASSWORD = "test1234"


class TestHealthCheck:
    """Basic API health checks"""
    
    def test_api_root(self):
        """Test API root endpoint"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"✓ API root returns: {data['message']}")


class TestAuthLogin:
    """Authentication login tests"""
    
    def test_admin_login_success(self):
        """Test admin login returns token and user with role"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        
        data = response.json()
        assert "token" in data, "Token not in response"
        assert "user" in data, "User not in response"
        assert data["user"]["role"] == "admin", f"Expected admin role, got: {data['user']['role']}"
        assert data["user"]["email"] == ADMIN_EMAIL
        print(f"✓ Admin login successful - Role: {data['user']['role']}")
    
    def test_user_login_success(self):
        """Test regular user login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        assert response.status_code == 200, f"User login failed: {response.text}"
        
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["role"] == "user", f"Expected user role, got: {data['user']['role']}"
        print(f"✓ User login successful - Role: {data['user']['role']}")
    
    def test_login_invalid_credentials(self):
        """Test login with wrong credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "wrong@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        print("✓ Invalid credentials correctly rejected")


class TestAuthRegister:
    """User registration tests"""
    
    def test_user_registration(self):
        """Test new user signup creates account with user role"""
        unique_email = f"test_{uuid.uuid4().hex[:8]}@analiyx.com"
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "name": "Test New User",
            "email": unique_email,
            "password": "testpassword123"
        })
        assert response.status_code == 200, f"Registration failed: {response.text}"
        
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == unique_email
        assert data["user"]["role"] == "user", "New users should have 'user' role"
        assert data["user"]["plan"] == "Starter" or data["user"]["plan"] in ["Hobby", "Starter", "Free"]
        print(f"✓ User registration successful - Email: {unique_email}")
    
    def test_duplicate_email_registration(self):
        """Test that duplicate email registration fails"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "name": "Duplicate User",
            "email": ADMIN_EMAIL,  # Already exists
            "password": "testpassword123"
        })
        assert response.status_code == 400
        print("✓ Duplicate email correctly rejected")


class TestAuthMe:
    """Test /auth/me endpoint"""
    
    def test_get_current_user(self):
        """Test getting current authenticated user"""
        # First login
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        assert login_response.status_code == 200
        token = login_response.json()["token"]
        
        # Get current user
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["email"] == TEST_USER_EMAIL
        assert "plan" in data
        assert "credits" in data
        assert "status" in data
        print(f"✓ /auth/me returns user: {data['name']}")
    
    def test_get_current_user_no_auth(self):
        """Test /auth/me without token"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code in [401, 403]
        print("✓ /auth/me correctly requires authentication")


class TestAdminStats:
    """Admin dashboard stats tests"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        return response.json()["token"]
    
    def test_admin_stats(self, admin_token):
        """Test /api/admin/stats returns real stats"""
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Stats failed: {response.text}"
        
        data = response.json()
        assert "total_users" in data
        assert "active_subscriptions" in data
        assert "monthly_revenue" in data
        assert "data_sources" in data
        
        assert isinstance(data["total_users"], int)
        assert data["total_users"] >= 0
        print(f"✓ Admin stats - Users: {data['total_users']}, Subscriptions: {data['active_subscriptions']}")
    
    def test_admin_stats_no_auth(self):
        """Test admin stats without auth"""
        response = requests.get(f"{BASE_URL}/api/admin/stats")
        assert response.status_code in [401, 403]
        print("✓ Admin stats correctly requires auth")
    
    def test_admin_stats_user_forbidden(self):
        """Test regular user cannot access admin stats"""
        # Login as regular user
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        if login_response.status_code != 200:
            pytest.skip("User login failed")
        token = login_response.json()["token"]
        
        # Try to access admin stats
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ Regular user correctly forbidden from admin stats")


class TestAdminUserManagement:
    """Admin user management endpoint tests"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        return response.json()["token"]
    
    def test_get_all_users_details(self, admin_token):
        """Test /api/admin/manage/users/details returns user list with roles"""
        response = requests.get(
            f"{BASE_URL}/api/admin/manage/users/details",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert "users" in data
        assert "total" in data
        assert isinstance(data["users"], list)
        
        if len(data["users"]) > 0:
            user = data["users"][0]
            assert "id" in user
            assert "name" in user
            assert "email" in user
            assert "role" in user
            assert "status" in user
            assert "credits" in user
            print(f"✓ User details returned {data['total']} users")
        else:
            print("✓ User details endpoint works but no users found")
    
    def test_admin_users_paginated(self, admin_token):
        """Test /api/admin/users paginated endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/admin/users?page=1&limit=5",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "users" in data
        assert "total" in data
        assert "page" in data
        print(f"✓ Paginated users - Total: {data['total']}, Page: {data['page']}")


class TestAdminUserActions:
    """Test admin user action buttons (Disable, Extend Trial, Credits)"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        return response.json()["token"]
    
    @pytest.fixture
    def test_user_id(self, admin_token):
        """Get test user ID"""
        response = requests.get(
            f"{BASE_URL}/api/admin/manage/users/details",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        if response.status_code != 200:
            pytest.skip("Could not get users")
        
        users = response.json()["users"]
        # Find non-admin user
        for user in users:
            if user["email"] != ADMIN_EMAIL and user["role"] != "admin":
                return user["id"]
        pytest.skip("No test user found")
    
    def test_update_user_status(self, admin_token, test_user_id):
        """Test Disable/Enable user functionality"""
        # Disable user
        response = requests.put(
            f"{BASE_URL}/api/admin/manage/users/{test_user_id}/status",
            json={"status": "inactive"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Disable failed: {response.text}"
        
        data = response.json()
        assert data["success"] == True
        print(f"✓ User disabled successfully")
        
        # Re-enable user
        response = requests.put(
            f"{BASE_URL}/api/admin/manage/users/{test_user_id}/status",
            json={"status": "active"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        print(f"✓ User re-enabled successfully")
    
    def test_extend_trial(self, admin_token, test_user_id):
        """Test +7 Days trial extension"""
        response = requests.post(
            f"{BASE_URL}/api/admin/manage/users/{test_user_id}/extend-trial",
            json={"days": 7},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Extend trial failed: {response.text}"
        
        data = response.json()
        assert data["success"] == True
        assert "new_end_date" in data
        print(f"✓ Trial extended - New end date: {data['new_end_date']}")
    
    def test_add_credits(self, admin_token, test_user_id):
        """Test + Credits functionality"""
        response = requests.put(
            f"{BASE_URL}/api/admin/manage/users/{test_user_id}/credits",
            json={"credits": 100, "action": "add"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Add credits failed: {response.text}"
        
        data = response.json()
        assert data["success"] == True
        assert "new_credits" in data
        print(f"✓ Credits added - New balance: {data['new_credits']}")


class TestAdminCharts:
    """Test admin chart data endpoints"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        return response.json()["token"]
    
    def test_user_growth_chart(self, admin_token):
        """Test user growth chart data"""
        response = requests.get(
            f"{BASE_URL}/api/admin/charts/user-growth",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data
        print(f"✓ User growth chart - {len(data['data'])} data points")
    
    def test_revenue_chart(self, admin_token):
        """Test revenue chart data"""
        response = requests.get(
            f"{BASE_URL}/api/admin/charts/revenue",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data
        print(f"✓ Revenue chart - {len(data['data'])} data points")


class TestDataSourceUpload:
    """Test file upload API"""
    
    @pytest.fixture
    def user_token(self):
        """Get regular user token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("User login failed")
        return response.json()["token"]
    
    def test_upload_csv_file(self, user_token):
        """Test CSV file upload"""
        # Create a simple CSV content
        csv_content = "name,value,category\nItem1,100,A\nItem2,200,B\nItem3,150,A"
        
        files = {
            'file': ('test_data.csv', csv_content, 'text/csv')
        }
        
        response = requests.post(
            f"{BASE_URL}/api/data-sources/upload-file",
            files=files,
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200, f"Upload failed: {response.text}"
        
        data = response.json()
        assert data["success"] == True
        assert "file_id" in data
        assert "analytics" in data
        assert data["analytics"]["total_rows"] == 3
        assert data["analytics"]["total_columns"] == 3
        print(f"✓ CSV uploaded - {data['analytics']['total_rows']} rows, {data['analytics']['total_columns']} columns")
    
    def test_get_uploaded_files(self, user_token):
        """Test get uploaded files list"""
        response = requests.get(
            f"{BASE_URL}/api/data-sources/uploaded-files",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "files" in data
        print(f"✓ Uploaded files list - {len(data['files'])} files")
    
    def test_upload_invalid_file_type(self, user_token):
        """Test upload rejects invalid file types"""
        files = {
            'file': ('test.txt', 'This is not a CSV', 'text/plain')
        }
        
        response = requests.post(
            f"{BASE_URL}/api/data-sources/upload-file",
            files=files,
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 400
        print("✓ Invalid file type correctly rejected")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
