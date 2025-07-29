"""
Metrics converter for autonomize_observer.

Extracts and converts metrics data from traces for analytics.
"""

from dataclasses import dataclass
from typing import Any, Dict, List
from ..kafka.schemas import CompleteTrace, LLMCallEvent
from .base_converter import BaseConverter


@dataclass
class MetricsData:
    """Extracted metrics data."""

    total_cost: float
    total_tokens: int
    total_input_tokens: int
    total_output_tokens: int
    models_used: List[str]
    providers_used: List[str]
    cost_per_token: float
    duration_ms: float
    call_count: int


class MetricsConverter(BaseConverter):
    """Converter for extracting metrics data."""

    def convert_complete_trace(self, complete_trace: CompleteTrace) -> MetricsData:
        """Extract metrics from CompleteTrace."""

        # Extract metrics from metadata
        metrics = (
            complete_trace.metadata.get("metrics", {})
            if complete_trace.metadata
            else {}
        )

        total_cost = metrics.get("total_cost", 0.0)
        total_tokens = metrics.get("total_tokens", 0)

        return MetricsData(
            total_cost=total_cost,
            total_tokens=total_tokens,
            total_input_tokens=metrics.get("total_input_tokens", 0),
            total_output_tokens=metrics.get("total_output_tokens", 0),
            models_used=self._extract_models_from_trace(complete_trace),
            providers_used=self._extract_providers_from_trace(complete_trace),
            cost_per_token=total_cost / total_tokens if total_tokens > 0 else 0.0,
            duration_ms=complete_trace.duration_ms or 0.0,
            call_count=1,
        )

    def convert_llm_call_event(self, llm_event: LLMCallEvent) -> MetricsData:
        """Extract metrics from LLMCallEvent."""

        usage = llm_event.usage or {}
        total_tokens = usage.get("total_tokens", 0)
        total_cost = llm_event.cost or 0.0

        return MetricsData(
            total_cost=total_cost,
            total_tokens=total_tokens,
            total_input_tokens=usage.get("prompt_tokens", 0),
            total_output_tokens=usage.get("completion_tokens", 0),
            models_used=[llm_event.model] if llm_event.model else [],
            providers_used=[llm_event.provider] if llm_event.provider else [],
            cost_per_token=total_cost / total_tokens if total_tokens > 0 else 0.0,
            duration_ms=llm_event.duration_ms or 0.0,
            call_count=1,
        )

    def _extract_models_from_trace(self, complete_trace: CompleteTrace) -> List[str]:
        """Extract unique models from trace."""
        models = set()

        if complete_trace.metadata and "custom_events" in complete_trace.metadata:
            for event in complete_trace.metadata["custom_events"]:
                if event.get("event_type") == "cost_tracking":
                    model_name = event.get("data", {}).get("model_name")
                    if model_name:
                        models.add(model_name)

        return list(models)

    def _extract_providers_from_trace(self, complete_trace: CompleteTrace) -> List[str]:
        """Extract unique providers from trace."""
        providers = set()

        for model in self._extract_models_from_trace(complete_trace):
            provider = self._guess_provider_from_model(model)
            if provider != "unknown":
                providers.add(provider)

        return list(providers)
