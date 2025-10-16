from typing import Dict, Any
from .base_agent import BaseAgent


class DriveAgent(BaseAgent):
    async def poll(self) -> None:
        # stub: scan Drive for documents with action items
        return

    async def act(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # stub: create document or add comment
        return {"status": "ok"}
