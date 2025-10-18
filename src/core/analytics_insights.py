from typing import Any, Dict, List
import json
from datetime import datetime


async def compute_metrics(store) -> Dict[str, Any]:
    """Compute analytics metrics from workflow_runs table exposed by TaskStore.

    Returns a dict with keys: success_rate, avg_duration (seconds), failure_rate,
    top_failed_tools, most_active_workflows
    """
    runs = await store.list_runs(limit=1000)
    if not runs:
        return {
            "success_rate": 0.0,
            "avg_duration": 0.0,
            "failure_rate": 0.0,
            "top_failed_tools": [],
            "most_active_workflows": [],
            "total_runs": 0,
        }

    total = len(runs)
    successes = [r for r in runs if r.get("status") == "success"]
    failures = [r for r in runs if r.get("status") != "success"]

    # avg_duration: parse started_at/finished_at ISO strings
    durations = []
    for r in runs:
        try:
            s = r.get("started_at")
            f = r.get("finished_at")
            if s and f:
                dt_s = datetime.fromisoformat(s)
                dt_f = datetime.fromisoformat(f)
                durations.append((dt_f - dt_s).total_seconds())
        except Exception:
            continue

    avg_duration = sum(durations) / len(durations) if durations else 0.0

    # top_failed_tools: inspect logs for 'executions' and failure counts per tool
    from typing import Dict

    tool_fail_counts: Dict[str, int] = {}
    wf_counts: Dict[str, int] = {}
    for r in runs:
        wf = r.get("workflow_name")
        wf_counts[wf] = wf_counts.get(wf, 0) + 1
        log = r.get("log") or {}
        execs = []
        if isinstance(log, str):
            try:
                execs = json.loads(log).get("executions", [])
            except Exception:
                execs = []
        elif isinstance(log, dict):
            execs = log.get("executions", [])
        for ex in execs:
            if ex.get("status") != "ok":
                t = ex.get("tool") or "unknown"
                tool_fail_counts[t] = tool_fail_counts.get(t, 0) + 1

    top_failed_tools = sorted(tool_fail_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    most_active_workflows = sorted(wf_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "success_rate": len(successes) / total * 100.0,
        "avg_duration": avg_duration,
        "failure_rate": len(failures) / total * 100.0,
        "top_failed_tools": [{"tool": k, "fails": v} for k, v in top_failed_tools],
        "most_active_workflows": [{"workflow": k, "runs": v} for k, v in most_active_workflows],
        "total_runs": total,
    }


async def get_recent_failures(store, limit: int = 10) -> List[Dict[str, Any]]:
    runs = await store.list_runs(limit=limit)
    failures = [r for r in runs if r.get("status") != "success"]
    return failures[:limit]
