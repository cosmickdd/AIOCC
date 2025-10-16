"""Demo runner for AIOCC workflows.

Runs the weekly_review workflow via the WorkflowPlanner and prints the execution summary.
"""
from src.core.toolrouter_config import ToolRouterStub
from src.core.task_store import TaskStore
from src.core.workflow_planner import WorkflowPlanner


def run_weekly_review_demo():
    router = ToolRouterStub()
    store = TaskStore()
    planner = WorkflowPlanner(router=router, store=store)

    print("Running demo: weekly_review")
    # planner.run is async; execute in event loop for demo
    import asyncio

    summary = asyncio.run(planner.run("weekly_review"))
    print("Execution summary:")
    for exec_result in summary.get("executions", []):
        status = exec_result.get("status") or exec_result.get("result", {}).get("status") if isinstance(exec_result.get("result"), dict) else exec_result.get("status")
        print(f" - {exec_result.get('tool')}.{exec_result.get('action')} -> {status}")


if __name__ == "__main__":
    run_weekly_review_demo()
