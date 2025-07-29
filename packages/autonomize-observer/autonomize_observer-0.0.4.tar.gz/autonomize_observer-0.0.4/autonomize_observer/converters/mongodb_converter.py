"""
MongoDB converter for autonomize_observer.

Converts SDK schemas to MongoDB-compatible data structures for observability storage.
"""

import hashlib
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
from ..kafka.schemas import CompleteTrace, LLMCallEvent, SpanInfo
from .base_converter import BaseConverter


@dataclass
class ObservabilityTrace:
    """MongoDB-compatible trace structure."""

    trace_id: str
    flow_id: str
    trace_name: str
    execution_type: str
    user_id: Optional[str]
    session_id: Optional[str]
    project: str
    started_at: datetime
    completed_at: Optional[datetime]
    duration_ms: Optional[float]
    trace_inputs: Optional[Dict[str, Any]]
    trace_outputs: Optional[Dict[str, Any]]
    total_cost: float
    total_tokens: int
    total_input_tokens: int
    total_output_tokens: int
    total_observations: int
    models_used: List[str]
    providers_used: List[str]
    status: str
    error_message: Optional[str]
    metadata: Dict[str, Any]


@dataclass
class ObservabilityObservation:
    """MongoDB-compatible observation structure."""

    observation_id: str
    trace_id: str
    observation_type: str
    name: str
    operation_name: str
    user_id: Optional[str]
    session_id: Optional[str]
    project: str
    started_at: datetime
    completed_at: Optional[datetime]
    duration_ms: Optional[float]
    parent_observation_id: Optional[str]
    status: str
    input_data: Optional[Dict[str, Any]]
    output_data: Optional[Dict[str, Any]]
    metadata: Dict[str, Any]
    model_name: Optional[str]
    provider: Optional[str]
    model_parameters: Dict[str, Any]
    input_tokens: int
    output_tokens: int
    total_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float
    error_message: Optional[str]


@dataclass
class ObservabilityModelUsage:
    """MongoDB-compatible model usage structure."""

    call_id: str
    session_id: Optional[str]
    user_id: Optional[str]
    project: str
    usage_context: str
    model_name: str
    provider: str
    started_at: datetime
    completed_at: Optional[datetime]
    duration_ms: Optional[float]
    messages: List[Dict[str, Any]]
    parameters: Dict[str, Any]
    response: Dict[str, Any]
    input_tokens: int
    output_tokens: int
    total_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float
    success: bool
    error_message: Optional[str]
    metadata: Dict[str, Any]


class MongoDBConverter(BaseConverter):
    """Converter for MongoDB observability storage."""

    def convert_complete_trace(
        self, complete_trace: CompleteTrace
    ) -> ObservabilityTrace:
        """Convert CompleteTrace to MongoDB-compatible format (without observations)."""

        # Generate unique trace_id for this execution
        # Keep flow_id as provided by the tracing service
        unique_trace_id = self._generate_unique_trace_id()

        # Extract models and providers from metadata
        models_used, providers_used = self._extract_models_and_providers(complete_trace)

        # Extract metrics from metadata
        metrics = (
            complete_trace.metadata.get("metrics", {})
            if complete_trace.metadata
            else {}
        )

        # Determine status (lowercase for API compatibility)
        status = "failed" if complete_trace.error else "success"

        return ObservabilityTrace(
            trace_id=unique_trace_id,  # Generate unique trace_id per execution
            flow_id=complete_trace.flow_id,  # Keep flow_id from tracing service
            trace_name=complete_trace.flow_name,
            execution_type="agent_flow",
            user_id=complete_trace.user_id,
            session_id=complete_trace.session_id,
            project=complete_trace.project_name,
            started_at=datetime.fromtimestamp(complete_trace.start_time),
            completed_at=(
                datetime.fromtimestamp(complete_trace.end_time)
                if complete_trace.end_time
                else None
            ),
            duration_ms=complete_trace.duration_ms,
            trace_inputs=complete_trace.flow_inputs,
            trace_outputs=complete_trace.flow_outputs,
            total_cost=metrics.get("total_cost", 0.0),
            total_tokens=metrics.get("total_tokens", 0),
            total_input_tokens=metrics.get("total_input_tokens", 0),
            total_output_tokens=metrics.get("total_output_tokens", 0),
            total_observations=complete_trace.total_components,
            models_used=models_used,
            providers_used=providers_used,
            status=status,
            error_message=complete_trace.error,
            metadata=complete_trace.metadata or {},
        )

    def convert_trace_observations(
        self, complete_trace: CompleteTrace, trace_id: str
    ) -> List[ObservabilityObservation]:
        """Convert spans to observations for separate storage."""

        observations = []
        for span_info in complete_trace.spans:
            observation = self._convert_span_to_observation(
                span_info, complete_trace, trace_id
            )
            observations.append(observation)

        return observations

    def _generate_unique_trace_id(self) -> str:
        """
        Generate a unique trace_id for each execution.

        This ensures each execution gets a unique identifier while
        keeping the flow_id stable (provided by the tracing service).
        """
        return str(uuid.uuid4())

    def _generate_stable_flow_id(self, complete_trace: CompleteTrace) -> str:
        """
        DEPRECATED: This method is no longer used.

        The flow_id should come from the tracing service, not be generated here.
        Keeping this method for backward compatibility but it's not called.
        """
        # Build flow signature from stable characteristics
        flow_signature_parts = [
            complete_trace.flow_name or "unknown_flow",
            complete_trace.project_name or "unknown_project",
        ]

        # Add component signatures for flow definition stability
        component_signatures = []
        for span in complete_trace.spans:
            # Use component type + name (not instance IDs which change)
            component_sig = f"{span.component_name}-{span.component_id.split('-')[0]}"
            if component_sig not in component_signatures:
                component_signatures.append(component_sig)

        # Sort for consistency
        component_signatures.sort()
        flow_signature_parts.extend(component_signatures)

        # Create stable hash
        flow_signature = "|".join(flow_signature_parts)
        flow_hash = hashlib.md5(flow_signature.encode()).hexdigest()[:8]

        # Create readable flow_id
        flow_name_clean = (complete_trace.flow_name or "flow").replace(" ", "_").lower()
        stable_flow_id = f"{flow_name_clean}_{flow_hash}"

        return stable_flow_id

    def convert_llm_call_event(
        self, llm_event: LLMCallEvent
    ) -> ObservabilityModelUsage:
        """Convert LLMCallEvent to MongoDB-compatible format."""

        # Extract usage info
        usage = llm_event.usage or {}
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", input_tokens + output_tokens)

        total_cost = llm_event.cost or 0.0

        return ObservabilityModelUsage(
            call_id=llm_event.call_id,
            session_id=llm_event.session_id,
            user_id=llm_event.user_id,
            project="GenesisStudio",
            usage_context="standalone",
            model_name=llm_event.model or "unknown",
            provider=llm_event.provider
            or self._guess_provider_from_model(llm_event.model),
            started_at=datetime.fromisoformat(
                llm_event.timestamp.replace("Z", "+00:00")
            ),
            completed_at=datetime.fromisoformat(
                llm_event.timestamp.replace("Z", "+00:00")
            ),
            duration_ms=llm_event.duration_ms or 0,
            messages=llm_event.messages or [],
            parameters=llm_event.params or {},
            response={"content": llm_event.response} if llm_event.response else {},
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            input_cost=total_cost * 0.4 if total_cost > 0 else 0.0,
            output_cost=total_cost * 0.6 if total_cost > 0 else 0.0,
            total_cost=total_cost,
            success=not bool(llm_event.error),
            error_message=llm_event.error,
            metadata=llm_event.metadata or {},
        )

    def _convert_span_to_observation(
        self, span_info: SpanInfo, complete_trace: CompleteTrace, trace_id: str
    ) -> ObservabilityObservation:
        """Convert SpanInfo to ObservabilityObservation."""

        # Determine observation type (lowercase for API compatibility)
        observation_type = "span"  # Default to span

        # Extract cost and usage from span metadata (original approach)
        span_metadata = span_info.metadata or {}
        cost = 0.0
        usage = {}
        model_name = None
        provider = None

        if "cost" in span_metadata:
            cost = float(span_metadata["cost"])
        if "usage" in span_metadata:
            usage = span_metadata["usage"]

        # NEW: Extract cost and model data from trace-level metadata for LLM components
        if self._is_llm_component(span_info.component_name):
            cost, usage, model_name, provider = self._extract_llm_data_for_component(
                span_info, complete_trace
            )
            # Set observation type to GENERATION for LLM components
            observation_type = "generation"

        # Extract tokens
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", input_tokens + output_tokens)

        # Determine status (lowercase for API compatibility)
        status = "failed" if span_info.error else "success"

        return ObservabilityObservation(
            observation_id=span_info.span_id,
            trace_id=trace_id,
            observation_type=observation_type,
            name=span_info.component_name,
            operation_name=span_info.component_id,
            user_id=complete_trace.user_id,
            session_id=complete_trace.session_id,
            project=complete_trace.project_name,
            started_at=datetime.fromtimestamp(span_info.start_time),
            completed_at=(
                datetime.fromtimestamp(span_info.end_time)
                if span_info.end_time
                else None
            ),
            duration_ms=span_info.duration_ms,
            parent_observation_id=span_info.parent_span_id,  # ✅ Now uses actual parent relationships
            status=status,
            input_data=span_info.input_data,
            output_data=span_info.output_data,
            metadata=span_metadata,
            model_name=model_name or span_metadata.get("model"),
            provider=provider or span_metadata.get("provider"),
            model_parameters=span_metadata.get("model_parameters", {}),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            input_cost=cost * 0.4 if cost > 0 else 0.0,
            output_cost=cost * 0.6 if cost > 0 else 0.0,
            total_cost=cost,
            error_message=span_info.error,
        )

    def _extract_models_and_providers(
        self, complete_trace: CompleteTrace
    ) -> tuple[List[str], List[str]]:
        """Extract unique models and providers from trace metadata."""
        models_used = []
        providers_used = []

        if complete_trace.metadata and "custom_events" in complete_trace.metadata:
            for event in complete_trace.metadata["custom_events"]:
                if event.get("event_type") == "cost_tracking":
                    event_data = event.get("data", {})
                    model_name = event_data.get("model_name")
                    if model_name and model_name not in models_used:
                        models_used.append(model_name)

                    # Guess provider from model name
                    provider = self._guess_provider_from_model(model_name)
                    if provider and provider not in providers_used:
                        providers_used.append(provider)

        return models_used, providers_used

    def _is_llm_component(self, component_name: str) -> bool:
        """Check if a component is an LLM-related component."""
        if not component_name:
            return False

        component_lower = component_name.lower()

        # Specific LLM model indicators (more precise)
        llm_model_indicators = [
            "openai",
            "gpt",
            "azure",
            "anthropic",
            "claude",
            "llm",
            "completion",
            "generate",
            "agent",
        ]

        # Exclude input/output components that might contain "chat" or "ai"
        excluded_patterns = [
            "input",
            "output",
            "display",
            "text",
            "prompt",
        ]

        # Check if it's excluded first
        if any(pattern in component_lower for pattern in excluded_patterns):
            # Only allow if it has very specific LLM indicators
            specific_llm_patterns = [
                "openaimodel",
                "gptmodel",
                "azureopenaimodel",
                "anthropicmodel",
            ]
            return any(
                pattern in component_lower.replace(" ", "")
                for pattern in specific_llm_patterns
            )

        # Check for LLM indicators
        return any(indicator in component_lower for indicator in llm_model_indicators)

    def _extract_llm_data_from_trace(
        self, complete_trace: CompleteTrace
    ) -> tuple[float, dict, str, str]:
        """Extract LLM cost and usage data from trace-level metadata."""
        cost = 0.0
        usage = {}
        model_name = None
        provider = None

        if not complete_trace.metadata:
            return cost, usage, model_name, provider

        # Extract from metrics
        metrics = complete_trace.metadata.get("metrics", {})
        if metrics:
            cost = metrics.get("total_cost", 0.0)
            usage = {
                "prompt_tokens": metrics.get("total_input_tokens", 0),
                "completion_tokens": metrics.get("total_output_tokens", 0),
                "total_tokens": metrics.get("total_tokens", 0),
            }

        # Extract model information from custom events
        custom_events = complete_trace.metadata.get("custom_events", [])
        for event in custom_events:
            if event.get("event_type") == "cost_tracking":
                event_data = event.get("data", {})
                model_name = event_data.get("model_name")
                if model_name:
                    provider = self._guess_provider_from_model(model_name)
                break

        # Also check params for model info
        params = complete_trace.metadata.get("params", {})
        if not model_name and "models_used" in params:
            model_name = params["models_used"]
            provider = self._guess_provider_from_model(model_name)

        return cost, usage, model_name, provider

    def _extract_llm_data_for_component(
        self, span_info: SpanInfo, complete_trace: CompleteTrace
    ) -> tuple[float, dict, str, str]:
        """Extract LLM cost and usage data for a specific component.

        Maps cost events to components using component type and provider hints.
        """
        cost = 0.0
        usage = {}
        model_name = None
        provider = None

        if not complete_trace.metadata:
            return cost, usage, model_name, provider

        # Get all cost tracking events
        custom_events = complete_trace.metadata.get("custom_events", [])
        cost_events = [
            event
            for event in custom_events
            if event.get("event_type") == "cost_tracking"
        ]

        if not cost_events:
            return cost, usage, model_name, provider

        # Determine component type
        component_name_lower = span_info.component_name.lower()

        # Match cost events to components based on component type
        matched_event = None

        # Strategy 1: Match by component provider
        if "azure" in component_name_lower:
            # Azure components use Azure OpenAI models (typically gpt-4o-2024-11-20)
            for event in cost_events:
                event_data = event.get("data", {})
                event_model = event_data.get("model_name", "")
                if "2024-11-20" in event_model or "azure" in event_model.lower():
                    matched_event = event_data
                    break
        elif "agent" in component_name_lower:
            # Agent components use regular OpenAI models (typically gpt-4o-2024-08-06)
            for event in cost_events:
                event_data = event.get("data", {})
                event_model = event_data.get("model_name", "")
                if "2024-08-06" in event_model and "azure" not in event_model.lower():
                    matched_event = event_data
                    break

        # Strategy 2: Match by timing (closest to component start time)
        if not matched_event:
            span_start = span_info.start_time
            best_match = None
            best_time_diff = float("inf")

            for event in cost_events:
                event_data = event.get("data", {})
                event_timestamp = event.get("timestamp")

                if not event_timestamp:
                    continue

                try:
                    from datetime import datetime

                    event_time = datetime.fromisoformat(
                        event_timestamp.replace("Z", "+00:00")
                    ).timestamp()
                    time_diff = abs(event_time - span_start)

                    if time_diff < best_time_diff:
                        best_time_diff = time_diff
                        best_match = event_data
                except:
                    continue

            matched_event = best_match

        # Strategy 3: Fall back to first available event
        if not matched_event and cost_events:
            matched_event = cost_events[0].get("data", {})

        # Extract data from matched event
        if matched_event:
            model_name = matched_event.get("model_name")
            token_usage = matched_event.get("token_usage", {})
            cost = matched_event.get("cost", 0.0)

            usage = {
                "prompt_tokens": token_usage.get("prompt_tokens", 0),
                "completion_tokens": token_usage.get("completion_tokens", 0),
                "total_tokens": token_usage.get("total_tokens", 0),
            }

            if model_name:
                provider = self._guess_provider_from_model(model_name)

        return cost, usage, model_name, provider
