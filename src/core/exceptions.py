class ToolConnectionError(Exception):
    """Raised when a tool connection cannot be established."""


class WorkflowExecutionError(Exception):
    """Raised when executing a workflow fails in the planner or router."""


class InvalidWorkflowError(Exception):
    """Raised when a requested workflow does not exist or is malformed."""
