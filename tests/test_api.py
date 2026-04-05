import pytest
from fastapi.testclient import TestClient
from agenttrap.api.main import app

client = TestClient(app)

def test_list_scenarios():
    response = client.get("/api/scenarios")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_create_run_and_list():
    payload = {
        "name": "Test API Run",
        "agent_configs": ["baseline"],
        "scenarios": ["SI-01"],
        "model": "openai/gpt-4o-mini",
        "notes": "Test runner"
    }
    
    # 1. Create
    res = client.post("/api/runs", json=payload)
    assert res.status_code == 200
    run_id = res.json()["run_id"]
    
    # 2. List
    res_list = client.get("/api/runs")
    assert res_list.status_code == 200
    runs = res_list.json()
    assert any(r["id"] == run_id for r in runs)
    
    # 3. Retrieve
    res_get = client.get(f"/api/runs/{run_id}")
    assert res_get.status_code == 200
    assert res_get.json()["name"] == "Test API Run"
