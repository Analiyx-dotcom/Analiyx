"""
Test AI Visibility and Cashfree Payment Integration APIs - Iteration 3
Tests for items 17-19: AI Visibility (GPT-5.2 analysis), Cashfree payment order creation
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@papermap.com"
ADMIN_PASSWORD = "admin123"
TEST_USER_EMAIL = "testuser@analiyx.com"
TEST_USER_PASSWORD = "test1234"


@pytest.fixture(scope="module")
def user_token():
    """Get user auth token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    })
    if response.status_code != 200:
        pytest.skip(f"User login failed: {response.text}")
    return response.json()["token"]


@pytest.fixture(scope="module")
def admin_token():
    """Get admin auth token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code != 200:
        pytest.skip(f"Admin login failed: {response.text}")
    return response.json()["token"]


class TestAIVisibilityAPI:
    """Test AI Visibility URL analysis endpoint - Uses GPT-5.2"""
    
    def test_analyze_url_simple_site(self, user_token):
        """POST /api/ai-visibility/analyze analyzes a URL and returns scores"""
        # Use a simple site that will load quickly
        response = requests.post(
            f"{BASE_URL}/api/ai-visibility/analyze",
            json={"url": "https://example.com"},
            headers={"Authorization": f"Bearer {user_token}"},
            timeout=30  # GPT-5.2 call can take time
        )
        assert response.status_code == 200, f"AI analysis failed: {response.text}"
        
        data = response.json()
        assert data["success"] == True
        assert "url" in data
        assert "analysis" in data
        
        analysis = data["analysis"]
        # Verify all required score fields
        assert "overall_score" in analysis, "Missing overall_score"
        assert "seo_score" in analysis, "Missing seo_score"
        assert "ai_visibility_score" in analysis, "Missing ai_visibility_score"
        assert "content_quality_score" in analysis, "Missing content_quality_score"
        assert "technical_seo_score" in analysis, "Missing technical_seo_score"
        
        # Verify scores are numbers between 0-100
        for score_key in ["overall_score", "seo_score", "ai_visibility_score", "content_quality_score", "technical_seo_score"]:
            score = analysis[score_key]
            assert isinstance(score, (int, float)), f"{score_key} should be a number"
            assert 0 <= score <= 100, f"{score_key} should be 0-100, got {score}"
        
        # Verify arrays exist
        assert "strengths" in analysis, "Missing strengths"
        assert "improvements" in analysis, "Missing improvements"
        assert "ai_recommendations" in analysis, "Missing ai_recommendations"
        
        print(f"✓ AI Visibility analysis complete:")
        print(f"  Overall Score: {analysis['overall_score']}/100")
        print(f"  SEO Score: {analysis['seo_score']}/100")
        print(f"  AI Visibility Score: {analysis['ai_visibility_score']}/100")
    
    def test_analyze_url_without_https(self, user_token):
        """API should handle URLs without https prefix"""
        response = requests.post(
            f"{BASE_URL}/api/ai-visibility/analyze",
            json={"url": "example.com"},  # No https://
            headers={"Authorization": f"Bearer {user_token}"},
            timeout=30
        )
        assert response.status_code == 200, f"URL without https failed: {response.text}"
        
        data = response.json()
        assert data["success"] == True
        assert "analysis" in data
        print(f"✓ URL without https:// prefix handled correctly")
    
    def test_analyze_url_requires_auth(self):
        """POST /api/ai-visibility/analyze requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/ai-visibility/analyze",
            json={"url": "https://example.com"}
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"✓ AI Visibility correctly requires authentication")
    
    def test_analyze_url_empty(self, user_token):
        """API rejects empty URL"""
        response = requests.post(
            f"{BASE_URL}/api/ai-visibility/analyze",
            json={"url": ""},
            headers={"Authorization": f"Bearer {user_token}"}
        )
        # Could be 400 or 422 depending on validation
        assert response.status_code in [400, 422], f"Expected 400/422 for empty URL, got {response.status_code}"
        print(f"✓ Empty URL correctly rejected")
    
    def test_get_analysis_history(self, user_token):
        """GET /api/ai-visibility/history returns previous analyses"""
        response = requests.get(
            f"{BASE_URL}/api/ai-visibility/history",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200, f"Get history failed: {response.text}"
        
        data = response.json()
        assert "analyses" in data
        assert isinstance(data["analyses"], list)
        
        if len(data["analyses"]) > 0:
            entry = data["analyses"][0]
            assert "url" in entry
            assert "analysis" in entry
            print(f"✓ AI analysis history: {len(data['analyses'])} entries")
        else:
            print(f"✓ AI analysis history endpoint works (0 entries)")


class TestCashfreePaymentAPI:
    """Test Cashfree payment order creation - Uses PRODUCTION API"""
    
    def test_create_payment_order_starter(self, user_token):
        """POST /api/payments/create-order creates Cashfree order for Starter plan"""
        response = requests.post(
            f"{BASE_URL}/api/payments/create-order",
            json={
                "plan": "Starter",
                "return_url": "https://insights-hub-44.preview.emergentagent.com"
            },
            headers={"Authorization": f"Bearer {user_token}"},
            timeout=15
        )
        assert response.status_code == 200, f"Payment order creation failed: {response.text}"
        
        data = response.json()
        assert data["success"] == True
        assert "order_id" in data, "Missing order_id"
        assert "cf_order_id" in data, "Missing cf_order_id (Cashfree order ID)"
        assert "payment_session_id" in data, "Missing payment_session_id"
        assert "order_amount" in data
        assert "order_currency" in data
        
        # Verify amount and currency
        assert data["order_amount"] == 2999, f"Expected 2999 for Starter, got {data['order_amount']}"
        assert data["order_currency"] == "INR", f"Expected INR, got {data['order_currency']}"
        
        print(f"✓ Cashfree payment order created:")
        print(f"  Order ID: {data['order_id']}")
        print(f"  CF Order ID: {data['cf_order_id']}")
        print(f"  Amount: ₹{data['order_amount']}")
        print(f"  Payment Session ID present: {bool(data['payment_session_id'])}")
    
    def test_create_payment_order_business_pro(self, user_token):
        """POST /api/payments/create-order creates order for Business Pro plan"""
        response = requests.post(
            f"{BASE_URL}/api/payments/create-order",
            json={
                "plan": "Business Pro",
                "return_url": "https://insights-hub-44.preview.emergentagent.com"
            },
            headers={"Authorization": f"Bearer {user_token}"},
            timeout=15
        )
        assert response.status_code == 200, f"Business Pro order failed: {response.text}"
        
        data = response.json()
        assert data["success"] == True
        assert data["order_amount"] == 7999, f"Expected 7999 for Business Pro, got {data['order_amount']}"
        assert data["order_currency"] == "INR"
        print(f"✓ Business Pro order created: ₹{data['order_amount']}")
    
    def test_create_payment_order_invalid_plan(self, user_token):
        """POST /api/payments/create-order rejects invalid plan"""
        response = requests.post(
            f"{BASE_URL}/api/payments/create-order",
            json={
                "plan": "InvalidPlan",
                "return_url": "https://example.com"
            },
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 400, f"Expected 400 for invalid plan, got {response.status_code}"
        print(f"✓ Invalid plan correctly rejected")
    
    def test_create_payment_requires_auth(self):
        """POST /api/payments/create-order requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/payments/create-order",
            json={"plan": "Starter"}
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"✓ Payment order correctly requires authentication")


class TestPreviouslyWorkingFeatures:
    """Verify previously tested features still work (regression tests)"""
    
    def test_contact_form(self):
        """POST /api/contact still works"""
        response = requests.post(f"{BASE_URL}/api/contact", json={
            "name": "Regression Test",
            "email": "regression@test.com",
            "message": "Regression test for contact form"
        })
        assert response.status_code == 200
        print(f"✓ Contact form still working")
    
    def test_admin_stats(self, admin_token):
        """Admin stats endpoint still works"""
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
        assert "monthly_revenue" in data
        print(f"✓ Admin stats: {data['total_users']} users, revenue: {data['monthly_revenue']}")
    
    def test_workspaces_list(self, user_token):
        """Workspace list still works"""
        response = requests.get(
            f"{BASE_URL}/api/workspaces/list",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "workspaces" in data
        print(f"✓ Workspaces list: {len(data['workspaces'])} workspaces")
    
    def test_support_tickets_list(self, user_token):
        """Support tickets list still works"""
        response = requests.get(
            f"{BASE_URL}/api/support/tickets",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "tickets" in data
        print(f"✓ Support tickets: {len(data['tickets'])} tickets")
    
    def test_admin_user_management(self, admin_token):
        """Admin user management still works"""
        response = requests.get(
            f"{BASE_URL}/api/admin/manage/users/details",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        print(f"✓ Admin user management: {len(data['users'])} users")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
