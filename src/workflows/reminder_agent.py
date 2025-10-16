from typing import Dict, Any
from src.agents.base_agent import BaseAgent


class ReminderAgent(BaseAgent):
    async def poll(self) -> None:
        # Periodically check TaskStore (via core) for overdue tasks and schedule reminders
        return

    async def act(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Send reminder via ToolRouter
        return {"status": "ok"}
