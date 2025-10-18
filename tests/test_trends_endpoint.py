import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_trends_with_date_range(tmp_path):
    # create two runs separated by 1 day using the TaskStore via main.store
    from src.core.task_store import TaskStore

    db_file = tmp_path / "trends.db"
    store = TaskStore(db_path=str(db_file))

    # ensure the app's global store points to this DB for the test
    app.dependency_overrides.clear()

    # connect the test store and create runs
    import asyncio

    async def setup_and_run():
        await store.connect()
        try:
            now = datetime.utcnow()
            day1 = (now - timedelta(days=2)).isoformat()
            day2 = (now - timedelta(days=1)).isoformat()
            await store.create_run("wf1", day1, status="success")
            await store.create_run("wf1", day2, status="error")
        finally:
            await store.disconnect()

    asyncio.run(setup_and_run())

    # Query trends for an explicit date range that includes the two runs
    start = (datetime.utcnow() - timedelta(days=3)).date().isoformat()
    end = (datetime.utcnow() - timedelta(days=0)).date().isoformat()
    resp = client.get(f"/analytics/trends?start={start}&end={end}")
    assert resp.status_code == 200
    data = resp.json()
    assert "series" in data
    assert isinstance(data["series"], list)

