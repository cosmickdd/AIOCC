from typing import Dict, Any, List
import asyncio
from datetime import datetime

from src.core.config import settings
from src.utils.logger import get_logger

logger = get_logger("SlackAgent")


# Try to import the async Slack client in a safe way. Some slack_sdk
# installations expose different module paths depending on version; we
# expose a module-level name so tests can reliably patch it.
try:
    from slack_sdk.web.async_client import AsyncWebClient  # type: ignore
except Exception:
    AsyncWebClient = None  # type: ignore


class SlackAgent:
    """Simple Slack agent that can send messages and poll a channel.

    If SLACK_BOT_TOKEN is set in `settings`, it will attempt to use the async
    slack_sdk client. Otherwise it falls back to mock behavior for local dev.
    """

    def __init__(self, router=None):
        self.router = router
        self.token = getattr(settings, "SLACK_BOT_TOKEN", None)
        self._client = None

    async def _ensure_client(self):
        if not self.token:
            return None
        try:
            # Prefer the module-level AsyncWebClient if available (and
            # patchable in tests). Fall back to importing the SDK at runtime
            # if needed.
            ClientCls = AsyncWebClient
            if ClientCls is None:
                from slack_sdk.web.async_client import AsyncWebClient as ClientCls  # type: ignore

            if self._client is None:
                self._client = ClientCls(token=self.token)
            return self._client
        except Exception:
            logger.info("slack_sdk not available; falling back to HTTP or mock")
            return None

    async def connect(self) -> Dict[str, Any]:
        if not self.token:
            logger.info("No SLACK_BOT_TOKEN provided; SlackAgent in mock mode")
            return {"status": "mock"}
        client = await self._ensure_client()
        if client:
            try:
                resp = await client.auth_test()
                return {"status": "connected", "team": resp.get("team")}
            except Exception as e:
                logger.exception("Slack auth failed: %s", e)
                return {"status": "error", "error": str(e)}
        return {"status": "mock"}

    async def poll(self, channel: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch recent messages from a channel. In mock mode return sample data."""
        if not self.token:
            # return mock data
            now = datetime.utcnow().isoformat()
            return [{"text": "Mock message 1", "ts": now}, {"text": "Mock message 2", "ts": now}]

        client = await self._ensure_client()
        if client:
            try:
                res = await client.conversations_history(channel=channel, limit=limit)
                return res.get("messages", [])
            except Exception as e:
                logger.exception("Failed to poll Slack: %s", e)
                return []
        return []

    async def act(self, channel: str, text: str) -> Dict[str, Any]:
        """Send message to a Slack channel. Uses real client if token present, otherwise mock."""
        if not self.token:
            logger.info("Mock send to %s: %s", channel, text)
            return {"status": "mock", "channel": channel, "text": text}

        client = await self._ensure_client()
        if client:
            try:
                resp = await client.chat_postMessage(channel=channel, text=text)
                return {"status": "ok", "ts": resp.get("ts"), "channel": resp.get("channel")}
            except Exception as e:
                logger.exception("Failed to send Slack message: %s", e)
                return {"status": "error", "error": str(e)}

        # Final fallback
        logger.info("Fallback send to %s: %s", channel, text)
        return {"status": "mock", "channel": channel, "text": text}

    # sync compatibility
    def send(self, channel: str, text: str) -> Dict[str, Any]:
        return asyncio.run(self.act(channel, text))
