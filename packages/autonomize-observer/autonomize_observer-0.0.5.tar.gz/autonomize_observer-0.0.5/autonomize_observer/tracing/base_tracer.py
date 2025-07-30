from __future__ import annotations
import asyncio
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Optional
import time
import uuid

if TYPE_CHECKING:
    from collections.abc import Sequence


class BaseTracer(ABC):
    """Base class for all tracers in the ML observability system."""

    def __init__(
        self, trace_name: str, trace_type: str, project_name: str, trace_id: uuid.UUID
    ):
        self.trace_name = trace_name
        self.trace_type = trace_type
        self.project_name = project_name
        self.trace_id = trace_id
        self.spans = {}
        self.start_time = time.time()

    @property
    @abstractmethod
    def ready(self) -> bool:
        """Check if tracer is ready to use."""
        raise NotImplementedError

    @abstractmethod
    def add_trace(
        self,
        trace_id: str,
        trace_name: str,
        trace_type: str,
        inputs: dict[str, Any],
        metadata: dict[str, Any] | None = None,
        vertex: Any | None = None,
    ) -> None:
        """Add a new trace span."""
        raise NotImplementedError

    @abstractmethod
    def end_trace(
        self,
        trace_id: str,
        trace_name: str,
        outputs: dict[str, Any] | None = None,
        error: Exception | None = None,
        logs: Sequence[Any] = (),
    ) -> None:
        """End a trace span."""
        raise NotImplementedError

    @abstractmethod
    def end(
        self,
        inputs: dict[str, Any],
        outputs: dict[str, Any],
        error: Exception | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """End the entire trace."""
        raise NotImplementedError

    def get_langchain_callback(self):
        """Return langchain callback if applicable."""
        return None
