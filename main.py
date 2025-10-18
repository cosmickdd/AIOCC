import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from src.utils.logger import get_logger
from src.core.task_store import TaskStore
from src.core.toolrouter_config import ToolRouterStub
from src.core.analytics import AnalyticsEngine
from src.core.analytics_insights import compute_metrics, get_recent_failures
from src.core.workflow_planner import WorkflowPlanner
from src.agents.slack_agent import SlackAgent
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings

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
async def create_task(source: str, title: str, description: Optional[str] = None, owner: Optional[str] = None):
    task = await store.add_task_async(source=source, title=title, description=description, owner=owner)
    return {"task": task.__dict__}


@app.get("/tasks")
async def list_tasks(status: Optional[str] = None):
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
    params: Optional[Dict[str, Any]] = None


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
async def get_workflow_logs(limit: int = 50, offset: int = 0, query: Optional[str] = None):
    try:
        runs = await store.list_runs(limit=limit, offset=offset, query=query)
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


@app.get("/analytics/trends")
async def analytics_trends(days: int = 30, workflow: Optional[str] = None, start: Optional[str] = None, end: Optional[str] = None):
    """Return simple time-series of success/failure counts by day for the last `days` days.

    Query params:
    - days: lookback window in days (default 30)
    - workflow: optional workflow name to filter
    """
    try:
        runs = await store.list_runs(limit=5000)
        from datetime import datetime, timedelta

        # Determine date range: explicit start/end take precedence
        if start:
            try:
                start_dt = datetime.fromisoformat(start)
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid start date format; use ISO format YYYY-MM-DD")
        else:
            start_dt = None

        if end:
            try:
                end_dt = datetime.fromisoformat(end)
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid end date format; use ISO format YYYY-MM-DD")
        else:
            end_dt = None

        if start_dt and end_dt and end_dt < start_dt:
            raise HTTPException(status_code=400, detail="end date must be after start date")

        if not start_dt or not end_dt:
            # fallback to days window
            end_dt = datetime.utcnow()
            start_dt = end_dt - timedelta(days=days)

        # bucket by date
        buckets = {}
        delta = (end_dt.date() - start_dt.date()).days
        for i in range(delta + 1):
            d = (start_dt + timedelta(days=i)).date().isoformat()
            buckets[d] = {"success": 0, "failure": 0}

        for r in runs:
            wf = r.get("workflow_name")
            if workflow and wf != workflow:
                continue
            s = r.get("started_at")
            if not s:
                continue
            try:
                dt = datetime.fromisoformat(s)
            except Exception:
                continue
            if dt < start_dt or dt > end_dt:
                continue
            key = dt.date().isoformat()
            if r.get("status") == "success":
                buckets[key]["success"] += 1
            else:
                buckets[key]["failure"] += 1

        series = [
            {"date": k, "success": v["success"], "failure": v["failure"]}
            for k, v in sorted(buckets.items())
        ]
        return {"series": series}
    except Exception as e:
        logger.exception("Failed to compute trends: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents/status")
async def agents_status():
    """Return connectivity status for configured agents (Slack/Gmail/Notion)."""
    try:
        statuses = {}
        try:
            statuses["slack"] = await slack_agent.connect()
        except Exception as e:
            statuses["slack"] = {"status": "error", "error": str(e)}
        # Gmail and Notion agents may be created on demand
        from src.agents.gmail_agent import GmailAgent
        from src.agents.notion_agent import NotionAgent

        gmail = GmailAgent()
        notion = NotionAgent()
        try:
            statuses["gmail"] = await gmail.connect()
        except Exception as e:
            statuses["gmail"] = {"status": "error", "error": str(e)}
        try:
            statuses["notion"] = await notion.connect()
        except Exception as e:
            statuses["notion"] = {"status": "error", "error": str(e)}

        return {"agents": statuses}
    except Exception as e:
        logger.exception("Failed to fetch agent statuses: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


class AgentActionRequest(BaseModel):
    action: str
    payload: Optional[Dict[str, Any]] = None


@app.post("/agents/{agent}/action")
async def agent_action(agent: str, req: AgentActionRequest):
    """Trigger a simple agent action for testing (e.g., send test Slack message)."""
    try:
        agent = agent.lower()
        if agent == "slack":
            # send a test message to channel in payload.channel
            chan = (req.payload or {}).get("channel", "#general")
            text = (req.payload or {}).get("text", "Test message from AIOCC")
            res = await slack_agent.act(chan, text)
            return {"result": res}
        elif agent == "gmail":
            from src.agents.gmail_agent import GmailAgent

            g = GmailAgent()
            res = await g.act(req.action, req.payload or {})
            return {"result": res}
        elif agent == "notion":
            from src.agents.notion_agent import NotionAgent

            n = NotionAgent()
            res = await n.act(req.action, req.payload or {})
            return {"result": res}
        else:
            raise HTTPException(status_code=404, detail="Unknown agent")
    except Exception as e:
        logger.exception("Agent action failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/integrations")
def integrations():
    """Return which integrations appear configured. This endpoint does NOT return secrets.

    Example output: { slack: true, gmail: false }
    """
    try:
        return {
            "slack": bool(getattr(settings, "SLACK_BOT_TOKEN", None)),
            "gmail": bool(getattr(settings, "GMAIL_API_KEY", None)),
            "notion": bool(getattr(settings, "NOTION_API_KEY", None)),
        }
    except Exception as e:
        logger.exception("Failed to read integrations: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=True)
