from typing import Dict, Any, List, Optional
from src.core.interfaces import ToolRouterInterface
from src.core.task_store import TaskStore
from src.utils.logger import get_logger
from src.workflows.workflow_templates.weekly_review import weekly_review_plan
from src.workflows.workflow_templates.weekly_review_cross_tool import weekly_review_cross_tool_plan
from datetime import datetime
import asyncio


logger = get_logger("WorkflowPlanner")


class WorkflowPlanner:
    """Loads workflow templates and executes them via ToolRouter meta-tools (stubbed).

    The planner supports parameterized runs where a mapping of params will replace
    placeholders in plan step payloads. Placeholders use the format {{param}}.
    """

    def __init__(self, router: ToolRouterInterface, store: TaskStore):
        self.router = router
        self.store = store
        # registry maps workflow name to a function returning plan
        self.registry: Dict[str, Any] = {
            "weekly_review": weekly_review_plan,
            "weekly_review_cross_tool": weekly_review_cross_tool_plan,
        }

    def list_workflows(self) -> List[str]:
        return list(self.registry.keys())

    def load_plan(self, workflow_name: str) -> Dict[str, Any]:
        if workflow_name not in self.registry:
            raise KeyError(f"workflow not found: {workflow_name}")
        plan_def = self.registry[workflow_name]()
        logger.info("Loaded plan for %s", workflow_name)
        return plan_def

    @staticmethod
    def _replace_placeholders(obj: Any, params: Dict[str, Any]) -> Any:
        """Recursively replace placeholders in dict/list/str using params."""
        if isinstance(obj, str):
            result = obj
            for k, v in params.items():
                placeholder = f"{{{{{k}}}}}"
                result = result.replace(placeholder, str(v))
            return result
        elif isinstance(obj, dict):
            return {k: WorkflowPlanner._replace_placeholders(v, params) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [WorkflowPlanner._replace_placeholders(v, params) for v in obj]
        else:
            return obj

    async def run(self, workflow_name: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run the named workflow and return a summary of actions taken (stubbed).

        params: optional runtime parameters used to fill placeholders in step payloads.
        """
        params = params or {}
        plan_def = self.load_plan(workflow_name)

        # Apply params to plan-level fields (deep replace)
        plan_def = WorkflowPlanner._replace_placeholders(plan_def, params)

        plan_record = self.router.plan(plan_def)

        # Persist run start
        started_at = datetime.utcnow().isoformat()
        run_id = None
        try:
            if hasattr(self.store, "create_run"):
                run_id = await self.store.create_run(workflow_name, started_at, status="pending")
        except Exception as e:
            logger.exception("Failed to persist run: %s", e)


        # Create a sequence of executions from the plan steps (mapping)
        executions: List[Dict[str, Any]] = []
        for step in plan_def.get("steps", []):
            step_name = step.get("step")
            payload = step.get("payload", {})
            payload = WorkflowPlanner._replace_placeholders(payload, params)

            # Map to simple tool actions for demo. Add cross-tool mapping.
            if step_name == "fetch_tasks":
                executions.append({"tool": "notion", "action": "fetch_tasks", "payload": payload})
            elif step_name == "summarize":
                executions.append({"tool": "openai", "action": "summarize", "payload": payload})
            elif step_name == "notify":
                executions.append({"tool": "slack", "action": "post_message", "payload": payload})
            elif step_name == "fetch_emails":
                executions.append({"tool": "gmail", "action": "fetch_messages", "payload": payload})
            elif step_name == "persist_summary":
                executions.append({"tool": "notion", "action": "create_summary_page", "payload": payload})
            else:
                executions.append({"tool": "generic", "action": step_name, "payload": payload})

        # Execute with basic retry/backoff
        results: List[Dict[str, Any]] = []
        for idx, ex in enumerate(executions):
            attempt = 0
            max_attempts = 3
            backoff = 0.5
            while attempt < max_attempts:
                try:
                    # router.multi_execute may be async or sync and may return a coroutine or value
                    execute_result = self.router.multi_execute([ex])
                    if asyncio.iscoroutine(execute_result):
                        res = await execute_result
                    else:
                        res = execute_result
                    # router.multi_execute returns list; extend results
                    if isinstance(res, list):
                        results.extend(res)
                    else:
                        results.append(res)
                    break
                except Exception as e:
                    attempt += 1
                    logger.exception("Execution failed for %s, attempt %s: %s", ex, attempt, e)
                    if attempt >= max_attempts:
                        results.append({"tool": ex.get("tool"), "action": ex.get("action"), "status": "error", "error": str(e)})
                    else:
                        # sleep synchronously since this run() is sync
                        import time

                        time.sleep(backoff * attempt)


        summary = {
            "plan_id": plan_record.get("plan_id"),
            "executions": results,
            "params": params,
            "run_id": run_id,
        }
        # Persist run finish
        try:
            if run_id and hasattr(self.store, "update_run"):
                finished_at = datetime.utcnow().isoformat()
                status = "success" if all(r.get("status") == "ok" for r in results) else "error"
                log = {"executions": results, "params": params}
                await self.store.update_run(run_id, finished_at, status, log)
        except Exception:
            logger.exception("Failed to update run record")
        logger.info("Workflow %s executed: %s", workflow_name, summary)
        return summary
