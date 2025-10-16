from typing import Any, Dict, List, Optional

from src.utils.logger import get_logger
from src.core.interfaces import ToolRouterInterface
from src.core.config import settings



logger = get_logger("ToolRouterStub")


class ToolRouterStub(ToolRouterInterface):
    """A lightweight stub for Composio ToolRouter used for local development and testing.

    In production, swap this for the real Composio ToolRouter client and remove the stub.
    """

    def __init__(self, api_key: Optional[str] = None):
        # Prefer pydantic settings for validated config
        self.api_key = api_key or settings.COMPOSIO_API_KEY
        self.connections: Dict[str, Any] = {}

    # Connection management
    def connect(self, name: str, token: Optional[str] = None) -> Dict[str, str]:
        self.connections[name] = {"token": token}
        logger.info("Connected stub tool: %s", name)
        return {"status": "connected", "tool": name}

    def manage_connections(self) -> Dict[str, Any]:
        """Return a summary of connected tools (stub)."""
        return {"connections": list(self.connections.keys())}

    # Meta-tools
    def plan(self, plan_definition: dict) -> Dict[str, Any]:
        """Accept a plan and return a plan_id and a normalized plan (stubbed).

        plan_definition: a dict describing steps. Returns a plan record with id.
        """
        plan_id = f"plan_{len(plan_definition.get('steps', []))}"
        logger.info("Registered plan %s", plan_id)
        return {"plan_id": plan_id, "plan": plan_definition}

    def multi_execute(self, executions: List[dict]) -> List[dict]:
        """Simulate executing multiple actions across tools.

        executions: list of {tool, action, payload}
        Returns a list of execution results.
        """
        results = []
        for ex in executions:
            tool = ex.get("tool")
            action = ex.get("action")
            payload = ex.get("payload")
            logger.info("Stub executing %s.%s with payload %s", tool, action, payload)
            # For cross-tool orchestration, inject realistic mappings
            if tool == "gmail":
                # return some messages
                results.append({"tool": tool, "action": action, "status": "ok", "payload": payload, "messages": [{"id": "m1", "subject": "Weekly update"}]})
            elif tool == "slack":
                results.append({"tool": tool, "action": action, "status": "ok", "payload": payload, "ts": "12345"})
            elif tool == "notion":
                results.append({"tool": tool, "action": action, "status": "ok", "payload": payload, "page_id": "p_1"})
            else:
                results.append({"tool": tool, "action": action, "status": "ok", "payload": payload})
        return results

    def search(self, query: str) -> Dict[str, Any]:
        """Stub for contextual search across connected tools."""
        logger.info("Stub search: %s", query)
        return {"query": query, "results": []}

    def remote_workbench(self, tool: str, test_payload: dict) -> Dict[str, Any]:
        """Simulate remote workbench testing of a tool action."""
        logger.info("Remote workbench: %s -> %s", tool, test_payload)
        return {"tool": tool, "tested": True, "payload": test_payload}

    def invoke(self, tool: str, method: str, payload: Optional[dict] = None) -> dict:
        # Simple local stub behavior for direct tool invocation
        logger.info("Invoking %s.%s with %s", tool, method, payload)
        return {"tool": tool, "method": method, "payload": payload or {}, "status": "ok"}
