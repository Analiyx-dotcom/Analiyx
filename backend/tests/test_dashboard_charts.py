"""
Test suite for Dashboard Redesign Features: Charts generation, Notes CRUD, Reports listing
Iteration 9 - Testing auto-generated charts, notes, reports, and AI chat on dashboard
"""
import pytest
import requests
import os
import time
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://deep-report-beta.preview.emergentagent.com').rstrip('/')
TEST_FILE_ID = "69b7a1709080c98d829232c7"  # Existing test file from user testpay@analiyx.com

@pytest.fixture(scope="module")
def auth_token():
    """Authenticate test user and return token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "testpay@analiyx.com",
        "password": "test1234"
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    assert "token" in data, "No token in response"
    return data["token"]

@pytest.fixture
def auth_headers(auth_token):
    """Return headers with auth token"""
    return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}


class TestChartGeneration:
    """Test auto-generated chart configurations from uploaded files"""
    
    def test_generate_charts_for_file(self, auth_headers):
        """GET /api/charts/generate/{file_id} - Auto-generates chart configs"""
        response = requests.get(f"{BASE_URL}/api/charts/generate/{TEST_FILE_ID}", headers=auth_headers)
        assert response.status_code == 200, f"Chart generation failed: {response.text}"
        
        data = response.json()
        assert "filename" in data, "Response should contain filename"
        assert "charts" in data, "Response should contain charts array"
        assert isinstance(data["charts"], list), "Charts should be a list"
        assert len(data["charts"]) > 0, "Should generate at least one chart"
        
        # Verify chart types
        chart_types = [c["type"] for c in data["charts"]]
        assert "kpi" in chart_types, "Should generate KPI cards"
        print(f"Generated {len(data['charts'])} charts: {chart_types}")
        
        # Verify KPI chart structure
        kpi_chart = next((c for c in data["charts"] if c["type"] == "kpi"), None)
        if kpi_chart:
            assert "data" in kpi_chart, "KPI chart should have data"
            assert isinstance(kpi_chart["data"], list), "KPI data should be a list"
            for kpi in kpi_chart["data"]:
                assert "label" in kpi, "Each KPI should have a label"
                assert "value" in kpi, "Each KPI should have a value"
                assert "format" in kpi, "Each KPI should have a format"
    
    def test_generate_charts_invalid_file(self, auth_headers):
        """GET /api/charts/generate/{invalid_id} - Returns 404"""
        response = requests.get(f"{BASE_URL}/api/charts/generate/000000000000000000000000", headers=auth_headers)
        assert response.status_code == 404, f"Should return 404 for invalid file ID"
    
    def test_generate_charts_requires_auth(self):
        """GET /api/charts/generate/{file_id} - Requires authentication"""
        response = requests.get(f"{BASE_URL}/api/charts/generate/{TEST_FILE_ID}")
        assert response.status_code in [401, 403], f"Should require authentication"


class TestNotesCRUD:
    """Test Notes CRUD operations"""
    
    created_note_id = None
    
    def test_create_note(self, auth_headers):
        """POST /api/charts/notes - Creates a note"""
        note_data = {
            "title": f"TEST_Note_{datetime.now().strftime('%H%M%S')}",
            "content": "This is a test note content for testing the notes feature."
        }
        response = requests.post(f"{BASE_URL}/api/charts/notes", json=note_data, headers=auth_headers)
        assert response.status_code == 200, f"Note creation failed: {response.text}"
        
        data = response.json()
        assert "id" in data, "Response should contain note id"
        assert "title" in data, "Response should contain note title"
        assert data["title"] == note_data["title"], "Note title should match"
        
        TestNotesCRUD.created_note_id = data["id"]
        print(f"Created note with ID: {data['id']}")
    
    def test_get_notes(self, auth_headers):
        """GET /api/charts/notes - Returns user's notes"""
        response = requests.get(f"{BASE_URL}/api/charts/notes", headers=auth_headers)
        assert response.status_code == 200, f"Get notes failed: {response.text}"
        
        data = response.json()
        assert "notes" in data, "Response should contain notes array"
        assert isinstance(data["notes"], list), "Notes should be a list"
        
        # If we created a note, verify it appears in the list
        if TestNotesCRUD.created_note_id:
            note_ids = [n["id"] for n in data["notes"]]
            assert TestNotesCRUD.created_note_id in note_ids, "Created note should appear in list"
            
            # Verify note structure
            note = next((n for n in data["notes"] if n["id"] == TestNotesCRUD.created_note_id), None)
            assert note is not None
            assert "title" in note
            assert "content" in note
            assert "created_at" in note
            assert "updated_at" in note
        
        print(f"Retrieved {len(data['notes'])} notes")
    
    def test_update_note(self, auth_headers):
        """PUT /api/charts/notes/{id} - Updates a note"""
        if not TestNotesCRUD.created_note_id:
            pytest.skip("No note created to update")
        
        update_data = {
            "title": f"TEST_Updated_Note_{datetime.now().strftime('%H%M%S')}",
            "content": "Updated content for the test note."
        }
        response = requests.put(
            f"{BASE_URL}/api/charts/notes/{TestNotesCRUD.created_note_id}",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == 200, f"Note update failed: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, "Update should return success"
        
        # Verify update by fetching notes
        get_response = requests.get(f"{BASE_URL}/api/charts/notes", headers=auth_headers)
        notes = get_response.json()["notes"]
        updated_note = next((n for n in notes if n["id"] == TestNotesCRUD.created_note_id), None)
        assert updated_note is not None
        assert updated_note["title"] == update_data["title"], "Title should be updated"
        assert updated_note["content"] == update_data["content"], "Content should be updated"
        
        print(f"Updated note: {updated_note['title']}")
    
    def test_delete_note(self, auth_headers):
        """DELETE /api/charts/notes/{id} - Deletes a note"""
        if not TestNotesCRUD.created_note_id:
            pytest.skip("No note created to delete")
        
        response = requests.delete(
            f"{BASE_URL}/api/charts/notes/{TestNotesCRUD.created_note_id}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Note deletion failed: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, "Delete should return success"
        
        # Verify deletion
        get_response = requests.get(f"{BASE_URL}/api/charts/notes", headers=auth_headers)
        notes = get_response.json()["notes"]
        note_ids = [n["id"] for n in notes]
        assert TestNotesCRUD.created_note_id not in note_ids, "Deleted note should not appear in list"
        
        print(f"Deleted note ID: {TestNotesCRUD.created_note_id}")
    
    def test_delete_nonexistent_note(self, auth_headers):
        """DELETE /api/charts/notes/{invalid_id} - Returns 404"""
        response = requests.delete(
            f"{BASE_URL}/api/charts/notes/000000000000000000000000",
            headers=auth_headers
        )
        assert response.status_code == 404, "Should return 404 for invalid note ID"
    
    def test_notes_requires_auth(self):
        """Notes endpoints require authentication"""
        # GET without auth
        response = requests.get(f"{BASE_URL}/api/charts/notes")
        assert response.status_code in [401, 403], "GET notes should require auth"
        
        # POST without auth
        response = requests.post(f"{BASE_URL}/api/charts/notes", json={"title": "Test", "content": "Test"})
        assert response.status_code in [401, 403], "POST notes should require auth"


class TestReportsListing:
    """Test Reports listing endpoint"""
    
    def test_get_reports(self, auth_headers):
        """GET /api/charts/reports - Returns reports list"""
        response = requests.get(f"{BASE_URL}/api/charts/reports", headers=auth_headers)
        assert response.status_code == 200, f"Get reports failed: {response.text}"
        
        data = response.json()
        assert "reports" in data, "Response should contain reports array"
        assert isinstance(data["reports"], list), "Reports should be a list"
        
        # User should have at least one file/report
        if len(data["reports"]) > 0:
            report = data["reports"][0]
            assert "id" in report, "Report should have id"
            assert "filename" in report, "Report should have filename"
            assert "source_type" in report, "Report should have source_type"
            assert "total_rows" in report, "Report should have total_rows"
            assert "total_columns" in report, "Report should have total_columns"
            assert "has_charts" in report, "Report should have has_charts flag"
            print(f"Found report: {report['filename']} ({report['total_rows']} rows x {report['total_columns']} cols)")
        
        print(f"Retrieved {len(data['reports'])} reports")
    
    def test_reports_requires_auth(self):
        """GET /api/charts/reports - Requires authentication"""
        response = requests.get(f"{BASE_URL}/api/charts/reports")
        assert response.status_code in [401, 403], "Should require authentication"


class TestDashboardAIChat:
    """Test AI Chat on dashboard (without workspace context)"""
    
    def test_dashboard_ai_chat(self, auth_headers):
        """POST /api/ai/chat - Works without workspace_id (global dashboard context)"""
        response = requests.post(
            f"{BASE_URL}/api/ai/chat",
            json={"query": "Hello, what can you help me with?"},
            headers=auth_headers
        )
        assert response.status_code == 200, f"Dashboard AI chat failed: {response.text}"
        
        data = response.json()
        assert "answer" in data, "Response should contain answer"
        assert "session_id" in data, "Response should contain session_id"
        assert len(data["answer"]) > 0, "Answer should not be empty"
        print(f"AI Response (first 100 chars): {data['answer'][:100]}...")
    
    def test_dashboard_ai_chat_multiturn(self, auth_headers):
        """POST /api/ai/chat - Multi-turn conversation on dashboard"""
        # First message
        response1 = requests.post(
            f"{BASE_URL}/api/ai/chat",
            json={"query": "Remember my name is TestBot"},
            headers=auth_headers
        )
        assert response1.status_code == 200
        session_id = response1.json().get("session_id")
        
        # Second message with session continuity
        response2 = requests.post(
            f"{BASE_URL}/api/ai/chat",
            json={"query": "What was my name again?", "session_id": session_id},
            headers=auth_headers
        )
        assert response2.status_code == 200
        answer = response2.json()["answer"]
        # AI should remember the name from the previous message
        print(f"Multi-turn response: {answer[:150]}...")


class TestDashboardSummary:
    """Test Dashboard Summary endpoint"""
    
    def test_get_dashboard_summary(self, auth_headers):
        """GET /api/dashboard/summary - Returns dashboard stats"""
        response = requests.get(f"{BASE_URL}/api/dashboard/summary", headers=auth_headers)
        assert response.status_code == 200, f"Dashboard summary failed: {response.text}"
        
        data = response.json()
        # Verify expected fields exist
        expected_fields = ["workspaces", "total_files"]
        for field in expected_fields:
            assert field in data, f"Summary should contain {field}"
        
        print(f"Dashboard Summary: {data}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
