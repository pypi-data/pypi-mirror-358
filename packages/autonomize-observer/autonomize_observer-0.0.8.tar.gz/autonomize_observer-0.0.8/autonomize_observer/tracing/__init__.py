"""Tracing module for autonomize observer."""

from .base_tracer import BaseTracer

# Import the main agent tracer implementation
try:
    from .agent_tracer import AgentTracer, streaming_trace

    # Make AgentTracer available as AgentTracer for convenience
    AgentTracer = AgentTracer
    _has_tracer = True
except ImportError:
    _has_tracer = False
    AgentTracer = None
    AgentTracer = None
    streaming_trace = None

# Export list
__all__ = [
    "BaseTracer",
]

# Add available tracers to exports
if _has_tracer:
    __all__.extend(["AgentTracer", "AgentTracer", "streaming_trace"])
