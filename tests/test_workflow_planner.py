import pytest

from src.core.toolrouter_config import ToolRouterStub
from src.core.task_store import TaskStore
from src.core.workflow_planner import WorkflowPlanner


@pytest.mark.asyncio
async def test_weekly_review_runs_with_params():
    router = ToolRouterStub()
    store = TaskStore(db_path=":memory:")
    await store.connect()
    try:
        planner = WorkflowPlanner(router=router, store=store)

        params = {"channel": "#ops", "manager_email": "manager@example.com"}
        summary = await planner.run("weekly_review", params=params)

        assert summary["plan_id"].startswith("plan_")
        assert summary["params"]["channel"] == "#ops"
        assert any(ex["tool"] == "slack" for ex in summary["executions"])
    finally:
        await store.disconnect()
