import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.utils.logger import get_logger
from src.core.task_store import TaskStore
from src.core.toolrouter_config import ToolRouterStub
from src.core.analytics import AnalyticsEngine
from src.core.analytics_insights import compute_metrics, get_recent_failures
from src.core.workflow_planner import WorkflowPlanner
from src.agents.slack_agent import SlackAgent
from fastapi.middleware.cors import CORSMiddleware

logger = get_logger("main")

app = FastAPI(title="AIOCC - AI Operations Command Center")

# CORS - allow local dashboard to query analytics endpoints
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
# Also allow Next.js dev default origin when NEXT_PUBLIC_API_URL isn't used
ALLOWED_ORIGINS = [FRONTEND_URL, "http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate async TaskStore and router (they are lightweight until connected)
store = TaskStore()
router = ToolRouterStub()
analytics = AnalyticsEngine(store)
planner = WorkflowPlanner(router=router, store=store)
slack_agent = SlackAgent(router=router)


@app.on_event("startup")
async def startup_event():
    # Connect the async DB
    await store.connect()


@app.on_event("shutdown")
async def shutdown_event():
    await store.disconnect()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/tasks")
async def create_task(source: str, title: str, description: str | None = None, owner: str | None = None):
    task = await store.add_task_async(source=source, title=title, description=description, owner=owner)
    return {"task": task.__dict__}


@app.get("/tasks")
async def list_tasks(status: str | None = None):
    tasks = await store.list_tasks_async(status=status)
    return {"tasks": [t.__dict__ for t in tasks]}


@app.get("/analytics/overview")
async def analytics_overview():
    return {
        "overdue_percentage": await analytics.overdue_percentage(),
        "active_tasks": await analytics.active_tasks_count(),
        "average_response_time": await analytics.average_response_time(),
    }


class WorkflowExecuteRequest(BaseModel):
    workflow_name: str
    params: dict | None = None


@app.post("/workflows/execute")
async def execute_workflow(req: WorkflowExecuteRequest):
    """Execute a pre-defined workflow by name with optional params.

    Body: { workflow_name: str, params?: dict }
    Returns a detailed execution summary JSON.
    """
    try:
        summary = await planner.run(req.workflow_name, params=req.params or {})
        return {"workflow": req.workflow_name, "summary": summary}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception("Workflow execution failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/workflows/list")
def list_workflows():
    return {"workflows": planner.list_workflows()}


class SlackSendRequest(BaseModel):
    channel: str
    text: str


@app.post("/agents/slack/send")
async def send_slack(req: SlackSendRequest):
    try:
        res = await slack_agent.act(req.channel, req.text)
        return {"result": res}
    except Exception as e:
        logger.exception("Slack send failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/workflows/logs")
async def get_workflow_logs(limit: int = 20):
    try:
        runs = await store.list_runs(limit=limit)
        return {"runs": runs}
    except Exception as e:
        logger.exception("Failed to fetch workflow logs: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/insights")
async def analytics_insights():
    try:
        metrics = await compute_metrics(store)
        return {"metrics": metrics}
    except Exception as e:
        logger.exception("Failed to compute analytics: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/failures")
async def analytics_failures(limit: int = 20):
    try:
        failures = await get_recent_failures(store, limit=limit)
        return {"failures": failures}
    except Exception as e:
        logger.exception("Failed to fetch failures: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=True)
