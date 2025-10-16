from typing import Dict, Any, List
import asyncio
from datetime import datetime

from src.core.config import settings
from src.utils.logger import get_logger

logger = get_logger("GmailAgent")


# Try to import a real client if available; tests may patch this symbol.
try:
    # Placeholder for real Gmail client imports
    GmailClient = None
except Exception:
    GmailClient = None


class GmailAgent:
    """Simple Gmail agent (mock-first) that can poll and act on messages.

    Methods are async to match the rest of the agents.
    """

    def __init__(self, router=None):
        self.router = router
        self.token = getattr(settings, "GMAIL_API_KEY", None)
        self._client = None

    async def _ensure_client(self):
        if not self.token:
            return None
        # if a real client were available it would be instantiated here
        if GmailClient is None:
            return None
        if self._client is None:
            self._client = GmailClient(api_key=self.token)
        return self._client

    async def connect(self) -> Dict[str, Any]:
        if not self.token:
            logger.info("No GMAIL_API_KEY provided; GmailAgent in mock mode")
            return {"status": "mock"}
        client = await self._ensure_client()
        if client:
            # would perform oauth flow / auth_test
            return {"status": "connected"}
        return {"status": "mock"}

    async def poll(self, label: str = "STARRED", limit: int = 10) -> List[Dict[str, Any]]:
        """Return a list of message dicts. In mock mode returns sample messages."""
        if not self.token:
            now = datetime.utcnow().isoformat()
            return [
                {"id": "m1", "subject": "Weekly update", "from": "alice@example.com", "snippet": "Here are my updates", "ts": now},
                {"id": "m2", "subject": "Action needed", "from": "bob@example.com", "snippet": "Please review", "ts": now},
            ]

        client = await self._ensure_client()
        if client:
            # integrate with real Gmail API
            try:
                res = client.fetch_messages(label=label, limit=limit)
                if asyncio.iscoroutine(res):
                    msgs = await res  # type: ignore
                else:
                    msgs = res
                return msgs
            except Exception as e:
                logger.exception("Gmail poll failed: %s", e)
                return []
        return []

    async def act(self, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Perform actions like mark_processed or send_followup."""
        if not self.token:
            logger.info("Mock Gmail action %s with %s", action, payload)
            return {"status": "ok", "action": action, "payload": payload}

        client = await self._ensure_client()
        if client:
            try:
                if action == "mark_processed":
                    res = client.mark_message(payload.get("id"))
                    if asyncio.iscoroutine(res):
                        res = await res  # type: ignore
                    return {"status": "ok", "result": res}
                elif action == "send_followup":
                    res = client.send_message(payload)
                    if asyncio.iscoroutine(res):
                        res = await res  # type: ignore
                    return {"status": "ok", "result": res}
            except Exception as e:
                logger.exception("Gmail act failed: %s", e)
                return {"status": "error", "error": str(e)}
        return {"status": "error", "error": "no-client"}

    # sync compatibility
    def send(self, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return asyncio.run(self.act(action, payload))

