from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class ToolRouterInterface(ABC):
    """Abstract interface for a ToolRouter client (Composio or stub).

    Implementations should provide plan and multi_execute semantics used by the
    WorkflowPlanner.
    """

    @abstractmethod
    def connect(self, name: str, token: Optional[str] = None) -> Dict[str, Any]:
        raise NotImplementedError()

    @abstractmethod
    def plan(self, plan_definition: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError()

    @abstractmethod
    def multi_execute(self, executions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        raise NotImplementedError()

    @abstractmethod
    def search(self, query: str) -> Dict[str, Any]:
        raise NotImplementedError()

    @abstractmethod
    def manage_connections(self) -> Dict[str, Any]:
        raise NotImplementedError()

    @abstractmethod
    def remote_workbench(self, tool: str, test_payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError()

    @abstractmethod
    def invoke(self, tool: str, method: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        raise NotImplementedError()
