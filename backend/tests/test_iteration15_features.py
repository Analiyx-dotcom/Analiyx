"""
Iteration 15 Backend Tests - Testing 3 new features:
1. GA4 Nango scope fix - connection_config.scopes in connect session payload
2. Chart Color Theme Selector - GET/PUT /api/charts/theme
3. Bookmark AI Chat messages to Notes - POST/GET /api/charts/notes
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


class TestAuthentication:
    """Verify test credentials work"""
    
    def test_test_user_login(self):
        """Test user can login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data, "No token in response"
        print(f"✓ Test user login successful")


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for test user"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip("Authentication failed - skipping authenticated tests")


@pytest.fixture
def auth_headers(auth_token):
    """Headers with auth token"""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }


# ============ Feature 1: Nango Connect Session with connection_config.scopes ============

class TestNangoConnectSessionScopes:
    """Test that Nango connect session uses connection_config.scopes for GA4 and Google Ads"""
    
    def test_connect_session_creates_successfully(self, auth_headers):
        """POST /api/nango/connect-session creates session successfully"""
        response = requests.post(
            f"{BASE_URL}/api/nango/connect-session",
            headers=auth_headers,
            json={}
        )
        assert response.status_code == 200, f"Connect session failed: {response.text}"
        data = response.json()
        # Nango returns a token nested in data object
        token_data = data.get("data", data)  # Handle both {"data": {...}} and direct response
        assert "token" in token_data, f"No token in response: {data}"
        assert token_data["token"].startswith("nango_connect_session_"), f"Invalid token format: {token_data['token']}"
        print(f"✓ Nango connect session created successfully with token")
    
    def test_connect_session_for_google_analytics(self, auth_headers):
        """POST /api/nango/connect-session works for google-analytics provider"""
        response = requests.post(
            f"{BASE_URL}/api/nango/connect-session",
            headers=auth_headers,
            json={"allowed_integrations": ["google-analytics"]}
        )
        assert response.status_code == 200, f"Connect session failed: {response.text}"
        data = response.json()
        token_data = data.get("data", data)
        assert "token" in token_data, f"No token in response: {data}"
        assert token_data["token"].startswith("nango_connect_session_"), f"Invalid token format"
        print(f"✓ Nango connect session for google-analytics created successfully")
    
    def test_connect_session_for_google_ads(self, auth_headers):
        """POST /api/nango/connect-session works for google-ads provider"""
        response = requests.post(
            f"{BASE_URL}/api/nango/connect-session",
            headers=auth_headers,
            json={"allowed_integrations": ["google-ads"]}
        )
        assert response.status_code == 200, f"Connect session failed: {response.text}"
        data = response.json()
        token_data = data.get("data", data)
        assert "token" in token_data, f"No token in response: {data}"
        assert token_data["token"].startswith("nango_connect_session_"), f"Invalid token format"
        print(f"✓ Nango connect session for google-ads created successfully")
    
    def test_connect_session_requires_auth(self):
        """POST /api/nango/connect-session requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/nango/connect-session",
            json={}
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"✓ Nango connect session requires authentication")


# ============ Feature 2: Chart Color Theme Selector ============

class TestChartThemeAPI:
    """Test chart theme GET/PUT endpoints"""
    
    def test_get_theme_returns_default_for_new_users(self, auth_headers):
        """GET /api/charts/theme returns 'default' for users without saved theme"""
        response = requests.get(
            f"{BASE_URL}/api/charts/theme",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Get theme failed: {response.text}"
        data = response.json()
        assert "theme" in data, f"No theme in response: {data}"
        # Should return 'default' or a valid theme
        print(f"✓ GET /api/charts/theme returned theme: {data['theme']}")
    
    def test_save_chart_theme_forest(self, auth_headers):
        """PUT /api/charts/theme saves 'forest' theme"""
        response = requests.put(
            f"{BASE_URL}/api/charts/theme",
            headers=auth_headers,
            json={"theme": "forest"}
        )
        assert response.status_code == 200, f"Save theme failed: {response.text}"
        data = response.json()
        assert data.get("success") == True, f"Expected success: {data}"
        assert data.get("theme") == "forest", f"Expected theme 'forest': {data}"
        print(f"✓ PUT /api/charts/theme saved 'forest' theme")
    
    def test_get_theme_returns_saved_theme(self, auth_headers):
        """GET /api/charts/theme returns previously saved theme"""
        # First save a theme
        requests.put(
            f"{BASE_URL}/api/charts/theme",
            headers=auth_headers,
            json={"theme": "azure"}
        )
        # Then get it
        response = requests.get(
            f"{BASE_URL}/api/charts/theme",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Get theme failed: {response.text}"
        data = response.json()
        assert data.get("theme") == "azure", f"Expected 'azure', got: {data}"
        print(f"✓ GET /api/charts/theme returned saved theme 'azure'")
    
    def test_save_all_theme_options(self, auth_headers):
        """PUT /api/charts/theme works for all 6 theme options"""
        themes = ["default", "forest", "azure", "mint", "violet", "ocean"]
        for theme in themes:
            response = requests.put(
                f"{BASE_URL}/api/charts/theme",
                headers=auth_headers,
                json={"theme": theme}
            )
            assert response.status_code == 200, f"Save theme '{theme}' failed: {response.text}"
            data = response.json()
            assert data.get("theme") == theme, f"Expected '{theme}', got: {data}"
        print(f"✓ All 6 themes saved successfully: {themes}")
    
    def test_theme_requires_auth(self):
        """GET/PUT /api/charts/theme requires authentication"""
        # GET without auth
        response = requests.get(f"{BASE_URL}/api/charts/theme")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        
        # PUT without auth
        response = requests.put(
            f"{BASE_URL}/api/charts/theme",
            json={"theme": "forest"}
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"✓ Chart theme endpoints require authentication")


# ============ Feature 3: Bookmark AI Chat to Notes ============

class TestNotesAPI:
    """Test notes CRUD for bookmark feature"""
    
    def test_create_note_for_bookmark(self, auth_headers):
        """POST /api/charts/notes creates a note (for bookmark feature)"""
        response = requests.post(
            f"{BASE_URL}/api/charts/notes",
            headers=auth_headers,
            json={
                "title": "TEST_AI Chat Bookmark",
                "content": "This is a bookmarked AI chat response for testing."
            }
        )
        assert response.status_code == 200, f"Create note failed: {response.text}"
        data = response.json()
        assert "id" in data, f"No id in response: {data}"
        assert data.get("title") == "TEST_AI Chat Bookmark", f"Title mismatch: {data}"
        print(f"✓ POST /api/charts/notes created note with id: {data['id']}")
        return data["id"]
    
    def test_get_notes_returns_list(self, auth_headers):
        """GET /api/charts/notes returns list of notes"""
        # First create a note
        requests.post(
            f"{BASE_URL}/api/charts/notes",
            headers=auth_headers,
            json={
                "title": "TEST_Note for list test",
                "content": "Content for list test"
            }
        )
        
        # Then get all notes
        response = requests.get(
            f"{BASE_URL}/api/charts/notes",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Get notes failed: {response.text}"
        data = response.json()
        assert "notes" in data, f"No notes in response: {data}"
        assert isinstance(data["notes"], list), f"Notes is not a list: {data}"
        print(f"✓ GET /api/charts/notes returned {len(data['notes'])} notes")
    
    def test_note_has_required_fields(self, auth_headers):
        """Notes have required fields: id, title, content, created_at, updated_at"""
        # Create a note
        create_resp = requests.post(
            f"{BASE_URL}/api/charts/notes",
            headers=auth_headers,
            json={
                "title": "TEST_Field validation note",
                "content": "Content for field validation"
            }
        )
        note_id = create_resp.json().get("id")
        
        # Get notes and find the created one
        response = requests.get(
            f"{BASE_URL}/api/charts/notes",
            headers=auth_headers
        )
        data = response.json()
        notes = data.get("notes", [])
        
        # Find our test note
        test_note = next((n for n in notes if n.get("id") == note_id), None)
        assert test_note is not None, f"Created note not found in list"
        
        # Check required fields
        required_fields = ["id", "title", "content", "created_at", "updated_at"]
        for field in required_fields:
            assert field in test_note, f"Missing field '{field}' in note: {test_note}"
        print(f"✓ Note has all required fields: {required_fields}")
    
    def test_notes_requires_auth(self):
        """POST/GET /api/charts/notes requires authentication"""
        # POST without auth
        response = requests.post(
            f"{BASE_URL}/api/charts/notes",
            json={"title": "Test", "content": "Test"}
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        
        # GET without auth
        response = requests.get(f"{BASE_URL}/api/charts/notes")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"✓ Notes endpoints require authentication")
    
    def test_update_note(self, auth_headers):
        """PUT /api/charts/notes/{id} updates a note"""
        # Create a note
        create_resp = requests.post(
            f"{BASE_URL}/api/charts/notes",
            headers=auth_headers,
            json={
                "title": "TEST_Note to update",
                "content": "Original content"
            }
        )
        note_id = create_resp.json().get("id")
        
        # Update the note
        response = requests.put(
            f"{BASE_URL}/api/charts/notes/{note_id}",
            headers=auth_headers,
            json={
                "title": "TEST_Updated title",
                "content": "Updated content"
            }
        )
        assert response.status_code == 200, f"Update note failed: {response.text}"
        data = response.json()
        assert data.get("success") == True, f"Expected success: {data}"
        print(f"✓ PUT /api/charts/notes/{note_id} updated successfully")
    
    def test_delete_note(self, auth_headers):
        """DELETE /api/charts/notes/{id} deletes a note"""
        # Create a note
        create_resp = requests.post(
            f"{BASE_URL}/api/charts/notes",
            headers=auth_headers,
            json={
                "title": "TEST_Note to delete",
                "content": "Content to delete"
            }
        )
        note_id = create_resp.json().get("id")
        
        # Delete the note
        response = requests.delete(
            f"{BASE_URL}/api/charts/notes/{note_id}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Delete note failed: {response.text}"
        data = response.json()
        assert data.get("success") == True, f"Expected success: {data}"
        print(f"✓ DELETE /api/charts/notes/{note_id} deleted successfully")


# ============ Cleanup ============

class TestCleanup:
    """Cleanup test data"""
    
    def test_cleanup_test_notes(self, auth_headers):
        """Delete all TEST_ prefixed notes"""
        response = requests.get(
            f"{BASE_URL}/api/charts/notes",
            headers=auth_headers
        )
        if response.status_code == 200:
            notes = response.json().get("notes", [])
            deleted_count = 0
            for note in notes:
                if note.get("title", "").startswith("TEST_"):
                    del_resp = requests.delete(
                        f"{BASE_URL}/api/charts/notes/{note['id']}",
                        headers=auth_headers
                    )
                    if del_resp.status_code == 200:
                        deleted_count += 1
            print(f"✓ Cleaned up {deleted_count} test notes")
    
    def test_reset_theme_to_default(self, auth_headers):
        """Reset chart theme to default"""
        response = requests.put(
            f"{BASE_URL}/api/charts/theme",
            headers=auth_headers,
            json={"theme": "default"}
        )
        if response.status_code == 200:
            print(f"✓ Reset chart theme to default")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
