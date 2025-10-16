from .task_store import TaskStore


class AnalyticsEngine:
    def __init__(self, store: TaskStore):
        self.store = store

    async def overdue_percentage(self) -> float:
        tasks = await self.store.list_tasks_async()
        if not tasks:
            return 0.0
        overdue = [t for t in tasks if t.status == "overdue"]
        return len(overdue) / len(tasks) * 100.0

    async def active_tasks_count(self) -> int:
        tasks = await self.store.list_tasks_async()
        return len([t for t in tasks if t.status in ("open", "in_progress")])

    async def average_response_time(self) -> float:
        # Placeholder: in production compute from task metadata timestamps
        return 0.0
