"""
Test Shopify and Zoho Dashboard Endpoints - Iteration 17
Tests the new dashboard endpoints for Shopify store analytics and Zoho Books/CRM.
All endpoints return sample data by design (is_sample_data: true).
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_USER_EMAIL = "testuser@test.com"
TEST_USER_PASSWORD = "test1234"


class TestShopifyDashboard:
    """Tests for GET /api/shopify/report endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        if login_response.status_code != 200:
            pytest.skip("Login failed - cannot test authenticated endpoints")
        self.token = login_response.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_shopify_report_returns_200(self):
        """Test that Shopify report endpoint returns 200 OK"""
        response = requests.get(f"{BASE_URL}/api/shopify/report", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("PASSED: Shopify report returns 200 OK")
    
    def test_shopify_report_has_sample_data_flag(self):
        """Test that response includes is_sample_data flag"""
        response = requests.get(f"{BASE_URL}/api/shopify/report", headers=self.headers)
        data = response.json()
        assert "is_sample_data" in data, "Missing is_sample_data flag"
        assert data["is_sample_data"] == True, "Expected is_sample_data to be True"
        print("PASSED: Shopify report has is_sample_data=True")
    
    def test_shopify_report_has_store_name(self):
        """Test that response includes store_name"""
        response = requests.get(f"{BASE_URL}/api/shopify/report", headers=self.headers)
        data = response.json()
        assert "store_name" in data, "Missing store_name"
        assert isinstance(data["store_name"], str), "store_name should be a string"
        print(f"PASSED: Shopify report has store_name: {data['store_name']}")
    
    def test_shopify_report_has_summary(self):
        """Test that response includes summary with required fields"""
        response = requests.get(f"{BASE_URL}/api/shopify/report", headers=self.headers)
        data = response.json()
        assert "summary" in data, "Missing summary"
        summary = data["summary"]
        required_fields = ["total_orders", "total_revenue", "total_visitors", "avg_order_value", 
                          "conversion_rate", "returning_customer_rate", "cart_abandonment_rate"]
        for field in required_fields:
            assert field in summary, f"Missing summary field: {field}"
        print(f"PASSED: Shopify summary has all required fields")
    
    def test_shopify_report_has_daily_performance(self):
        """Test that response includes daily_performance array"""
        response = requests.get(f"{BASE_URL}/api/shopify/report", headers=self.headers)
        data = response.json()
        assert "daily_performance" in data, "Missing daily_performance"
        assert isinstance(data["daily_performance"], list), "daily_performance should be a list"
        assert len(data["daily_performance"]) > 0, "daily_performance should not be empty"
        # Check first item structure
        first_day = data["daily_performance"][0]
        required_fields = ["date", "orders", "revenue", "visitors", "add_to_cart", "conversion_rate"]
        for field in required_fields:
            assert field in first_day, f"Missing daily_performance field: {field}"
        print(f"PASSED: Shopify daily_performance has {len(data['daily_performance'])} days")
    
    def test_shopify_report_has_top_products(self):
        """Test that response includes top_products array"""
        response = requests.get(f"{BASE_URL}/api/shopify/report", headers=self.headers)
        data = response.json()
        assert "top_products" in data, "Missing top_products"
        assert isinstance(data["top_products"], list), "top_products should be a list"
        assert len(data["top_products"]) > 0, "top_products should not be empty"
        # Check first product structure
        first_product = data["top_products"][0]
        required_fields = ["name", "sku", "sold", "revenue", "inventory", "status"]
        for field in required_fields:
            assert field in first_product, f"Missing top_products field: {field}"
        print(f"PASSED: Shopify top_products has {len(data['top_products'])} products")
    
    def test_shopify_report_has_recent_orders(self):
        """Test that response includes recent_orders array"""
        response = requests.get(f"{BASE_URL}/api/shopify/report", headers=self.headers)
        data = response.json()
        assert "recent_orders" in data, "Missing recent_orders"
        assert isinstance(data["recent_orders"], list), "recent_orders should be a list"
        assert len(data["recent_orders"]) > 0, "recent_orders should not be empty"
        # Check first order structure
        first_order = data["recent_orders"][0]
        required_fields = ["order_id", "customer", "items", "total", "status", "date"]
        for field in required_fields:
            assert field in first_order, f"Missing recent_orders field: {field}"
        print(f"PASSED: Shopify recent_orders has {len(data['recent_orders'])} orders")
    
    def test_shopify_report_has_traffic_sources(self):
        """Test that response includes traffic_sources array"""
        response = requests.get(f"{BASE_URL}/api/shopify/report", headers=self.headers)
        data = response.json()
        assert "traffic_sources" in data, "Missing traffic_sources"
        assert isinstance(data["traffic_sources"], list), "traffic_sources should be a list"
        assert len(data["traffic_sources"]) > 0, "traffic_sources should not be empty"
        # Check first source structure
        first_source = data["traffic_sources"][0]
        required_fields = ["source", "visitors", "percentage"]
        for field in required_fields:
            assert field in first_source, f"Missing traffic_sources field: {field}"
        print(f"PASSED: Shopify traffic_sources has {len(data['traffic_sources'])} sources")
    
    def test_shopify_report_requires_auth(self):
        """Test that endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/shopify/report")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("PASSED: Shopify report requires authentication")


class TestZohoBooksReport:
    """Tests for GET /api/zoho/books/report endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        if login_response.status_code != 200:
            pytest.skip("Login failed - cannot test authenticated endpoints")
        self.token = login_response.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_zoho_books_report_returns_200(self):
        """Test that Zoho Books report endpoint returns 200 OK"""
        response = requests.get(f"{BASE_URL}/api/zoho/books/report", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("PASSED: Zoho Books report returns 200 OK")
    
    def test_zoho_books_report_has_sample_data_flag(self):
        """Test that response includes is_sample_data flag"""
        response = requests.get(f"{BASE_URL}/api/zoho/books/report", headers=self.headers)
        data = response.json()
        assert "is_sample_data" in data, "Missing is_sample_data flag"
        assert data["is_sample_data"] == True, "Expected is_sample_data to be True"
        print("PASSED: Zoho Books report has is_sample_data=True")
    
    def test_zoho_books_report_has_module_books(self):
        """Test that response includes module='books'"""
        response = requests.get(f"{BASE_URL}/api/zoho/books/report", headers=self.headers)
        data = response.json()
        assert "module" in data, "Missing module field"
        assert data["module"] == "books", f"Expected module='books', got '{data['module']}'"
        print("PASSED: Zoho Books report has module='books'")
    
    def test_zoho_books_report_has_summary(self):
        """Test that response includes summary with required fields"""
        response = requests.get(f"{BASE_URL}/api/zoho/books/report", headers=self.headers)
        data = response.json()
        assert "summary" in data, "Missing summary"
        summary = data["summary"]
        required_fields = ["total_income", "total_expenses", "net_profit", "profit_margin",
                          "total_invoiced", "paid_invoices", "overdue_amount", "accounts_receivable"]
        for field in required_fields:
            assert field in summary, f"Missing summary field: {field}"
        print(f"PASSED: Zoho Books summary has all required fields")
    
    def test_zoho_books_report_has_monthly_performance(self):
        """Test that response includes monthly_performance array"""
        response = requests.get(f"{BASE_URL}/api/zoho/books/report", headers=self.headers)
        data = response.json()
        assert "monthly_performance" in data, "Missing monthly_performance"
        assert isinstance(data["monthly_performance"], list), "monthly_performance should be a list"
        assert len(data["monthly_performance"]) > 0, "monthly_performance should not be empty"
        # Check first item structure
        first_month = data["monthly_performance"][0]
        required_fields = ["month", "income", "expenses", "profit"]
        for field in required_fields:
            assert field in first_month, f"Missing monthly_performance field: {field}"
        print(f"PASSED: Zoho Books monthly_performance has {len(data['monthly_performance'])} months")
    
    def test_zoho_books_report_has_invoices(self):
        """Test that response includes invoices array"""
        response = requests.get(f"{BASE_URL}/api/zoho/books/report", headers=self.headers)
        data = response.json()
        assert "invoices" in data, "Missing invoices"
        assert isinstance(data["invoices"], list), "invoices should be a list"
        assert len(data["invoices"]) > 0, "invoices should not be empty"
        # Check first invoice structure
        first_invoice = data["invoices"][0]
        required_fields = ["invoice_id", "customer", "amount", "status", "due_date", "issue_date"]
        for field in required_fields:
            assert field in first_invoice, f"Missing invoices field: {field}"
        print(f"PASSED: Zoho Books invoices has {len(data['invoices'])} invoices")
    
    def test_zoho_books_report_has_expense_categories(self):
        """Test that response includes expense_categories array"""
        response = requests.get(f"{BASE_URL}/api/zoho/books/report", headers=self.headers)
        data = response.json()
        assert "expense_categories" in data, "Missing expense_categories"
        assert isinstance(data["expense_categories"], list), "expense_categories should be a list"
        assert len(data["expense_categories"]) > 0, "expense_categories should not be empty"
        # Check first category structure
        first_category = data["expense_categories"][0]
        required_fields = ["category", "amount", "percentage"]
        for field in required_fields:
            assert field in first_category, f"Missing expense_categories field: {field}"
        print(f"PASSED: Zoho Books expense_categories has {len(data['expense_categories'])} categories")
    
    def test_zoho_books_report_requires_auth(self):
        """Test that endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/zoho/books/report")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("PASSED: Zoho Books report requires authentication")


class TestZohoCRMReport:
    """Tests for GET /api/zoho/crm/report endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        if login_response.status_code != 200:
            pytest.skip("Login failed - cannot test authenticated endpoints")
        self.token = login_response.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_zoho_crm_report_returns_200(self):
        """Test that Zoho CRM report endpoint returns 200 OK"""
        response = requests.get(f"{BASE_URL}/api/zoho/crm/report", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("PASSED: Zoho CRM report returns 200 OK")
    
    def test_zoho_crm_report_has_sample_data_flag(self):
        """Test that response includes is_sample_data flag"""
        response = requests.get(f"{BASE_URL}/api/zoho/crm/report", headers=self.headers)
        data = response.json()
        assert "is_sample_data" in data, "Missing is_sample_data flag"
        assert data["is_sample_data"] == True, "Expected is_sample_data to be True"
        print("PASSED: Zoho CRM report has is_sample_data=True")
    
    def test_zoho_crm_report_has_module_crm(self):
        """Test that response includes module='crm'"""
        response = requests.get(f"{BASE_URL}/api/zoho/crm/report", headers=self.headers)
        data = response.json()
        assert "module" in data, "Missing module field"
        assert data["module"] == "crm", f"Expected module='crm', got '{data['module']}'"
        print("PASSED: Zoho CRM report has module='crm'")
    
    def test_zoho_crm_report_has_summary(self):
        """Test that response includes summary with required fields"""
        response = requests.get(f"{BASE_URL}/api/zoho/crm/report", headers=self.headers)
        data = response.json()
        assert "summary" in data, "Missing summary"
        summary = data["summary"]
        required_fields = ["total_pipeline_value", "total_deals_won", "active_deals", 
                          "win_rate", "avg_deal_size", "total_leads"]
        for field in required_fields:
            assert field in summary, f"Missing summary field: {field}"
        print(f"PASSED: Zoho CRM summary has all required fields")
    
    def test_zoho_crm_report_has_pipeline_stages(self):
        """Test that response includes pipeline_stages array"""
        response = requests.get(f"{BASE_URL}/api/zoho/crm/report", headers=self.headers)
        data = response.json()
        assert "pipeline_stages" in data, "Missing pipeline_stages"
        assert isinstance(data["pipeline_stages"], list), "pipeline_stages should be a list"
        assert len(data["pipeline_stages"]) > 0, "pipeline_stages should not be empty"
        # Check first stage structure
        first_stage = data["pipeline_stages"][0]
        required_fields = ["stage", "deals", "value"]
        for field in required_fields:
            assert field in first_stage, f"Missing pipeline_stages field: {field}"
        print(f"PASSED: Zoho CRM pipeline_stages has {len(data['pipeline_stages'])} stages")
    
    def test_zoho_crm_report_has_recent_deals(self):
        """Test that response includes recent_deals array"""
        response = requests.get(f"{BASE_URL}/api/zoho/crm/report", headers=self.headers)
        data = response.json()
        assert "recent_deals" in data, "Missing recent_deals"
        assert isinstance(data["recent_deals"], list), "recent_deals should be a list"
        assert len(data["recent_deals"]) > 0, "recent_deals should not be empty"
        # Check first deal structure
        first_deal = data["recent_deals"][0]
        required_fields = ["deal_name", "stage", "amount", "probability", "close_date", "owner"]
        for field in required_fields:
            assert field in first_deal, f"Missing recent_deals field: {field}"
        print(f"PASSED: Zoho CRM recent_deals has {len(data['recent_deals'])} deals")
    
    def test_zoho_crm_report_has_monthly_deals(self):
        """Test that response includes monthly_deals array"""
        response = requests.get(f"{BASE_URL}/api/zoho/crm/report", headers=self.headers)
        data = response.json()
        assert "monthly_deals" in data, "Missing monthly_deals"
        assert isinstance(data["monthly_deals"], list), "monthly_deals should be a list"
        assert len(data["monthly_deals"]) > 0, "monthly_deals should not be empty"
        # Check first month structure
        first_month = data["monthly_deals"][0]
        required_fields = ["month", "won", "lost", "value_won"]
        for field in required_fields:
            assert field in first_month, f"Missing monthly_deals field: {field}"
        print(f"PASSED: Zoho CRM monthly_deals has {len(data['monthly_deals'])} months")
    
    def test_zoho_crm_report_has_lead_sources(self):
        """Test that response includes lead_sources array"""
        response = requests.get(f"{BASE_URL}/api/zoho/crm/report", headers=self.headers)
        data = response.json()
        assert "lead_sources" in data, "Missing lead_sources"
        assert isinstance(data["lead_sources"], list), "lead_sources should be a list"
        assert len(data["lead_sources"]) > 0, "lead_sources should not be empty"
        # Check first source structure
        first_source = data["lead_sources"][0]
        required_fields = ["source", "leads", "percentage"]
        for field in required_fields:
            assert field in first_source, f"Missing lead_sources field: {field}"
        print(f"PASSED: Zoho CRM lead_sources has {len(data['lead_sources'])} sources")
    
    def test_zoho_crm_report_requires_auth(self):
        """Test that endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/zoho/crm/report")
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("PASSED: Zoho CRM report requires authentication")


class TestExistingDashboardEndpoints:
    """Verify existing dashboard endpoints still work"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        if login_response.status_code != 200:
            pytest.skip("Login failed - cannot test authenticated endpoints")
        self.token = login_response.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_google_analytics_report_returns_200(self):
        """Test GA4 report endpoint still works"""
        response = requests.get(f"{BASE_URL}/api/google-analytics/report", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "is_sample_data" in data
        print("PASSED: Google Analytics report returns 200 OK")
    
    def test_google_ads_campaigns_returns_200(self):
        """Test Google Ads campaigns endpoint still works"""
        response = requests.get(f"{BASE_URL}/api/google-ads/campaigns", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "is_sample_data" in data
        print("PASSED: Google Ads campaigns returns 200 OK")
    
    def test_meta_ads_report_returns_200(self):
        """Test Meta Ads report endpoint still works"""
        response = requests.get(f"{BASE_URL}/api/meta-ads/report", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "is_sample_data" in data
        print("PASSED: Meta Ads report returns 200 OK")
    
    def test_google_sheets_report_returns_200(self):
        """Test Google Sheets report endpoint still works"""
        response = requests.get(f"{BASE_URL}/api/google-sheets/report", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "is_sample_data" in data
        print("PASSED: Google Sheets report returns 200 OK")


class TestAPIContractsFile:
    """Verify API_CONTRACTS.md exists and documents all endpoints"""
    
    def test_api_contracts_file_exists(self):
        """Test that API_CONTRACTS.md file exists"""
        import os
        contracts_path = "/app/API_CONTRACTS.md"
        assert os.path.exists(contracts_path), f"API_CONTRACTS.md not found at {contracts_path}"
        print("PASSED: API_CONTRACTS.md exists")
    
    def test_api_contracts_documents_all_endpoints(self):
        """Test that API_CONTRACTS.md documents all 7 dashboard endpoints"""
        with open("/app/API_CONTRACTS.md", "r") as f:
            content = f.read()
        
        # Check for all 7 endpoints
        endpoints = [
            "/api/google-analytics/report",
            "/api/google-ads/campaigns",
            "/api/meta-ads/report",
            "/api/google-sheets/report",
            "/api/shopify/report",
            "/api/zoho/books/report",
            "/api/zoho/crm/report"
        ]
        
        for endpoint in endpoints:
            # Check for endpoint path or section header
            endpoint_name = endpoint.split("/")[-1]
            assert endpoint in content or endpoint_name in content.lower(), f"Missing documentation for {endpoint}"
        
        print(f"PASSED: API_CONTRACTS.md documents all {len(endpoints)} endpoints")
