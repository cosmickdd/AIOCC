from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


def test_list_workflows():
    resp = client.get("/workflows/list")
    assert resp.status_code == 200
    data = resp.json()
    assert "weekly_review" in data.get("workflows", [])


def test_execute_workflow_endpoint():
    payload = {"workflow_name": "weekly_review", "params": {"channel": "#tests", "manager_email": "m@test.com"}}
    resp = client.post("/workflows/execute", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["workflow"] == "weekly_review"
    assert "summary" in data
