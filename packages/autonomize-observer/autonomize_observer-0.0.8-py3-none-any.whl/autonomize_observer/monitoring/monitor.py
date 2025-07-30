"""
Comprehensive monitoring and observability for LLM applications.

This module provides:
- Cost tracking for various LLM providers
- Async monitoring with Kafka support
- Client wrapping for OpenAI, Anthropic, and other providers
- Integration with observability systems

Note: All monitoring is now done via Kafka and MongoDB for centralized observability.
"""

import asyncio
import concurrent.futures
import functools
import logging
import os
import time
import threading
import uuid
from contextlib import contextmanager
from typing import Any, Callable, Dict, List, Optional, Union
from datetime import datetime, timezone

from autonomize_observer.core.exceptions import (
    ModelHubAPIException,
)
from autonomize_observer.utils import setup_logger
from .cost_tracking import CostTracker

# Import Kafka components with fallback
try:
    from autonomize_observer.kafka import (
        KafkaTraceProducer,
        LLMCallEvent,
        KAFKA_AVAILABLE,
    )
except ImportError:
    KAFKA_AVAILABLE = False
    KafkaTraceProducer = None
    LLMCallEvent = None

logger = setup_logger(__name__)

# Global state
_cost_tracker: Optional[CostTracker] = None
_initialized = False

# Add thread-local storage for run management
_local = threading.local()

# Global thread pool for non-blocking operations
_monitoring_executor = None
_monitoring_lock = threading.Lock()


class KafkaLLMMonitor:
    """
    Kafka-based LLM monitor for direct LLM call tracking.

    Sends LLM events to Kafka for centralized processing, replacing the
    local AsyncMonitor approach with a scalable distributed architecture.
    """

    def __init__(self, kafka_config: Optional[Dict[str, Any]] = None):
        """
        Initialize Kafka LLM monitor.

        Args:
            kafka_config: Optional Kafka configuration overrides
        """
        if not KAFKA_AVAILABLE:
            logger.warning(
                "Kafka not available. Install confluent-kafka for LLM monitoring: "
                "pip install confluent-kafka"
            )
            self._producer = None
            self._enabled = False
            return

        # Load Kafka configuration from environment
        kafka_config = kafka_config or {}
        default_config = {
            "bootstrap_servers": os.getenv(
                "AUTONOMIZE_KAFKA_BROKERS", "localhost:9092"
            ),
            "topic": os.getenv("AUTONOMIZE_KAFKA_TOPIC", "genesis-traces"),
            "client_id": os.getenv("AUTONOMIZE_KAFKA_CLIENT_ID", "genesis-llm-monitor"),
            "kafka_username": os.getenv("AUTONOMIZE_KAFKA_USERNAME"),
            "kafka_password": os.getenv("AUTONOMIZE_KAFKA_PASSWORD"),
            "security_protocol": os.getenv(
                "AUTONOMIZE_KAFKA_SECURITY_PROTOCOL", "PLAINTEXT"
            ),
            "sasl_mechanism": os.getenv("AUTONOMIZE_KAFKA_SASL_MECHANISM", "PLAIN"),
        }

        # Remove None values
        default_config = {k: v for k, v in default_config.items() if v is not None}

        # Merge with user config
        final_config = {**default_config, **kafka_config}

        try:
            self._producer = KafkaTraceProducer(**final_config)
            self._enabled = True
            logger.info("Kafka LLM monitor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka LLM monitor: {e}")
            self._producer = None
            self._enabled = False

    @property
    def enabled(self) -> bool:
        """Check if Kafka monitoring is enabled."""
        return self._enabled

    def track_llm_start(
        self,
        call_id: str,
        model: str,
        provider: str,
        messages: List[Dict],
        params: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        project_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Track LLM call start without blocking.

        Args:
            call_id: Unique identifier for this LLM call
            model: Model name (e.g., 'gpt-4o', 'claude-3-5-sonnet')
            provider: Provider name (e.g., 'openai', 'anthropic')
            messages: Input messages/prompts
            params: Request parameters (temperature, max_tokens, etc.)
            user_id: Optional user identifier
            session_id: Optional session identifier
            project_name: Optional project name for organization
            metadata: Optional additional metadata

        Returns:
            bool: True if event was sent successfully
        """
        if not self._enabled:
            return False

        # Get project name from argument or environment variables
        final_project_name = (
            project_name or os.getenv("EXPERIMENT_NAME") or os.getenv("PROJECT_NAME")
        )

        try:
            return self._producer.send_llm_start(
                call_id=call_id,
                model=model,
                provider=provider,
                messages=messages,
                params=params,
                user_id=user_id,
                session_id=session_id,
                project_name=final_project_name,
                metadata=metadata,
            )
        except Exception as e:
            logger.error(f"Failed to track LLM start: {e}")
            return False

    def track_llm_end(
        self,
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
    ) -> bool:
        """
        Track LLM call completion without blocking.

        Args:
            call_id: Unique identifier for this LLM call
            model: Model name
            provider: Provider name
            duration_ms: Call duration in milliseconds
            usage: Token usage {prompt_tokens, completion_tokens, total_tokens}
            messages: Optional input messages to include in end event
            response: Response content (will be truncated)
            cost: Calculated cost for the call
            error: Error message if call failed
            user_id: Optional user identifier
            session_id: Optional session identifier
            project_name: Optional
            metadata: Optional additional metadata

        Returns:
            bool: True if event was sent successfully
        """
        if not self._enabled:
            return False

        try:
            return self._producer.send_llm_end(
                call_id=call_id,
                model=model,
                provider=provider,
                duration_ms=duration_ms,
                usage=usage,
                messages=messages,
                response=response,
                cost=cost,
                error=error,
                user_id=user_id,
                session_id=session_id,
                project_name=project_name,
                metadata=metadata,
            )
        except Exception as e:
            logger.error(f"Failed to track LLM end: {e}")
            return False

    def track_llm_metric(
        self,
        call_id: str,
        metrics: Dict[str, float],
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Track additional LLM metrics without blocking.

        Args:
            call_id: Unique identifier for this LLM call
            metrics: Dictionary of metric name -> value
            user_id: Optional user identifier
            session_id: Optional session identifier
            metadata: Optional additional metadata

        Returns:
            bool: True if event was sent successfully
        """
        if not self._enabled:
            return False

        try:
            return self._producer.send_llm_metric(
                call_id=call_id,
                metrics=metrics,
                user_id=user_id,
                session_id=session_id,
                metadata=metadata,
            )
        except Exception as e:
            logger.error(f"Failed to track LLM metric: {e}")
            return False

    def flush(self, timeout: float = 10.0) -> int:
        """
        Flush pending messages.

        Args:
            timeout: Maximum time to wait for messages to be delivered

        Returns:
            Number of messages still pending after timeout
        """
        if self._producer:
            return self._producer.flush(timeout)
        return 0

    def get_stats(self) -> Dict[str, Any]:
        """Get monitor statistics."""
        if self._producer:
            return self._producer.get_stats()
        return {"enabled": False, "reason": "Kafka not available"}

    def close(self):
        """Close the monitor and cleanup resources."""
        if self._producer:
            self._producer.close()
            self._producer = None
        self._enabled = False
        logger.info("Kafka LLM monitor closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Global monitor instance
_kafka_llm_monitor: Optional[KafkaLLMMonitor] = None
_monitor_lock = threading.Lock()


def get_kafka_llm_monitor(
    kafka_config: Optional[Dict[str, Any]] = None,
) -> KafkaLLMMonitor:
    """
    Get or create the global Kafka LLM monitor instance.

    Args:
        kafka_config: Optional Kafka configuration overrides

    Returns:
        KafkaLLMMonitor instance
    """
    global _kafka_llm_monitor

    with _monitor_lock:
        if _kafka_llm_monitor is None:
            _kafka_llm_monitor = KafkaLLMMonitor(kafka_config)
        return _kafka_llm_monitor


def close_kafka_llm_monitor():
    """Close the global Kafka LLM monitor."""
    global _kafka_llm_monitor

    with _monitor_lock:
        if _kafka_llm_monitor:
            _kafka_llm_monitor.close()
            _kafka_llm_monitor = None


# Helper function for easy integration
def track_llm_call(
    model: str,
    provider: str,
    messages: List[Dict],
    usage: Dict[str, int],
    duration_ms: float,
    response: Optional[str] = None,
    cost: Optional[float] = None,
    error: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    project_name: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Track a complete LLM call with start and end events.

    Args:
        model: Model name
        provider: Provider name
        messages: Input messages
        usage: Token usage
        duration_ms: Call duration
        response: Response content
        cost: Calculated cost
        error: Error message if failed
        params: Request parameters
        user_id: User identifier
        session_id: Session identifier
        project_name: Project name
        metadata: Additional metadata

    Returns:
        str: Call ID for this LLM call
    """
    call_id = str(uuid.uuid4())
    monitor = get_kafka_llm_monitor()

    # Send start event
    monitor.track_llm_start(
        call_id=call_id,
        model=model,
        provider=provider,
        messages=messages,
        params=params,
        user_id=user_id,
        session_id=session_id,
        project_name=project_name,
        metadata=metadata,
    )

    # Send end event
    monitor.track_llm_end(
        call_id=call_id,
        model=model,
        provider=provider,
        duration_ms=duration_ms,
        usage=usage,
        messages=messages,
        response=response,
        cost=cost,
        error=error,
        user_id=user_id,
        session_id=session_id,
        project_name=project_name,
        metadata=metadata,
    )

    return call_id


def initialize(cost_rates: Optional[dict] = None):
    """
    Initialize the cost tracker and monitoring system.
    Must be called once at startup.

    Args:
        cost_rates (dict, optional): Dictionary of cost rates for different models
    """
    global _cost_tracker, _initialized

    # Check if already initialized
    if _initialized:
        logger.debug("Observability system already initialized, skipping.")
        return

    _cost_tracker = CostTracker(cost_rates=cost_rates)

    # Mark as initialized
    _initialized = True
    logger.debug("Observability system initialized with Kafka and MongoDB integration.")


def monitor(
    client,
    provider: Optional[str] = None,
    project_name: Optional[str] = None,
    cost_rates: Optional[dict] = None,
):
    """
    Enable monitoring on an LLM client.
    Supports multiple providers: 'openai', 'azure_openai', 'anthropic', etc.
    If provider is not provided, it is inferred from the client's module.

    Args:
        client: The LLM client to monitor
        provider (str, optional): The provider name (openai, azure_openai, anthropic)
        cost_rates (dict, optional): Dictionary of cost rates for different models
    """
    # ALWAYS initialize first - this sets up cost tracker
    initialize(cost_rates=cost_rates)

    if provider is None:
        # Try checking the class name first.
        client_name = client.__class__.__name__.lower()
        if "azure" in client_name:
            provider = "azure_openai"
        elif "openai" in client_name:
            provider = "openai"
        elif "anthropic" in client_name:
            provider = "anthropic"
        else:
            # Fallback to module-based detection.
            mod = client.__class__.__module__.lower()
            if "openai" in mod:
                provider = "openai"
            elif "azure" in mod:
                provider = "azure_openai"
            elif "anthropic" in mod:
                provider = "anthropic"
            else:
                provider = "unknown"

    logger.debug("Detected provider: %s", provider)

    if provider in ("openai", "azure_openai"):
        wrap_openai(client, project_name)
    elif provider == "anthropic":
        wrap_anthropic(client, project_name)
    else:
        logger.warning("Monitoring not implemented for provider %s", provider)

    return client


def wrap_openai(client, project_name: Optional[str] = None):
    """
    Wraps an OpenAI client to enable monitoring and logging capabilities.

    This function intercepts the client's completion creation methods to track
    costs and send data to Kafka for observability.

    Args:
        client: An instance of the OpenAI client to be wrapped.

    Returns:
        None. The function modifies the client instance in-place by wrapping its methods.
    """
    # Check if we should use Kafka monitoring
    use_kafka = os.getenv("AUTONOMIZE_TRACING_ENABLED", "false").lower() == "true"

    if use_kafka:
        _wrap_openai_with_kafka_optimized(client, project_name)
    else:
        _wrap_openai_with_basic_tracking(client, project_name)


def wrap_anthropic(client, project_name: Optional[str] = None):
    """
    Wraps an Anthropic client to enable monitoring and logging capabilities.

    This function intercepts the client's message creation methods to track
    costs and send data to Kafka for observability.

    Args:
        client: An instance of the Anthropic client to be wrapped.

    Returns:
        None. The function modifies the client instance in-place by wrapping its methods.
    """
    # Check if we should use Kafka monitoring
    use_kafka = os.getenv("AUTONOMIZE_TRACING_ENABLED", "false").lower() == "true"

    if use_kafka:
        _wrap_anthropic_with_kafka(client, project_name)
    else:
        _wrap_anthropic_with_basic_tracking(client, project_name)


def _wrap_openai_with_kafka_optimized(client, project_name: Optional[str] = None):
    """Wrap OpenAI client with fully non-blocking Kafka monitoring."""
    if (
        hasattr(client, "chat")
        and hasattr(client.chat, "completions")
        and hasattr(client.chat.completions, "create")
    ):
        original_create = client.chat.completions.create
        is_async_client = _is_async_client(client)

        if is_async_client:

            async def wrapped_async_create(*args, **kwargs):
                model = kwargs.get("model", "gpt-3.5-turbo")
                messages = kwargs.get("messages", [])
                user_id = getattr(_local, "user_id", None)
                session_id = getattr(_local, "session_id", None)

                # Generate call_id immediately (no blocking)
                call_id = str(uuid.uuid4())
                start_time = time.time()

                try:
                    # 🚀 EXECUTE LLM CALL (no monitoring overhead here)
                    result = await original_create(*args, **kwargs)

                    # 🎯 POST-PROCESSING: Submit monitoring to background thread
                    duration_ms = (time.time() - start_time) * 1000
                    usage = {
                        "prompt_tokens": result.usage.prompt_tokens,
                        "completion_tokens": result.usage.completion_tokens,
                        "total_tokens": result.usage.total_tokens,
                    }
                    response = (
                        result.choices[0].message.content if result.choices else None
                    )

                    # ✅ NON-BLOCKING: Submit to background thread
                    track_monitoring_background(
                        call_id=call_id,
                        model=model,
                        usage=usage,
                        response=response,
                        duration_ms=duration_ms,
                        messages=messages,  # Pass the captured messages
                        project_name=project_name,  # 🔥 Pass project_name
                    )

                    return result

                except Exception as e:
                    # Even error handling is non-blocking
                    duration_ms = (time.time() - start_time) * 1000
                    track_monitoring_background(
                        call_id=call_id,
                        model=model,
                        usage={
                            "prompt_tokens": 0,
                            "completion_tokens": 0,
                            "total_tokens": 0,
                        },
                        response="",
                        duration_ms=duration_ms,
                        messages=messages,  # Pass messages even in error case
                        project_name=project_name,  # 🔥 Pass project_name
                    )
                    raise

            client.chat.completions.create = wrapped_async_create
        else:

            def wrapped_create(*args, **kwargs):
                model = kwargs.get("model", "gpt-3.5-turbo")
                messages = kwargs.get("messages", [])
                user_id = getattr(_local, "user_id", None)
                session_id = getattr(_local, "session_id", None)

                # Generate call_id immediately (no blocking)
                call_id = str(uuid.uuid4())
                start_time = time.time()

                try:
                    # 🚀 EXECUTE LLM CALL (no monitoring overhead here)
                    result = original_create(*args, **kwargs)

                    # 🎯 POST-PROCESSING: Submit monitoring to background thread
                    duration_ms = (time.time() - start_time) * 1000
                    usage = {
                        "prompt_tokens": result.usage.prompt_tokens,
                        "completion_tokens": result.usage.completion_tokens,
                        "total_tokens": result.usage.total_tokens,
                    }
                    response = (
                        result.choices[0].message.content if result.choices else None
                    )

                    # ✅ NON-BLOCKING: Submit to background thread
                    track_monitoring_background(
                        call_id=call_id,
                        model=model,
                        usage=usage,
                        response=response,
                        duration_ms=duration_ms,
                        messages=messages,  # Pass the captured messages
                        project_name=project_name,  # 🔥 Pass project_name
                    )

                    return result

                except Exception as e:
                    # Even error handling is non-blocking
                    duration_ms = (time.time() - start_time) * 1000
                    track_monitoring_background(
                        call_id=call_id,
                        model=model,
                        usage={
                            "prompt_tokens": 0,
                            "completion_tokens": 0,
                            "total_tokens": 0,
                        },
                        response="",
                        duration_ms=duration_ms,
                        messages=messages,  # Pass messages even in error case
                        project_name=project_name,  # 🔥 Pass project_name
                    )
                    raise

            client.chat.completions.create = wrapped_create

    logger.debug("Optimized non-blocking Kafka monitoring enabled for OpenAI client")


def _wrap_openai_with_basic_tracking(client, project_name: Optional[str] = None):
    """Wrap OpenAI client with basic cost tracking (no Kafka)."""
    if (
        hasattr(client, "chat")
        and hasattr(client.chat, "completions")
        and hasattr(client.chat.completions, "create")
    ):
        original_create = client.chat.completions.create
        is_async_client = _is_async_client(client)

        if is_async_client:

            async def wrapped_async_create(*args, **kwargs):
                try:
                    result = await original_create(*args, **kwargs)

                    # 🔥 NO CLIENT-SIDE COST CALCULATION: Worker will handle cost calculation
                    # Removed _cost_tracker.track_cost() call for better production performance

                    return result
                except Exception as e:
                    logger.error(f"Error in OpenAI call: {e}")
                    raise

            client.chat.completions.create = wrapped_async_create
        else:

            def wrapped_create(*args, **kwargs):
                try:
                    result = original_create(*args, **kwargs)

                    # 🔥 NO CLIENT-SIDE COST CALCULATION: Worker will handle cost calculation
                    # Removed _cost_tracker.track_cost() call for better production performance

                    return result
                except Exception as e:
                    logger.error(f"Error in OpenAI call: {e}")
                    raise

            client.chat.completions.create = wrapped_create

    logger.debug("Basic monitoring enabled for OpenAI client")


def _wrap_anthropic_with_kafka(client, project_name: Optional[str] = None):
    """Wrap Anthropic client with Kafka-based monitoring."""
    kafka_monitor = get_kafka_llm_monitor()

    if not kafka_monitor.enabled:
        logger.warning("Kafka LLM monitoring not available, using basic tracking")
        return _wrap_anthropic_with_basic_tracking(client)

    is_async_client = _is_async_client(client)

    if hasattr(client, "messages") and hasattr(client.messages, "create"):
        original_create = client.messages.create

        def wrapped_create(*args, **kwargs):
            call_id = str(uuid.uuid4())
            model = kwargs.get("model", "claude-3-5-sonnet")
            messages = kwargs.get("messages", [])

            user_id = getattr(_local, "user_id", None)
            session_id = getattr(_local, "session_id", None)

            start_time = time.time()
            kafka_monitor.track_llm_start(
                call_id=call_id,
                model=model,
                provider="anthropic",
                messages=messages,
                params={
                    k: v for k, v in kwargs.items() if k not in ["messages", "model"]
                },
                user_id=user_id,
                session_id=session_id,
                project_name=project_name,
            )

            try:
                result = original_create(*args, **kwargs)

                usage = {
                    "prompt_tokens": result.usage.input_tokens,
                    "completion_tokens": result.usage.output_tokens,
                    "total_tokens": result.usage.input_tokens
                    + result.usage.output_tokens,
                }

                # 🔥 NO CLIENT-SIDE COST CALCULATION: Worker will calculate cost
                # This removes computation overhead from client for better production performance
                cost = None  # Worker calculates cost

                response = result.content[0].text if result.content else None

                duration_ms = (time.time() - start_time) * 1000
                kafka_monitor.track_llm_end(
                    call_id=call_id,
                    model=model,
                    provider="anthropic",
                    duration_ms=duration_ms,
                    usage=usage,
                    messages=messages,
                    response=response,
                    cost=cost,  # None - worker calculates
                    user_id=user_id,
                    session_id=session_id,
                    project_name=project_name,
                )

                return result

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                kafka_monitor.track_llm_end(
                    call_id=call_id,
                    model=model,
                    provider="anthropic",
                    duration_ms=duration_ms,
                    usage={
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_tokens": 0,
                    },
                    messages=messages,
                    error=str(e),
                    user_id=user_id,
                    session_id=session_id,
                    project_name=project_name,
                )
                raise

        client.messages.create = wrapped_create

    # Wrap async methods if available
    if is_async_client and hasattr(client.messages, "acreate"):
        original_acreate = client.messages.acreate

        async def wrapped_acreate(*args, **kwargs):
            call_id = str(uuid.uuid4())
            model = kwargs.get("model", "claude-3-5-sonnet")
            messages = kwargs.get("messages", [])

            user_id = getattr(_local, "user_id", None)
            session_id = getattr(_local, "session_id", None)

            start_time = time.time()
            kafka_monitor.track_llm_start(
                call_id=call_id,
                model=model,
                provider="anthropic",
                messages=messages,
                params={
                    k: v for k, v in kwargs.items() if k not in ["messages", "model"]
                },
                user_id=user_id,
                session_id=session_id,
            )

            try:
                result = await original_acreate(*args, **kwargs)

                usage = {
                    "prompt_tokens": result.usage.input_tokens,
                    "completion_tokens": result.usage.output_tokens,
                    "total_tokens": result.usage.input_tokens
                    + result.usage.output_tokens,
                }

                # 🔥 NO CLIENT-SIDE COST CALCULATION: Worker will calculate cost
                # This removes computation overhead from client for better production performance
                cost = None  # Worker calculates cost

                response = result.content[0].text if result.content else None

                duration_ms = (time.time() - start_time) * 1000
                kafka_monitor.track_llm_end(
                    call_id=call_id,
                    model=model,
                    provider="anthropic",
                    duration_ms=duration_ms,
                    usage=usage,
                    messages=messages,
                    response=response,
                    cost=cost,  # None - worker calculates
                    user_id=user_id,
                    session_id=session_id,
                )

                return result

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                kafka_monitor.track_llm_end(
                    call_id=call_id,
                    model=model,
                    provider="anthropic",
                    duration_ms=duration_ms,
                    usage={
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_tokens": 0,
                    },
                    messages=messages,
                    error=str(e),
                    user_id=user_id,
                    session_id=session_id,
                )
                raise

        client.messages.acreate = wrapped_acreate

    logger.debug("Kafka monitoring enabled for Anthropic client")


def _wrap_anthropic_with_basic_tracking(client):
    """Wrap Anthropic client with basic cost tracking (no Kafka)."""
    if hasattr(client, "messages") and hasattr(client.messages, "create"):
        original_create = client.messages.create

        def wrapped_create(*args, **kwargs):
            try:
                result = original_create(*args, **kwargs)

                # 🔥 NO CLIENT-SIDE COST CALCULATION: Worker will handle cost calculation
                # Removed _cost_tracker.track_cost() call for better production performance

                return result
            except Exception as e:
                logger.error(f"Error in Anthropic call: {e}")
                raise

        client.messages.create = wrapped_create

    # Wrap async methods if available
    is_async_client = _is_async_client(client)
    if is_async_client and hasattr(client.messages, "acreate"):
        original_acreate = client.messages.acreate

        async def wrapped_acreate(*args, **kwargs):
            try:
                result = await original_acreate(*args, **kwargs)

                # 🔥 NO CLIENT-SIDE COST CALCULATION: Worker will handle cost calculation
                # Removed _cost_tracker.track_cost() call for better production performance

                return result
            except Exception as e:
                logger.error(f"Error in Anthropic call: {e}")
                raise

        client.messages.acreate = wrapped_acreate

    logger.debug("Basic monitoring enabled for Anthropic client")


# Decorators for function tracing
def trace_async(name: Optional[str] = None):
    """Decorator for async functions with basic tracing."""

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = name or func.__name__

            logger.debug(f"Starting async function: {func_name}")

            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                logger.debug(
                    f"Completed async function: {func_name} in {duration_ms:.2f}ms"
                )
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(
                    f"Failed async function: {func_name} in {duration_ms:.2f}ms - {e}"
                )
                raise

        return wrapper

    return decorator


def trace_sync(name: Optional[str] = None):
    """Decorator for sync functions with basic tracing."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = name or func.__name__

            logger.debug(f"Starting function: {func_name}")

            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                logger.debug(f"Completed function: {func_name} in {duration_ms:.2f}ms")
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(
                    f"Failed function: {func_name} in {duration_ms:.2f}ms - {e}"
                )
                raise

        return wrapper

    return decorator


def agent(name=None):
    """
    Decorator for agent functions with basic logging.
    """

    def decorator(fn):
        def wrapper(*args, **kwargs):
            agent_name = name or fn.__name__
            logger.debug(f"Starting agent: {agent_name}")
            try:
                result = fn(*args, **kwargs)
                logger.debug(f"Completed agent: {agent_name}")
                return result
            except Exception as e:
                logger.error(f"Failed agent: {agent_name} - {e}")
                raise

        return wrapper

    return decorator


def tool(name=None):
    """
    Decorator for tool functions with basic logging.
    """

    def decorator(fn):
        def wrapper(*args, **kwargs):
            tool_name = name or fn.__name__
            logger.debug(f"Starting tool: {tool_name}")
            try:
                result = fn(*args, **kwargs)
                logger.debug(f"Completed tool: {tool_name}")
                return result
            except Exception as e:
                logger.error(f"Failed tool: {tool_name} - {e}")
                raise

        return wrapper

    return decorator


class Identify:
    """
    A simple context manager for setting user context.
    """

    def __init__(self, user_props=None):
        self.user_props = user_props or {}

    def __enter__(self):
        # Set user context in thread-local storage
        _local.user_id = self.user_props.get("user_id")
        _local.session_id = self.user_props.get("session_id")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Clear user context
        _local.user_id = None
        _local.session_id = None


def identify(user_props=None):
    """
    Creates and returns an Identify context manager for setting user context.

    Args:
        user_props (dict, optional): Dictionary containing user properties

    Returns:
        Identify: A context manager instance that handles user context.
    """
    return Identify(user_props)


def _is_async_client(client):
    """
    Robust detection of async LLM clients across different providers.
    """
    client_class_name = client.__class__.__name__
    client_module = client.__class__.__module__.lower()

    # Method 1: Known async class name patterns
    async_class_patterns = {
        "AsyncOpenAI",
        "AsyncAzureOpenAI",
        "AsyncAnthropic",
        "AsyncClient",
    }

    if client_class_name in async_class_patterns:
        return True

    # Method 2: Check if "async" is in the class name (case insensitive)
    if "async" in client_class_name.lower():
        return True

    # Method 3: Check for async methods
    async_method_names = ["create", "acreate", "__call__", "stream", "astream"]

    for method_name in async_method_names:
        method = getattr(client, method_name, None)
        if method and asyncio.iscoroutinefunction(method):
            return True

    # Method 4: Check module patterns as fallback
    async_module_patterns = ["async", "aio"]
    if any(pattern in client_module for pattern in async_module_patterns):
        return True

    return False


def get_monitoring_executor():
    """Get or create the monitoring thread pool executor."""
    global _monitoring_executor
    if _monitoring_executor is None:
        with _monitoring_lock:
            if _monitoring_executor is None:
                _monitoring_executor = concurrent.futures.ThreadPoolExecutor(
                    max_workers=2,  # Small pool for monitoring
                    thread_name_prefix="monitoring",
                )
    return _monitoring_executor


def track_llm_call_async(
    model: str,
    provider: str,
    messages: List[Dict],
    usage: Dict[str, int],
    duration_ms: float,
    response: Optional[str] = None,
    cost: Optional[float] = None,
    error: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Track LLM call asynchronously without blocking.
    Returns immediately with call_id, processes monitoring in background.

    🔥 WORKER-SIDE COST CALCULATION: Client only sends raw token data,
    worker calculates costs for better production performance.
    """
    call_id = str(uuid.uuid4())

    def _background_processing():
        """Execute monitoring operations in background thread."""
        try:
            monitor = get_kafka_llm_monitor()

            # 🔥 NO CLIENT-SIDE COST CALCULATION: Let worker handle cost calculation
            # This removes computation overhead from client and centralizes cost logic
            calculated_cost = None  # Worker will calculate this

            # Send start event
            monitor.track_llm_start(
                call_id=call_id,
                model=model,
                provider=provider,
                messages=messages,
                params=params,
                user_id=user_id,
                session_id=session_id,
                metadata=metadata,
            )

            # Send end event (no cost, worker will calculate)
            monitor.track_llm_end(
                call_id=call_id,
                model=model,
                provider=provider,
                duration_ms=duration_ms,
                usage=usage,
                messages=messages,
                response=response,
                cost=calculated_cost,  # None - worker calculates
                error=error,
                user_id=user_id,
                session_id=session_id,
                metadata=metadata,
            )

            logger.debug(
                f"✅ Background monitoring completed for call {call_id} (worker will calculate cost)"
            )

        except Exception as e:
            logger.warning(f"❌ Background monitoring failed for call {call_id}: {e}")

    # Submit to background thread pool (non-blocking)
    executor = get_monitoring_executor()
    executor.submit(_background_processing)

    return call_id


def track_monitoring_background_anthropic(
    call_id: str,
    model: str,
    usage: Dict[str, int],
    response: str,
    duration_ms: float,
    messages: Optional[List[Dict]] = None,
    project_name: Optional[str] = None,
    error: Optional[str] = None,
):
    """
    Ultra-light monitoring function for Anthropic in production use.

    🔥 WORKER-SIDE COST CALCULATION: Only sends raw token data to Kafka,
    worker handles all cost calculation for better performance.
    """

    def _ultra_light_monitoring():
        try:
            # Send both start and end events for proper simple LLM monitoring
            monitor = get_kafka_llm_monitor()
            if monitor.enabled:
                # Send LLM start event
                monitor.track_llm_start(
                    call_id=call_id,
                    model=model,
                    provider="anthropic",
                    messages=messages or [],
                    user_id=getattr(_local, "user_id", None),
                    session_id=getattr(_local, "session_id", None),
                    project_name=project_name,
                )

                # Send LLM end event with results
                monitor.track_llm_end(
                    call_id=call_id,
                    model=model,
                    provider="anthropic",
                    duration_ms=duration_ms,
                    usage=usage,
                    messages=messages,
                    response=response,
                    cost=None,  # Worker will calculate cost
                    error=error,
                    user_id=getattr(_local, "user_id", None),
                    session_id=getattr(_local, "session_id", None),
                    project_name=project_name,
                )

        except Exception as e:
            # Silent failure - never break LLM calls
            pass

    # Fire and forget
    executor = get_monitoring_executor()
    executor.submit(_ultra_light_monitoring)


def track_monitoring_background(
    call_id: str,
    model: str,
    usage: Dict[str, int],
    response: str,
    duration_ms: float,
    messages: Optional[List[Dict]] = None,
    project_name: Optional[str] = None,
):
    """
    Ultra-light monitoring function for production use.

    🔥 WORKER-SIDE COST CALCULATION: Only sends raw token data to Kafka,
    worker handles all cost calculation for better performance.
    """

    def _ultra_light_monitoring():
        try:
            # 🔥 NO CLIENT-SIDE COST CALCULATION: Removed for worker-side calculation
            # This eliminates computation overhead on client side

            # Send both start and end events for proper simple LLM monitoring
            monitor = get_kafka_llm_monitor()
            if monitor.enabled:
                # Send LLM start event
                monitor.track_llm_start(
                    call_id=call_id,
                    model=model,
                    provider="openai",  # Default
                    messages=messages or [],
                    user_id=getattr(_local, "user_id", None),
                    session_id=getattr(_local, "session_id", None),
                    project_name=project_name
                    or os.getenv(
                        "OBSERVABILITY_EXPERIMENT_NAME",
                        os.getenv("OBSERVABILITY_PROJECT_NAME"),
                    ),
                )

                # Send LLM end event with results
                monitor.track_llm_end(
                    call_id=call_id,
                    model=model,
                    provider="openai",  # Default
                    duration_ms=duration_ms,
                    usage=usage,
                    messages=messages,  # Now properly passing messages
                    response=response,
                    cost=None,  # Worker will calculate cost
                    user_id=getattr(_local, "user_id", None),
                    session_id=getattr(_local, "session_id", None),
                    project_name=project_name
                    or os.getenv(
                        "OBSERVABILITY_EXPERIMENT_NAME",
                        os.getenv("OBSERVABILITY_PROJECT_NAME"),
                    ),
                )

        except Exception as e:
            # Silent failure - never break LLM calls
            pass

    # Fire and forget
    executor = get_monitoring_executor()
    executor.submit(_ultra_light_monitoring)
