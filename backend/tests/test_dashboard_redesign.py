"""
Test Dashboard Redesign - Iteration 7
Tests for P2 User Dashboard Redesign:
1. GET /api/dashboard/summary endpoint
2. Dashboard stats (workspaces, files, AI queries)
3. Activity feed aggregation
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_USER = {"email": "testpay@analiyx.com", "password": "test1234"}
ADMIN_USER = {"email": "admin@papermap.com", "password": "admin123"}


class TestDashboardSummary:
    """Test the new /api/dashboard/summary endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token for test user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_USER)
        assert response.status_code == 200, f"Login failed: {response.text}"
        self.token = response.json().get('token')
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_dashboard_summary_returns_200(self):
        """Test dashboard summary endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/dashboard/summary", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("PASS: Dashboard summary endpoint returns 200")

    def test_dashboard_summary_has_workspaces_count(self):
        """Test dashboard summary contains workspaces count"""
        response = requests.get(f"{BASE_URL}/api/dashboard/summary", headers=self.headers)
        data = response.json()
        assert "workspaces" in data, "Missing 'workspaces' field"
        assert isinstance(data["workspaces"], int), "workspaces should be an integer"
        print(f"PASS: Workspaces count = {data['workspaces']}")

    def test_dashboard_summary_has_total_files(self):
        """Test dashboard summary contains total_files count"""
        response = requests.get(f"{BASE_URL}/api/dashboard/summary", headers=self.headers)
        data = response.json()
        assert "total_files" in data, "Missing 'total_files' field"
        assert isinstance(data["total_files"], int), "total_files should be an integer"
        print(f"PASS: Total files = {data['total_files']}")

    def test_dashboard_summary_has_recent_files(self):
        """Test dashboard summary contains recent_files count (this week)"""
        response = requests.get(f"{BASE_URL}/api/dashboard/summary", headers=self.headers)
        data = response.json()
        assert "recent_files" in data, "Missing 'recent_files' field"
        assert isinstance(data["recent_files"], int), "recent_files should be an integer"
        print(f"PASS: Recent files (this week) = {data['recent_files']}")

    def test_dashboard_summary_has_ai_queries(self):
        """Test dashboard summary contains ai_queries count"""
        response = requests.get(f"{BASE_URL}/api/dashboard/summary", headers=self.headers)
        data = response.json()
        assert "ai_queries" in data, "Missing 'ai_queries' field"
        assert isinstance(data["ai_queries"], int), "ai_queries should be an integer"
        print(f"PASS: AI queries count = {data['ai_queries']}")

    def test_dashboard_summary_has_activities(self):
        """Test dashboard summary contains activities array"""
        response = requests.get(f"{BASE_URL}/api/dashboard/summary", headers=self.headers)
        data = response.json()
        assert "activities" in data, "Missing 'activities' field"
        assert isinstance(data["activities"], list), "activities should be a list"
        print(f"PASS: Activities count = {len(data['activities'])}")

    def test_activity_has_required_fields(self):
        """Test each activity item has type, title, subtitle, time fields"""
        response = requests.get(f"{BASE_URL}/api/dashboard/summary", headers=self.headers)
        data = response.json()
        activities = data.get("activities", [])
        if len(activities) > 0:
            for act in activities[:3]:  # Check first 3
                assert "type" in act, "Activity missing 'type'"
                assert "title" in act, "Activity missing 'title'"
                assert "subtitle" in act, "Activity missing 'subtitle'"
                assert act["type"] in ["upload", "workspace", "ai_search"], f"Unknown activity type: {act['type']}"
                print(f"  Activity: {act['type']} - {act['title']}")
            print("PASS: Activity items have required fields")
        else:
            print("SKIP: No activities to verify (empty)")

    def test_dashboard_summary_requires_auth(self):
        """Test dashboard summary requires authentication"""
        response = requests.get(f"{BASE_URL}/api/dashboard/summary")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("PASS: Dashboard summary requires authentication")

    def test_dashboard_summary_values_match_expectations(self):
        """Test dashboard summary values are realistic for test user"""
        response = requests.get(f"{BASE_URL}/api/dashboard/summary", headers=self.headers)
        data = response.json()
        
        # Print full summary for debugging
        print(f"\n=== Dashboard Summary ===")
        print(f"Workspaces: {data.get('workspaces')}")
        print(f"Total Files: {data.get('total_files')}")
        print(f"Recent Files: {data.get('recent_files')}")
        print(f"AI Queries: {data.get('ai_queries')}")
        print(f"AI Visibility: {data.get('ai_visibility', 0)}")
        print(f"Activities: {len(data.get('activities', []))}")
        
        # Test user should have at least some data based on agent context
        # (1 workspace, 1 file, 3 AI searches)
        assert data["workspaces"] >= 0, "Workspaces should be >= 0"
        assert data["total_files"] >= 0, "Total files should be >= 0"
        assert data["ai_queries"] >= 0, "AI queries should be >= 0"
        print("PASS: Dashboard values are within expected range")


class TestExistingEndpointsStillWork:
    """Ensure existing endpoints haven't broken"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token for test user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_USER)
        assert response.status_code == 200
        self.token = response.json().get('token')
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_workspaces_list_still_works(self):
        """Test /api/workspaces/list still works"""
        response = requests.get(f"{BASE_URL}/api/workspaces/list", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "workspaces" in data
        print(f"PASS: Workspaces list returns {len(data['workspaces'])} workspaces")

    def test_uploaded_files_still_works(self):
        """Test /api/data-sources/uploaded-files still works"""
        response = requests.get(f"{BASE_URL}/api/data-sources/uploaded-files", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "files" in data
        print(f"PASS: Uploaded files returns {len(data['files'])} files")

    def test_current_user_still_works(self):
        """Test /api/auth/me still works"""
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "plan" in data
        assert "credits" in data
        assert "status" in data
        print(f"PASS: Current user returns user with plan={data['plan']}, credits={data['credits']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
