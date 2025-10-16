import asyncio
from src.core.workflow_planner import WorkflowPlanner
from src.core.toolrouter_config import ToolRouterStub
from src.core.task_store import TaskStore


async def main():
    # Use a local sqlite file for demo
    store = TaskStore(db_path="demo_cross_tool.db")
    await store.connect()
    router = ToolRouterStub()
    planner = WorkflowPlanner(router=router, store=store)
    result = await planner.run("weekly_review_cross_tool", params={"channel": "#general", "database_id": "db_1"})
    print("=== Workflow Run Summary ===")
    import json

    print(json.dumps(result, indent=2))
    await store.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
