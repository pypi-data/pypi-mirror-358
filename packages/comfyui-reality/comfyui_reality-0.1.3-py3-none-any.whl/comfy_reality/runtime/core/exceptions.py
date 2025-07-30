"""Runtime exceptions."""

from typing import Any


class RuntimeError(Exception):
    """Base runtime exception."""

    def __init__(self, message: str, code: str | None = None, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.code = code or self.__class__.__name__
        self.details = details or {}


class TaskError(RuntimeError):
    """Task execution error."""

    def __init__(self, message: str, task_id: str | None = None, **kwargs: Any):
        super().__init__(message, **kwargs)
        self.task_id = task_id
        if task_id:
            self.details["task_id"] = task_id


class WorkflowError(RuntimeError):
    """Workflow execution error."""

    def __init__(self, message: str, workflow_id: str | None = None, **kwargs: Any):
        super().__init__(message, **kwargs)
        self.workflow_id = workflow_id
        if workflow_id:
            self.details["workflow_id"] = workflow_id


class ValidationError(RuntimeError):
    """Validation error."""

    def __init__(self, message: str, field: str | None = None, value: Any | None = None, **kwargs: Any):
        super().__init__(message, **kwargs)
        if field:
            self.details["field"] = field
        if value is not None:
            self.details["value"] = value


class ConfigurationError(RuntimeError):
    """Configuration error."""

    def __init__(self, message: str, config_key: str | None = None, **kwargs: Any):
        super().__init__(message, **kwargs)
        if config_key:
            self.details["config_key"] = config_key
