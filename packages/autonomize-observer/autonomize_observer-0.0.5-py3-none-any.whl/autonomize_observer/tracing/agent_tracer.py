"""
Agent-based tracer for Genesis Studio flows.

This tracer assembles complete traces locally with all business logic and metrics,
then sends them to message queues for processing by simple, generic workers.
"""

import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, List

from ..tracing.base_tracer import BaseTracer
from ..kafka.producer import KafkaTraceProducer
from ..kafka.schemas import CompleteTrace, SpanInfo, _safe_serialize_value

# Optional imports
try:
    from ..monitoring.cost_tracking import CostTracker

    COST_TRACKING_AVAILABLE = True
except ImportError:
    COST_TRACKING_AVAILABLE = False
    CostTracker = None

try:
    from langchain.callbacks.base import BaseCallbackHandler

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    BaseCallbackHandler = object

logger = logging.getLogger(__name__)


class AgentTracer(BaseTracer):
    """
    Agent-based tracer for Genesis Studio flows.

    This tracer assembles complete traces locally with all business logic,
    calculates comprehensive metrics, and sends complete trace objects to
    message queues for processing by simple, generic workers.
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
        kafka_topic: str = "genesis-traces",
        # Authentication parameters
        kafka_username: Optional[str] = None,
        kafka_password: Optional[str] = None,
        security_protocol: str = "PLAINTEXT",
        sasl_mechanism: str = "PLAIN",
        **kwargs,
    ):
        """
        Initialize Agent tracer.

        Args:
            trace_name: Name of the trace (flow/agent name)
            trace_id: Unique identifier for the trace
            flow_id: Flow identifier
            project_name: Project name for organization
            user_id: Optional user identifier
            session_id: Optional session identifier
            kafka_bootstrap_servers: Kafka broker addresses
            kafka_topic: Kafka topic for trace events
            kafka_username: Optional SASL username for authentication
            kafka_password: Optional SASL password for authentication
            security_protocol: Security protocol (PLAINTEXT, SASL_SSL, etc.)
            sasl_mechanism: SASL mechanism (PLAIN, SCRAM-SHA-256, etc.)
        """
        # Clean up trace name for better readability
        cleaned_trace_name = self._clean_trace_name(trace_name)
        super().__init__(cleaned_trace_name, "flow", project_name, trace_id)

        # Store additional parameters as instance variables
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

        # Trace assembly state
        self._trace_start_time = None
        self._spans: Dict[str, SpanInfo] = {}
        self._complete_trace: Optional[CompleteTrace] = None
        self._span_execution_order = []  # Track execution order for parent inference

        # Metadata and metrics storage
        self._tags = {}
        self._params = {}
        self._metrics = {}
        self._custom_events = []

        # LangChain callback for cost tracking
        self._callback_handler = None
        if LANGCHAIN_AVAILABLE:
            self._callback_handler = AgentLangChainCallback(self)

        # Setup Kafka producer
        self._setup_kafka_producer()

        logger.info(f"Agent tracer initialized for flow: {flow_id}")

    def _clean_trace_name(self, trace_name: str) -> str:
        """Clean up trace name for better readability in MLflow."""
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
        """Check if tracer is ready to use."""
        return self._ready

    def _setup_kafka_producer(self):
        """Setup Kafka producer with proper configuration."""
        try:
            if not self.kafka_bootstrap_servers:
                logger.warning(
                    "No Kafka bootstrap servers configured, tracer will be disabled"
                )
                return

            # Initialize Kafka producer
            self._kafka_producer = KafkaTraceProducer(
                bootstrap_servers=self.kafka_bootstrap_servers,
                topic=self.kafka_topic,
                client_id=f"genesis-studio-{self.flow_id[:8]}",
                # Authentication parameters
                kafka_username=self.kafka_username,
                kafka_password=self.kafka_password,
                security_protocol=self.security_protocol,
                sasl_mechanism=self.sasl_mechanism,
            )

            self._ready = True
            logger.debug(f"Kafka producer initialized for topic: {self.kafka_topic}")

        except Exception as e:
            logger.error(f"Failed to setup Kafka producer: {e}")
            self._ready = False

    def add_trace(
        self,
        trace_id: str,
        trace_name: str,
        trace_type: str,
        inputs: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        vertex: Any = None,
        parent_id: Optional[str] = None,
    ) -> None:
        """
        Start a new span (component trace).

        Args:
            trace_id: Component identifier
            trace_name: Name of the span (component name)
            trace_type: Type of trace (always "span" for components)
            inputs: Input data for the component
            metadata: Additional metadata
            vertex: Vertex object (not used in Agent tracer)
            parent_id: Optional parent component ID for hierarchical tracing
        """
        if not self._ready:
            logger.debug("Agent tracer not ready, skipping span start")
            return

        # Initialize trace if this is the first span
        if self._trace_start_time is None:
            self._start_trace()

        # Generate span ID
        span_id = f"{trace_id}-{int(time.time() * 1000)}"

        # Find parent span ID if parent component ID is provided
        parent_span_id = None
        if parent_id:
            # Find the span for the parent component
            for span in self._spans.values():
                if span.component_id == parent_id:
                    parent_span_id = span.span_id
                    break
            if parent_span_id:
                logger.debug(f"🔗 Found parent {parent_id} for {trace_name}")
            else:
                logger.debug(f"⚠️ Parent {parent_id} not found for {trace_name}")

        # Create span info with safely serialized inputs
        span_info = SpanInfo(
            span_id=span_id,
            component_id=trace_id,
            component_name=trace_name,
            start_time=time.time(),
            parent_span_id=parent_span_id,  # Set parent relationship
            input_data=_safe_serialize_value(inputs) if inputs else {},
            metadata=_safe_serialize_value(metadata) if metadata else {},
        )

        # Store span locally
        self._spans[span_id] = span_info
        self._span_execution_order.append(span_id)  # Track execution order

        logger.debug(f"Started span for {trace_name} ({trace_id})")

    def end_trace(
        self,
        trace_id: str,
        trace_name: str,
        outputs: Optional[Dict[str, Any]] = None,
        error: Optional[Exception] = None,
        logs: Any = (),
    ):
        """
        End a span (component trace).

        Args:
            trace_id: Component identifier (used to find span)
            trace_name: Name of the component
            outputs: Output data from the component
            error: Optional error that occurred
            logs: Logs from component execution
        """
        if not self._ready:
            logger.debug("Agent tracer not ready, skipping span end")
            return

        # Find the span by component_id
        span_info = None
        for span in self._spans.values():
            if span.component_id == trace_id:
                span_info = span
                break

        if not span_info:
            logger.warning(f"No span found for component {trace_id}")
            return

        # Update span with end information and safely serialized outputs
        span_info.end_time = time.time()
        span_info.duration_ms = (span_info.end_time - span_info.start_time) * 1000
        span_info.output_data = _safe_serialize_value(outputs) if outputs else {}
        span_info.error = str(error) if error else None

        logger.debug(
            f"Ended span for {span_info.component_name} ({trace_id}) - "
            f"duration: {span_info.duration_ms:.2f}ms"
        )

    def _start_trace(self):
        """Initialize the trace."""
        self._trace_start_time = time.time()
        logger.debug(f"Started trace for agent {self.trace_name}")

    def end(
        self,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        error: Optional[Exception] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        End the entire trace and send complete trace with all metrics to Kafka.

        This is where we assemble the complete trace with all business logic and metrics.
        """
        if not self._ready:
            logger.debug("Agent tracer not ready, skipping trace end")
            return

        try:
            # Calculate total duration
            end_time = time.time()
            duration_ms = (
                (end_time - self._trace_start_time) * 1000
                if self._trace_start_time
                else 0
            )

            # Extract flow-level inputs and outputs from spans
            flow_inputs, flow_outputs = self._extract_flow_inputs_outputs()

            # Combine with provided inputs/outputs (safely serialize them first)
            if inputs:
                safe_inputs = _safe_serialize_value(inputs)
                flow_inputs.update(safe_inputs)
            if outputs:
                safe_outputs = _safe_serialize_value(outputs)
                flow_outputs.update(safe_outputs)

            # Infer parent-child relationships between spans
            self._infer_parent_relationships()

            # Calculate comprehensive metrics
            computed_metrics = self._calculate_comprehensive_metrics()

            # Extract model names from cost events for trace parameters
            models_used = self._extract_models_used()

            # Assemble complete metadata with all computed metrics (safely serialize metadata)
            complete_metadata = {
                "project_name": self.project_name,
                "start_timestamp": (
                    datetime.fromtimestamp(
                        self._trace_start_time, timezone.utc
                    ).isoformat()
                    if self._trace_start_time
                    else None
                ),
                "end_timestamp": datetime.now(timezone.utc).isoformat(),
                "tags": self._tags,
                "params": {
                    **self._params,
                    **models_used,  # Add model names to params
                },
                "metrics": {
                    **self._metrics,
                    **computed_metrics,
                },  # Include computed metrics
                "custom_events": self._custom_events,
            }

            if metadata:
                safe_metadata = _safe_serialize_value(metadata)
                complete_metadata.update(safe_metadata)

            # Create complete trace object with all business logic applied
            complete_trace = CompleteTrace(
                trace_id=str(self.trace_id),
                flow_id=self.flow_id,
                flow_name=self.trace_name,
                start_time=self._trace_start_time or time.time(),
                end_time=end_time,
                duration_ms=duration_ms,
                user_id=self.user_id,
                session_id=self.session_id,
                project_name=self.project_name,
                spans=list(self._spans.values()),
                flow_inputs=flow_inputs if flow_inputs else None,
                flow_outputs=flow_outputs if flow_outputs else None,
                metadata=complete_metadata,
                error=str(error) if error else None,
                total_components=len(self._spans),
            )

            # Send complete trace to Kafka
            success = self._kafka_producer.send_complete_trace(complete_trace)

            if success:
                logger.info(
                    f"Sent complete trace for agent {self.trace_name} "
                    f"(duration: {duration_ms:.2f}ms, {len(self._spans)} components, "
                    f"{len(computed_metrics)} computed metrics)"
                )
            else:
                logger.warning(
                    f"Failed to send complete trace for agent {self.trace_name}"
                )

            # Flush pending messages with increased timeout for production
            try:
                if self._kafka_producer:
                    pending = self._kafka_producer.flush(timeout=5.0)
                    if pending > 0:
                        logger.warning(f"{pending} messages still pending after flush")
            except Exception as e:
                logger.error(f"Error flushing Kafka producer: {e}")

            # Get final stats
            if self._kafka_producer:
                stats = self._kafka_producer.get_stats()
                logger.info(f"Agent tracer stats: {stats}")

        except Exception as e:
            logger.error(f"Error ending trace: {e}")

    def _calculate_comprehensive_metrics(self) -> Dict[str, float]:
        """
        Calculate streamlined metrics from custom events (business logic in SDK).

        Reduces metric redundancy while keeping essential monitoring data.
        """
        metrics = {}

        # Extract cost tracking events
        cost_events = [
            e for e in self._custom_events if e.get("event_type") == "cost_tracking"
        ]

        if not cost_events:
            return metrics

        # Initialize totals
        total_input_tokens = 0
        total_output_tokens = 0
        total_tokens = 0
        total_cost = 0.0
        total_calls = len(cost_events)

        # Per-model and per-provider tracking
        by_model = {}
        by_provider = {}

        for event in cost_events:
            event_data = event.get("data", {})

            # Extract basic metrics
            model_name = event_data.get("model_name", "unknown")
            cost = event_data.get("cost", 0.0)
            token_usage = event_data.get("token_usage", {})

            input_tokens = token_usage.get("prompt_tokens", 0) or token_usage.get(
                "input", 0
            )
            output_tokens = token_usage.get("completion_tokens", 0) or token_usage.get(
                "output", 0
            )
            event_total_tokens = input_tokens + output_tokens

            # Add to totals
            total_input_tokens += input_tokens
            total_output_tokens += output_tokens
            total_tokens += event_total_tokens
            total_cost += cost

            # Track by model
            if model_name not in by_model:
                by_model[model_name] = {
                    "calls": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "cost": 0.0,
                }
            by_model[model_name]["calls"] += 1
            by_model[model_name]["input_tokens"] += input_tokens
            by_model[model_name]["output_tokens"] += output_tokens
            by_model[model_name]["total_tokens"] += event_total_tokens
            by_model[model_name]["cost"] += cost

            # Guess provider from model name for tracking
            provider = self._guess_provider_from_model(model_name)
            if provider not in by_provider:
                by_provider[provider] = {
                    "calls": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "cost": 0.0,
                }
            by_provider[provider]["calls"] += 1
            by_provider[provider]["input_tokens"] += input_tokens
            by_provider[provider]["output_tokens"] += output_tokens
            by_provider[provider]["total_tokens"] += event_total_tokens
            by_provider[provider]["cost"] += cost

        # 🎯 TIER 1: CORE METRICS (Always Include) - 8 essential metrics
        metrics.update(
            {
                "total_cost": total_cost,
                "total_tokens": total_tokens,
                "total_input_tokens": total_input_tokens,
                "total_output_tokens": total_output_tokens,
                "total_llm_calls": total_calls,
            }
        )

        # Core efficiency metrics
        if total_tokens > 0:
            metrics["cost_per_token"] = total_cost / total_tokens

        if total_input_tokens > 0 and total_output_tokens > 0:
            metrics["output_input_ratio"] = total_output_tokens / total_input_tokens

        if total_calls > 0:
            metrics["avg_cost_per_call"] = total_cost / total_calls

        # 🔧 TIER 2: BREAKDOWN METRICS (Only when multiple models/providers)

        # Top model metrics (only if multiple models)
        if len(by_model) > 1:
            top_model = max(by_model.items(), key=lambda x: x[1]["total_tokens"])
            model_name, model_stats = top_model

            # Use safe model name for metric (replace special chars)
            safe_model_name = (
                model_name.replace("-", "_").replace(".", "_").replace(" ", "_")
            )

            metrics.update(
                {
                    f"top_model_{safe_model_name}_tokens": model_stats["total_tokens"],
                    f"top_model_{safe_model_name}_cost": model_stats["cost"],
                }
            )
            logger.debug(f"Added top model metrics for: {model_name}")

        # Provider breakdown (only if multiple providers)
        if len(by_provider) > 1:
            for provider, stats in by_provider.items():
                safe_provider = (
                    provider.replace("-", "_").replace(".", "_").replace(" ", "_")
                )
                metrics.update(
                    {
                        f"{safe_provider}_tokens": stats["total_tokens"],
                        f"{safe_provider}_cost": stats["cost"],
                    }
                )
            logger.debug(f"Added provider breakdown for: {list(by_provider.keys())}")

        # 📈 TIER 3: ADVANCED METRICS (Useful for analytics)
        if total_calls > 0:
            metrics["avg_tokens_per_call"] = total_tokens / total_calls

        logger.info(
            f"✅ Calculated {len(metrics)} streamlined metrics "
            f"({len(by_model)} models, {len(by_provider)} providers)"
        )
        return metrics

    def _infer_parent_relationships(self):
        """
        Infer parent-child relationships using timing-based execution order.

        This method only fills in missing parent relationships. If parent relationships
        are already set (from TracingService with graph structure), they are preserved.

        Approach inspired by LangWatch but adapted for timing-based inference:
        1. Components that start later may be children of components that started earlier
        2. Use execution timing and overlap to determine likely parent-child relationships
        3. Avoid hardcoded component name patterns for better scalability
        """
        if not self._spans:
            logger.debug("No spans to process for parent relationships")
            return

        # Get spans sorted by start time
        sorted_spans = sorted(self._spans.values(), key=lambda s: s.start_time)

        # Check how many spans already have parent relationships
        spans_with_parents = sum(
            1 for span in sorted_spans if span.parent_span_id is not None
        )

        if spans_with_parents > 0:
            logger.info(
                f"🔗 Found {spans_with_parents}/{len(sorted_spans)} spans with parent relationships from TracingService"
            )
            # Only infer for spans that don't have parents
            spans_needing_inference = [
                span for span in sorted_spans if span.parent_span_id is None
            ]
            if not spans_needing_inference:
                logger.info(
                    "🔗 All parent relationships already set by TracingService - skipping inference"
                )
                return
            logger.info(
                f"🔍 Inferring parents for {len(spans_needing_inference)} remaining spans"
            )
        else:
            logger.info(
                "🔍 No parent relationships from TracingService - applying full inference"
            )
            spans_needing_inference = sorted_spans

        # Apply timing-based parent-child relationships inspired by LangWatch approach
        relationships_set = 0

        for span in spans_needing_inference:
            # Find potential parents: components that started before this one
            potential_parents = [
                s for s in sorted_spans if s.start_time <= span.start_time and s != span
            ]

            if not potential_parents:
                # This is likely a root span
                continue

            # Choose the most recent parent based on execution overlap
            best_parent = self._find_best_parent_by_timing(span, potential_parents)

            if best_parent:
                span.parent_span_id = best_parent.span_id
                relationships_set += 1
                logger.debug(
                    f"✅ Set parent: {span.component_name} → {best_parent.component_name}"
                )

        logger.info(
            f"🔗 Parent relationships: {relationships_set} relationships set for {len(spans_needing_inference)} spans needing inference"
        )

        # Debug: Show final parent structure
        for span in sorted_spans:
            parent_name = "ROOT"
            if span.parent_span_id:
                parent_span = next(
                    (s for s in sorted_spans if s.span_id == span.parent_span_id), None
                )
                if parent_span:
                    parent_name = parent_span.component_name
            logger.debug(f"🌳 {span.component_name} → parent: {parent_name}")

    def _find_best_parent_by_timing(
        self, span: SpanInfo, potential_parents: List[SpanInfo]
    ) -> Optional[SpanInfo]:
        """Find the best parent based on timing overlap and execution order."""
        if not potential_parents:
            return None

        best_parent = None
        best_score = float("-inf")

        for parent in potential_parents:
            # Calculate timing score based on overlap and proximity
            score = 0

            # Factor 1: Execution overlap (higher is better)
            parent_end = parent.end_time or parent.start_time
            span_start = span.start_time

            if parent.start_time <= span_start <= parent_end:
                # Span starts during parent execution - excellent
                score += 100
            else:
                # Penalize distance (closer is better)
                distance = abs(span_start - parent_end)
                score += max(0, 50 - distance)  # Closer parents get higher scores

            # Factor 2: Prefer more recent parents (started later)
            recency_bonus = parent.start_time * 0.001  # Small bonus for later starts
            score += recency_bonus

            # Factor 3: Avoid very short-lived parents unless they clearly contain the span
            parent_duration = parent_end - parent.start_time
            if parent_duration < 1.0 and not (
                parent.start_time <= span_start <= parent_end
            ):
                score -= 20  # Penalize short parents that don't contain the span

            if score > best_score:
                best_score = score
                best_parent = parent

        if best_parent:
            logger.debug(
                f"🎯 Best parent for {span.component_name}: {best_parent.component_name} (score: {best_score:.2f})"
            )

        return best_parent

    def _guess_provider_from_model(self, model_name: str) -> str:
        """Guess provider from model name."""
        model_lower = model_name.lower()
        if any(name in model_lower for name in ["gpt", "openai", "o1", "o3"]):
            return "openai"
        elif any(name in model_lower for name in ["claude", "anthropic"]):
            return "anthropic"
        elif any(name in model_lower for name in ["gemini", "google", "bard"]):
            return "google"
        elif any(name in model_lower for name in ["llama", "meta"]):
            return "meta"
        elif any(name in model_lower for name in ["mistral", "mixtral"]):
            return "mistral"
        else:
            return "unknown"

    def _extract_flow_inputs_outputs(self) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Extract component-by-component inputs/outputs organized by component name."""
        flow_inputs = {}
        flow_outputs = {}

        if not self._spans:
            return flow_inputs, flow_outputs

        # Sort spans by start time to get flow order
        sorted_spans = sorted(self._spans.values(), key=lambda x: x.start_time)

        # Build component-by-component structure like "Chat Input (ChatInput-abc123)"
        for span in sorted_spans:
            component_key = f"{span.component_name} ({span.component_id})"

            # Add component inputs
            if span.input_data:
                flow_inputs[component_key] = span.input_data

            # Add component outputs
            if span.output_data:
                flow_outputs[component_key] = span.output_data

        logger.debug(
            f"Extracted flow data - inputs: {list(flow_inputs.keys())}, "
            f"outputs: {list(flow_outputs.keys())}"
        )
        return flow_inputs, flow_outputs

    def get_trace_url(self) -> Optional[str]:
        """
        Get URL to view the trace (not applicable for Agent tracer).

        Returns:
            None (traces will be viewable in MLflow after consumer processing)
        """
        return None

    def add_tags(self, tags: Dict[str, str]):
        """Add tags to the trace."""
        self._tags.update(tags)

    def log_param(self, key: str, value: Any):
        """Log parameter."""
        self._params[key] = value

    def log_metric(self, key: str, value: float):
        """Log metric."""
        self._metrics[key] = value

    def add_custom_event(self, event_type: str, data: Dict[str, Any]):
        """Add custom event (e.g., cost tracking)."""
        event = {
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data,
        }
        self._custom_events.append(event)

    def get_langchain_callback(self):
        """Get LangChain callback handler for cost tracking."""
        return self._callback_handler

    def close(self):
        """Close the Kafka producer."""
        try:
            if self._kafka_producer:
                self._kafka_producer.close()
                self._kafka_producer = None
                logger.debug("Agent tracer closed")
        except Exception as e:
            logger.error(f"Error closing Agent tracer: {e}")

    def __del__(self):
        """Destructor to ensure cleanup."""
        self.close()

    def _extract_models_used(self) -> Dict[str, str]:
        """Extract model names from cost events for trace parameters."""
        models_used = {}
        unique_models = set()

        # Extract unique model names from cost events
        for event in self._custom_events:
            if event.get("event_type") == "cost_tracking":
                model_name = event.get("data", {}).get("model_name", "unknown")
                if model_name and model_name != "unknown":
                    unique_models.add(model_name)

        if unique_models:
            # Add a comma-separated list of all models used
            models_used["models_used"] = ", ".join(sorted(unique_models))

            # Add count of unique models
            models_used["models_count"] = str(len(unique_models))

            # Add individual model parameters for easier filtering (first 3 models)
            for i, model_name in enumerate(sorted(unique_models)[:3], 1):
                safe_param_name = f"model_{i}"
                models_used[safe_param_name] = model_name

        logger.debug(f"Extracted models for trace params: {list(unique_models)}")
        return models_used


class AgentLangChainCallback(BaseCallbackHandler):
    """LangChain callback handler for Agent-based cost tracking."""

    def __init__(self, tracer):
        super().__init__()
        self.tracer = tracer
        self.llm_runs = {}
        if CostTracker:
            self.cost_tracker = CostTracker()
        else:
            self.cost_tracker = None
            logger.warning("CostTracker not available - cost tracking disabled")

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs
    ) -> None:
        """Start LLM run tracking."""
        logger.debug("Agent LLM callback: on_llm_start called")

        run_id = str(kwargs.get("run_id", ""))
        if not run_id:
            return

        model_name = "unknown"

        # ENHANCED: Try multiple methods to get the actual model name

        # Method 1: Extract from kwargs (most reliable)
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

    def on_llm_end(self, response, **kwargs) -> None:
        """End LLM run and calculate costs."""
        logger.debug("Agent LLM callback: on_llm_end called")

        run_id = str(kwargs.get("run_id", ""))
        if not run_id or run_id not in self.llm_runs:
            return

        run_info = self.llm_runs[run_id]

        try:
            # Extract token usage and calculate costs
            if not self.cost_tracker:
                return

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

            # Calculate and send cost if token usage found
            if token_usage and isinstance(token_usage, dict):
                prompt_tokens = token_usage.get("prompt_tokens", 0)
                completion_tokens = token_usage.get("completion_tokens", 0)
                total_tokens = token_usage.get(
                    "total_tokens", prompt_tokens + completion_tokens
                )

                cost = self.cost_tracker.track_cost(
                    model_name=model_name,
                    input_tokens=prompt_tokens,
                    output_tokens=completion_tokens,
                )

                # Send cost event to Kafka with full token usage structure
                self.tracer.add_custom_event(
                    "cost_tracking",
                    {
                        "event_type": "cost_tracking",
                        "model_name": model_name,
                        "token_usage": {
                            "prompt_tokens": prompt_tokens,
                            "completion_tokens": completion_tokens,
                            "total_tokens": total_tokens,
                        },
                        "cost": cost,
                        "run_id": run_id,
                    },
                )

                logger.info(
                    f"💰 Added cost data to trace for model {model_name}: ${cost:.6f}"
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
                        prompt_tokens = estimated_tokens["prompt_tokens"]
                        completion_tokens = estimated_tokens["completion_tokens"]
                        total_tokens = estimated_tokens["total_tokens"]

                        cost = self.cost_tracker.track_cost(
                            model_name=model_name,
                            input_tokens=prompt_tokens,
                            output_tokens=completion_tokens,
                        )

                        # Send estimated cost event with FULL token usage structure (same as real tokens)
                        self.tracer.add_custom_event(
                            "cost_tracking",
                            {
                                "event_type": "cost_tracking",
                                "model_name": model_name,
                                "token_usage": {
                                    "prompt_tokens": prompt_tokens,
                                    "completion_tokens": completion_tokens,
                                    "total_tokens": total_tokens,
                                },
                                "cost": cost,
                                "run_id": run_id,
                                "estimated": True,  # Mark as estimated
                            },
                        )

                        logger.info(
                            f"💰 Added ESTIMATED cost data to trace for model {model_name}: ${cost:.6f} "
                            f"(prompt: {prompt_tokens}, completion: {completion_tokens} tokens)"
                        )
                    else:
                        logger.warning(
                            f"❌ Could not estimate token usage for model {model_name}"
                        )

                except Exception as e:
                    logger.error(f"Error estimating token usage: {e}")
                    logger.warning(
                        f"❌ No token usage found for model {model_name}. Response type: {type(response)}, has llm_output: {hasattr(response, 'llm_output')}, has generations: {hasattr(response, 'generations')}"
                    )

        except Exception as e:
            logger.error(f"Error in on_llm_end: {e}")
            import traceback

            logger.error(traceback.format_exc())

        finally:
            # Clean up run info
            if run_id in self.llm_runs:
                del self.llm_runs[run_id]

    def _extract_actual_model_name(self, response) -> str:
        """Extract the actual model name from response metadata."""
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
                        # Anthropic format
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

    def on_llm_error(self, error: Exception, **kwargs) -> None:
        """Handle LLM errors."""
        run_id = str(kwargs.get("run_id", ""))
        if run_id in self.llm_runs:
            del self.llm_runs[run_id]
