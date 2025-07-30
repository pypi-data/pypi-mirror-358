"""Tracing module for autonomize observer."""

from .base_tracer import BaseTracer

# Import AgentTracer if Kafka dependencies are available
try:
    from .agent_tracer import AgentTracer
except ImportError:
    AgentTracer = None

__all__ = [
    "BaseTracer",
    "AgentTracer",
]
