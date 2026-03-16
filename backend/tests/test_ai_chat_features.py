"""
Test AI Chat Features - Interactive multi-turn conversation
Iteration 8: Testing new ChatGPT-like chat interface
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_USER_EMAIL = "testpay@analiyx.com"
TEST_USER_PASSWORD = "test1234"
TEST_WORKSPACE_ID = "69b7a0e32859d535c59a7a6b"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for test user"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    assert "token" in data, "No token in login response"
    return data["token"]


@pytest.fixture(scope="module")
def api_client(auth_token):
    """Authenticated requests session"""
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}"
    })
    return session


class TestAIChatEndpoint:
    """Tests for POST /api/ai/chat - Multi-turn chat"""
    
    def test_chat_basic_query(self, api_client):
        """Test basic chat query to /api/ai/chat"""
        response = api_client.post(f"{BASE_URL}/api/ai/chat", json={
            "query": "Hello, what data do I have?",
            "workspace_id": TEST_WORKSPACE_ID
        })
        
        assert response.status_code == 200, f"Chat failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "answer" in data, "Response missing 'answer' field"
        assert "sources" in data, "Response missing 'sources' field"
        assert "session_id" in data, "Response missing 'session_id' field"
        
        # Verify session_id format
        assert data["session_id"].startswith("chat_"), "Session ID should start with 'chat_'"
        assert TEST_WORKSPACE_ID in data["session_id"], "Session ID should contain workspace_id"
        
        print(f"✓ Chat response received with session_id: {data['session_id']}")
        print(f"✓ Answer length: {len(data['answer'])} chars")
        print(f"✓ Sources: {data['sources']}")
    
    def test_chat_with_session_id(self, api_client):
        """Test chat maintains context with session_id"""
        # First message
        response1 = api_client.post(f"{BASE_URL}/api/ai/chat", json={
            "query": "What columns are in my data?",
            "workspace_id": TEST_WORKSPACE_ID
        })
        assert response1.status_code == 200
        session_id = response1.json()["session_id"]
        
        # Follow-up message with same session
        response2 = api_client.post(f"{BASE_URL}/api/ai/chat", json={
            "query": "Can you tell me more about the first column?",
            "workspace_id": TEST_WORKSPACE_ID,
            "session_id": session_id
        })
        
        assert response2.status_code == 200, f"Follow-up failed: {response2.text}"
        data = response2.json()
        
        # Session ID should remain the same
        assert data["session_id"] == session_id, "Session ID changed unexpectedly"
        assert len(data["answer"]) > 0, "Empty follow-up response"
        
        print(f"✓ Follow-up response maintains session: {session_id}")
    
    def test_chat_empty_query_rejected(self, api_client):
        """Test that empty query returns 400"""
        response = api_client.post(f"{BASE_URL}/api/ai/chat", json={
            "query": "",
            "workspace_id": TEST_WORKSPACE_ID
        })
        
        assert response.status_code == 400, f"Expected 400 for empty query, got {response.status_code}"
        print("✓ Empty query correctly rejected with 400")
    
    def test_chat_whitespace_query_rejected(self, api_client):
        """Test that whitespace-only query returns 400"""
        response = api_client.post(f"{BASE_URL}/api/ai/chat", json={
            "query": "   ",
            "workspace_id": TEST_WORKSPACE_ID
        })
        
        assert response.status_code == 400, f"Expected 400 for whitespace query, got {response.status_code}"
        print("✓ Whitespace query correctly rejected with 400")
    
    def test_chat_without_workspace_id(self, api_client):
        """Test chat works without workspace_id (global context)"""
        response = api_client.post(f"{BASE_URL}/api/ai/chat", json={
            "query": "What data do I have?"
        })
        
        assert response.status_code == 200, f"Global chat failed: {response.text}"
        data = response.json()
        assert "session_id" in data
        assert "global" in data["session_id"] or data["session_id"].endswith("_global"), \
            f"Expected global session, got: {data['session_id']}"
        
        print(f"✓ Global chat works without workspace_id")


class TestChatHistoryEndpoint:
    """Tests for GET /api/ai/chat/history/{workspace_id}"""
    
    def test_get_chat_history(self, api_client):
        """Test retrieving chat history for a workspace"""
        response = api_client.get(f"{BASE_URL}/api/ai/chat/history/{TEST_WORKSPACE_ID}")
        
        assert response.status_code == 200, f"Get history failed: {response.text}"
        data = response.json()
        
        assert "history" in data, "Response missing 'history' field"
        assert isinstance(data["history"], list), "History should be a list"
        
        # Check history structure if not empty
        if len(data["history"]) > 0:
            first_msg = data["history"][0]
            assert "role" in first_msg, "History item missing 'role'"
            assert "content" in first_msg, "History item missing 'content'"
            assert "timestamp" in first_msg, "History item missing 'timestamp'"
            assert first_msg["role"] in ["user", "assistant"], f"Invalid role: {first_msg['role']}"
        
        print(f"✓ Chat history retrieved: {len(data['history'])} messages")
    
    def test_chat_history_requires_auth(self):
        """Test that chat history requires authentication"""
        response = requests.get(f"{BASE_URL}/api/ai/chat/history/{TEST_WORKSPACE_ID}")
        
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ Chat history correctly requires authentication")


class TestLegacySearchEndpoint:
    """Tests for POST /api/ai/search - Backward compatible legacy endpoint"""
    
    def test_legacy_search_endpoint(self, api_client):
        """Test legacy /api/ai/search still works"""
        response = api_client.post(f"{BASE_URL}/api/ai/search", json={
            "query": "Summarize my data",
            "workspace_id": TEST_WORKSPACE_ID
        })
        
        assert response.status_code == 200, f"Legacy search failed: {response.text}"
        data = response.json()
        
        # Should have same response structure as chat
        assert "answer" in data, "Legacy search missing 'answer'"
        assert "sources" in data, "Legacy search missing 'sources'"
        assert "session_id" in data, "Legacy search missing 'session_id'"
        
        print(f"✓ Legacy /api/ai/search still works")
        print(f"✓ Answer preview: {data['answer'][:100]}...")


class TestChatAuthAndPermissions:
    """Tests for authentication and permissions"""
    
    def test_chat_requires_auth(self):
        """Test chat requires authentication"""
        response = requests.post(f"{BASE_URL}/api/ai/chat", json={
            "query": "test",
            "workspace_id": TEST_WORKSPACE_ID
        })
        
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ Chat endpoint correctly requires authentication")
    
    def test_legacy_search_requires_auth(self):
        """Test legacy search requires authentication"""
        response = requests.post(f"{BASE_URL}/api/ai/search", json={
            "query": "test",
            "workspace_id": TEST_WORKSPACE_ID
        })
        
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✓ Legacy search correctly requires authentication")


# Additional tests for edge cases
class TestChatEdgeCases:
    """Edge case tests"""
    
    def test_chat_with_invalid_workspace_id(self, api_client):
        """Test chat with invalid workspace ID format"""
        response = api_client.post(f"{BASE_URL}/api/ai/chat", json={
            "query": "test query",
            "workspace_id": "invalid-id"
        })
        
        # Should return 400 or 500 for invalid ObjectId
        assert response.status_code in [400, 422, 500], \
            f"Expected error status for invalid workspace ID, got {response.status_code}"
        print("✓ Invalid workspace ID handled correctly")
    
    def test_chat_history_with_invalid_workspace(self, api_client):
        """Test chat history with invalid workspace ID"""
        response = api_client.get(f"{BASE_URL}/api/ai/chat/history/invalid-id")
        
        assert response.status_code in [400, 422, 500], \
            f"Expected error for invalid workspace ID in history, got {response.status_code}"
        print("✓ Invalid workspace ID in history handled correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
