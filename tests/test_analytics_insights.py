import pytest
from datetime import datetime, timedelta

from src.core.task_store import TaskStore
from src.core.analytics_insights import compute_metrics, get_recent_failures


@pytest.mark.asyncio
async def test_compute_metrics_and_failures(tmp_path):
    db_file = tmp_path / "analytics.db"
    store = TaskStore(db_path=str(db_file))
    await store.connect()
    try:
        # create runs: 3 success, 2 failures
        now = datetime.utcnow()
        runs = [
            ("weekly_review", now - timedelta(seconds=30), now, "success", {"executions": [{"tool": "notion", "status": "ok"}]}),
            ("weekly_review", now - timedelta(seconds=20), now, "success", {"executions": [{"tool": "slack", "status": "ok"}]}),
            ("weekly_review_cross_tool", now - timedelta(seconds=40), now, "error", {"executions": [{"tool": "gmail", "status": "error"}]}),
            ("weekly_review_cross_tool", now - timedelta(seconds=50), now, "error", {"executions": [{"tool": "notion", "status": "error"}]}),
            ("weekly_review", now - timedelta(seconds=10), now, "success", {"executions": [{"tool": "openai", "status": "ok"}]}),
        ]

        for wf, s, f, status, log in runs:
            await store.create_run(wf, s.isoformat(), status=status, log=log)

        metrics = await compute_metrics(store)
        assert "success_rate" in metrics
        assert metrics["total_runs"] == 5
        assert metrics["failure_rate"] > 0

        failures = await get_recent_failures(store, limit=5)
        assert isinstance(failures, list)
        assert len(failures) >= 2
    finally:
        await store.disconnect()
