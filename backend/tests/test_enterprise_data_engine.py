"""
Enterprise Data Engine Backend Tests - Iteration 15
Tests for:
- Datasource connect endpoints (POST/GET/DELETE/test)
- SQL query validation and cache stats
- Semantic glossary CRUD
- Metadata jobs listing
"""
import os
import pytest
import requests
from pathlib import Path

def _load_frontend_env():
    if os.environ.get("REACT_APP_BACKEND_URL"):
        return
    env_path = Path("/app/frontend/.env")
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("REACT_APP_BACKEND_URL="):
                os.environ["REACT_APP_BACKEND_URL"] = line.split("=", 1)[1].strip()
                break

_load_frontend_env()
BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
assert BASE_URL, "REACT_APP_BACKEND_URL not set"


@pytest.fixture(scope="module")
def token():
    resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "testuser@test.com",
        "password": "test1234",
    })
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    return resp.json().get("token")


@pytest.fixture(scope="module")
def headers(token):
    return {"Authorization": f"Bearer {token}"}


# ---------- Datasource Endpoints ----------

class TestDatasourceConnect:
    def test_connect_rejects_invalid_db_type(self, headers):
        payload = {
            "name": "TEST_bad_type",
            "db_type": "oracle",
            "host": "127.0.0.1",
            "port": 5432,
            "database": "test",
            "username": "u",
            "password": "p",
        }
        r = requests.post(f"{BASE_URL}/api/datasources/connect", json=payload, headers=headers)
        assert r.status_code == 400
        assert "Unsupported" in r.json().get("detail", "")

    def test_connect_fails_on_unreachable_host(self, headers):
        payload = {
            "name": "TEST_unreachable",
            "db_type": "postgresql",
            "host": "127.0.0.1",
            "port": 65530,  # nothing listening
            "database": "nodb",
            "username": "nouser",
            "password": "nopass",
        }
        r = requests.post(f"{BASE_URL}/api/datasources/connect", json=payload, headers=headers)
        # Expected: 400 with 'Connection failed' message
        assert r.status_code == 400, r.text
        assert "Connection failed" in r.json().get("detail", "")

    def test_connect_requires_auth(self):
        r = requests.post(f"{BASE_URL}/api/datasources/connect", json={
            "name": "x", "db_type": "postgresql", "host": "h", "port": 5432,
            "database": "d", "username": "u", "password": "p"
        })
        assert r.status_code in (401, 403)

    def test_list_datasources_returns_list(self, headers):
        r = requests.get(f"{BASE_URL}/api/datasources/", headers=headers)
        assert r.status_code == 200
        data = r.json()
        assert "datasources" in data
        assert isinstance(data["datasources"], list)

    def test_test_nonexistent_datasource_returns_404(self, headers):
        r = requests.post(f"{BASE_URL}/api/datasources/nonexistent-id/test", headers=headers)
        assert r.status_code == 404

    def test_delete_nonexistent_datasource_returns_404(self, headers):
        r = requests.delete(f"{BASE_URL}/api/datasources/nonexistent-id", headers=headers)
        assert r.status_code == 404

    def test_supported_types(self, headers):
        r = requests.get(f"{BASE_URL}/api/datasources/supported-types", headers=headers)
        assert r.status_code == 200
        assert "postgresql" in r.json().get("types", [])
        assert "mysql" in r.json().get("types", [])


# ---------- Query Endpoints ----------

class TestQueryValidation:
    def test_validate_select_ok(self):
        r = requests.post(f"{BASE_URL}/api/query/validate", json={
            "sql": "SELECT id, name FROM users LIMIT 10",
            "db_type": "postgresql",
        })
        assert r.status_code == 200
        data = r.json()
        assert data["valid"] is True
        assert data["issues"] == []

    def test_validate_rejects_drop(self):
        r = requests.post(f"{BASE_URL}/api/query/validate", json={
            "sql": "DROP TABLE users",
            "db_type": "postgresql",
        })
        assert r.status_code == 200
        data = r.json()
        assert data["valid"] is False
        assert any("DROP" in i for i in data["issues"])

    def test_validate_rejects_delete(self):
        r = requests.post(f"{BASE_URL}/api/query/validate", json={
            "sql": "DELETE FROM users WHERE id=1",
        })
        data = r.json()
        assert data["valid"] is False
        assert any("DELETE" in i for i in data["issues"])

    def test_validate_rejects_insert(self):
        r = requests.post(f"{BASE_URL}/api/query/validate", json={
            "sql": "INSERT INTO users(id) VALUES(1)",
        })
        data = r.json()
        assert data["valid"] is False
        assert any("INSERT" in i for i in data["issues"])

    def test_validate_warns_no_limit(self):
        r = requests.post(f"{BASE_URL}/api/query/validate", json={
            "sql": "SELECT * FROM users"
        })
        data = r.json()
        assert data["valid"] is True
        assert any("LIMIT" in w for w in data["warnings"])


class TestQueryCacheAndHistory:
    def test_cache_stats_connected(self):
        r = requests.get(f"{BASE_URL}/api/query/cache/stats")
        assert r.status_code == 200
        data = r.json()
        assert data.get("connected") is True
        assert "keys_count" in data

    def test_query_history(self, headers):
        r = requests.get(f"{BASE_URL}/api/query/history", headers=headers)
        assert r.status_code == 200
        data = r.json()
        assert "history" in data
        assert isinstance(data["history"], list)


# ---------- Semantic Glossary ----------

class TestGlossaryCRUD:
    @pytest.fixture
    def created_term(self, headers):
        payload = {
            "term": "TEST_MRR",
            "definition": "Monthly Recurring Revenue",
            "synonyms": "recurring revenue, subscription revenue",
            "related_tables": ["subscriptions"],
            "related_columns": ["subscriptions.amount"],
        }
        r = requests.post(f"{BASE_URL}/api/semantic/glossary", json=payload, headers=headers)
        assert r.status_code == 200, r.text
        term = r.json()
        assert "id" in term
        yield term
        # Cleanup
        requests.delete(f"{BASE_URL}/api/semantic/glossary/{term['id']}", headers=headers)

    def test_create_glossary_term_fields(self, created_term):
        assert created_term["term"] == "TEST_MRR"
        assert created_term["definition"] == "Monthly Recurring Revenue"
        assert "recurring revenue" in created_term["synonyms"]
        assert created_term["related_tables"] == ["subscriptions"]

    def test_list_glossary_terms(self, headers, created_term):
        r = requests.get(f"{BASE_URL}/api/semantic/glossary", headers=headers)
        assert r.status_code == 200
        data = r.json()
        assert "terms" in data
        term_ids = [t["id"] for t in data["terms"]]
        assert created_term["id"] in term_ids

    def test_update_glossary_term(self, headers, created_term):
        r = requests.put(
            f"{BASE_URL}/api/semantic/glossary/{created_term['id']}",
            json={"definition": "Updated: MRR is total monthly subscription revenue"},
            headers=headers,
        )
        assert r.status_code == 200
        updated = r.json()
        assert "Updated:" in updated["definition"]
        # Persistence check
        r2 = requests.get(f"{BASE_URL}/api/semantic/glossary/{created_term['id']}", headers=headers)
        assert r2.status_code == 200
        assert "Updated:" in r2.json()["definition"]

    def test_delete_glossary_term(self, headers):
        # Create
        r = requests.post(f"{BASE_URL}/api/semantic/glossary", json={
            "term": "TEST_to_delete", "definition": "will be deleted"
        }, headers=headers)
        assert r.status_code == 200
        tid = r.json()["id"]

        # Delete
        r = requests.delete(f"{BASE_URL}/api/semantic/glossary/{tid}", headers=headers)
        assert r.status_code == 200
        assert r.json()["success"] is True

        # Verify gone
        r = requests.get(f"{BASE_URL}/api/semantic/glossary/{tid}", headers=headers)
        assert r.status_code == 404

    def test_glossary_requires_auth(self):
        r = requests.get(f"{BASE_URL}/api/semantic/glossary")
        assert r.status_code in (401, 403)


# ---------- Metadata Jobs ----------

class TestMetadataJobs:
    def test_list_jobs_returns_list(self, headers):
        r = requests.get(f"{BASE_URL}/api/metadata/jobs", headers=headers)
        assert r.status_code == 200
        data = r.json()
        assert "jobs" in data
        assert isinstance(data["jobs"], list)

    def test_jobs_requires_auth(self):
        r = requests.get(f"{BASE_URL}/api/metadata/jobs")
        assert r.status_code in (401, 403)
