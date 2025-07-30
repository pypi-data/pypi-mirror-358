"""Tracing module for autonomize observer."""

from .base_tracer import BaseTracer

# Import the main agent tracer implementation
try:
    from .agent_tracer import StreamingAgentTracer, streaming_trace

    # Make StreamingAgentTracer available as AgentTracer for convenience
    AgentTracer = StreamingAgentTracer
    _has_tracer = True
except ImportError:
    _has_tracer = False
    StreamingAgentTracer = None
    AgentTracer = None
    streaming_trace = None

# Export list
__all__ = [
    "BaseTracer",
]

# Add available tracers to exports
if _has_tracer:
    __all__.extend(["StreamingAgentTracer", "AgentTracer", "streaming_trace"])
