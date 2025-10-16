import pytest

from src.core.task_store import TaskStore
from src.core.toolrouter_config import ToolRouterStub
from src.core.workflow_planner import WorkflowPlanner


@pytest.mark.asyncio
async def test_workflow_logs_and_retry(tmp_path):
    # prepare in-memory db
    store = TaskStore(db_path=":memory:")
    await store.connect()
    try:
        # Create a router that raises on first multi_execute call to force retries
        class FailOnceRouter(ToolRouterStub):
            def __init__(self):
                super().__init__()
                self.called = 0

            def multi_execute(self, executions):
                self.called += 1
                if self.called == 1:
                    raise Exception("transient")
                return [{"tool": executions[0]["tool"], "action": executions[0]["action"], "status": "ok"}]

        router = FailOnceRouter()
        planner = WorkflowPlanner(router=router, store=store)

        summary = await planner.run("weekly_review", params={"channel": "#tests", "manager_email": "m@test.com"})
        assert "run_id" in summary and summary["run_id"] is not None

        runs = await store.list_runs(limit=10)
        assert len(runs) >= 1
        run = runs[0]
        assert run["status"] in ("success", "error")
        assert isinstance(run["log"], dict)
    finally:
        await store.disconnect()
