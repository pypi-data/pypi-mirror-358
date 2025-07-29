"""
Base processor interface for autonomize_observer.

Defines the abstract interface for processing observability messages.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from ..converters.base_converter import BaseConverter


class BaseProcessor(ABC):
    """Abstract base class for observability message processors."""

    def __init__(self, converters: Optional[List[BaseConverter]] = None):
        """
        Initialize the processor.

        Args:
            converters: List of data converters to use for processing
        """
        self.converters = converters or []
        self.statistics = {
            "messages_processed": 0,
            "messages_failed": 0,
            "last_error": None,
        }

    @abstractmethod
    async def process_message(self, message_data: Dict[str, Any]) -> bool:
        """
        Process a single message.

        Args:
            message_data: Raw message data from Kafka

        Returns:
            bool: True if processed successfully
        """
        raise NotImplementedError

    def add_converter(self, converter: BaseConverter):
        """Add a data converter to the processor."""
        self.converters.append(converter)

    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return self.statistics.copy()

    def _update_statistics(self, success: bool, error: Optional[str] = None):
        """Update processing statistics."""
        if success:
            self.statistics["messages_processed"] += 1
        else:
            self.statistics["messages_failed"] += 1
            if error:
                self.statistics["last_error"] = error
