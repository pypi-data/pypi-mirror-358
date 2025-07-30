"""
Kafka module for autonomize_observer.

Provides Kafka producer and schema definitions for high-performance async tracing.
"""

# Import schemas first
from .schemas import TraceEventType, TraceEvent, SpanInfo, CompleteTrace, LLMCallEvent

# Import producer with optional dependency handling
try:
    from .producer import KafkaTraceProducer

    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    KafkaTraceProducer = None

__all__ = [
    "TraceEventType",
    "TraceEvent",
    "SpanInfo",
    "CompleteTrace",
    "LLMCallEvent",
    "KafkaTraceProducer",
    "KAFKA_AVAILABLE",
]
