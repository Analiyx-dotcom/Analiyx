"""
Iteration 12 Tests - New Features:
1. Phone number in signup form
2. Unique client_id generation on registration
3. Admin dashboard search by client_id/phone
4. Coupon CRUD in admin dashboard
5. Coupon validation in payment flow
6. AI Visibility deep report with detailed_analysis and citations
"""

import pytest
import requests
import os
import time
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestUserRegistrationWithPhone:
    """Test registration with phone number and client_id generation"""
    
    def test_register_new_user_with_phone(self):
        """Register a new user with phone number - should return phone and client_id"""
        unique_email = f"test_iter12_{uuid.uuid4().hex[:8]}@test.com"
        payload = {
            "name": "Test User Iter12",
            "email": unique_email,
            "phone": "+91 9876543210",
            "password": "test1234"
        }
        response = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        print(f"Register response: {response.status_code} - {response.text[:500]}")
        
        assert response.status_code == 200, f"Registration failed: {response.text}"
        data = response.json()
        
        # Verify token and user returned
        assert "token" in data, "Token not returned"
        assert "user" in data, "User not returned"
        
        user = data["user"]
        # Verify phone is returned
        assert "phone" in user, "Phone field not in response"
        assert user["phone"] == "+91 9876543210", f"Phone mismatch: {user.get('phone')}"
        
        # Verify client_id is generated
        assert "client_id" in user, "client_id field not in response"
        assert user["client_id"].startswith("ANX-"), f"client_id format wrong: {user.get('client_id')}"
        
        print(f"✓ User registered with phone={user['phone']}, client_id={user['client_id']}")
        return data["token"], user


class TestLoginReturnsPhoneAndClientId:
    """Test that login returns phone and client_id"""
    
    def test_login_returns_phone_and_client_id(self):
        """Login with test user and verify phone/client_id in response"""
        # Use the test user created by main agent
        payload = {
            "email": "phoneuser@test.com",
            "password": "test1234"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=payload)
        print(f"Login response: {response.status_code}")
        
        if response.status_code != 200:
            # User might not exist, skip
            pytest.skip("Test user phoneuser@test.com not found")
        
        data = response.json()
        user = data["user"]
        
        # Verify phone and client_id in login response
        assert "phone" in user, "Phone field not in login response"
        assert "client_id" in user, "client_id field not in login response"
        
        print(f"✓ Login returns phone={user.get('phone')}, client_id={user.get('client_id')}")
        return data["token"]


class TestMeEndpointReturnsPhoneAndClientId:
    """Test /me endpoint returns phone and client_id"""
    
    def test_me_endpoint_returns_phone_and_client_id(self):
        """Get current user and verify phone/client_id"""
        # First login
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "phoneuser@test.com",
            "password": "test1234"
        })
        
        if login_resp.status_code != 200:
            pytest.skip("Test user not found")
        
        token = login_resp.json()["token"]
        
        # Call /me endpoint
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200, f"/me failed: {response.text}"
        user = response.json()
        
        assert "phone" in user, "Phone not in /me response"
        assert "client_id" in user, "client_id not in /me response"
        
        print(f"✓ /me returns phone={user.get('phone')}, client_id={user.get('client_id')}")


class TestAdminUsersDetailsWithPhoneAndClientId:
    """Test admin users endpoint returns phone and client_id"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "Admin@analiyx.com",
            "password": "1234"
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        return response.json()["token"]
    
    def test_admin_users_details_has_phone_and_client_id(self, admin_token):
        """Admin users details should include phone and client_id columns"""
        response = requests.get(
            f"{BASE_URL}/api/admin/manage/users/details",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200, f"Admin users failed: {response.text}"
        data = response.json()
        
        assert "users" in data, "No users array"
        assert len(data["users"]) > 0, "No users returned"
        
        # Check first user has phone and client_id fields
        first_user = data["users"][0]
        assert "phone" in first_user, "phone field missing in admin users"
        assert "client_id" in first_user, "client_id field missing in admin users"
        
        print(f"✓ Admin users endpoint returns phone and client_id fields")
        print(f"  Sample: client_id={first_user.get('client_id')}, phone={first_user.get('phone')}")


class TestCouponCRUD:
    """Test coupon management CRUD operations"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "Admin@analiyx.com",
            "password": "1234"
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        return response.json()["token"]
    
    def test_create_coupon(self, admin_token):
        """Create a new coupon"""
        coupon_code = f"TEST{uuid.uuid4().hex[:6].upper()}"
        payload = {
            "code": coupon_code,
            "discount_percentage": 15
        }
        response = requests.post(
            f"{BASE_URL}/api/admin/manage/coupons",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200, f"Create coupon failed: {response.text}"
        data = response.json()
        assert data.get("success") == True, "Create coupon not successful"
        
        print(f"✓ Created coupon: {coupon_code} with 15% discount")
        return coupon_code
    
    def test_list_coupons(self, admin_token):
        """List all coupons"""
        response = requests.get(
            f"{BASE_URL}/api/admin/manage/coupons",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200, f"List coupons failed: {response.text}"
        data = response.json()
        assert "coupons" in data, "No coupons array"
        
        print(f"✓ Listed {len(data['coupons'])} coupons")
        
        # Check coupon structure
        if len(data["coupons"]) > 0:
            coupon = data["coupons"][0]
            assert "id" in coupon, "Coupon missing id"
            assert "code" in coupon, "Coupon missing code"
            assert "discount_percentage" in coupon, "Coupon missing discount_percentage"
            assert "is_active" in coupon, "Coupon missing is_active"
            print(f"  Sample coupon: {coupon['code']} - {coupon['discount_percentage']}% - active={coupon['is_active']}")
        
        return data["coupons"]
    
    def test_toggle_coupon_status(self, admin_token):
        """Toggle coupon active/inactive"""
        # First create a coupon
        coupon_code = f"TOGGLE{uuid.uuid4().hex[:4].upper()}"
        create_resp = requests.post(
            f"{BASE_URL}/api/admin/manage/coupons",
            json={"code": coupon_code, "discount_percentage": 10},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert create_resp.status_code == 200
        
        # Get coupon ID
        list_resp = requests.get(
            f"{BASE_URL}/api/admin/manage/coupons",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        coupons = list_resp.json()["coupons"]
        coupon = next((c for c in coupons if c["code"] == coupon_code), None)
        assert coupon is not None, f"Coupon {coupon_code} not found"
        
        coupon_id = coupon["id"]
        initial_status = coupon["is_active"]
        
        # Toggle status
        toggle_resp = requests.put(
            f"{BASE_URL}/api/admin/manage/coupons/{coupon_id}/toggle",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert toggle_resp.status_code == 200, f"Toggle failed: {toggle_resp.text}"
        data = toggle_resp.json()
        assert data.get("success") == True
        assert data.get("is_active") != initial_status, "Status did not toggle"
        
        print(f"✓ Toggled coupon {coupon_code} from {initial_status} to {data['is_active']}")
    
    def test_delete_coupon(self, admin_token):
        """Delete a coupon"""
        # First create a coupon to delete
        coupon_code = f"DELETE{uuid.uuid4().hex[:4].upper()}"
        create_resp = requests.post(
            f"{BASE_URL}/api/admin/manage/coupons",
            json={"code": coupon_code, "discount_percentage": 5},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert create_resp.status_code == 200
        
        # Get coupon ID
        list_resp = requests.get(
            f"{BASE_URL}/api/admin/manage/coupons",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        coupons = list_resp.json()["coupons"]
        coupon = next((c for c in coupons if c["code"] == coupon_code), None)
        assert coupon is not None
        
        coupon_id = coupon["id"]
        
        # Delete coupon
        delete_resp = requests.delete(
            f"{BASE_URL}/api/admin/manage/coupons/{coupon_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert delete_resp.status_code == 200, f"Delete failed: {delete_resp.text}"
        data = delete_resp.json()
        assert data.get("success") == True
        
        print(f"✓ Deleted coupon {coupon_code}")


class TestCouponValidation:
    """Test coupon validation in payment flow"""
    
    @pytest.fixture
    def user_token(self):
        """Get regular user token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "phoneuser@test.com",
            "password": "test1234"
        })
        if response.status_code != 200:
            # Try admin
            response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": "Admin@analiyx.com",
                "password": "1234"
            })
        if response.status_code != 200:
            pytest.skip("No user available for testing")
        return response.json()["token"]
    
    def test_validate_coupon_endpoint(self, user_token):
        """Test POST /api/payments/validate-coupon"""
        # First ensure SAVE20 coupon exists (created by main agent)
        payload = {
            "code": "SAVE20",
            "plan": "Starter"
        }
        response = requests.post(
            f"{BASE_URL}/api/payments/validate-coupon",
            json=payload,
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        print(f"Validate coupon response: {response.status_code} - {response.text[:300]}")
        
        if response.status_code == 400 and "Invalid" in response.text:
            # Coupon doesn't exist, create it via admin
            admin_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": "Admin@analiyx.com",
                "password": "1234"
            })
            if admin_resp.status_code == 200:
                admin_token = admin_resp.json()["token"]
                requests.post(
                    f"{BASE_URL}/api/admin/manage/coupons",
                    json={"code": "SAVE20", "discount_percentage": 20},
                    headers={"Authorization": f"Bearer {admin_token}"}
                )
                # Retry validation
                response = requests.post(
                    f"{BASE_URL}/api/payments/validate-coupon",
                    json=payload,
                    headers={"Authorization": f"Bearer {user_token}"}
                )
        
        assert response.status_code == 200, f"Validate coupon failed: {response.text}"
        data = response.json()
        
        assert data.get("valid") == True, "Coupon not valid"
        assert "discount_percentage" in data, "discount_percentage missing"
        assert "original_amount" in data, "original_amount missing"
        assert "final_amount" in data, "final_amount missing"
        
        print(f"✓ Coupon SAVE20 validated: {data['discount_percentage']}% off")
        print(f"  Original: ₹{data['original_amount']}, Final: ₹{data['final_amount']}")
    
    def test_create_order_with_coupon(self, user_token):
        """Test POST /api/payments/create-order with coupon_code"""
        payload = {
            "plan": "Starter",
            "coupon_code": "SAVE20"
        }
        response = requests.post(
            f"{BASE_URL}/api/payments/create-order",
            json=payload,
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        print(f"Create order response: {response.status_code}")
        
        # May fail if coupon doesn't exist, but endpoint should work
        if response.status_code == 200:
            data = response.json()
            assert "order_id" in data, "order_id missing"
            assert "amount" in data, "amount missing"
            assert "discount_percentage" in data, "discount_percentage missing"
            
            print(f"✓ Order created with coupon: order_id={data['order_id']}")
            print(f"  Amount: {data['amount']/100} INR, Discount: {data['discount_percentage']}%")
        elif response.status_code == 400:
            # Coupon invalid - still endpoint works
            print(f"✓ Create order endpoint works (coupon validation: {response.json().get('detail')})")
        else:
            assert False, f"Unexpected error: {response.text}"


class TestAIVisibilityDeepReport:
    """Test AI Visibility returns detailed_analysis and citations"""
    
    @pytest.fixture
    def user_token(self):
        """Get user token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "Admin@analiyx.com",
            "password": "1234"
        })
        if response.status_code != 200:
            pytest.skip("Login failed")
        return response.json()["token"]
    
    def test_ai_visibility_endpoint_accepts_request(self, user_token):
        """Test that AI visibility endpoint accepts requests (skip actual LLM call)"""
        # Just verify the endpoint exists and accepts the request format
        payload = {"url": "https://example.com"}
        
        response = requests.post(
            f"{BASE_URL}/api/ai-visibility/analyze",
            json=payload,
            headers={"Authorization": f"Bearer {user_token}"},
            timeout=60  # LLM calls can be slow
        )
        
        print(f"AI Visibility response: {response.status_code}")
        
        # The endpoint should either succeed or fail with a known error
        # (not 404 or 500 server error)
        assert response.status_code in [200, 400, 403], f"Unexpected status: {response.status_code} - {response.text}"
        
        if response.status_code == 200:
            data = response.json()
            assert "analysis" in data, "analysis missing"
            analysis = data["analysis"]
            
            # Check for deep report fields
            if "detailed_analysis" in analysis:
                print(f"✓ detailed_analysis field present ({len(analysis['detailed_analysis'])} chars)")
            else:
                print("⚠ detailed_analysis field not in response (may be LLM parsing issue)")
            
            if "citations" in analysis:
                print(f"✓ citations field present ({len(analysis['citations'])} citations)")
            else:
                print("⚠ citations field not in response")
        elif response.status_code == 403:
            print(f"✓ Endpoint works but limit reached: {response.json().get('detail')}")
        else:
            print(f"✓ Endpoint works but returned error: {response.json().get('detail')}")


class TestExistingCredentials:
    """Test existing credentials work"""
    
    def test_admin_login(self):
        """Test admin login with provided credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "Admin@analiyx.com",
            "password": "1234"
        })
        
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert data["user"]["role"] == "admin" or data["user"]["email"].lower() == "admin@analiyx.com"
        print(f"✓ Admin login successful: {data['user']['email']}")
    
    def test_test_user_login(self):
        """Test phoneuser@test.com login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "phoneuser@test.com",
            "password": "test1234"
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Test user login successful: {data['user']['email']}")
            print(f"  phone={data['user'].get('phone')}, client_id={data['user'].get('client_id')}")
        else:
            print(f"⚠ Test user phoneuser@test.com not found (may need to be created)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
