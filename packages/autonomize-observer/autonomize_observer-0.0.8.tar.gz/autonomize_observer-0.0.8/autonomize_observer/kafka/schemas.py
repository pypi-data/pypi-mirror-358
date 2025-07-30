"""
Message schemas for Kafka trace events.

Defines the structure and types for trace events sent to Kafka topics.
"""

import json
import types
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional, Union, List, AsyncIterator, Generator, Iterator
from dataclasses import dataclass, asdict


def _safe_serialize_value(obj: Any) -> Any:
    """
    Safely serialize values that might contain non-serializable objects.

    Handles generators, iterators, and other objects similar to Langflow's approach.
    """
    if obj is None:
        return None

    # Handle generators, iterators, and async iterators
    if isinstance(obj, (AsyncIterator, Generator, Iterator, types.GeneratorType)):
        return "Unconsumed Stream"

    # Handle dictionaries recursively
    if isinstance(obj, dict):
        return {k: _safe_serialize_value(v) for k, v in obj.items()}

    # Handle lists and tuples recursively
    if isinstance(obj, (list, tuple)):
        return [_safe_serialize_value(item) for item in obj]

    # Handle primitive types
    if isinstance(obj, (str, int, float, bool)):
        return obj

    # Handle datetime
    if isinstance(obj, datetime):
        return obj.isoformat()

    # Handle enums
    if isinstance(obj, Enum):
        return obj.value

    # For any other object, convert to string representation
    try:
        # Try to use JSON serialization first
        json.dumps(obj)
        return obj
    except (TypeError, ValueError):
        # If not JSON serializable, convert to string
        try:
            return str(obj)
        except Exception:
            # If str() also fails, return a safe representation
            return f"<{type(obj).__name__} object>"


class TraceEventType(str, Enum):
    """Types of trace events."""

    TRACE_START = "trace_start"
    TRACE_END = "trace_end"
    SPAN_START = "span_start"
    SPAN_END = "span_end"
    COMPLETE_TRACE = "complete_trace"  # New type for complete traces
    CUSTOM = "custom"  # For custom events like LLM callbacks


@dataclass
class SpanInfo:
    """Information about a single span within a trace."""

    span_id: str
    component_id: str
    component_name: str
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    parent_span_id: Optional[str] = None  # ✅ Added parent relationship tracking
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values and safely serializing objects."""
        data = asdict(self)
        # Safely serialize all values
        safe_data = {
            k: _safe_serialize_value(v) for k, v in data.items() if v is not None
        }
        return safe_data


@dataclass
class CompleteTrace:
    """Schema for complete trace objects sent to Kafka."""

    # Core identifiers
    trace_id: str
    flow_id: str
    flow_name: str

    # Timing
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None

    # Context
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    project_name: str = "GenesisStudio"

    # Spans
    spans: List[SpanInfo] = None

    # Flow-level data
    flow_inputs: Optional[Dict[str, Any]] = None
    flow_outputs: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

    # Error handling
    error: Optional[str] = None

    # Metrics
    total_components: int = 0

    def __post_init__(self):
        """Initialize default values."""
        if self.spans is None:
            self.spans = []
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with safe serialization."""
        data = asdict(self)
        # Convert SpanInfo objects to dicts
        data["spans"] = [
            span.to_dict() if isinstance(span, SpanInfo) else span
            for span in data["spans"]
        ]
        # Safely serialize all values
        safe_data = {
            k: _safe_serialize_value(v) for k, v in data.items() if v is not None
        }
        return safe_data

    def to_json(self) -> str:
        """Convert to JSON string with safe serialization."""
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_json(cls, json_str: str) -> "CompleteTrace":
        """Create CompleteTrace from JSON string."""
        data = json.loads(json_str)
        # Convert span dicts back to SpanInfo objects
        if "spans" in data:
            data["spans"] = [
                SpanInfo(**span) if isinstance(span, dict) else span
                for span in data["spans"]
            ]
        return cls(**data)

    def get_partition_key(self) -> str:
        """Get the partition key for Kafka partitioning (trace_id)."""
        return self.trace_id

    def add_span(self, span: SpanInfo):
        """Add a span to the trace."""
        self.spans.append(span)
        self.total_components = len(self.spans)


@dataclass
class TraceEvent:
    """Schema for trace events sent to Kafka."""

    # Core identifiers
    trace_id: str
    event_type: TraceEventType
    timestamp: str

    # Optional span information
    span_id: Optional[str] = None
    parent_span_id: Optional[str] = None
    component_id: Optional[str] = None
    component_name: Optional[str] = None

    # Flow context
    flow_id: Optional[str] = None
    flow_name: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None

    # Event data
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

    # Performance metrics
    duration_ms: Optional[float] = None
    error: Optional[str] = None

    @classmethod
    def create_trace_start(
        cls,
        trace_id: str,
        flow_id: str,
        flow_name: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "TraceEvent":
        """Create a trace start event."""
        return cls(
            trace_id=trace_id,
            event_type=TraceEventType.TRACE_START,
            timestamp=datetime.now(timezone.utc).isoformat(),
            flow_id=flow_id,
            flow_name=flow_name,
            user_id=user_id,
            session_id=session_id,
            metadata=metadata or {},
        )

    @classmethod
    def create_trace_end(
        cls,
        trace_id: str,
        duration_ms: float,
        metadata: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> "TraceEvent":
        """Create a trace end event."""
        return cls(
            trace_id=trace_id,
            event_type=TraceEventType.TRACE_END,
            timestamp=datetime.now(timezone.utc).isoformat(),
            duration_ms=duration_ms,
            metadata=metadata or {},
            error=error,
        )

    @classmethod
    def create_span_start(
        cls,
        trace_id: str,
        span_id: str,
        component_id: str,
        component_name: str,
        parent_span_id: Optional[str] = None,
        input_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "TraceEvent":
        """Create a span start event."""
        return cls(
            trace_id=trace_id,
            event_type=TraceEventType.SPAN_START,
            timestamp=datetime.now(timezone.utc).isoformat(),
            span_id=span_id,
            parent_span_id=parent_span_id,
            component_id=component_id,
            component_name=component_name,
            input_data=input_data or {},
            metadata=metadata or {},
        )

    @classmethod
    def create_span_end(
        cls,
        trace_id: str,
        span_id: str,
        duration_ms: float,
        output_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> "TraceEvent":
        """Create a span end event."""
        return cls(
            trace_id=trace_id,
            event_type=TraceEventType.SPAN_END,
            timestamp=datetime.now(timezone.utc).isoformat(),
            span_id=span_id,
            duration_ms=duration_ms,
            output_data=output_data or {},
            metadata=metadata or {},
            error=error,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values and safely serializing objects."""
        data = asdict(self)
        # Safely serialize all values
        safe_data = {
            k: _safe_serialize_value(v) for k, v in data.items() if v is not None
        }
        return safe_data

    def to_json(self) -> str:
        """Convert to JSON string with safe serialization."""
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_json(cls, json_str: str) -> "TraceEvent":
        """Create TraceEvent from JSON string."""
        data = json.loads(json_str)
        # Convert event_type back to enum
        if "event_type" in data:
            data["event_type"] = TraceEventType(data["event_type"])
        return cls(**data)

    def get_partition_key(self) -> str:
        """Get the partition key for Kafka partitioning (trace_id)."""
        return self.trace_id


@dataclass
class LLMCallEvent:
    """Event for direct LLM call monitoring (not part of a flow trace)."""

    event_type: str  # llm_call_start, llm_call_end, llm_metric
    event_id: str
    timestamp: str
    call_id: str  # Unique identifier for this LLM call

    # LLM call specific fields
    model: Optional[str] = None
    provider: Optional[str] = None

    # Timing
    duration_ms: Optional[float] = None

    # Token usage
    usage: Optional[Dict[str, int]] = (
        None  # {prompt_tokens, completion_tokens, total_tokens}
    )

    # Request/response data
    messages: Optional[List[Dict]] = None  # Input messages
    response: Optional[str] = None  # Response content (truncated)

    # Parameters
    params: Optional[Dict[str, Any]] = None  # {temperature, max_tokens, etc.}

    # Error handling
    error: Optional[str] = None

    # User context
    user_id: Optional[str] = None
    session_id: Optional[str] = None

    # Project context
    project_name: Optional[str] = None

    # Cost tracking
    cost: Optional[float] = None

    # Metadata
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Kafka serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LLMCallEvent":
        """Create from dictionary for Kafka deserialization."""
        return cls(**data)

    @classmethod
    def create_llm_start(
        cls,
        call_id: str,
        model: str,
        provider: str,
        messages: List[Dict],
        params: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        project_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "LLMCallEvent":
        """Factory method for LLM call start events."""
        return cls(
            event_type="llm_call_start",
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            call_id=call_id,
            model=model,
            provider=provider,
            messages=messages,
            params=params or {},
            user_id=user_id,
            session_id=session_id,
            project_name=project_name,
            metadata=metadata or {},
        )

    @classmethod
    def create_llm_end(
        cls,
        call_id: str,
        model: str,
        provider: str,
        duration_ms: float,
        usage: Dict[str, int],
        messages: Optional[List[Dict]] = None,
        response: Optional[str] = None,
        cost: Optional[float] = None,
        error: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        project_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "LLMCallEvent":
        """Factory method for LLM call end events."""
        return cls(
            event_type="llm_call_end",
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            call_id=call_id,
            model=model,
            provider=provider,
            duration_ms=duration_ms,
            usage=usage,
            messages=messages,
            response=response[:500] if response else None,
            cost=cost,
            error=error,
            user_id=user_id,
            session_id=session_id,
            project_name=project_name,
            metadata=metadata or {},
        )

    @classmethod
    def create_llm_metric(
        cls,
        call_id: str,
        metrics: Dict[str, float],
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "LLMCallEvent":
        """Factory method for LLM metric events."""
        return cls(
            event_type="llm_metric",
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            call_id=call_id,
            user_id=user_id,
            session_id=session_id,
            metadata={**(metadata or {}), "metrics": metrics},
        )

    def get_partition_key(self) -> str:
        """Get the partition key for Kafka partitioning (call_id)."""
        return self.call_id

    def to_json(self) -> str:
        """Convert to JSON string for Kafka serialization."""
        return json.dumps(self.to_dict(), default=str)
