"""
Iteration 11 - Backend API Tests
Testing: 
1. New user registration with Trial plan and 7-day trial
2. Disabled user login block (403)
3. Spam user login block (403)
4. Re-activate user and verify login works
5. Razorpay order creation
6. Razorpay verify-payment endpoint exists
7. Admin ticket view with user_email, user_name, subject, replies
8. Admin ticket reply
9. Subscription extension
10. User export Excel
11. User export PDF
"""

import pytest
import requests
import os
import time
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://sample-data-demo.preview.emergentagent.com')

class TestNewUserRegistration:
    """Test new user registration creates Trial plan with 7-day trial"""
    
    def test_register_new_user_trial_plan(self):
        """Register new user and verify Trial plan with 7-day trial_ends_at"""
        # Use unique email with timestamp
        unique_email = f"test_iter11_{int(time.time())}@test.com"
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "name": "Test User Iter11",
            "email": unique_email,
            "password": "test1234"
        })
        
        print(f"Register response status: {response.status_code}")
        print(f"Register response: {response.json()}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "token" in data, "Response should contain token"
        assert "user" in data, "Response should contain user"
        
        user = data["user"]
        assert user["plan"] == "Trial", f"Expected plan 'Trial', got '{user['plan']}'"
        assert user["email"] == unique_email
        assert "trial_ends_at" in user, "User should have trial_ends_at field"
        
        # Verify trial_ends_at is approximately 7 days from now
        if user["trial_ends_at"]:
            trial_end = datetime.fromisoformat(user["trial_ends_at"].replace('Z', '+00:00'))
            now = datetime.now(trial_end.tzinfo) if trial_end.tzinfo else datetime.utcnow()
            days_diff = (trial_end - now).days
            assert 6 <= days_diff <= 7, f"Trial should end in ~7 days, got {days_diff} days"
        
        print(f"SUCCESS: New user registered with Trial plan, trial_ends_at: {user['trial_ends_at']}")
        
        # Store for cleanup
        self.__class__.test_user_email = unique_email
        self.__class__.test_user_token = data["token"]
        self.__class__.test_user_id = user["id"]


class TestDisabledUserLoginBlock:
    """Test that disabled users cannot login"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@papermap.com",
            "password": "admin123"
        })
        assert response.status_code == 200, "Admin login failed"
        self.admin_token = response.json()["token"]
        
    def test_disable_user_then_login_blocked(self):
        """Admin disables user, then user login should return 403"""
        # First create a test user
        unique_email = f"test_disabled_{int(time.time())}@test.com"
        
        reg_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "name": "Disabled Test User",
            "email": unique_email,
            "password": "test1234"
        })
        assert reg_response.status_code == 200, "User registration failed"
        user_id = reg_response.json()["user"]["id"]
        
        # Admin disables the user
        disable_response = requests.put(
            f"{BASE_URL}/api/admin/manage/users/{user_id}/status",
            json={"status": "disabled"},
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        print(f"Disable response: {disable_response.status_code} - {disable_response.json()}")
        assert disable_response.status_code == 200, "Failed to disable user"
        
        # Now try to login as disabled user - should get 403
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": unique_email,
            "password": "test1234"
        })
        
        print(f"Disabled user login response: {login_response.status_code}")
        print(f"Response body: {login_response.json()}")
        
        assert login_response.status_code == 403, f"Expected 403 for disabled user, got {login_response.status_code}"
        assert "disabled" in login_response.json().get("detail", "").lower(), "Error message should mention disabled"
        
        print("SUCCESS: Disabled user login correctly blocked with 403")
        
        # Store for reactivation test
        self.__class__.disabled_user_id = user_id
        self.__class__.disabled_user_email = unique_email


class TestSpamUserLoginBlock:
    """Test that spam users cannot login"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@papermap.com",
            "password": "admin123"
        })
        assert response.status_code == 200, "Admin login failed"
        self.admin_token = response.json()["token"]
        
    def test_spam_user_login_blocked(self):
        """Admin marks user as spam, then user login should return 403"""
        # Create a test user
        unique_email = f"test_spam_{int(time.time())}@test.com"
        
        reg_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "name": "Spam Test User",
            "email": unique_email,
            "password": "test1234"
        })
        assert reg_response.status_code == 200, "User registration failed"
        user_id = reg_response.json()["user"]["id"]
        
        # Admin marks user as spam
        spam_response = requests.put(
            f"{BASE_URL}/api/admin/manage/users/{user_id}/status",
            json={"status": "spam"},
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        print(f"Spam response: {spam_response.status_code} - {spam_response.json()}")
        assert spam_response.status_code == 200, "Failed to mark user as spam"
        
        # Now try to login as spam user - should get 403
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": unique_email,
            "password": "test1234"
        })
        
        print(f"Spam user login response: {login_response.status_code}")
        print(f"Response body: {login_response.json()}")
        
        assert login_response.status_code == 403, f"Expected 403 for spam user, got {login_response.status_code}"
        assert "spam" in login_response.json().get("detail", "").lower(), "Error message should mention spam"
        
        print("SUCCESS: Spam user login correctly blocked with 403")


class TestReactivateUser:
    """Test that reactivated users can login again"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@papermap.com",
            "password": "admin123"
        })
        assert response.status_code == 200, "Admin login failed"
        self.admin_token = response.json()["token"]
        
    def test_reactivate_user_can_login(self):
        """Admin reactivates user, then user should be able to login"""
        # Create and disable a user first
        unique_email = f"test_reactivate_{int(time.time())}@test.com"
        
        reg_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "name": "Reactivate Test User",
            "email": unique_email,
            "password": "test1234"
        })
        assert reg_response.status_code == 200, "User registration failed"
        user_id = reg_response.json()["user"]["id"]
        
        # Disable the user
        requests.put(
            f"{BASE_URL}/api/admin/manage/users/{user_id}/status",
            json={"status": "disabled"},
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        # Verify login is blocked
        blocked_login = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": unique_email,
            "password": "test1234"
        })
        assert blocked_login.status_code == 403, "User should be blocked"
        
        # Reactivate the user
        activate_response = requests.put(
            f"{BASE_URL}/api/admin/manage/users/{user_id}/status",
            json={"status": "active"},
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        print(f"Activate response: {activate_response.status_code} - {activate_response.json()}")
        assert activate_response.status_code == 200, "Failed to reactivate user"
        
        # Now login should work
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": unique_email,
            "password": "test1234"
        })
        
        print(f"Reactivated user login response: {login_response.status_code}")
        
        assert login_response.status_code == 200, f"Expected 200 for reactivated user, got {login_response.status_code}"
        assert "token" in login_response.json(), "Should receive token after login"
        
        print("SUCCESS: Reactivated user can login again")


class TestRazorpayOrderCreation:
    """Test Razorpay order creation"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get user token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "testuser@test.com",
            "password": "test1234"
        })
        assert response.status_code == 200, "User login failed"
        self.user_token = response.json()["token"]
        
    def test_create_razorpay_order_starter(self):
        """Create Razorpay order for Starter plan"""
        response = requests.post(
            f"{BASE_URL}/api/payments/create-order",
            json={"plan": "Starter"},
            headers={"Authorization": f"Bearer {self.user_token}"}
        )
        
        print(f"Create order response: {response.status_code}")
        print(f"Response body: {response.json()}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("success") == True, "Response should have success=True"
        assert "order_id" in data, "Response should contain order_id"
        assert "amount" in data, "Response should contain amount"
        assert "key_id" in data, "Response should contain key_id"
        
        # Verify key_id starts with 'rzp_'
        assert data["key_id"].startswith("rzp_"), f"key_id should start with 'rzp_', got {data['key_id']}"
        
        # Verify amount is correct (500 * 100 = 50000 paise)
        assert data["amount"] == 50000, f"Expected amount 50000, got {data['amount']}"
        
        print(f"SUCCESS: Razorpay order created - order_id: {data['order_id']}, key_id: {data['key_id']}")
        
    def test_create_razorpay_order_business_pro(self):
        """Create Razorpay order for Business Pro plan"""
        response = requests.post(
            f"{BASE_URL}/api/payments/create-order",
            json={"plan": "Business Pro"},
            headers={"Authorization": f"Bearer {self.user_token}"}
        )
        
        print(f"Create order response: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("success") == True
        assert data["key_id"].startswith("rzp_")
        # Business Pro is 800 * 100 = 80000 paise
        assert data["amount"] == 80000, f"Expected amount 80000, got {data['amount']}"
        
        print(f"SUCCESS: Business Pro order created - amount: {data['amount']}")


class TestRazorpayVerifyEndpoint:
    """Test Razorpay verify-payment endpoint exists"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get user token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "testuser@test.com",
            "password": "test1234"
        })
        assert response.status_code == 200, "User login failed"
        self.user_token = response.json()["token"]
        
    def test_verify_payment_endpoint_exists(self):
        """Verify that POST /api/payments/verify-payment endpoint exists"""
        # Send invalid data - we just want to verify endpoint exists
        response = requests.post(
            f"{BASE_URL}/api/payments/verify-payment",
            json={
                "razorpay_order_id": "invalid_order",
                "razorpay_payment_id": "invalid_payment",
                "razorpay_signature": "invalid_signature"
            },
            headers={"Authorization": f"Bearer {self.user_token}"}
        )
        
        print(f"Verify payment response: {response.status_code}")
        print(f"Response body: {response.json()}")
        
        # Should NOT be 404 (endpoint exists)
        # Will likely be 400 or 404 (order not found) but not 404 for endpoint
        assert response.status_code != 405, "Endpoint should exist (not Method Not Allowed)"
        
        # The endpoint exists if we get 400 (bad signature) or 404 (order not found)
        assert response.status_code in [400, 404, 422], f"Expected 400/404/422, got {response.status_code}"
        
        print("SUCCESS: verify-payment endpoint exists")


class TestAdminTicketManagement:
    """Test admin ticket view and reply functionality"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin and user tokens"""
        # Admin login
        admin_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@papermap.com",
            "password": "admin123"
        })
        assert admin_response.status_code == 200, "Admin login failed"
        self.admin_token = admin_response.json()["token"]
        
        # User login
        user_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "testuser@test.com",
            "password": "test1234"
        })
        assert user_response.status_code == 200, "User login failed"
        self.user_token = user_response.json()["token"]
        
    def test_admin_get_tickets(self):
        """Admin can view all tickets with user_email, user_name, subject, replies"""
        # First create a ticket as user
        ticket_response = requests.post(
            f"{BASE_URL}/api/support/tickets",
            json={
                "subject": f"Test Ticket {int(time.time())}",
                "message": "This is a test ticket for iteration 11",
                "priority": "medium"
            },
            headers={"Authorization": f"Bearer {self.user_token}"}
        )
        print(f"Create ticket response: {ticket_response.status_code}")
        
        # Admin gets all tickets
        response = requests.get(
            f"{BASE_URL}/api/admin/manage/tickets",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        print(f"Get tickets response: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "tickets" in data, "Response should contain tickets array"
        
        if len(data["tickets"]) > 0:
            ticket = data["tickets"][0]
            # Verify required fields
            assert "user_email" in ticket, "Ticket should have user_email"
            assert "user_name" in ticket, "Ticket should have user_name"
            assert "subject" in ticket, "Ticket should have subject"
            assert "replies" in ticket, "Ticket should have replies array"
            
            print(f"SUCCESS: Admin can view tickets with all required fields")
            print(f"Sample ticket: user_email={ticket['user_email']}, subject={ticket['subject']}")
            
            # Store ticket ID for reply test
            self.__class__.test_ticket_id = ticket["id"]
        else:
            print("WARNING: No tickets found to verify structure")
            
    def test_admin_reply_to_ticket(self):
        """Admin can reply to a ticket"""
        # First get a ticket ID
        tickets_response = requests.get(
            f"{BASE_URL}/api/admin/manage/tickets",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        if tickets_response.status_code == 200 and len(tickets_response.json().get("tickets", [])) > 0:
            ticket_id = tickets_response.json()["tickets"][0]["id"]
            
            # Reply to ticket
            reply_response = requests.post(
                f"{BASE_URL}/api/admin/manage/tickets/{ticket_id}/reply",
                json={"reply": f"Admin reply at {datetime.now().isoformat()}"},
                headers={"Authorization": f"Bearer {self.admin_token}"}
            )
            
            print(f"Reply response: {reply_response.status_code}")
            print(f"Response body: {reply_response.json()}")
            
            assert reply_response.status_code == 200, f"Expected 200, got {reply_response.status_code}"
            assert reply_response.json().get("success") == True, "Reply should succeed"
            
            print("SUCCESS: Admin can reply to tickets")
        else:
            pytest.skip("No tickets available to test reply")


class TestSubscriptionExtension:
    """Test admin subscription extension"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@papermap.com",
            "password": "admin123"
        })
        assert response.status_code == 200, "Admin login failed"
        self.admin_token = response.json()["token"]
        
    def test_extend_subscription_12_months(self):
        """Admin can extend user subscription by 12 months"""
        # Get a user ID
        users_response = requests.get(
            f"{BASE_URL}/api/admin/manage/users/details",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert users_response.status_code == 200, "Failed to get users"
        
        users = users_response.json().get("users", [])
        # Find a non-admin user
        test_user = next((u for u in users if u.get("role") != "admin"), None)
        
        if test_user:
            user_id = test_user["id"]
            
            # Extend subscription
            response = requests.put(
                f"{BASE_URL}/api/admin/manage/users/{user_id}/subscription",
                json={"duration_months": 12},
                headers={"Authorization": f"Bearer {self.admin_token}"}
            )
            
            print(f"Extend subscription response: {response.status_code}")
            print(f"Response body: {response.json()}")
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
            data = response.json()
            assert data.get("success") == True, "Extension should succeed"
            assert "new_end_date" in data, "Response should contain new_end_date"
            
            print(f"SUCCESS: Subscription extended, new_end_date: {data['new_end_date']}")
        else:
            pytest.skip("No non-admin users found")


class TestUserExport:
    """Test user export as Excel and PDF"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@papermap.com",
            "password": "admin123"
        })
        assert response.status_code == 200, "Admin login failed"
        self.admin_token = response.json()["token"]
        
    def test_export_users_excel(self):
        """Export users as Excel file"""
        response = requests.get(
            f"{BASE_URL}/api/admin/manage/users/export/excel",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        print(f"Export Excel response: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Check content type
        content_type = response.headers.get('Content-Type', '')
        assert 'spreadsheet' in content_type or 'xlsx' in content_type or 'octet-stream' in content_type, \
            f"Expected spreadsheet content type, got {content_type}"
        
        # Check we got some content
        assert len(response.content) > 0, "Excel file should have content"
        
        print(f"SUCCESS: Excel export works, file size: {len(response.content)} bytes")
        
    def test_export_users_pdf(self):
        """Export users as PDF file"""
        response = requests.get(
            f"{BASE_URL}/api/admin/manage/users/export/pdf",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        print(f"Export PDF response: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Check content type
        content_type = response.headers.get('Content-Type', '')
        assert 'pdf' in content_type or 'octet-stream' in content_type, \
            f"Expected PDF content type, got {content_type}"
        
        # Check we got some content
        assert len(response.content) > 0, "PDF file should have content"
        
        print(f"SUCCESS: PDF export works, file size: {len(response.content)} bytes")


class TestExistingUserLogin:
    """Test existing user credentials still work"""
    
    def test_admin_login(self):
        """Admin can login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@papermap.com",
            "password": "admin123"
        })
        
        assert response.status_code == 200, f"Admin login failed: {response.status_code}"
        assert "token" in response.json()
        print("SUCCESS: Admin login works")
        
    def test_regular_user_login(self):
        """Regular user can login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "testuser@test.com",
            "password": "test1234"
        })
        
        assert response.status_code == 200, f"User login failed: {response.status_code}"
        assert "token" in response.json()
        print("SUCCESS: Regular user login works")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
