import pytest
from unittest.mock import AsyncMock, patch

from src.agents.slack_agent import SlackAgent
from src.core.config import settings


@pytest.mark.asyncio
async def test_slack_agent_with_token(monkeypatch):
    # Set token on settings
    monkeypatch.setattr(settings, "SLACK_BOT_TOKEN", "x-token", raising=False)

    # Mock AsyncWebClient to return a client with auth_test and chat_postMessage
    mock_client = AsyncMock()
    mock_client.auth_test.return_value = {"team": "T"}
    mock_client.chat_postMessage.return_value = {"ts": "123", "channel": "C"}

    # Patch the module-level symbol exposed by our SlackAgent so tests are
    # independent of slack_sdk package layout.
    with patch("src.agents.slack_agent.AsyncWebClient", return_value=mock_client):
        agent = SlackAgent()
        res = await agent.connect()
        assert res["status"] in ("connected", "mock")

        send = await agent.act("#test", "hello")
        assert send["status"] in ("ok", "mock")


@pytest.mark.asyncio
async def test_slack_agent_without_token(monkeypatch):
    # Ensure no token present
    monkeypatch.setattr(settings, "SLACK_BOT_TOKEN", None, raising=False)
    agent = SlackAgent()
    res = await agent.connect()
    assert res["status"] == "mock"

    send = await agent.act("#test", "hello")
    assert send["status"] == "mock"
