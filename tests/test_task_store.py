import pytest

from src.core.task_store import TaskStore


@pytest.mark.asyncio
async def test_add_and_get_task(tmp_path):
    db_file = tmp_path / "test_tasks.db"
    store = TaskStore(db_path=str(db_file))
    await store.connect()
    try:
        t = await store.add_task_async(source="test", title="hello", description="desc")
        assert t.id is not None
        got = await store.get_task_async(t.id)
        assert got is not None
        assert got.title == "hello"
    finally:
        await store.disconnect()
