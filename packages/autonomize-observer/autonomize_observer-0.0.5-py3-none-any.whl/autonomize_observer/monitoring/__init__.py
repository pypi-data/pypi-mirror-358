"""
Monitoring and observability module for LLM applications.

This module provides comprehensive monitoring capabilities including:
- Cost tracking for various LLM providers
- Async monitoring with Kafka support
- Client wrapping for OpenAI, Anthropic, and other providers

Usage:
    from autonomize_observer.monitoring import monitor, initialize

    # Initialize monitoring
    initialize()

    # Monitor an LLM client
    client = monitor(openai_client, provider="openai")
"""

from .monitor import (
    # Core functions
    initialize,
    monitor,
    # Decorators
    trace_async,
    trace_sync,
    agent,
    tool,
    # Classes
    Identify,
    # Utility functions
    identify,
    wrap_openai,
    wrap_anthropic,
    # Kafka LLM monitoring (consolidated into monitor.py)
    KafkaLLMMonitor,
    get_kafka_llm_monitor,
    close_kafka_llm_monitor,
    track_llm_call,
)

from .cost_tracking import CostTracker

__all__ = [
    # Core functions
    "initialize",
    "monitor",
    # Decorators
    "trace_async",
    "trace_sync",
    "agent",
    "tool",
    # Classes
    "Identify",
    "CostTracker",
    "KafkaLLMMonitor",
    # Utility functions
    "identify",
    "wrap_openai",
    "wrap_anthropic",
    "get_kafka_llm_monitor",
    "close_kafka_llm_monitor",
    "track_llm_call",
]
