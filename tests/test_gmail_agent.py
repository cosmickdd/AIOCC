import pytest
from src.agents.gmail_agent import GmailAgent


@pytest.mark.asyncio
async def test_gmail_agent_mock():
    agent = GmailAgent(router=None)
    res = await agent.connect()
    assert res["status"] == "mock"
    msgs = await agent.poll()
    assert isinstance(msgs, list) and len(msgs) >= 1
    act = await agent.act("mark_processed", {"id": "m1"})
    assert act["status"] == "ok"
