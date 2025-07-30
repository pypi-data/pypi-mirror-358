"""
Autonomize Observer SDK for ML Observability.

This SDK provides observability capabilities for machine learning workloads
including tracing, monitoring, and analytics.
"""

from .version import __version__

# Core components
from .core.exceptions import ModelHubAPIException

# Kafka schemas
from .kafka.schemas import CompleteTrace, LLMCallEvent, SpanInfo

# Tracing
from .tracing.agent_tracer import AgentTracer

# Monitoring
from .monitoring.cost_tracking import CostTracker

# Utilities
from .utils.logger import setup_logger

# Converters (new)
from .converters.base_converter import BaseConverter
from .converters.mongodb_converter import MongoDBConverter
from .converters.metrics_converter import MetricsConverter

# Processing (new)
from .processing.base_processor import BaseProcessor
from .processing.observability_processor import ObservabilityProcessor

__all__ = [
    # Version
    "__version__",
    # Core
    "ModelHubAPIException",
    # Kafka schemas
    "CompleteTrace",
    "LLMCallEvent",
    "SpanInfo",
    # Tracing
    "AgentTracer",
    # Monitoring
    "CostTracker",
    # Utilities
    "setup_logger",
    # Converters
    "BaseConverter",
    "MongoDBConverter",
    "MetricsConverter",
    # Processing
    "BaseProcessor",
    "ObservabilityProcessor",
]
