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
    summary = planner.run("weekly_review")
    print("Execution summary:")
    for exec_result in summary.get("executions", []):
        print(f" - {exec_result['tool']}.{exec_result['action']} -> {exec_result['status']}")


if __name__ == "__main__":
    run_weekly_review_demo()
