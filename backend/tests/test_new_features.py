"""
Test New Features: Contact, Workspaces, Support Tickets, Admin Trial Extension
Tests for items 1-16 implementation including: contact form, workspaces, support, admin trial extension
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


class TestContactAPI:
    """Test contact form API endpoint"""
    
    def test_contact_form_submission(self):
        """POST /api/contact should accept and store contact form"""
        response = requests.post(f"{BASE_URL}/api/contact", json={
            "name": "Test Contact User",
            "email": "test_contact@example.com",
            "company": "Test Company",
            "phone": "+91 9876543210",
            "message": "This is a test message from automated testing."
        })
        assert response.status_code == 200, f"Contact submission failed: {response.text}"
        
        data = response.json()
        assert data["success"] == True
        assert "message" in data
        print(f"✓ Contact form submitted successfully")
    
    def test_contact_form_minimal(self):
        """POST /api/contact works with minimal required fields"""
        response = requests.post(f"{BASE_URL}/api/contact", json={
            "name": "Minimal User",
            "email": "minimal@example.com",
            "message": "Minimal test message"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print(f"✓ Contact form with minimal fields works")
    
    def test_contact_form_invalid_email(self):
        """POST /api/contact rejects invalid email"""
        response = requests.post(f"{BASE_URL}/api/contact", json={
            "name": "Test User",
            "email": "invalid-email",
            "message": "Test message"
        })
        assert response.status_code == 422, f"Expected 422 for invalid email, got {response.status_code}"
        print(f"✓ Contact form correctly rejects invalid email")


class TestWorkspacesAPI:
    """Test workspace CRUD endpoints"""
    
    @pytest.fixture
    def user_token(self):
        """Get user auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("User login failed")
        return response.json()["token"]
    
    def test_create_workspace(self, user_token):
        """POST /api/workspaces/create creates a workspace"""
        unique_name = f"TEST_Workspace_{uuid.uuid4().hex[:6]}"
        response = requests.post(
            f"{BASE_URL}/api/workspaces/create",
            json={
                "name": unique_name,
                "data_sources": ["Excel", "CSV"]
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200, f"Workspace creation failed: {response.text}"
        
        data = response.json()
        assert data["success"] == True
        assert "workspace_id" in data
        assert data["name"] == unique_name
        print(f"✓ Workspace created: {unique_name} (ID: {data['workspace_id']})")
        return data["workspace_id"]
    
    def test_list_workspaces(self, user_token):
        """GET /api/workspaces/list returns user workspaces"""
        response = requests.get(
            f"{BASE_URL}/api/workspaces/list",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200, f"List workspaces failed: {response.text}"
        
        data = response.json()
        assert "workspaces" in data
        assert isinstance(data["workspaces"], list)
        
        if len(data["workspaces"]) > 0:
            ws = data["workspaces"][0]
            assert "id" in ws
            assert "name" in ws
            assert "data_sources" in ws
            print(f"✓ Listed {len(data['workspaces'])} workspaces")
        else:
            print(f"✓ Workspaces list endpoint works (0 workspaces)")
    
    def test_create_workspace_no_auth(self):
        """POST /api/workspaces/create requires auth"""
        response = requests.post(
            f"{BASE_URL}/api/workspaces/create",
            json={"name": "Unauthorized Workspace", "data_sources": []}
        )
        assert response.status_code in [401, 403]
        print(f"✓ Workspace creation correctly requires auth")
    
    def test_workspace_flow(self, user_token):
        """Test create -> list -> verify workspace appears"""
        # Create workspace
        unique_name = f"TEST_FlowWS_{uuid.uuid4().hex[:6]}"
        create_resp = requests.post(
            f"{BASE_URL}/api/workspaces/create",
            json={"name": unique_name, "data_sources": ["Google Ads", "Meta Ads"]},
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert create_resp.status_code == 200
        ws_id = create_resp.json()["workspace_id"]
        
        # Verify in list
        list_resp = requests.get(
            f"{BASE_URL}/api/workspaces/list",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert list_resp.status_code == 200
        
        workspaces = list_resp.json()["workspaces"]
        found = any(ws["id"] == ws_id for ws in workspaces)
        assert found, "Created workspace not found in list"
        print(f"✓ Workspace created and verified in list")


class TestSupportTicketsAPI:
    """Test support ticket endpoints"""
    
    @pytest.fixture
    def user_token(self):
        """Get user auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("User login failed")
        return response.json()["token"]
    
    def test_create_support_ticket(self, user_token):
        """POST /api/support/tickets creates a ticket"""
        response = requests.post(
            f"{BASE_URL}/api/support/tickets",
            json={
                "subject": f"TEST_Ticket_{uuid.uuid4().hex[:6]}",
                "message": "This is a test support ticket from automated testing.",
                "priority": "high"
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200, f"Ticket creation failed: {response.text}"
        
        data = response.json()
        assert data["success"] == True
        assert "ticket_id" in data
        print(f"✓ Support ticket created: {data['ticket_id']}")
    
    def test_get_user_tickets(self, user_token):
        """GET /api/support/tickets returns user tickets"""
        response = requests.get(
            f"{BASE_URL}/api/support/tickets",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200, f"Get tickets failed: {response.text}"
        
        data = response.json()
        assert "tickets" in data
        assert isinstance(data["tickets"], list)
        
        if len(data["tickets"]) > 0:
            ticket = data["tickets"][0]
            assert "id" in ticket
            assert "subject" in ticket
            assert "status" in ticket
            assert "priority" in ticket
            print(f"✓ Listed {len(data['tickets'])} tickets")
        else:
            print(f"✓ Tickets list endpoint works (0 tickets)")
    
    def test_create_ticket_no_auth(self):
        """POST /api/support/tickets requires auth"""
        response = requests.post(
            f"{BASE_URL}/api/support/tickets",
            json={"subject": "Unauth", "message": "Test", "priority": "low"}
        )
        assert response.status_code in [401, 403]
        print(f"✓ Support tickets correctly requires auth")
    
    def test_support_ticket_flow(self, user_token):
        """Test create ticket -> get tickets -> verify ticket appears"""
        # Create ticket
        unique_subject = f"TEST_Flow_Ticket_{uuid.uuid4().hex[:6]}"
        create_resp = requests.post(
            f"{BASE_URL}/api/support/tickets",
            json={"subject": unique_subject, "message": "Flow test", "priority": "medium"},
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert create_resp.status_code == 200
        ticket_id = create_resp.json()["ticket_id"]
        
        # Verify in list
        list_resp = requests.get(
            f"{BASE_URL}/api/support/tickets",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert list_resp.status_code == 200
        
        tickets = list_resp.json()["tickets"]
        found = any(t["id"] == ticket_id for t in tickets)
        assert found, "Created ticket not found in list"
        print(f"✓ Support ticket created and verified in list")


class TestAdminTrialExtension:
    """Test admin trial extension and user management"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        return response.json()["token"]
    
    @pytest.fixture
    def test_user_id(self, admin_token):
        """Get a non-admin user ID for testing"""
        response = requests.get(
            f"{BASE_URL}/api/admin/manage/users/details",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        if response.status_code != 200:
            pytest.skip("Could not get users")
        
        users = response.json()["users"]
        for user in users:
            if user["email"] == TEST_USER_EMAIL:
                return user["id"]
        
        # Fallback to any non-admin user
        for user in users:
            if user["role"] != "admin":
                return user["id"]
        pytest.skip("No suitable test user found")
    
    def test_extend_trial_7_days(self, admin_token, test_user_id):
        """POST /api/admin/manage/users/{id}/extend-trial extends trial and updates user"""
        response = requests.post(
            f"{BASE_URL}/api/admin/manage/users/{test_user_id}/extend-trial",
            json={"days": 7},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Extend trial failed: {response.text}"
        
        data = response.json()
        assert data["success"] == True
        assert "new_end_date" in data
        assert "message" in data
        assert "7" in data["message"]
        print(f"✓ Trial extended to: {data['new_end_date']}")
    
    def test_extend_trial_custom_days(self, admin_token, test_user_id):
        """Extend trial with custom days"""
        response = requests.post(
            f"{BASE_URL}/api/admin/manage/users/{test_user_id}/extend-trial",
            json={"days": 14},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        print(f"✓ Trial extended by 14 days")
    
    def test_extend_trial_no_auth(self, test_user_id):
        """Extend trial requires admin auth"""
        response = requests.post(
            f"{BASE_URL}/api/admin/manage/users/{test_user_id}/extend-trial",
            json={"days": 7}
        )
        assert response.status_code in [401, 403]
        print(f"✓ Extend trial correctly requires admin auth")
    
    def test_extend_trial_user_forbidden(self, test_user_id):
        """Regular user cannot extend trials"""
        # Login as regular user
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        if login_resp.status_code != 200:
            pytest.skip("User login failed")
        user_token = login_resp.json()["token"]
        
        response = requests.post(
            f"{BASE_URL}/api/admin/manage/users/{test_user_id}/extend-trial",
            json={"days": 7},
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 403
        print(f"✓ Regular user correctly forbidden from extending trials")


class TestAdminRevenue:
    """Test admin revenue endpoint returns INR"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        return response.json()["token"]
    
    def test_revenue_chart_data(self, admin_token):
        """GET /api/admin/charts/revenue returns revenue data"""
        response = requests.get(
            f"{BASE_URL}/api/admin/charts/revenue",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
        
        if len(data["data"]) > 0:
            entry = data["data"][0]
            assert "month" in entry
            assert "amount" in entry
            print(f"✓ Revenue chart data: {len(data['data'])} months")
    
    def test_admin_stats_revenue(self, admin_token):
        """GET /api/admin/stats includes monthly_revenue"""
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "monthly_revenue" in data
        assert isinstance(data["monthly_revenue"], (int, float))
        print(f"✓ Admin stats monthly revenue: {data['monthly_revenue']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
