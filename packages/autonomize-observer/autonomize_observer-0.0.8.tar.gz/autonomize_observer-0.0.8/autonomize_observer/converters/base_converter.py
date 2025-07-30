"""
Base converter interface for autonomize_observer.

Defines the abstract interface for converting between different data formats.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union
from ..kafka.schemas import CompleteTrace, LLMCallEvent


class BaseConverter(ABC):
    """Abstract base class for data converters."""

    @abstractmethod
    def convert_complete_trace(self, complete_trace: CompleteTrace) -> Any:
        """
        Convert a CompleteTrace to the target format.

        Args:
            complete_trace: The CompleteTrace object to convert

        Returns:
            Converted data in target format
        """
        raise NotImplementedError

    @abstractmethod
    def convert_llm_call_event(self, llm_event: LLMCallEvent) -> Any:
        """
        Convert an LLMCallEvent to the target format.

        Args:
            llm_event: The LLMCallEvent object to convert

        Returns:
            Converted data in target format
        """
        raise NotImplementedError

    def convert_message(self, message_data: Dict[str, Any]) -> Any:
        """
        Convert a raw message dictionary to the target format.

        Args:
            message_data: Raw message data from Kafka

        Returns:
            Converted data in target format
        """
        # Determine message type and route to appropriate converter
        if self._is_complete_trace_format(message_data):
            # Handle spans conversion from dicts to SpanInfo objects
            message_copy = message_data.copy()
            if "spans" in message_copy and isinstance(message_copy["spans"], list):
                from ..kafka.schemas import SpanInfo

                message_copy["spans"] = [
                    SpanInfo(**span) if isinstance(span, dict) else span
                    for span in message_copy["spans"]
                ]

            complete_trace = CompleteTrace(**message_copy)
            return self.convert_complete_trace(complete_trace)
        elif self._is_llm_call_event(message_data):
            llm_event = LLMCallEvent.from_dict(message_data)
            return self.convert_llm_call_event(llm_event)
        else:
            raise ValueError(f"Unknown message format: {list(message_data.keys())}")

    def _is_complete_trace_format(self, message_data: dict) -> bool:
        """Check if message is in the expected complete trace format."""
        required_fields = ["trace_id", "flow_id", "flow_name", "start_time"]
        return all(field in message_data for field in required_fields)

    def _is_llm_call_event(self, message_data: dict) -> bool:
        """Check if message is an LLM call event."""
        return (
            "call_id" in message_data
            and "event_type" in message_data
            and message_data.get("event_type")
            in ["llm_call_start", "llm_call_end", "llm_metric"]
        )

    def _guess_provider_from_model(self, model_name: str) -> str:
        """Utility method to guess provider from model name."""
        if not model_name:
            return "unknown"

        model_lower = model_name.lower()

        if "gpt" in model_lower or "davinci" in model_lower or "curie" in model_lower:
            return "openai"
        elif "claude" in model_lower:
            return "anthropic"
        elif "gemini" in model_lower or "palm" in model_lower:
            return "google"
        elif "llama" in model_lower or "codellama" in model_lower:
            return "meta"
        elif "mistral" in model_lower:
            return "mistral"
        elif "command" in model_lower:
            return "cohere"
        else:
            return "unknown"
