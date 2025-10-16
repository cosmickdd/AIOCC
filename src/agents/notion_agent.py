from typing import Optional, Dict, Any, List
import asyncio
from datetime import datetime

from src.core.config import settings
from src.utils.logger import get_logger
from .base_agent import BaseAgent

logger = get_logger("NotionAgent")


try:
    NotionClient = None
except Exception:
    NotionClient = None


class NotionAgent(BaseAgent):
    def __init__(self, router=None):
        super().__init__(router)
        self.token = getattr(settings, "NOTION_API_KEY", None)
        self._client = None

    async def _ensure_client(self):
        if not self.token:
            return None
        if NotionClient is None:
            return None
        if self._client is None:
            self._client = NotionClient(token=self.token)
        return self._client

    async def connect(self) -> Dict[str, Any]:
        if not self.token:
            logger.info("No NOTION_API_KEY provided; NotionAgent in mock mode")
            return {"status": "mock"}
        client = await self._ensure_client()
        if client:
            return {"status": "connected"}
        return {"status": "mock"}

    async def poll(self, database_id: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        if not self.token:
            now = datetime.utcnow().isoformat()
            return [
                {"id": "t1", "title": "Finish report", "status": "open", "ts": now},
                {"id": "t2", "title": "Plan meeting", "status": "open", "ts": now},
            ]
        client = await self._ensure_client()
        if client:
            try:
                res = client.query_tasks(database_id=database_id, limit=limit)
                if asyncio.iscoroutine(res):
                    tasks = await res  # type: ignore
                else:
                    tasks = res
                return tasks
            except Exception as e:
                logger.exception("Notion poll failed: %s", e)
                return []
        return []

    async def act(self, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        # create page or update task
        if not self.token:
            logger.info("Mock Notion action %s: %s", action, payload)
            return {"status": "ok", "action": action, "payload": payload}
        client = await self._ensure_client()
        if client:
            try:
                if action == "create_summary_page":
                    res = client.create_page(payload)
                    if asyncio.iscoroutine(res):
                        page = await res  # type: ignore
                    else:
                        page = res
                    return {"status": "ok", "page_id": page.get("id")}
                elif action == "update_task":
                    res = client.update_task(payload.get("id"), payload)
                    if asyncio.iscoroutine(res):
                        res = await res  # type: ignore
                    return {"status": "ok", "result": res}
            except Exception as e:
                logger.exception("Notion act failed: %s", e)
                return {"status": "error", "error": str(e)}
        return {"status": "error", "error": "no-client"}

    def send(self, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return asyncio.run(self.act(action, payload))
