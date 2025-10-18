from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass, field
import json
from pathlib import Path
import tempfile

import asyncio
from databases import Database
from sqlalchemy import (create_engine, MetaData, Table, Column, Integer, String, Text)

from src.utils.logger import get_logger
from src.core.config import settings
from src.core.exceptions import WorkflowExecutionError

logger = get_logger("TaskStore")


@dataclass
class Task:
    id: int
    source: str
    title: str
    description: Optional[str] = None
    owner: Optional[str] = None
    status: str = "open"
    metadata: Dict[str, Any] = field(default_factory=dict)


metadata_obj = MetaData()
tasks_table = Table(
    "tasks",
    metadata_obj,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("source", String(255)),
    Column("title", String(255)),
    Column("description", Text),
    Column("owner", String(255)),
    Column("status", String(50)),
    Column("metadata", Text),
)

workflow_runs_table = Table(
    "workflow_runs",
    metadata_obj,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("workflow_name", String(255)),
    Column("started_at", String(64)),
    Column("finished_at", String(64)),
    Column("status", String(50)),
    Column("log", Text),
)


class TaskStore:
    """Async TaskStore using databases and SQLAlchemy table definitions."""

    def __init__(self, db_url: Optional[str] = None, db_path: Optional[str] = None):
        # Backwards-compatible constructor: if db_path provided (tests), map to a sqlite URL
        if db_path is not None:
            if db_path == ":memory" or db_path == ":memory:":
                # Create a temporary file-backed SQLite DB so that both the
                # synchronous metadata.create_all (SQLAlchemy engine) and the
                # async `databases` connection operate on the same file. Using
                # SQLite in-memory would create isolated databases per
                # connection which breaks table visibility in tests.
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
                tmp.close()
                self._temp_db_file = tmp.name
                self.db_url = f"sqlite+aiosqlite:///{self._temp_db_file}"
            else:
                # treat db_path as file path
                self.db_url = f"sqlite+aiosqlite:///{db_path}"
        else:
            self.db_url = db_url or settings.DATABASE_URL
        # ensure directory exists for sqlite
        if db_path is not None and db_path not in (":memory", ":memory:"):
            # Use the explicit db_path provided by tests — safer on Windows
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        elif self.db_url.startswith("sqlite"):
            # Try to extract a file path from the URL (e.g. sqlite+aiosqlite:///C:/...)
            marker = ':///'
            if marker in self.db_url:
                path = self.db_url.split(marker, 1)[1]
            else:
                # fallback: remove protocol
                path = self.db_url.split('://', 1)[-1]
            if path and not path.startswith(":memory"):
                Path(path).parent.mkdir(parents=True, exist_ok=True)

        # Initialize the async Database instance for runtime operations
        self._db = Database(self.db_url)

        # Create engine for metadata.create_all on startup in tests/local runs.
        # For file-backed sqlite URLs this will create the needed tables so
        # the async connection can see them. Using an in-memory sqlite URL
        # would create separate databases per connection which is why we
        # use a temporary file above in that case.
        engine = create_engine(self.db_url.replace("+aiosqlite", ""))
        metadata_obj.create_all(engine)

    async def connect(self):
        await self._db.connect()

    async def create_run(self, workflow_name: str, started_at: str, status: str = "pending", log: Optional[Union[dict, list, str]] = None) -> int:
        try:
            import json as _json

            log_payload = _json.dumps(log or {})
            query = workflow_runs_table.insert().values(workflow_name=workflow_name, started_at=started_at, finished_at="", status=status, log=log_payload)
            run_id = await self._db.execute(query)
            return int(run_id)
        except Exception as e:
            logger.exception("Failed to create workflow run: %s", e)
            raise WorkflowExecutionError("Failed to create workflow run") from e

    async def update_run(self, run_id: int, finished_at: str, status: str, log: Optional[Union[dict, list, str]] = None):
        try:
            import json as _json

            log_payload = _json.dumps(log or {})
            query = workflow_runs_table.update().where(workflow_runs_table.c.id == run_id).values(finished_at=finished_at, status=status, log=log_payload)
            await self._db.execute(query)
        except Exception as e:
            logger.exception("Failed to update workflow run: %s", e)
            raise WorkflowExecutionError("Failed to update workflow run") from e

    async def list_runs(self, limit: int = 20, offset: int = 0, query: Optional[str] = None):
        try:
            import json as _json

            # Build base select
            sel = workflow_runs_table.select()
            # Apply simple search on workflow_name or status if provided
            if query:
                # SQLite simple LIKE search; databases/sqlalchemy will handle parameterization
                sel = sel.where(
                    (workflow_runs_table.c.workflow_name.ilike(f"%{query}%")) | (workflow_runs_table.c.status.ilike(f"%{query}%"))
                )
            # Order and limit/offset
            sel = sel.order_by(workflow_runs_table.c.id.desc()).limit(limit).offset(offset)
            rows = await self._db.fetch_all(sel)
            out = []
            for r in rows:
                obj = dict(r)
                try:
                    obj["log"] = _json.loads(obj.get("log") or "{}")
                except Exception:
                    obj["log"] = obj.get("log")
                out.append(obj)
            return out
        except Exception as e:
            logger.exception("Failed to list workflow runs: %s", e)
            raise WorkflowExecutionError("Failed to list workflow runs") from e

    async def disconnect(self):
        await self._db.disconnect()

    # Synchronous wrappers for legacy tests that call sync methods
    def _run_sync(self, coro):
        return asyncio.run(coro)

    async def add_task_async(self, source: str, title: str, description: Optional[str] = None, owner: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Task:
        try:
            query = tasks_table.insert().values(
                source=source,
                title=title,
                description=description,
                owner=owner,
                status="open",
                metadata=json.dumps(metadata or {}),
            )
            task_id = await self._db.execute(query)
            return Task(id=int(task_id), source=source, title=title, description=description, owner=owner, status="open", metadata=metadata or {})
        except Exception as e:
            logger.exception("Failed to add task: %s", e)
            raise WorkflowExecutionError("Failed to add task") from e

    async def list_tasks_async(self, status: Optional[str] = None) -> List[Task]:
        try:
            if status:
                query = tasks_table.select().where(tasks_table.c.status == status)
            else:
                query = tasks_table.select()
            rows = await self._db.fetch_all(query)
            return [Task(id=r["id"], source=r["source"], title=r["title"], description=r["description"], owner=r["owner"], status=r["status"], metadata=json.loads(r["metadata"] or "{}")) for r in rows]
        except Exception as e:
            logger.exception("Failed to list tasks: %s", e)
            raise WorkflowExecutionError("Failed to list tasks") from e

    async def get_task_async(self, task_id: int) -> Optional[Task]:
        try:
            query = tasks_table.select().where(tasks_table.c.id == task_id)
            r = await self._db.fetch_one(query)
            if not r:
                return None
            return Task(id=r["id"], source=r["source"], title=r["title"], description=r["description"], owner=r["owner"], status=r["status"], metadata=json.loads(r["metadata"] or "{}"))
        except Exception as e:
            logger.exception("Failed to get task: %s", e)
            raise WorkflowExecutionError("Failed to get task") from e

    async def update_status_async(self, task_id: int, status: str) -> bool:
        try:
            query = tasks_table.update().where(tasks_table.c.id == task_id).values(status=status)
            await self._db.execute(query)
            return True
        except Exception as e:
            logger.exception("Failed to update status: %s", e)
            raise WorkflowExecutionError("Failed to update status") from e

    # Removed synchronous wrappers for full async API surface.

