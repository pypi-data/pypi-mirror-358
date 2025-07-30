"""
Streaming Agent-based tracer inspired by Langflow's approach.

This tracer implements streaming/incremental span sending:
1. Start trace context
2. Send individual spans as they start/end
3. No massive memory accumulation
4. Real-time monitoring capabilities
"""

import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, List
from contextlib import contextmanager
import threading

from .base_tracer import BaseTracer
from ..kafka.producer import KafkaTraceProducer
from ..kafka.schemas import _safe_serialize_value

# Streaming tracer is lightweight - no heavy dependencies
COST_TRACKING_AVAILABLE = False  # Cost calculation happens in worker

try:
    from langchain.callbacks.base import BaseCallbackHandler

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    BaseCallbackHandler = object

logger = logging.getLogger(__name__)


class StreamingTraceContext:
    """Context for managing streaming trace state."""

    def __init__(
        self,
        trace_id: str,
        flow_id: str,
        trace_name: str,
        project_name: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ):
        self.trace_id = trace_id
        self.flow_id = flow_id
        self.trace_name = trace_name
        self.project_name = project_name
        self.user_id = user_id
        self.session_id = session_id

        # Tracking state
        self.start_time = time.time()
        self.active_spans: Dict[str, Dict[str, Any]] = {}
        self.completed_spans: List[str] = []

        # Thread safety
        self._lock = threading.Lock()

        # Metadata
        self.tags: Dict[str, str] = {}
        self.params: Dict[str, Any] = {}
        self.metrics: Dict[str, float] = {}


class AgentTracer(BaseTracer):
    """
    Streaming Agent tracer that sends spans incrementally like Langflow.

    Workflow:
    1. start_trace() - Initialize trace context, send trace_start event
    2. add_trace() - Start component span, send span_start event
    3. end_trace() - End component span, send span_end event
    4. end() - Finalize trace, send trace_end event
    """

    def __init__(
        self,
        trace_name: str,
        trace_id: uuid.UUID,
        flow_id: str,
        project_name: str = "GenesisStudio",
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        kafka_bootstrap_servers: Optional[str] = None,
        kafka_topic: str = "genesis-traces-streaming",
        # Authentication parameters
        kafka_username: Optional[str] = None,
        kafka_password: Optional[str] = None,
        security_protocol: str = "PLAINTEXT",
        sasl_mechanism: str = "PLAIN",
        **kwargs,
    ):
        """Initialize streaming tracer."""
        # Clean up trace name using robust generic approach
        cleaned_trace_name = self._clean_trace_name(trace_name)
        super().__init__(cleaned_trace_name, "flow", project_name, trace_id)

        # Store configuration
        self.flow_id = flow_id
        self.user_id = user_id
        self.session_id = session_id

        # Kafka configuration
        self.kafka_bootstrap_servers = kafka_bootstrap_servers
        self.kafka_topic = kafka_topic
        self.kafka_username = kafka_username
        self.kafka_password = kafka_password
        self.security_protocol = security_protocol
        self.sasl_mechanism = sasl_mechanism

        # Initialize Kafka producer
        self._kafka_producer = None
        self._ready = False

        # Trace context (like Langflow's TraceContext)
        self._trace_context: Optional[StreamingTraceContext] = None

        # LangChain callback
        self._callback_handler = None
        if LANGCHAIN_AVAILABLE:
            self._callback_handler = StreamingLangChainCallback(self)

        # Setup Kafka producer
        self._setup_kafka_producer()

        logger.info(f"✅ Streaming tracer initialized for flow: {flow_id}")

    def _clean_trace_name(self, trace_name: str) -> str:
        """
        Clean up trace name for better readability using robust generic patterns.

        This applies the same generic approach as the previous agent tracer.
        """
        if not trace_name:
            return "AgentExecutor"

        # Handle generic/untitled flows
        if trace_name.startswith("Untitled") or trace_name.lower() in [
            "untitled",
            "new flow",
            "flow",
        ]:
            return "AgentExecutor"

        # Clean up the trace name
        cleaned = trace_name.strip()

        # Remove UUID suffix pattern (e.g., "MyFlow - 597cd666-9580-462a-8ffa-b9939b6df0f0")
        if " - " in cleaned and len(cleaned.split(" - ")[-1]) >= 30:
            cleaned = cleaned.split(" - ")[0].strip()

        # Remove common document patterns
        if cleaned.endswith(")") and "(" in cleaned:
            # Handle patterns like "Untitled document (2)"
            base_name = cleaned.split("(")[0].strip()
            if base_name.lower() in ["untitled document", "untitled", "document"]:
                return "AgentExecutor"
            if base_name:
                cleaned = base_name

        # If still generic after cleaning, use AgentExecutor
        if not cleaned or cleaned.lower() in ["untitled", "document", "new", "flow"]:
            return "AgentExecutor"

        return cleaned

    @property
    def ready(self) -> bool:
        """Check if tracer is ready."""
        return self._ready

    def _setup_kafka_producer(self):
        """Setup Kafka producer with authentication."""
        try:
            self._kafka_producer = KafkaTraceProducer(
                bootstrap_servers=self.kafka_bootstrap_servers,
                topic=self.kafka_topic,
                kafka_username=self.kafka_username,
                kafka_password=self.kafka_password,
                security_protocol=self.security_protocol,
                sasl_mechanism=self.sasl_mechanism,
            )
            self._ready = True
            logger.debug("✅ Streaming Kafka producer initialized")
        except Exception as e:
            logger.warning(f"❌ Failed to initialize Kafka producer: {e}")
            self._ready = False

    def start_trace(self) -> None:
        """
        Start the trace context and send trace_start event.

        This is like Langflow's start_tracers().
        """
        if not self._ready:
            logger.debug("Streaming tracer not ready, skipping trace start")
            return

        try:
            # Initialize trace context
            self._trace_context = StreamingTraceContext(
                trace_id=str(self.trace_id),
                flow_id=self.flow_id,
                trace_name=self.trace_name,
                project_name=self.project_name,
                user_id=self.user_id,
                session_id=self.session_id,
            )

            # Send trace_start event to Kafka using specific method
            success = self._kafka_producer.send_trace_start(
                trace_id=self._trace_context.trace_id,
                flow_id=self._trace_context.flow_id,
                flow_name=self._trace_context.trace_name,
                user_id=self._trace_context.user_id,
                session_id=self._trace_context.session_id,
                metadata={
                    "project_name": self._trace_context.project_name,
                    "environment": "production",
                },
            )
            if success:
                logger.info(
                    f"✅ Started streaming trace: {self._trace_context.trace_id}"
                )
            else:
                logger.warning(f"❌ Failed to send trace_start event")

        except Exception as e:
            logger.error(f"Error starting streaming trace: {e}")

    def add_trace(
        self,
        trace_id: str,  # component_id
        trace_name: str,
        trace_type: str,
        inputs: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        vertex: Any = None,
        parent_id: Optional[str] = None,
    ) -> None:
        """
        Start a component span and send span_start event.

        This is like Langflow's add_trace() for individual components.
        """
        if not self._ready or not self._trace_context:
            return

        try:
            # Create span info
            span_start_time = time.time()
            safe_inputs = _safe_serialize_value(inputs) if inputs else {}
            safe_metadata = _safe_serialize_value(metadata) if metadata else {}

            with self._trace_context._lock:
                # Store active span
                self._trace_context.active_spans[trace_id] = {
                    "span_id": trace_id,
                    "component_name": trace_name,
                    "trace_type": trace_type,
                    "start_time": span_start_time,
                    "inputs": safe_inputs,
                    "metadata": safe_metadata,
                    "parent_id": parent_id,
                }

            # Send span_start event to Kafka using specific method
            success = self._kafka_producer.send_span_start(
                trace_id=self._trace_context.trace_id,
                span_id=trace_id,
                component_id=trace_id,  # Use span_id as component_id
                component_name=trace_name,
                parent_span_id=parent_id,
                input_data=safe_inputs,
                metadata=safe_metadata,
            )
            if success:
                logger.debug(f"✅ Started span: {trace_id} ({trace_name})")
            else:
                logger.warning(f"❌ Failed to send span_start event for {trace_id}")

        except Exception as e:
            logger.error(f"Error starting span {trace_id}: {e}")

    def end_trace(
        self,
        trace_id: str,
        trace_name: str,
        outputs: Optional[Dict[str, Any]] = None,
        error: Optional[Exception] = None,
        logs: Any = (),
    ):
        """
        End a component span and send span_end event.

        This is like Langflow's end_trace() for individual components.
        """
        if not self._ready or not self._trace_context:
            return

        try:
            span_end_time = time.time()
            safe_outputs = _safe_serialize_value(outputs) if outputs else {}

            # Get span info and mark as completed
            span_info = None
            with self._trace_context._lock:
                span_info = self._trace_context.active_spans.pop(trace_id, None)
                if span_info:
                    self._trace_context.completed_spans.append(trace_id)

            if not span_info:
                logger.warning(f"Trying to end unknown span: {trace_id}")
                return

            # Calculate duration
            duration_ms = (span_end_time - span_info["start_time"]) * 1000

            # Lightweight metadata - worker handles cost calculation
            enhanced_metadata = {
                "component_name": trace_name,
                "status": "error" if error else "success",
                "component_type": self._infer_component_type(trace_name, None),
            }

            # Send span_end event to Kafka using specific method
            success = self._kafka_producer.send_span_end(
                trace_id=self._trace_context.trace_id,
                span_id=trace_id,
                duration_ms=duration_ms,
                output_data=safe_outputs,
                metadata=enhanced_metadata,
                error=str(error) if error else None,
            )
            if success:
                logger.debug(
                    f"✅ Ended span: {trace_id} (duration: {duration_ms:.2f}ms)"
                )
            else:
                logger.warning(f"❌ Failed to send span_end event for {trace_id}")

        except Exception as e:
            logger.error(f"Error ending span {trace_id}: {e}")

    def _infer_component_type(self, component_name: str, model_name: str) -> str:
        """
        Infer component type using generic pattern matching.

        More robust than hardcoded name checks.
        """
        if model_name:
            return "llm"  # Has model = LLM component

        # Generic pattern-based detection
        name_lower = component_name.lower()

        type_patterns = {
            "agent": ["agent", "executor", "workflow", "orchestrator"],
            "input": ["input", "prompt", "question", "query"],
            "output": ["output", "response", "result", "answer"],
            "retrieval": ["retrieval", "vector", "search", "rag", "knowledge"],
            "memory": ["memory", "history", "context", "conversation"],
            "tool": ["tool", "function", "api", "external", "utility"],
            "processing": ["process", "transform", "parse", "format"],
        }

        for component_type, patterns in type_patterns.items():
            if any(pattern in name_lower for pattern in patterns):
                return component_type

        return "component"  # Generic fallback

    def _guess_provider_from_model(self, model_name: str) -> str:
        """
        Guess provider from model name using comprehensive pattern matching with type safety.

        Same generic approach as the previous agent tracer.
        """
        if not model_name:
            return "unknown"

        # Ensure we have a string (handle cases where list might be passed)
        if isinstance(model_name, list):
            if len(model_name) > 0:
                # Take first string element from list
                for item in model_name:
                    if isinstance(item, str) and item.strip():
                        model_name = item
                        break
                else:
                    model_name = str(model_name[0]) if model_name else "unknown"
            else:
                return "unknown"
        elif not isinstance(model_name, str):
            model_name = str(model_name)

        model_lower = model_name.lower()

        # Provider pattern mapping - easily extensible
        provider_patterns = {
            "openai": [
                "gpt",
                "openai",
                "o1",
                "o3",
                "o4",
                "davinci",
                "babbage",
                "whisper",
                "tts",
            ],
            "anthropic": ["claude", "anthropic"],
            "google": ["gemini", "google", "palm", "bard"],
            "meta": ["llama", "meta"],
            "mistral": ["mistral", "mixtral", "codestral", "pixtral"],
            "amazon": ["nova", "amazon", "bedrock"],
            "deepseek": ["deepseek"],
            "cohere": ["command", "cohere"],
            "xai": ["grok", "xai"],
            "alibaba": ["qwen", "alibaba"],
            "perplexity": ["perplexity", "sonar"],
            "nvidia": ["nemotron", "nvidia"],
        }

        for provider, patterns in provider_patterns.items():
            if any(pattern in model_lower for pattern in patterns):
                return provider

        return "unknown"

    def _clean_model_name(self, model_name: str) -> str:
        """
        Clean and normalize model name using generic patterns with type safety.

        Same approach as the previous agent tracer for consistency.
        """
        if not model_name:
            return "unknown"

        # Ensure we have a string (handle cases where list might be passed)
        if isinstance(model_name, list):
            if len(model_name) > 0:
                # Take first string element from list
                for item in model_name:
                    if isinstance(item, str) and item.strip():
                        model_name = item
                        break
                else:
                    # If no valid string found, convert first item
                    model_name = str(model_name[0]) if model_name else "unknown"
            else:
                return "unknown"
        elif not isinstance(model_name, str):
            model_name = str(model_name)

        # Remove common prefixes and normalize
        cleaned = model_name.lower().strip()

        # Handle deployment prefixes generically
        prefixes_to_remove = ["azure/", "azure-", "bedrock/"]
        for prefix in prefixes_to_remove:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :]

        # Pattern-based model detection with hierarchical fallbacks (fixed hashable keys)
        # Check OpenAI models
        if "gpt-4.1" in cleaned:
            if "nano" in cleaned:
                return "gpt-4.1-nano"
            elif "mini" in cleaned:
                return "gpt-4.1-mini"
            return "gpt-4.1"
        elif "gpt-4o" in cleaned or "gpt4o" in cleaned:
            if "mini" in cleaned:
                return "gpt-4o-mini"
            return "gpt-4o"
        elif "gpt-4" in cleaned:
            if "turbo" in cleaned:
                return "gpt-4-turbo"
            elif "32k" in cleaned:
                return "gpt-4-32k"
            return "gpt-4"
        elif "gpt-3.5" in cleaned or "gpt-35" in cleaned:
            if "16k" in cleaned:
                return "gpt-3.5-turbo-16k-0613"
            return "gpt-3.5-turbo"

        # Check Anthropic models
        elif "claude" in cleaned:
            if "4" in cleaned:
                if "opus" in cleaned:
                    return "claude-4-opus"
                elif "sonnet" in cleaned:
                    return "claude-4-sonnet"
                return "claude-4-opus"  # default
            elif "3.7" in cleaned or "3-7" in cleaned:
                return "claude-3.7-sonnet"
            elif "3.5" in cleaned or "3-5" in cleaned:
                if "haiku" in cleaned:
                    return "claude-3.5-haiku"
                return "claude-3.5-sonnet"
            elif "3" in cleaned:
                if "opus" in cleaned:
                    return "claude-3-opus"
                elif "haiku" in cleaned:
                    return "claude-3-haiku"
                return "claude-3-sonnet"
            elif "2" in cleaned:
                return "claude-2.1"
            elif "instant" in cleaned:
                return "claude-instant-1.2"
            return "claude-3.5-sonnet"  # default

        # Check Google models
        elif "gemini" in cleaned:
            if "2.5" in cleaned:
                if "flash" in cleaned:
                    if "lite" in cleaned:
                        return "gemini-2.5-flash-lite"
                    return "gemini-2.5-flash"
                return "gemini-2.5-pro"
            elif "2.0" in cleaned or "2-0" in cleaned:
                if "flash" in cleaned:
                    if "lite" in cleaned:
                        return "gemini-2.0-flash-lite"
                    return "gemini-2.0-flash"
                return "gemini-2.0-pro"
            elif "1.5" in cleaned:
                if "flash" in cleaned:
                    if "8b" in cleaned:
                        return "gemini-1.5-flash-8b"
                    return "gemini-1.5-flash"
                return "gemini-1.5-pro"
            return "gemini-1.0-pro"  # default

        # Check Meta Llama models
        elif "llama" in cleaned:
            if "4" in cleaned:
                if "scout" in cleaned:
                    return "llama-4-scout"
                elif "maverick" in cleaned:
                    return "llama-4-maverick"
                elif "behemoth" in cleaned:
                    return "llama-4-behemoth"
            elif "3.3" in cleaned:
                return "llama-3.3-70b"
            elif "3.2" in cleaned:
                if "90b" in cleaned:
                    return "llama-3.2-90b"
                elif "11b" in cleaned:
                    return "llama-3.2-11b"
                elif "3b" in cleaned:
                    return "llama-3.2-3b"
                elif "1b" in cleaned:
                    return "llama-3.2-1b"
            elif "3.1" in cleaned:
                if "405b" in cleaned:
                    return "llama-3.1-405b"
                elif "70b" in cleaned:
                    return "llama-3.1-70b"
                elif "8b" in cleaned:
                    return "llama-3.1-8b"
            elif "3" in cleaned:
                if "70b" in cleaned:
                    return "llama-3-70b"
                elif "8b" in cleaned:
                    return "llama-3-8b"
            elif "2" in cleaned:
                if "70b" in cleaned:
                    return "llama-2-70b"
                elif "13b" in cleaned:
                    return "llama-2-13b"
                elif "7b" in cleaned:
                    return "llama-2-7b"
            return "llama-3-8b"  # default

        # Check Mistral models - FIXED: Check specific models first, then generic patterns
        elif "codestral" in cleaned:
            return "codestral"
        elif "pixtral" in cleaned:
            return "pixtral"
        elif "mistral" in cleaned or "mixtral" in cleaned:
            if "large" in cleaned:
                if "2" in cleaned:
                    return "mistral-large-2"
                return "mistral-large"
            elif "medium" in cleaned:
                return "mistral-medium"
            elif "small" in cleaned:
                return "mistral-small"
            elif "8x22b" in cleaned:
                return "mixtral-8x22b"
            elif "8x7b" in cleaned:
                return "mixtral-8x7b"
            elif "nemo" in cleaned:
                return "mistral-nemo"
            elif "7b" in cleaned:
                return "mistral-7b"
            return "mistral-small"  # default

        # Provider-based fallbacks if specific model not found
        provider = self._guess_provider_from_model(model_name)
        provider_defaults = {
            "openai": "gpt-3.5-turbo",
            "anthropic": "claude-3-sonnet",
            "google": "gemini-1.0-pro",
            "meta": "llama-3-8b",
            "mistral": "mistral-small",
        }

        if provider in provider_defaults:
            logger.debug(f"🔄 Using {provider} default model for: {model_name}")
            return provider_defaults[provider]

        # Final fallback
        return model_name

    def end(
        self,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        error: Optional[Exception] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        End the entire trace and send trace_end event.

        This is like Langflow's end_tracers().
        """
        if not self._ready or not self._trace_context:
            return

        try:
            trace_end_time = time.time()
            duration_ms = (trace_end_time - self._trace_context.start_time) * 1000

            # Lightweight trace metrics - worker handles cost calculation
            total_spans = len(self._trace_context.completed_spans)

            # Send trace_end event to Kafka (lightweight)
            trace_metadata = {
                "flow_id": self._trace_context.flow_id,
                "trace_name": self._trace_context.trace_name,
                "total_spans": total_spans,
                "status": "error" if error else "success",
                "project_name": getattr(
                    self._trace_context, "project_name", "GenesisStudio"
                ),
                **self._trace_context.tags,
                **self._trace_context.params,
                **self._trace_context.metrics,
                **(metadata or {}),
            }

            success = self._kafka_producer.send_trace_end(
                trace_id=self._trace_context.trace_id,
                duration_ms=duration_ms,
                metadata=trace_metadata,
                error=str(error) if error else None,
            )
            if success:
                logger.info(
                    f"✅ Completed streaming trace: {self._trace_context.trace_id} "
                    f"(duration: {duration_ms:.2f}ms, spans: {total_spans})"
                )
            else:
                logger.warning(f"❌ Failed to send trace_end event")

            # Flush any pending messages
            self._flush_producer()

        except Exception as e:
            logger.error(f"Error ending streaming trace: {e}")

    def add_cost_event(self, event_data: Dict[str, Any]) -> None:
        """Lightweight cost event tracking - worker handles calculation."""
        # In streaming mode, cost calculation is done by worker
        # Just log for debugging purposes
        logger.debug(
            f"Cost event data sent to worker: {event_data.get('model_name', 'unknown')}"
        )

    def add_tags(self, tags: Dict[str, str]):
        """Add tags to trace context."""
        if self._trace_context:
            self._trace_context.tags.update(tags)

    def log_param(self, key: str, value: Any):
        """Log parameter to trace context."""
        if self._trace_context:
            self._trace_context.params[key] = value

    def log_metric(self, key: str, value: float):
        """Log metric to trace context."""
        if self._trace_context:
            self._trace_context.metrics[key] = value

    def get_langchain_callback(self):
        """Get LangChain callback handler."""
        return self._callback_handler

    def _flush_producer(self):
        """Flush Kafka producer."""
        try:
            if self._kafka_producer:
                pending = self._kafka_producer.flush(timeout=5.0)
                if pending > 0:
                    logger.warning(f"{pending} messages still pending after flush")
        except Exception as e:
            logger.error(f"Error flushing producer: {e}")

    def close(self):
        """Close the tracer."""
        try:
            self._flush_producer()
            if self._kafka_producer:
                self._kafka_producer.close()
                self._kafka_producer = None
            logger.debug("Streaming tracer closed")
        except Exception as e:
            logger.error(f"Error closing streaming tracer: {e}")

    def __del__(self):
        """Destructor to ensure cleanup."""
        self.close()


class StreamingLangChainCallback(BaseCallbackHandler):
    """LangChain callback for streaming cost tracking."""

    def __init__(self, tracer: AgentTracer):
        super().__init__()
        self.tracer = tracer

        # Lightweight streaming mode - no cost calculation (done in worker)
        self.cost_tracker = None

        # Track active LLM runs for streaming mode
        self.llm_runs = {}

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs
    ) -> None:
        """
        Track LLM start using proven agent_tracer logic.
        """
        try:
            run_id = str(kwargs.get("run_id", ""))
            if not run_id:
                return

            model_name = "unknown"

            # PROVEN LOGIC from agent_tracer.py - Method 1: Extract from kwargs (most reliable)
            if "kwargs" in kwargs and isinstance(kwargs["kwargs"], dict):
                run_kwargs = kwargs["kwargs"]
                if "model" in run_kwargs:
                    model_name = run_kwargs["model"]
                elif "model_name" in run_kwargs:
                    model_name = run_kwargs["model_name"]

            # Method 2: Extract from serialized kwargs (backup)
            if model_name == "unknown" and "kwargs" in serialized:
                serialized_kwargs = serialized.get("kwargs", {})
                if isinstance(serialized_kwargs, dict):
                    if "model" in serialized_kwargs:
                        model_name = serialized_kwargs["model"]
                    elif "model_name" in serialized_kwargs:
                        model_name = serialized_kwargs["model_name"]

            # Method 3: Extract from component invocation kwargs (LangFlow specific)
            if model_name == "unknown" and "invocation_params" in kwargs:
                invocation_params = kwargs.get("invocation_params", {})
                if isinstance(invocation_params, dict):
                    if "model" in invocation_params:
                        model_name = invocation_params["model"]
                    elif "model_name" in invocation_params:
                        model_name = invocation_params["model_name"]

            # Method 4: FALLBACK ONLY - Extract from serialized info (class name - not reliable)
            if (
                model_name == "unknown"
                and "id" in serialized
                and isinstance(serialized["id"], list)
            ):
                class_name = serialized["id"][-1]
                # Only use class name if no other method worked
                model_name = class_name
                logger.warning(
                    f"⚠️ Using LangChain class name as model name fallback: {model_name}"
                )

            logger.debug(f"🔍 Extracted model name in on_llm_start: {model_name}")

            # Store run info for cost calculation
            self.llm_runs[run_id] = {
                "model_name": model_name,
                "start_time": time.time(),
                "prompts": prompts,
                "serialized": serialized,
            }

            # Send real-time LLM start event
            if self.tracer._trace_context and self.tracer._kafka_producer:
                try:
                    provider = self.tracer._guess_provider_from_model(model_name)
                    self.tracer._kafka_producer.send_custom_event(
                        trace_id=self.tracer._trace_context.trace_id,
                        event_type="llm_start",
                        data={
                            "run_id": run_id,
                            "model_info": {
                                "name": model_name,
                                "provider": provider,
                            },
                            "prompts": _safe_serialize_value(prompts),
                        },
                    )
                    logger.info(f"✅ Sent llm_start event for {model_name}")
                except Exception as e:
                    logger.error(f"❌ Failed to send llm_start event: {e}")

        except Exception as e:
            logger.error(f"❌ Critical error in on_llm_start: {e}")

    def on_llm_end(self, response, **kwargs) -> None:
        """
        End LLM run using proven agent_tracer logic.
        """
        try:
            run_id = str(kwargs.get("run_id", ""))
            if not run_id or run_id not in self.llm_runs:
                return

            run_info = self.llm_runs[run_id]

            # Extract token usage and model name using proven agent_tracer logic
            token_usage = None
            model_name = run_info["model_name"]

            # Try to get the actual model name from response metadata (more accurate)
            actual_model_name = self._extract_actual_model_name(response)
            if actual_model_name:
                model_name = actual_model_name
                logger.debug(f"Updated model name from response: {model_name}")

            # Try multiple locations for token usage (streaming vs non-streaming)
            # Method 1: Non-streaming responses - llm_output
            if hasattr(response, "llm_output") and response.llm_output:
                if (
                    isinstance(response.llm_output, dict)
                    and "token_usage" in response.llm_output
                ):
                    token_usage = response.llm_output["token_usage"]
                    logger.debug(f"Found token usage in llm_output: {token_usage}")

            # Method 2: Streaming responses - generations (handles nested structure)
            if (
                not token_usage
                and hasattr(response, "generations")
                and response.generations
            ):
                first_gen = response.generations[0]

                # Handle nested list structure for streaming
                if isinstance(first_gen, list) and len(first_gen) > 0:
                    generation = first_gen[0]  # Get actual Generation object
                else:
                    generation = first_gen  # Direct Generation object

                # Method 2a: generation.generation_info.token_usage (OpenAI/Azure streaming)
                if hasattr(generation, "generation_info") and isinstance(
                    generation.generation_info, dict
                ):
                    if "token_usage" in generation.generation_info:
                        token_usage = generation.generation_info["token_usage"]
                        logger.debug(
                            f"Found token usage in generation_info: {token_usage}"
                        )

                # Method 2b: generation.message.response_metadata (Alternative streaming)
                if not token_usage and hasattr(generation, "message"):
                    message = generation.message
                    if hasattr(message, "response_metadata") and isinstance(
                        message.response_metadata, dict
                    ):
                        # OpenAI format
                        if "token_usage" in message.response_metadata:
                            token_usage = message.response_metadata["token_usage"]
                            logger.debug(
                                f"Found token usage in response_metadata.token_usage: {token_usage}"
                            )
                        # Anthropic format
                        elif "usage" in message.response_metadata:
                            usage = message.response_metadata["usage"]
                            if isinstance(usage, dict):
                                # Convert Anthropic format to OpenAI format
                                token_usage = {
                                    "prompt_tokens": usage.get("input_tokens", 0),
                                    "completion_tokens": usage.get("output_tokens", 0),
                                    "total_tokens": usage.get("input_tokens", 0)
                                    + usage.get("output_tokens", 0),
                                }
                                logger.debug(
                                    f"Found Anthropic usage, converted: {token_usage}"
                                )

            # Method 3: Alternative - usage_metadata (some providers)
            if (
                not token_usage
                and hasattr(response, "usage_metadata")
                and isinstance(response.usage_metadata, dict)
            ):
                token_usage = response.usage_metadata
                logger.debug(f"Found token usage in usage_metadata: {token_usage}")

            # Send token usage if found, otherwise try fallback estimation
            if token_usage and isinstance(token_usage, dict):
                prompt_tokens = token_usage.get("prompt_tokens", 0)
                completion_tokens = token_usage.get("completion_tokens", 0)
                total_tokens = token_usage.get(
                    "total_tokens", prompt_tokens + completion_tokens
                )

                # Send llm_end event with token usage
                if self.tracer._trace_context and self.tracer._kafka_producer:
                    self.tracer._kafka_producer.send_custom_event(
                        trace_id=self.tracer._trace_context.trace_id,
                        event_type="llm_end",
                        data={
                            "run_id": run_id,
                            "model_name": model_name,
                            "prompts": run_info.get("prompts", []),
                            "response_data": self._extract_response_text(response),
                            "token_usage": token_usage,
                        },
                    )
                logger.info(
                    f"✅ Sent llm_end event for {model_name} with API token usage"
                )
            else:
                # FALLBACK: Estimate token usage for Azure OpenAI streaming responses
                logger.info(
                    f"🔄 No token usage found - attempting fallback estimation for {model_name}"
                )

                try:
                    # Try to estimate token usage using tiktoken
                    estimated_tokens = self._estimate_token_usage_fallback(
                        model_name=model_name,
                        prompts=run_info.get("prompts", []),
                        response=response,
                    )

                    if estimated_tokens:
                        # Send llm_end event with estimated token usage
                        if self.tracer._trace_context and self.tracer._kafka_producer:
                            self.tracer._kafka_producer.send_custom_event(
                                trace_id=self.tracer._trace_context.trace_id,
                                event_type="llm_end",
                                data={
                                    "run_id": run_id,
                                    "model_name": model_name,
                                    "prompts": run_info.get("prompts", []),
                                    "response_data": self._extract_response_text(
                                        response
                                    ),
                                    "token_usage": estimated_tokens,
                                },
                            )
                        logger.info(
                            f"✅ Sent llm_end event for {model_name} with estimated tokens"
                        )
                    else:
                        logger.warning(
                            f"❌ Could not estimate token usage for model {model_name}"
                        )

                except Exception as e:
                    logger.error(f"Error estimating token usage: {e}")

        except Exception as e:
            logger.error(f"Error in on_llm_end: {e}")
        finally:
            # Clean up run info
            if run_id in self.llm_runs:
                del self.llm_runs[run_id]

    def on_llm_error(self, error: Exception, **kwargs) -> None:
        """Handle LLM errors."""
        run_id = str(kwargs.get("run_id", ""))
        if run_id in self.llm_runs:
            del self.llm_runs[run_id]

    def on_chat_model_start(
        self, serialized: Dict[str, Any], messages: List[List], **kwargs
    ) -> None:
        """Handle chat model start (same as LLM start for our purposes)."""
        # Convert messages to prompts format for compatibility
        prompts = []
        for message_list in messages:
            # Convert message objects to string representation
            prompt_parts = []
            for msg in message_list:
                if hasattr(msg, "content"):
                    prompt_parts.append(str(msg.content))
                else:
                    prompt_parts.append(str(msg))
            prompts.append("\n".join(prompt_parts))

        # Delegate to on_llm_start
        self.on_llm_start(serialized, prompts, **kwargs)

    def _extract_response_text(self, response) -> str:
        """Extract response text for sending to worker."""
        try:
            if hasattr(response, "generations") and response.generations:
                first_gen = response.generations[0]
                if isinstance(first_gen, list) and len(first_gen) > 0:
                    generation = first_gen[0]
                else:
                    generation = first_gen

                if hasattr(generation, "text"):
                    return generation.text
                elif hasattr(generation, "message") and hasattr(
                    generation.message, "content"
                ):
                    return generation.message.content

            return str(response) if response else ""
        except Exception:
            return ""

    def _extract_actual_model_name(self, response) -> Optional[str]:
        """Extract the actual model name from response metadata (from proven agent_tracer)."""
        try:
            # Try to get model name from response metadata (most accurate)
            if hasattr(response, "generations") and response.generations:
                first_gen = response.generations[0]

                # Handle nested list structure for streaming
                if isinstance(first_gen, list) and len(first_gen) > 0:
                    generation = first_gen[0]
                else:
                    generation = first_gen

                # Method 1: Check generation_info for model_name
                if hasattr(generation, "generation_info") and isinstance(
                    generation.generation_info, dict
                ):
                    gen_info = generation.generation_info
                    if "model_name" in gen_info:
                        return gen_info["model_name"]
                    elif "model" in gen_info:
                        return gen_info["model"]

                # Method 2: Check message.response_metadata for model info
                if hasattr(generation, "message") and hasattr(
                    generation.message, "response_metadata"
                ):
                    metadata = generation.message.response_metadata
                    if isinstance(metadata, dict):
                        if "model_name" in metadata:
                            return metadata["model_name"]
                        elif "model" in metadata:
                            return metadata["model"]

            # Method 3: Check llm_output for model name (non-streaming)
            if hasattr(response, "llm_output") and isinstance(
                response.llm_output, dict
            ):
                llm_output = response.llm_output
                if "model_name" in llm_output:
                    return llm_output["model_name"]
                elif "model" in llm_output:
                    return llm_output["model"]

            # Method 4: Check response-level metadata
            if hasattr(response, "response_metadata") and isinstance(
                response.response_metadata, dict
            ):
                metadata = response.response_metadata
                if "model_name" in metadata:
                    return metadata["model_name"]
                elif "model" in metadata:
                    return metadata["model"]

            return None

        except Exception as e:
            logger.debug(f"Could not extract model name from response: {e}")
            return None

    def _estimate_token_usage_fallback(
        self, model_name: str, prompts: list, response
    ) -> dict:
        """
        Fallback method to estimate token usage using tiktoken when not provided by the API.

        Used for Azure OpenAI streaming responses that don't include token usage.
        """
        try:
            import tiktoken

            # Get encoding for the model
            if "gpt-4" in model_name.lower():
                encoding = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding
            elif "gpt-3.5" in model_name.lower():
                encoding = tiktoken.get_encoding("cl100k_base")  # GPT-3.5 encoding
            else:
                # Default to cl100k_base for most OpenAI models
                encoding = tiktoken.get_encoding("cl100k_base")

            # Count prompt tokens
            prompt_tokens = 0
            for prompt in prompts:
                if isinstance(prompt, str):
                    prompt_tokens += len(encoding.encode(prompt))

            # Count completion tokens from response
            completion_tokens = 0
            response_text = ""

            # Extract response text from various response formats
            if hasattr(response, "generations") and response.generations:
                first_gen = response.generations[0]
                if isinstance(first_gen, list) and len(first_gen) > 0:
                    # Streaming response - nested list
                    generation = first_gen[0]
                    if hasattr(generation, "text"):
                        response_text = generation.text
                    elif hasattr(generation, "message") and hasattr(
                        generation.message, "content"
                    ):
                        response_text = generation.message.content
                else:
                    # Non-streaming response
                    if hasattr(first_gen, "text"):
                        response_text = first_gen.text
                    elif hasattr(first_gen, "message") and hasattr(
                        first_gen.message, "content"
                    ):
                        response_text = first_gen.message.content

            if response_text and isinstance(response_text, str):
                completion_tokens = len(encoding.encode(response_text))

            total_tokens = prompt_tokens + completion_tokens

            if total_tokens > 0:
                logger.info(
                    f"✅ Estimated tokens for {model_name}: "
                    f"prompt={prompt_tokens}, completion={completion_tokens}, total={total_tokens}"
                )
                return {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens,
                }
            else:
                logger.warning(
                    f"❌ Token estimation resulted in 0 tokens for {model_name}"
                )
                return None

        except ImportError:
            logger.warning("tiktoken not available - cannot estimate token usage")
            return None
        except Exception as e:
            logger.error(f"Error in token estimation: {e}")
            return None


# Context manager for easy usage
@contextmanager
def streaming_trace(trace_name: str, trace_id: uuid.UUID, flow_id: str, **kwargs):
    """
    Context manager for streaming traces.

    Usage:
        with streaming_trace("My Flow", trace_id, flow_id) as tracer:
            tracer.add_trace("comp1", "Component 1", "llm", inputs)
            # ... do work ...
            tracer.end_trace("comp1", "Component 1", outputs)
    """
    tracer = AgentTracer(
        trace_name=trace_name, trace_id=trace_id, flow_id=flow_id, **kwargs
    )

    try:
        tracer.start_trace()
        yield tracer
    except Exception as e:
        tracer.end({}, {}, error=e)
        raise
    else:
        tracer.end({}, {})
    finally:
        tracer.close()
