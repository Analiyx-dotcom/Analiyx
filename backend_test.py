#!/usr/bin/env python3
"""
Comprehensive Backend API Test Suite for Analiyx Application
Tests all endpoints including health check, authentication, and admin functionality
"""
import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://insights-hub-44.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@papermap.com"
ADMIN_PASSWORD = "admin123"

# Test user credentials for registration and login
TEST_USER_NAME = "Alice Johnson"
TEST_USER_EMAIL = "alice.johnson@testdomain.com"
TEST_USER_PASSWORD = "securepass456"

# Global variables for tokens
admin_token = None
user_token = None

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
    
    def add_result(self, test_name, success, details=""):
        self.results.append({
            "test": test_name,
            "status": "✅ PASS" if success else "❌ FAIL",
            "details": details
        })
        if success:
            self.passed += 1
        else:
            self.failed += 1
    
    def print_summary(self):
        print(f"\n{'='*60}")
        print("TEST RESULTS SUMMARY")
        print(f"{'='*60}")
        for result in self.results:
            print(f"{result['status']} {result['test']}")
            if result['details']:
                print(f"     Details: {result['details']}")
        
        print(f"\n{'='*60}")
        print(f"TOTAL: {self.passed + self.failed} tests")
        print(f"PASSED: {self.passed}")
        print(f"FAILED: {self.failed}")
        print(f"SUCCESS RATE: {(self.passed/(self.passed+self.failed)*100):.1f}%")
        print(f"{'='*60}")

results = TestResults()

def test_health_check():
    """Test GET /api/ - Health check endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("message") == "Hello World":
                results.add_result("Health Check", True, "Endpoint returned correct message")
                return True
            else:
                results.add_result("Health Check", False, f"Wrong message: {data}")
                return False
        else:
            results.add_result("Health Check", False, f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        results.add_result("Health Check", False, f"Request failed: {str(e)}")
        return False

def test_register_user():
    """Test POST /api/auth/register - Register new user"""
    try:
        payload = {
            "name": TEST_USER_NAME,
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        response = requests.post(f"{BASE_URL}/auth/register", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            if "token" in data and "user" in data:
                global user_token
                user_token = data["token"]
                user_info = data["user"]
                
                # Validate user data
                if (user_info["name"] == TEST_USER_NAME and 
                    user_info["email"] == TEST_USER_EMAIL and
                    user_info["role"] == "user"):
                    results.add_result("User Registration", True, f"User registered with ID: {user_info['id']}")
                    return True
                else:
                    results.add_result("User Registration", False, f"Invalid user data: {user_info}")
                    return False
            else:
                results.add_result("User Registration", False, f"Missing token or user in response: {data}")
                return False
        else:
            results.add_result("User Registration", False, f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        results.add_result("User Registration", False, f"Request failed: {str(e)}")
        return False

def test_register_duplicate_email():
    """Test duplicate email registration fails"""
    try:
        payload = {
            "name": "Another User",
            "email": TEST_USER_EMAIL,  # Same email as previous test
            "password": "anotherpass"
        }
        
        response = requests.post(f"{BASE_URL}/auth/register", json=payload)
        
        if response.status_code == 400:
            data = response.json()
            if "already registered" in data.get("detail", "").lower():
                results.add_result("Duplicate Email Validation", True, "Correctly rejected duplicate email")
                return True
            else:
                results.add_result("Duplicate Email Validation", False, f"Wrong error message: {data}")
                return False
        else:
            results.add_result("Duplicate Email Validation", False, f"Should return 400, got {response.status_code}")
            return False
    except Exception as e:
        results.add_result("Duplicate Email Validation", False, f"Request failed: {str(e)}")
        return False

def test_register_invalid_email():
    """Test invalid email format is rejected"""
    try:
        payload = {
            "name": "Invalid Email User",
            "email": "invalid-email-format",  # Invalid email
            "password": "password123"
        }
        
        response = requests.post(f"{BASE_URL}/auth/register", json=payload)
        
        if response.status_code == 422:  # Pydantic validation error
            results.add_result("Invalid Email Validation", True, "Invalid email format rejected")
            return True
        else:
            results.add_result("Invalid Email Validation", False, f"Should return 422, got {response.status_code}")
            return False
    except Exception as e:
        results.add_result("Invalid Email Validation", False, f"Request failed: {str(e)}")
        return False

def test_login_user():
    """Test POST /api/auth/login - Login with valid credentials"""
    try:
        payload = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            if "token" in data and "user" in data:
                global user_token
                user_token = data["token"]
                results.add_result("User Login", True, f"Login successful for {data['user']['email']}")
                return True
            else:
                results.add_result("User Login", False, f"Missing token or user in response: {data}")
                return False
        else:
            results.add_result("User Login", False, f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        results.add_result("User Login", False, f"Request failed: {str(e)}")
        return False

def test_login_wrong_password():
    """Test login with wrong password returns 401"""
    try:
        payload = {
            "email": TEST_USER_EMAIL,
            "password": "wrongpassword"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=payload)
        
        if response.status_code == 401:
            results.add_result("Wrong Password Login", True, "Correctly rejected wrong password")
            return True
        else:
            results.add_result("Wrong Password Login", False, f"Should return 401, got {response.status_code}")
            return False
    except Exception as e:
        results.add_result("Wrong Password Login", False, f"Request failed: {str(e)}")
        return False

def test_login_nonexistent_user():
    """Test login with non-existent user returns 401"""
    try:
        payload = {
            "email": "nonexistent@example.com",
            "password": "password123"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=payload)
        
        if response.status_code == 401:
            results.add_result("Non-existent User Login", True, "Correctly rejected non-existent user")
            return True
        else:
            results.add_result("Non-existent User Login", False, f"Should return 401, got {response.status_code}")
            return False
    except Exception as e:
        results.add_result("Non-existent User Login", False, f"Request failed: {str(e)}")
        return False

def test_login_admin():
    """Test admin login"""
    try:
        payload = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            if "token" in data and "user" in data:
                global admin_token
                admin_token = data["token"]
                user_info = data["user"]
                
                if user_info.get("role") == "admin":
                    results.add_result("Admin Login", True, f"Admin login successful: {user_info['email']}")
                    return True
                else:
                    results.add_result("Admin Login", False, f"User role is {user_info.get('role')}, expected 'admin'")
                    return False
            else:
                results.add_result("Admin Login", False, f"Missing token or user in response: {data}")
                return False
        else:
            results.add_result("Admin Login", False, f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        results.add_result("Admin Login", False, f"Request failed: {str(e)}")
        return False

def test_get_current_user():
    """Test GET /api/auth/me - Get current authenticated user"""
    if not user_token:
        results.add_result("Get Current User", False, "No user token available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {user_token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("email") == TEST_USER_EMAIL:
                results.add_result("Get Current User", True, f"Retrieved user: {data['name']}")
                return True
            else:
                results.add_result("Get Current User", False, f"Wrong user data: {data}")
                return False
        else:
            results.add_result("Get Current User", False, f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        results.add_result("Get Current User", False, f"Request failed: {str(e)}")
        return False

def test_get_current_user_invalid_token():
    """Test GET /api/auth/me with invalid token"""
    try:
        headers = {"Authorization": "Bearer invalid_token_here"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        
        if response.status_code == 401:
            results.add_result("Invalid Token Validation", True, "Invalid token correctly rejected")
            return True
        else:
            results.add_result("Invalid Token Validation", False, f"Should return 401, got {response.status_code}")
            return False
    except Exception as e:
        results.add_result("Invalid Token Validation", False, f"Request failed: {str(e)}")
        return False

def test_admin_stats():
    """Test GET /api/admin/stats - Admin dashboard statistics"""
    if not admin_token:
        results.add_result("Admin Stats", False, "No admin token available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/admin/stats", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            required_fields = ["total_users", "active_subscriptions", "monthly_revenue", "data_sources"]
            
            if all(field in data for field in required_fields):
                results.add_result("Admin Stats", True, f"Stats: {data['total_users']} users, ${data['monthly_revenue']} revenue")
                return True
            else:
                results.add_result("Admin Stats", False, f"Missing required fields: {data}")
                return False
        else:
            results.add_result("Admin Stats", False, f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        results.add_result("Admin Stats", False, f"Request failed: {str(e)}")
        return False

def test_admin_users():
    """Test GET /api/admin/users - Get paginated users list"""
    if not admin_token:
        results.add_result("Admin Users List", False, "No admin token available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/admin/users?page=1&limit=5", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            required_fields = ["users", "total", "page", "total_pages"]
            
            if all(field in data for field in required_fields):
                users_count = len(data["users"])
                results.add_result("Admin Users List", True, f"Retrieved {users_count} users, total: {data['total']}")
                return True
            else:
                results.add_result("Admin Users List", False, f"Missing required fields: {data}")
                return False
        else:
            results.add_result("Admin Users List", False, f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        results.add_result("Admin Users List", False, f"Request failed: {str(e)}")
        return False

def test_admin_user_growth_chart():
    """Test GET /api/admin/charts/user-growth - User growth chart data"""
    if not admin_token:
        results.add_result("Admin User Growth Chart", False, "No admin token available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/admin/charts/user-growth", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            if "data" in data and isinstance(data["data"], list):
                chart_points = len(data["data"])
                results.add_result("Admin User Growth Chart", True, f"Retrieved {chart_points} chart data points")
                return True
            else:
                results.add_result("Admin User Growth Chart", False, f"Invalid chart data format: {data}")
                return False
        else:
            results.add_result("Admin User Growth Chart", False, f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        results.add_result("Admin User Growth Chart", False, f"Request failed: {str(e)}")
        return False

def test_admin_revenue_chart():
    """Test GET /api/admin/charts/revenue - Revenue trend data"""
    if not admin_token:
        results.add_result("Admin Revenue Chart", False, "No admin token available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/admin/charts/revenue", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            if "data" in data and isinstance(data["data"], list):
                chart_points = len(data["data"])
                results.add_result("Admin Revenue Chart", True, f"Retrieved {chart_points} revenue data points")
                return True
            else:
                results.add_result("Admin Revenue Chart", False, f"Invalid chart data format: {data}")
                return False
        else:
            results.add_result("Admin Revenue Chart", False, f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        results.add_result("Admin Revenue Chart", False, f"Request failed: {str(e)}")
        return False

def test_user_access_admin_endpoints():
    """Test that regular users get 403 when accessing admin endpoints"""
    if not user_token:
        results.add_result("User Access Control", False, "No user token available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {user_token}"}
        admin_endpoints = [
            "/admin/stats",
            "/admin/users",
            "/admin/charts/user-growth",
            "/admin/charts/revenue"
        ]
        
        forbidden_count = 0
        for endpoint in admin_endpoints:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            if response.status_code == 403:
                forbidden_count += 1
        
        if forbidden_count == len(admin_endpoints):
            results.add_result("User Access Control", True, f"All {forbidden_count} admin endpoints properly restricted")
            return True
        else:
            results.add_result("User Access Control", False, f"Only {forbidden_count}/{len(admin_endpoints)} endpoints restricted")
            return False
    except Exception as e:
        results.add_result("User Access Control", False, f"Request failed: {str(e)}")
        return False

def test_no_auth_admin_access():
    """Test that admin endpoints require authentication"""
    try:
        admin_endpoints = [
            "/admin/stats",
            "/admin/users",
            "/admin/charts/user-growth", 
            "/admin/charts/revenue"
        ]
        
        unauthorized_count = 0
        for endpoint in admin_endpoints:
            response = requests.get(f"{BASE_URL}{endpoint}")  # No auth header
            if response.status_code == 401 or response.status_code == 403:
                unauthorized_count += 1
        
        if unauthorized_count == len(admin_endpoints):
            results.add_result("No Auth Admin Access", True, f"All {unauthorized_count} admin endpoints require authentication")
            return True
        else:
            results.add_result("No Auth Admin Access", False, f"Only {unauthorized_count}/{len(admin_endpoints)} endpoints require auth")
            return False
    except Exception as e:
        results.add_result("No Auth Admin Access", False, f"Request failed: {str(e)}")
        return False

def run_all_tests():
    """Run all test cases in order"""
    print("🚀 Starting Analiyx Backend API Test Suite")
    print(f"Testing backend at: {BASE_URL}")
    print(f"Admin credentials: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
    print(f"Test user: {TEST_USER_EMAIL}")
    print("=" * 60)
    
    # Health and basic functionality
    print("\n📊 Testing Health Check...")
    test_health_check()
    
    # Authentication tests
    print("\n🔐 Testing Authentication...")
    test_register_user()
    test_register_duplicate_email()
    test_register_invalid_email()
    test_login_user()
    test_login_wrong_password()
    test_login_nonexistent_user()
    test_login_admin()
    test_get_current_user()
    test_get_current_user_invalid_token()
    
    # Admin functionality tests
    print("\n👑 Testing Admin Endpoints...")
    test_admin_stats()
    test_admin_users()
    test_admin_user_growth_chart()
    test_admin_revenue_chart()
    
    # Access control tests
    print("\n🔒 Testing Access Control...")
    test_user_access_admin_endpoints()
    test_no_auth_admin_access()
    
    # Print final results
    results.print_summary()
    
    # Return exit code based on results
    return 0 if results.failed == 0 else 1

if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)