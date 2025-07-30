"""
Observability processor for autonomize_observer.

Generic processor that can handle observability data with pluggable storage backends.
"""

import logging
import inspect
from typing import Any, Dict, List, Optional, Callable
from .base_processor import BaseProcessor
from ..converters.base_converter import BaseConverter
from ..converters.mongodb_converter import MongoDBConverter
from ..kafka.schemas import CompleteTrace, LLMCallEvent

logger = logging.getLogger(__name__)


class ObservabilityProcessor(BaseProcessor):
    """
    Generic observability processor with pluggable storage backends.

    This processor can be configured with different converters and storage
    handlers, making it reusable across different storage systems.
    """

    def __init__(
        self,
        converters: Optional[List[BaseConverter]] = None,
        storage_handlers: Optional[List[Callable]] = None,
    ):
        """
        Initialize the observability processor.

        Args:
            converters: List of data converters
            storage_handlers: List of storage handler functions
        """
        super().__init__(converters)
        self.storage_handlers = storage_handlers or []

        # Add default MongoDB converter if none provided
        if not self.converters:
            self.converters.append(MongoDBConverter())

    async def process_message(self, message_data: Dict[str, Any]) -> bool:
        """
        Process a single observability message.

        Args:
            message_data: Raw message data from Kafka

        Returns:
            bool: True if processed successfully
        """
        try:
            # Determine message type
            if self._is_complete_trace_format(message_data):
                return await self._process_complete_trace(message_data)
            elif self._is_llm_call_event(message_data):
                return await self._process_llm_call_event(message_data)
            else:
                logger.warning(f"Unknown message format: {list(message_data.keys())}")
                return True  # Skip unknown formats

        except Exception as e:
            error_msg = f"Error processing message: {e}"
            logger.error(error_msg)
            self._update_statistics(False, error_msg)
            return False

    async def _process_complete_trace(self, message_data: Dict[str, Any]) -> bool:
        """Process a complete trace message."""
        try:
            # Parse the CompleteTrace from dictionary
            # Handle spans conversion from dicts to SpanInfo objects
            message_copy = message_data.copy()
            if "spans" in message_copy and isinstance(message_copy["spans"], list):
                from ..kafka.schemas import SpanInfo

                message_copy["spans"] = [
                    SpanInfo(**span) if isinstance(span, dict) else span
                    for span in message_copy["spans"]
                ]

            complete_trace = CompleteTrace(**message_copy)

            # Convert using all converters
            converted_data = {}
            for converter in self.converters:
                converter_name = converter.__class__.__name__
                converted_data[converter_name] = converter.convert_complete_trace(
                    complete_trace
                )

            # Store using all storage handlers
            success = True
            for handler in self.storage_handlers:
                try:
                    handler_success = await self._call_storage_handler(
                        handler, "trace", converted_data, complete_trace
                    )
                    success = success and handler_success
                except Exception as e:
                    logger.error(f"Storage handler error: {e}")
                    success = False

            self._update_statistics(success)
            return success

        except Exception as e:
            error_msg = f"Error processing complete trace: {e}"
            logger.error(error_msg)
            self._update_statistics(False, error_msg)
            return False

    async def _process_llm_call_event(self, message_data: Dict[str, Any]) -> bool:
        """Process an LLM call event."""
        try:
            # Parse the LLMCallEvent
            llm_event = LLMCallEvent.from_dict(message_data)

            # Convert using all converters
            converted_data = {}
            for converter in self.converters:
                converter_name = converter.__class__.__name__
                converted_data[converter_name] = converter.convert_llm_call_event(
                    llm_event
                )

            # Store using all storage handlers
            success = True
            for handler in self.storage_handlers:
                try:
                    handler_success = await self._call_storage_handler(
                        handler, "llm_call", converted_data, llm_event
                    )
                    success = success and handler_success
                except Exception as e:
                    logger.error(f"Storage handler error: {e}")
                    success = False

            self._update_statistics(success)
            return success

        except Exception as e:
            error_msg = f"Error processing LLM call event: {e}"
            logger.error(error_msg)
            self._update_statistics(False, error_msg)
            return False

    async def _call_storage_handler(
        self,
        handler: Callable,
        data_type: str,
        converted_data: Dict[str, Any],
        original_data: Any,
    ) -> bool:
        """Call a storage handler function."""
        try:
            # Check if handler is callable
            if not callable(handler):
                logger.error(f"Invalid storage handler: {handler}")
                return False

            # Check if handler is async or sync
            if inspect.iscoroutinefunction(handler):
                # Async handler
                result = await handler(data_type, converted_data, original_data)
            else:
                # Sync handler
                result = handler(data_type, converted_data, original_data)

            # Ensure we return a boolean
            return bool(result)

        except Exception as e:
            logger.error(f"Storage handler execution error: {e}")
            return False

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

    def add_storage_handler(self, handler: Callable):
        """Add a storage handler function."""
        self.storage_handlers.append(handler)
