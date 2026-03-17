"""
Iteration 10 - Comprehensive Backend API Tests
Tests: Auth, AI Visibility, Payment, Notes, AI Chat, Dashboard
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://data-analytics-dev.preview.emergentagent.com')

# Test credentials
TEST_USER = {"email": "testuser@test.com", "password": "test1234"}
ADMIN_USER = {"email": "admin@papermap.com", "password": "admin123"}

class TestAuth:
    """Authentication endpoint tests"""
    
    def test_login_success_regular_user(self):
        """Test regular user login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_USER)
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == TEST_USER["email"]
        assert data["user"]["role"] == "user"
        print(f"✓ Regular user login successful - Plan: {data['user']['plan']}")
    
    def test_login_success_admin_user(self):
        """Test admin user login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN_USER)
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "token" in data
        assert data["user"]["role"] == "admin"
        print(f"✓ Admin user login successful - Role: {data['user']['role']}")
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "invalid@test.com", "password": "wrongpass"
        })
        assert response.status_code == 401
        print("✓ Invalid credentials rejected correctly")
    
    def test_get_current_user(self):
        """Test GET /api/auth/me"""
        # Login first
        login_res = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_USER)
        token = login_res.json()["token"]
        
        response = requests.get(f"{BASE_URL}/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == TEST_USER["email"]
        print(f"✓ GET /api/auth/me returns correct user - Credits: {data['credits']}")


class TestAIVisibility:
    """AI Visibility analysis tests"""
    
    @pytest.fixture
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_USER)
        return response.json()["token"]
    
    def test_ai_visibility_analyze(self, auth_token):
        """Test POST /api/ai-visibility/analyze - Full URL analysis"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(
            f"{BASE_URL}/api/ai-visibility/analyze",
            json={"url": "https://example.com"},
            headers=headers,
            timeout=60  # LLM calls can take time
        )
        # May return 200 or 403 (limit reached)
        if response.status_code == 200:
            data = response.json()
            assert data["success"] == True
            assert "analysis" in data
            assert "overall_score" in data["analysis"]
            print(f"✓ AI Visibility analysis completed - Score: {data['analysis']['overall_score']}")
        elif response.status_code == 403:
            assert "AI_VISIBILITY_LIMIT_REACHED" in response.json().get("detail", "")
            print("✓ AI Visibility limit enforcement working (403 returned)")
        else:
            pytest.fail(f"Unexpected status: {response.status_code} - {response.text}")
    
    def test_ai_visibility_requires_auth(self):
        """Test that AI Visibility requires authentication"""
        response = requests.post(f"{BASE_URL}/api/ai-visibility/analyze", json={"url": "https://example.com"})
        assert response.status_code == 403
        print("✓ AI Visibility correctly requires authentication")
    
    def test_ai_visibility_history(self, auth_token):
        """Test GET /api/ai-visibility/history"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/ai-visibility/history", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "analyses" in data
        print(f"✓ AI Visibility history returned {len(data['analyses'])} analyses")


class TestPayments:
    """Payment endpoints tests"""
    
    @pytest.fixture
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_USER)
        return response.json()["token"]
    
    def test_create_payment_order_starter(self, auth_token):
        """Test POST /api/payments/create-order for Starter plan"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(
            f"{BASE_URL}/api/payments/create-order",
            json={"plan": "Starter", "return_url": "https://example.com"},
            headers=headers
        )
        assert response.status_code == 200, f"Payment order failed: {response.text}"
        data = response.json()
        assert data["success"] == True
        assert "order_id" in data
        assert "payment_session_id" in data
        assert data["order_amount"] == 500
        print(f"✓ Payment order created - Order ID: {data['order_id']}, Session: {data['payment_session_id'][:20]}...")
    
    def test_create_payment_order_business_pro(self, auth_token):
        """Test POST /api/payments/create-order for Business Pro plan"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(
            f"{BASE_URL}/api/payments/create-order",
            json={"plan": "Business Pro", "return_url": "https://example.com"},
            headers=headers
        )
        assert response.status_code == 200, f"Payment order failed: {response.text}"
        data = response.json()
        assert data["success"] == True
        assert data["order_amount"] == 800
        print(f"✓ Business Pro order created - Amount: ₹{data['order_amount']}")
    
    def test_create_payment_invalid_plan(self, auth_token):
        """Test payment with invalid plan"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(
            f"{BASE_URL}/api/payments/create-order",
            json={"plan": "InvalidPlan", "return_url": "https://example.com"},
            headers=headers
        )
        assert response.status_code == 400
        print("✓ Invalid plan correctly rejected")
    
    def test_payments_require_auth(self):
        """Test that payment endpoints require authentication"""
        response = requests.post(
            f"{BASE_URL}/api/payments/create-order",
            json={"plan": "Starter"}
        )
        assert response.status_code == 403
        print("✓ Payment endpoints correctly require authentication")


class TestAIChat:
    """AI Chat endpoints tests"""
    
    @pytest.fixture
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_USER)
        return response.json()["token"]
    
    def test_ai_chat_basic(self, auth_token):
        """Test POST /api/ai/chat with basic query"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(
            f"{BASE_URL}/api/ai/chat",
            json={"query": "What is data analytics?"},
            headers=headers,
            timeout=30
        )
        assert response.status_code == 200, f"AI Chat failed: {response.text}"
        data = response.json()
        assert "answer" in data
        assert "session_id" in data
        assert len(data["answer"]) > 10
        print(f"✓ AI Chat response received - Length: {len(data['answer'])} chars")
    
    def test_ai_chat_empty_query(self, auth_token):
        """Test AI Chat with empty query"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(
            f"{BASE_URL}/api/ai/chat",
            json={"query": ""},
            headers=headers
        )
        assert response.status_code == 400
        print("✓ Empty query correctly rejected")
    
    def test_ai_chat_requires_auth(self):
        """Test that AI Chat requires authentication"""
        response = requests.post(f"{BASE_URL}/api/ai/chat", json={"query": "test"})
        assert response.status_code == 403
        print("✓ AI Chat correctly requires authentication")


class TestNotes:
    """Notes CRUD tests"""
    
    @pytest.fixture
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_USER)
        return response.json()["token"]
    
    def test_create_note(self, auth_token):
        """Test creating a new note"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        note_data = {"title": "TEST_Note_Iteration10", "content": "Test content for iteration 10"}
        response = requests.post(f"{BASE_URL}/api/charts/notes", json=note_data, headers=headers)
        assert response.status_code == 200, f"Create note failed: {response.text}"
        data = response.json()
        assert "id" in data
        print(f"✓ Note created - ID: {data['id']}")
        return data["id"]
    
    def test_get_notes(self, auth_token):
        """Test getting all notes"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/charts/notes", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "notes" in data
        print(f"✓ GET notes returned {len(data['notes'])} notes")
    
    def test_update_and_delete_note(self, auth_token):
        """Test note update and delete flow"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Create
        note_data = {"title": "TEST_ToUpdate", "content": "Original content"}
        create_res = requests.post(f"{BASE_URL}/api/charts/notes", json=note_data, headers=headers)
        assert create_res.status_code == 200
        note_id = create_res.json()["id"]
        
        # Update
        update_res = requests.put(
            f"{BASE_URL}/api/charts/notes/{note_id}",
            json={"title": "TEST_Updated", "content": "Updated content"},
            headers=headers
        )
        assert update_res.status_code == 200
        print(f"✓ Note updated - ID: {note_id}")
        
        # Delete
        delete_res = requests.delete(f"{BASE_URL}/api/charts/notes/{note_id}", headers=headers)
        assert delete_res.status_code == 200
        print(f"✓ Note deleted - ID: {note_id}")
        
        # Verify deletion
        verify_res = requests.get(f"{BASE_URL}/api/charts/notes", headers=headers)
        notes = verify_res.json().get("notes", [])
        assert not any(n.get("id") == note_id for n in notes)
        print("✓ Note deletion verified")


class TestDashboard:
    """Dashboard summary tests"""
    
    @pytest.fixture
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_USER)
        return response.json()["token"]
    
    def test_dashboard_summary(self, auth_token):
        """Test GET /api/dashboard/summary"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/dashboard/summary", headers=headers)
        assert response.status_code == 200, f"Dashboard summary failed: {response.text}"
        data = response.json()
        assert "workspaces" in data
        assert "total_files" in data
        print(f"✓ Dashboard summary - Workspaces: {data['workspaces']}, Files: {data['total_files']}")


class TestWorkspaces:
    """Workspace tests"""
    
    @pytest.fixture
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_USER)
        return response.json()["token"]
    
    def test_list_workspaces(self, auth_token):
        """Test GET /api/workspaces"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/workspaces", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "workspaces" in data
        print(f"✓ Workspaces list returned {len(data['workspaces'])} workspaces")
    
    def test_create_and_delete_workspace(self, auth_token):
        """Test workspace CRUD"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Create
        create_res = requests.post(
            f"{BASE_URL}/api/workspaces",
            json={"name": "TEST_Workspace_Iter10", "data_sources": ["CSV", "Excel"]},
            headers=headers
        )
        if create_res.status_code == 200:
            ws_id = create_res.json().get("id")
            print(f"✓ Workspace created - ID: {ws_id}")
            
            # Delete
            delete_res = requests.delete(f"{BASE_URL}/api/workspaces/{ws_id}", headers=headers)
            assert delete_res.status_code == 200
            print(f"✓ Workspace deleted - ID: {ws_id}")
        elif create_res.status_code == 403 and "WORKSPACE_LIMIT" in create_res.text:
            print("✓ Workspace limit enforcement working (403 returned)")
        else:
            pytest.fail(f"Unexpected: {create_res.status_code} - {create_res.text}")


class TestAdminEndpoints:
    """Admin-specific endpoint tests"""
    
    @pytest.fixture
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json=ADMIN_USER)
        return response.json()["token"]
    
    def test_admin_users_list(self, admin_token):
        """Test GET /api/admin/users"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/users", headers=headers)
        assert response.status_code == 200, f"Admin users failed: {response.text}"
        data = response.json()
        assert "users" in data
        print(f"✓ Admin users list returned {len(data['users'])} users")
    
    def test_admin_stats(self, admin_token):
        """Test GET /api/admin/stats"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/admin/stats", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
        print(f"✓ Admin stats - Total users: {data['total_users']}, Total files: {data.get('total_files', 0)}")


# Cleanup test data after all tests
@pytest.fixture(scope="session", autouse=True)
def cleanup_test_data():
    """Cleanup TEST_ prefixed data after test session"""
    yield
    # Login and cleanup
    login_res = requests.post(f"{BASE_URL}/api/auth/login", json=TEST_USER)
    if login_res.status_code == 200:
        token = login_res.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Cleanup notes
        notes_res = requests.get(f"{BASE_URL}/api/charts/notes", headers=headers)
        if notes_res.status_code == 200:
            for note in notes_res.json().get("notes", []):
                if note.get("title", "").startswith("TEST_"):
                    requests.delete(f"{BASE_URL}/api/charts/notes/{note['id']}", headers=headers)
        
        # Cleanup workspaces
        ws_res = requests.get(f"{BASE_URL}/api/workspaces", headers=headers)
        if ws_res.status_code == 200:
            for ws in ws_res.json().get("workspaces", []):
                if ws.get("name", "").startswith("TEST_"):
                    requests.delete(f"{BASE_URL}/api/workspaces/{ws['id']}", headers=headers)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
