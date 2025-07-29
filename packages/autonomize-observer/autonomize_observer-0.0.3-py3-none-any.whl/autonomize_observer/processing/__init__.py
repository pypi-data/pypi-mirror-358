"""
Processing module for autonomize_observer.

Provides generic message processing capabilities for observability data.
"""

from .base_processor import BaseProcessor
from .observability_processor import ObservabilityProcessor

__all__ = [
    "BaseProcessor",
    "ObservabilityProcessor",
]
