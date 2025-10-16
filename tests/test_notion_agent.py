import pytest
from src.agents.notion_agent import NotionAgent


@pytest.mark.asyncio
async def test_notion_agent_mock():
    agent = NotionAgent(router=None)
    res = await agent.connect()
    assert res["status"] == "mock"
    tasks = await agent.poll()
    assert isinstance(tasks, list) and len(tasks) >= 1
    act = await agent.act("create_summary_page", {"title": "Weekly"})
    assert act["status"] == "ok"
