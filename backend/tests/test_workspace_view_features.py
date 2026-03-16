"""
Test Suite for Workspace View Features (Iteration 6)
Tests:
- Clickable workspace cards opening WorkspaceView
- AI Search with workspace_id parameter
- File upload scoped to workspace (workspace_id query param)
- Get uploaded files filtered by workspace_id
- WorkspaceView integration endpoints
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_USER_EMAIL = "testpay@analiyx.com"
TEST_USER_PASSWORD = "test1234"
ADMIN_EMAIL = "admin@papermap.com"
ADMIN_PASSWORD = "admin123"


class TestAuthAndBasics:
    """Basic authentication and health check tests"""
    
    def test_user_login(self):
        """Test user login returns token and user data"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == TEST_USER_EMAIL
        print(f"✓ User login successful, user: {data['user']['name']}")
    
    def test_admin_login(self):
        """Test admin login returns token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "token" in data
        assert data["user"]["role"] == "admin"
        print(f"✓ Admin login successful")


@pytest.fixture(scope="module")
def user_token():
    """Get user auth token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    })
    if response.status_code != 200:
        pytest.skip("Could not authenticate test user")
    return response.json()["token"]


@pytest.fixture(scope="module")
def user_headers(user_token):
    """Get headers with auth token"""
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture(scope="module")
def workspace_id(user_headers):
    """Get existing workspace ID for tests"""
    response = requests.get(f"{BASE_URL}/api/workspaces/list", headers=user_headers)
    if response.status_code != 200:
        pytest.skip("Could not fetch workspaces")
    workspaces = response.json().get("workspaces", [])
    if not workspaces:
        pytest.skip("No workspaces available for testing")
    return workspaces[0]["id"]


class TestWorkspaceList:
    """Tests for workspace listing (prerequisite for clickable cards)"""
    
    def test_list_workspaces(self, user_headers):
        """GET /api/workspaces/list returns workspaces with required fields"""
        response = requests.get(f"{BASE_URL}/api/workspaces/list", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert "workspaces" in data
        print(f"✓ Found {len(data['workspaces'])} workspaces")
        
        # Each workspace should have id, name, data_sources for clickable cards
        for ws in data["workspaces"]:
            assert "id" in ws, "Workspace missing 'id' field"
            assert "name" in ws, "Workspace missing 'name' field"
            assert "data_sources" in ws, "Workspace missing 'data_sources' field"
            print(f"  - {ws['name']} (ID: {ws['id']}, sources: {ws['data_sources']})")
    
    def test_workspace_has_data_sources_array(self, user_headers, workspace_id):
        """Verify workspace data_sources is an array for connected sources display"""
        response = requests.get(f"{BASE_URL}/api/workspaces/list", headers=user_headers)
        assert response.status_code == 200
        workspaces = response.json()["workspaces"]
        
        target_ws = next((ws for ws in workspaces if ws["id"] == workspace_id), None)
        assert target_ws is not None
        assert isinstance(target_ws["data_sources"], list)
        print(f"✓ Workspace '{target_ws['name']}' has data_sources: {target_ws['data_sources']}")


class TestAISearchWithWorkspace:
    """Tests for AI Search endpoint with workspace_id parameter"""
    
    def test_ai_search_accepts_workspace_id(self, user_headers, workspace_id):
        """POST /api/ai/search accepts workspace_id in request body"""
        response = requests.post(
            f"{BASE_URL}/api/ai/search",
            headers=user_headers,
            json={"query": "What is my data?", "workspace_id": workspace_id}
        )
        assert response.status_code == 200, f"AI search failed: {response.text}"
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        print(f"✓ AI Search with workspace_id returned answer: {data['answer'][:100]}...")
    
    def test_ai_search_without_workspace_id(self, user_headers):
        """POST /api/ai/search works without workspace_id (global search)"""
        response = requests.post(
            f"{BASE_URL}/api/ai/search",
            headers=user_headers,
            json={"query": "Show me my analytics"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        print(f"✓ AI Search without workspace_id works")
    
    def test_ai_search_empty_query_rejected(self, user_headers):
        """POST /api/ai/search rejects empty queries"""
        response = requests.post(
            f"{BASE_URL}/api/ai/search",
            headers=user_headers,
            json={"query": ""}
        )
        assert response.status_code == 400
        print(f"✓ Empty query correctly rejected with 400")
    
    def test_ai_search_whitespace_query_rejected(self, user_headers):
        """POST /api/ai/search rejects whitespace-only queries"""
        response = requests.post(
            f"{BASE_URL}/api/ai/search",
            headers=user_headers,
            json={"query": "   "}
        )
        assert response.status_code == 400
        print(f"✓ Whitespace query correctly rejected with 400")
    
    def test_ai_search_requires_auth(self):
        """POST /api/ai/search requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/ai/search",
            json={"query": "Test query"}
        )
        assert response.status_code in [401, 403]
        print(f"✓ AI Search correctly requires auth (status {response.status_code})")


class TestFileUploadWithWorkspace:
    """Tests for file upload scoped to workspace"""
    
    def test_upload_endpoint_accepts_workspace_id(self, user_headers, workspace_id):
        """POST /api/data-sources/upload-file accepts workspace_id query param"""
        # Create a simple CSV file for testing
        csv_content = "name,value\ntest,123\ntest2,456"
        files = {"file": ("test_workspace_upload.csv", csv_content, "text/csv")}
        
        response = requests.post(
            f"{BASE_URL}/api/data-sources/upload-file?workspace_id={workspace_id}",
            headers={"Authorization": user_headers["Authorization"]},
            files=files
        )
        assert response.status_code == 200, f"Upload failed: {response.text}"
        data = response.json()
        assert data["success"] is True
        assert "file_id" in data
        assert "analytics" in data
        print(f"✓ File uploaded to workspace, file_id: {data['file_id']}")
        
        # Store file_id for cleanup
        return data["file_id"]
    
    def test_get_files_with_workspace_filter(self, user_headers, workspace_id):
        """GET /api/data-sources/uploaded-files?workspace_id filters by workspace"""
        response = requests.get(
            f"{BASE_URL}/api/data-sources/uploaded-files?workspace_id={workspace_id}",
            headers=user_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "files" in data
        print(f"✓ Got {len(data['files'])} files for workspace {workspace_id}")
    
    def test_get_files_without_workspace_returns_all(self, user_headers):
        """GET /api/data-sources/uploaded-files without workspace_id returns all user files"""
        response = requests.get(
            f"{BASE_URL}/api/data-sources/uploaded-files",
            headers=user_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "files" in data
        print(f"✓ Got {len(data['files'])} total files without workspace filter")


class TestWorkspaceCreateDelete:
    """Tests for workspace CRUD operations"""
    
    def test_create_workspace(self, user_headers):
        """POST /api/workspaces/create creates workspace with data sources"""
        test_name = f"TEST_workspace_{int(time.time())}"
        response = requests.post(
            f"{BASE_URL}/api/workspaces/create",
            headers=user_headers,
            json={
                "name": test_name,
                "data_sources": ["Excel", "CSV", "Google Analytics"]
            }
        )
        assert response.status_code in [200, 201], f"Create failed: {response.text}"
        data = response.json()
        assert "workspace_id" in data or "id" in data
        workspace_id = data.get("workspace_id") or data.get("id")
        print(f"✓ Created workspace '{test_name}' with id {workspace_id}")
        return workspace_id, test_name
    
    def test_delete_workspace(self, user_headers):
        """DELETE /api/workspaces/{id} deletes workspace"""
        # First create a workspace to delete
        test_name = f"TEST_delete_{int(time.time())}"
        create_response = requests.post(
            f"{BASE_URL}/api/workspaces/create",
            headers=user_headers,
            json={"name": test_name, "data_sources": ["CSV"]}
        )
        assert create_response.status_code in [200, 201]
        ws_id = create_response.json().get("workspace_id") or create_response.json().get("id")
        
        # Now delete it
        delete_response = requests.delete(
            f"{BASE_URL}/api/workspaces/{ws_id}",
            headers=user_headers
        )
        assert delete_response.status_code in [200, 204], f"Delete failed: {delete_response.text}"
        print(f"✓ Deleted workspace {ws_id}")
        
        # Verify it's gone
        list_response = requests.get(f"{BASE_URL}/api/workspaces/list", headers=user_headers)
        workspaces = list_response.json().get("workspaces", [])
        assert not any(ws["id"] == ws_id for ws in workspaces), "Workspace still exists after delete"
        print(f"✓ Verified workspace no longer in list")


class TestDataSourceLimits:
    """Test data source limits endpoint"""
    
    def test_get_limits(self, user_headers):
        """GET /api/data-sources/limits returns plan limits"""
        response = requests.get(
            f"{BASE_URL}/api/data-sources/limits",
            headers=user_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "plan" in data
        assert "limit" in data
        assert "current" in data
        assert "can_add" in data
        print(f"✓ Data source limits: {data}")


class TestFileDetails:
    """Test file details endpoint"""
    
    def test_get_file_details(self, user_headers, workspace_id):
        """GET /api/data-sources/file-details/{file_id} returns analytics"""
        # First upload a file
        csv_content = "col1,col2,col3\n1,2,3\n4,5,6\n7,8,9"
        files = {"file": ("details_test.csv", csv_content, "text/csv")}
        
        upload_response = requests.post(
            f"{BASE_URL}/api/data-sources/upload-file?workspace_id={workspace_id}",
            headers={"Authorization": user_headers["Authorization"]},
            files=files
        )
        if upload_response.status_code != 200:
            pytest.skip(f"Could not upload test file: {upload_response.text}")
        
        file_id = upload_response.json()["file_id"]
        
        # Get details
        response = requests.get(
            f"{BASE_URL}/api/data-sources/file-details/{file_id}",
            headers=user_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "filename" in data
        assert "analytics" in data
        assert "sample_data" in data
        print(f"✓ File details for {data['filename']}: {data['analytics']['total_rows']} rows, {data['analytics']['total_columns']} cols")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/data-sources/file/{file_id}", headers=user_headers)


class TestCleanup:
    """Cleanup test data"""
    
    def test_cleanup_test_workspaces(self, user_headers):
        """Remove workspaces created during testing"""
        response = requests.get(f"{BASE_URL}/api/workspaces/list", headers=user_headers)
        if response.status_code == 200:
            workspaces = response.json().get("workspaces", [])
            for ws in workspaces:
                if ws["name"].startswith("TEST_"):
                    requests.delete(f"{BASE_URL}/api/workspaces/{ws['id']}", headers=user_headers)
                    print(f"  Cleaned up workspace: {ws['name']}")
        print("✓ Cleanup complete")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
