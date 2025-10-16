from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseAgent(ABC):
    def __init__(self, router: Any):
        self.router = router

    @abstractmethod
    async def poll(self, *args: Any, **kwargs: Any) -> Any:
        """Poll the upstream tool and ingest tasks/events."""

    @abstractmethod
    async def act(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Perform an action in the upstream tool (send message, create task)."""
