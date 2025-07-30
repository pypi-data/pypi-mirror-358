"""
MongoDB converter for autonomize_observer.

Converts SDK schemas to MongoDB-compatible data structures for observability storage.
"""

import hashlib
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
from .base_converter import BaseConverter
from ..kafka.schemas import CompleteTrace, LLMCallEvent, SpanInfo

logger = logging.getLogger(__name__)


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
            "mistral",
            "codestral",
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
                "mistralmodel",
                "codestralmodel",
            ]
            return any(
                pattern in component_lower.replace(" ", "")
                for pattern in specific_llm_patterns
            )

        # Check for LLM indicators
        return any(indicator in component_lower for indicator in llm_model_indicators)

    def _extract_llm_data_for_component(
        self, span_info: SpanInfo, complete_trace: CompleteTrace
    ) -> tuple[float, dict, str, str]:
        """Extract LLM cost and usage data for a specific component.

        Simple approach: Use cost event model names as primary source.
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

        # Find matching cost event using timing
        matched_event = self._find_cost_event_by_timing(span_info, cost_events)

        if not matched_event:
            # Backup: Try model hints
            matched_event = self._find_cost_event_by_model_hints(
                span_info, cost_events, None
            )

        if matched_event:
            event_data = matched_event.get("data", {})
            token_usage = event_data.get("token_usage", {})
            cost = event_data.get("cost", 0.0)

            usage = {
                "prompt_tokens": token_usage.get("prompt_tokens", 0),
                "completion_tokens": token_usage.get("completion_tokens", 0),
                "total_tokens": token_usage.get("total_tokens", 0),
            }

            # Use the model name from the cost event
            model_name = event_data.get("model_name")
            if model_name:
                # CRITICAL FIX: Map LangChain wrapper names to actual model names
                actual_model_name = self._resolve_actual_model_name(
                    model_name, span_info
                )
                if actual_model_name != model_name:
                    logger.info(f"🔄 Mapped {model_name} → {actual_model_name}")
                    model_name = actual_model_name

                provider = self._guess_provider_from_model(model_name)
                logger.debug(f"✅ Found model from cost event: {model_name}")

        return cost, usage, model_name, provider

    def _find_cost_event_by_timing(
        self, span_info: SpanInfo, cost_events: List[Dict]
    ) -> Optional[Dict]:
        """Find cost event that best matches component timing."""
        span_start = span_info.start_time
        span_end = span_info.end_time or span_start

        best_match = None
        best_score = float("inf")

        for event in cost_events:
            event_timestamp = event.get("timestamp")
            if not event_timestamp:
                continue

            try:
                from datetime import datetime

                event_time = datetime.fromisoformat(
                    event_timestamp.replace("Z", "+00:00")
                ).timestamp()

                # Calculate timing score (lower is better)
                if span_start <= event_time <= span_end:
                    # Event happened during component execution - perfect match
                    score = 0
                else:
                    # Event happened outside - penalize by distance
                    score = min(
                        abs(event_time - span_start), abs(event_time - span_end)
                    )

                if score < best_score:
                    best_score = score
                    best_match = event

            except Exception as e:
                logger.debug(f"Error parsing event timestamp {event_timestamp}: {e}")
                continue

        if best_match:
            logger.debug(f"🎯 Matched cost event by timing (score: {best_score:.2f})")

        return best_match

    def _find_cost_event_by_model_hints(
        self,
        span_info: SpanInfo,
        cost_events: List[Dict],
        expected_model: Optional[str],
    ) -> Optional[Dict]:
        """Find cost event using model and provider hints as backup strategy."""
        component_name_lower = span_info.component_name.lower()

        # Strategy 1: If we know the expected model, look for it
        if expected_model:
            expected_lower = expected_model.lower()
            for event in cost_events:
                event_model = event.get("data", {}).get("model_name", "").lower()
                # Check if event model contains our expected model or vice versa
                if (
                    expected_lower in event_model
                    or event_model in expected_lower
                    or self._models_are_similar(expected_model, event_model)
                ):
                    logger.debug(
                        f"🎯 Matched by expected model: {expected_model} ≈ {event_model}"
                    )
                    return event

        # Strategy 2: Match by component provider hints (less reliable, but generic)
        provider_hints = {
            "azure": ["azure", "2024-11-20"],
            "openai": ["gpt", "openai", "2024-08-06"],
            "mistral": ["mistral", "codestral"],
            "anthropic": ["claude", "anthropic"],
            "google": ["gemini", "google"],
        }

        for provider, patterns in provider_hints.items():
            if provider in component_name_lower:
                for event in cost_events:
                    event_model = event.get("data", {}).get("model_name", "").lower()
                    if any(pattern in event_model for pattern in patterns):
                        logger.debug(f"🎯 Matched by provider hint: {provider}")
                        return event

        # Strategy 3: Return first available event (last resort)
        if cost_events:
            logger.debug("🎯 Using first available cost event as fallback")
            return cost_events[0]

        return None

    def _models_are_similar(self, model1: str, model2: str) -> bool:
        """Check if two model names refer to the same underlying model."""
        if not model1 or not model2:
            return False

        m1_lower = model1.lower()
        m2_lower = model2.lower()

        # Extract base model names
        m1_base = self._extract_base_model_name(m1_lower)
        m2_base = self._extract_base_model_name(m2_lower)

        return m1_base == m2_base

    def _extract_base_model_name(self, model_name: str) -> str:
        """Extract base model name from various formats."""
        model_lower = model_name.lower()

        # GPT models
        if "gpt-4o" in model_lower:
            return "gpt-4o"
        elif "gpt-4" in model_lower:
            return "gpt-4"
        elif "gpt-3.5" in model_lower:
            return "gpt-3.5"

        # Mistral models
        elif "codestral" in model_lower:
            return "codestral"
        elif "mistral" in model_lower:
            return "mistral"

        # Claude models
        elif "claude" in model_lower:
            return "claude"

        # Return original if no pattern matches
        return model_lower

    def _guess_provider_from_model(self, model_name: str) -> str:
        """Guess provider from model name."""
        if not model_name:
            return "unknown"

        model_lower = model_name.lower()

        if "gpt" in model_lower or "openai" in model_lower:
            return "openai"
        elif "claude" in model_lower or "anthropic" in model_lower:
            return "anthropic"
        elif "gemini" in model_lower or "bard" in model_lower:
            return "google"
        elif "mistral" in model_lower or "codestral" in model_lower:
            return "mistral"
        elif "llama" in model_lower:
            return "meta"
        else:
            return "unknown"

    def _resolve_actual_model_name(
        self, cost_event_model: str, span_info: SpanInfo
    ) -> str:
        """Map LangChain wrapper class names to actual model names using component metadata."""

        # If it's already a proper model name (has version info), keep it
        if any(
            pattern in cost_event_model.lower()
            for pattern in ["2024-", "latest", "turbo", "preview", "3.5", "4o"]
        ):
            return cost_event_model

        # If it's a LangChain wrapper class, look for actual model in component metadata
        langchain_wrappers = [
            "chatmistralai",
            "chatopenai",
            "azurechatopenai",
            "chatanthropic",
            "chatgoogle",
            "chatollama",
            "mistralai",
            "openai",
            "anthropic",
        ]

        if any(wrapper in cost_event_model.lower() for wrapper in langchain_wrappers):
            # Try to find actual model name in component metadata
            component_metadata = span_info.metadata or {}

            # Check multiple locations for the real model name
            actual_model = (
                component_metadata.get("model_name")
                or component_metadata.get("model")
                or (
                    span_info.input_data.get("model_name")
                    if span_info.input_data
                    else None
                )
                or (span_info.input_data.get("model") if span_info.input_data else None)
            )

            if actual_model and actual_model != cost_event_model:
                logger.debug(
                    f"🎯 Found actual model in component metadata: {actual_model}"
                )
                return actual_model

        # Return original if no mapping found
        return cost_event_model

    async def send_observations_batch(
        self,
        trace_id: str,
        observations: List[ObservabilityObservation],
        api_base_url: str,
    ) -> bool:
        """Send observations in batch to reduce network overhead by 90%."""
        try:
            import aiohttp
            import json
            from datetime import datetime

            # Convert observations to API-compatible format
            observations_data = []
            for obs in observations:
                obs_dict = {
                    "observation_id": obs.observation_id,
                    "trace_id": obs.trace_id,
                    "observation_type": obs.observation_type,
                    "name": obs.name,
                    "operation_name": obs.operation_name,
                    "user_id": obs.user_id,
                    "session_id": obs.session_id,
                    "project": obs.project,
                    "started_at": (
                        obs.started_at.isoformat() if obs.started_at else None
                    ),
                    "completed_at": (
                        obs.completed_at.isoformat() if obs.completed_at else None
                    ),
                    "duration_ms": obs.duration_ms,
                    "parent_observation_id": obs.parent_observation_id,
                    "status": obs.status,
                    "input_data": obs.input_data,
                    "output_data": obs.output_data,
                    "metadata": obs.metadata,
                    "model_name": obs.model_name,
                    "provider": obs.provider,
                    "model_parameters": obs.model_parameters,
                    "input_tokens": obs.input_tokens,
                    "output_tokens": obs.output_tokens,
                    "total_tokens": obs.total_tokens,
                    "input_cost": obs.input_cost,
                    "output_cost": obs.output_cost,
                    "total_cost": obs.total_cost,
                    "error_message": obs.error_message,
                }
                observations_data.append(obs_dict)

            # Batch request payload
            payload = {"trace_id": trace_id, "observations": observations_data}

            url = f"{api_base_url}/modelhub/api/v1/observability/observations/batch"

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(
                            f"✅ Batch sent {result.get('created_count', 0)} observations in {result.get('processing_time_ms', 0):.2f}ms"
                        )
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(
                            f"❌ Batch observations failed: {response.status} - {error_text}"
                        )
                        return False

        except Exception as e:
            logger.error(f"❌ Error sending observations batch: {e}")
            import traceback

            traceback.print_exc()
            return False

    async def send_trace_with_metrics_batch(
        self,
        trace: ObservabilityTrace,
        observations: List[ObservabilityObservation],
        api_base_url: str,
        model_metrics: Optional[Dict] = None,
        agent_metrics: Optional[Dict] = None,
    ) -> bool:
        """Send complete trace with pre-calculated metrics and batch observations (ultimate performance)."""
        try:
            import aiohttp
            import json

            # Convert trace to API format
            trace_data = {
                "trace_id": trace.trace_id,
                "flow_id": trace.flow_id,
                "trace_name": trace.trace_name,
                "execution_type": trace.execution_type,
                "user_id": trace.user_id,
                "session_id": trace.session_id,
                "project": trace.project,
                "started_at": (
                    trace.started_at.isoformat() if trace.started_at else None
                ),
                "completed_at": (
                    trace.completed_at.isoformat() if trace.completed_at else None
                ),
                "duration_ms": trace.duration_ms,
                "trace_inputs": trace.trace_inputs,
                "trace_outputs": trace.trace_outputs,
                "total_cost": trace.total_cost,
                "total_tokens": trace.total_tokens,
                "total_input_tokens": trace.total_input_tokens,
                "total_output_tokens": trace.total_output_tokens,
                "total_observations": trace.total_observations,
                "models_used": trace.models_used,
                "providers_used": trace.providers_used,
                "status": trace.status,
                "error_message": trace.error_message,
                "metadata": trace.metadata,
            }

            # Convert observations to API format
            observations_data = []
            for obs in observations:
                obs_dict = {
                    "observation_id": obs.observation_id,
                    "trace_id": obs.trace_id,
                    "observation_type": obs.observation_type,
                    "name": obs.name,
                    "operation_name": obs.operation_name,
                    "user_id": obs.user_id,
                    "session_id": obs.session_id,
                    "project": obs.project,
                    "started_at": (
                        obs.started_at.isoformat() if obs.started_at else None
                    ),
                    "completed_at": (
                        obs.completed_at.isoformat() if obs.completed_at else None
                    ),
                    "duration_ms": obs.duration_ms,
                    "parent_observation_id": obs.parent_observation_id,
                    "status": obs.status,
                    "input_data": obs.input_data,
                    "output_data": obs.output_data,
                    "metadata": obs.metadata,
                    "model_name": obs.model_name,
                    "provider": obs.provider,
                    "model_parameters": obs.model_parameters,
                    "input_tokens": obs.input_tokens,
                    "output_tokens": obs.output_tokens,
                    "total_tokens": obs.total_tokens,
                    "input_cost": obs.input_cost,
                    "output_cost": obs.output_cost,
                    "total_cost": obs.total_cost,
                    "error_message": obs.error_message,
                }
                observations_data.append(obs_dict)

            payload = {
                **trace_data,
                "observations": observations_data,
                "model_metrics": model_metrics,
                "agent_metrics": agent_metrics,
            }

            url = f"{api_base_url}/modelhub/api/v1/observability/traces/with-metrics"

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(
                        total=60
                    ),  # Longer timeout for complete trace
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(
                            f"🚀 Complete trace sent in {result.get('processing_time_ms', 0):.2f}ms"
                        )
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(
                            f"❌ Trace with metrics failed: {response.status} - {error_text}"
                        )
                        return False

        except Exception as e:
            logger.error(f"❌ Error sending trace with metrics: {e}")
            import traceback

            traceback.print_exc()
            return False
