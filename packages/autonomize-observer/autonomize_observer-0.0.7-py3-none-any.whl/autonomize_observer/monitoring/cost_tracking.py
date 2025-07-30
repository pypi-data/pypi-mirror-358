"""
This module provides cost tracking functionality for LLM API usage.
It includes utilities for tracking, calculating and logging costs across
different model providers like OpenAI, Anthropic, Mistral etc.
"""

import json
import os
from typing import Any, Dict, List, Optional

import threading
import time

from autonomize_observer.utils import setup_logger

logger = setup_logger(__name__)

# Default cost rates per 1000 tokens (USD) as of June 2025.
# Prices are based on official provider documentation and latest API pricing.
# Updated with comprehensive model coverage including OpenAI, Anthropic, Google, Meta, Mistral, and other providers.
DEFAULT_COST_RATES = {
    # OpenAI Pricing (Updated June 2025)
    # GPT-4o series
    "gpt-4o": {
        "input": 0.001,
        "output": 0.004,
        "provider": "OpenAI",
    },  # Updated Aug 2024 pricing
    "gpt-4o-2024-11-20": {"input": 0.001, "output": 0.004, "provider": "OpenAI"},
    "gpt-4o-2024-08-06": {"input": 0.001, "output": 0.004, "provider": "OpenAI"},
    "gpt-4o-2024-05-13": {"input": 0.0025, "output": 0.005, "provider": "OpenAI"},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006, "provider": "OpenAI"},
    "gpt-4o-mini-2024-07-18": {
        "input": 0.00015,
        "output": 0.0006,
        "provider": "OpenAI",
    },
    "chatgpt-4o-latest": {"input": 0.001, "output": 0.004, "provider": "OpenAI"},
    # GPT-4.1 series (December 2024)
    "gpt-4.1": {"input": 0.002, "output": 0.008, "provider": "OpenAI"},
    "gpt-4.1-mini": {"input": 0.0004, "output": 0.0016, "provider": "OpenAI"},
    "gpt-4.1-nano": {"input": 0.0001, "output": 0.0004, "provider": "OpenAI"},
    # GPT-4 series
    "gpt-4-turbo": {"input": 0.01, "output": 0.03, "provider": "OpenAI"},
    "gpt-4-turbo-2024-04-09": {"input": 0.01, "output": 0.03, "provider": "OpenAI"},
    "gpt-4": {"input": 0.03, "output": 0.06, "provider": "OpenAI"},
    "gpt-4-32k": {"input": 0.06, "output": 0.12, "provider": "OpenAI"},
    "gpt-4-0125-preview": {"input": 0.01, "output": 0.03, "provider": "OpenAI"},
    "gpt-4-1106-preview": {"input": 0.01, "output": 0.03, "provider": "OpenAI"},
    "gpt-4-vision-preview": {"input": 0.01, "output": 0.03, "provider": "OpenAI"},
    # o-series reasoning models
    "o1": {"input": 0.015, "output": 0.06, "provider": "OpenAI"},
    "o1-preview": {"input": 0.015, "output": 0.06, "provider": "OpenAI"},
    "o1-preview-2024-09-12": {"input": 0.015, "output": 0.06, "provider": "OpenAI"},
    "o1-mini": {"input": 0.003, "output": 0.012, "provider": "OpenAI"},
    "o1-mini-2024-09-12": {"input": 0.003, "output": 0.012, "provider": "OpenAI"},
    "o3": {"input": 0.001, "output": 0.004, "provider": "OpenAI"},  # Latest o3 pricing
    "o3-mini": {"input": 0.0005, "output": 0.0015, "provider": "OpenAI"},
    "o4-mini": {"input": 0.0006, "output": 0.0024, "provider": "OpenAI"},
    # GPT-3.5 series
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015, "provider": "OpenAI"},
    "gpt-3.5-turbo-0125": {"input": 0.0005, "output": 0.0015, "provider": "OpenAI"},
    "gpt-3.5-turbo-instruct": {"input": 0.0015, "output": 0.002, "provider": "OpenAI"},
    "gpt-3.5-turbo-1106": {"input": 0.001, "output": 0.002, "provider": "OpenAI"},
    "gpt-3.5-turbo-0613": {"input": 0.0015, "output": 0.002, "provider": "OpenAI"},
    "gpt-3.5-turbo-16k-0613": {"input": 0.003, "output": 0.004, "provider": "OpenAI"},
    "gpt-3.5-turbo-0301": {"input": 0.0015, "output": 0.002, "provider": "OpenAI"},
    # Legacy models
    "davinci-002": {"input": 0.02, "output": 0.02, "provider": "OpenAI"},
    "babbage-002": {"input": 0.0004, "output": 0.0004, "provider": "OpenAI"},
    "text-davinci-003": {"input": 0.02, "output": 0.02, "provider": "OpenAI"},
    "ft:gpt-3.5-turbo": {"input": 0.003, "output": 0.006, "provider": "OpenAI"},
    # OpenAI Audio/Speech models
    "whisper": {"input": 0.1, "output": 0, "provider": "OpenAI"},
    "tts-1-hd": {"input": 0.03, "output": 0, "provider": "OpenAI"},
    "tts-1": {"input": 0.015, "output": 0, "provider": "OpenAI"},
    # Anthropic Pricing (Updated June 2025)
    # Claude 4 series
    "claude-4-opus": {"input": 0.015, "output": 0.075, "provider": "Anthropic"},
    "claude-4-sonnet": {"input": 0.003, "output": 0.015, "provider": "Anthropic"},
    "claude-opus-4": {"input": 0.015, "output": 0.075, "provider": "Anthropic"},
    "claude-sonnet-4": {"input": 0.003, "output": 0.015, "provider": "Anthropic"},
    # Claude 3.7 series
    "claude-3.7-sonnet": {"input": 0.003, "output": 0.015, "provider": "Anthropic"},
    "claude-3-7-sonnet": {"input": 0.003, "output": 0.015, "provider": "Anthropic"},
    "claude-3-7-sonnet-20250219": {
        "input": 0.003,
        "output": 0.015,
        "provider": "Anthropic",
    },
    # Claude 3.5 series
    "claude-3.5-sonnet": {"input": 0.003, "output": 0.015, "provider": "Anthropic"},
    "claude-3-5-sonnet": {"input": 0.003, "output": 0.015, "provider": "Anthropic"},
    "claude-3.5-sonnet-20241022": {
        "input": 0.003,
        "output": 0.015,
        "provider": "Anthropic",
    },
    "claude-3.5-sonnet-20240620": {
        "input": 0.003,
        "output": 0.015,
        "provider": "Anthropic",
    },
    "claude-3.5-haiku": {
        "input": 0.0008,
        "output": 0.004,
        "provider": "Anthropic",
    },  # Updated pricing
    "claude-3-5-haiku": {"input": 0.0008, "output": 0.004, "provider": "Anthropic"},
    "claude-3.5-haiku-20241022": {
        "input": 0.0008,
        "output": 0.004,
        "provider": "Anthropic",
    },
    "claude-3.5-haiku-latest": {
        "input": 0.0008,
        "output": 0.004,
        "provider": "Anthropic",
    },
    # Claude 3 series
    "claude-3-opus": {"input": 0.015, "output": 0.075, "provider": "Anthropic"},
    "claude-3-opus-20240229": {
        "input": 0.015,
        "output": 0.075,
        "provider": "Anthropic",
    },
    "claude-3-sonnet": {"input": 0.003, "output": 0.015, "provider": "Anthropic"},
    "claude-3-sonnet-20240229": {
        "input": 0.003,
        "output": 0.015,
        "provider": "Anthropic",
    },
    "claude-3-haiku": {"input": 0.00025, "output": 0.00125, "provider": "Anthropic"},
    "claude-3-haiku-20240307": {
        "input": 0.00025,
        "output": 0.00125,
        "provider": "Anthropic",
    },
    # Claude 2 series
    "claude-2.1": {"input": 0.008, "output": 0.024, "provider": "Anthropic"},
    "claude-2.0": {"input": 0.008, "output": 0.024, "provider": "Anthropic"},
    "claude-2": {"input": 0.008, "output": 0.024, "provider": "Anthropic"},
    "claude-instant-1.2": {"input": 0.0008, "output": 0.0024, "provider": "Anthropic"},
    "claude-instant-1": {"input": 0.0008, "output": 0.0024, "provider": "Anthropic"},
    # Google Gemini Models (Updated June 2025)
    # Gemini 2.5 series
    "gemini-2.5-pro": {
        "input": 0.00125,
        "output": 0.01,
        "provider": "Google",
    },  # <=200k tokens
    "gemini-2.5-pro-long": {
        "input": 0.0025,
        "output": 0.015,
        "provider": "Google",
    },  # >200k tokens
    "gemini-2.5-flash": {"input": 0.0003, "output": 0.0025, "provider": "Google"},
    "gemini-2.5-flash-lite": {"input": 0.0001, "output": 0.0004, "provider": "Google"},
    # Gemini 2.0 series
    "gemini-2.0-pro": {"input": 0.00125, "output": 0.005, "provider": "Google"},
    "gemini-2.0-flash": {"input": 0.00015, "output": 0.0006, "provider": "Google"},
    "gemini-2.0-flash-lite": {
        "input": 0.000075,
        "output": 0.0003,
        "provider": "Google",
    },
    # Gemini 1.5 series
    "gemini-1.5-pro": {
        "input": 0.00125,
        "output": 0.005,
        "provider": "Google",
    },  # <=128k tokens
    "gemini-1.5-pro-long": {
        "input": 0.0025,
        "output": 0.01,
        "provider": "Google",
    },  # >128k tokens
    "gemini-1.5-pro-latest": {"input": 0.00125, "output": 0.005, "provider": "Google"},
    "gemini-1.5-flash": {
        "input": 0.000075,
        "output": 0.0003,
        "provider": "Google",
    },  # <=128k tokens
    "gemini-1.5-flash-long": {
        "input": 0.00015,
        "output": 0.0006,
        "provider": "Google",
    },  # >128k tokens
    "gemini-1.5-flash-8b": {
        "input": 0.0000375,
        "output": 0.00015,
        "provider": "Google",
    },
    # Gemini 1.0 series
    "gemini-1.0-pro": {"input": 0.0005, "output": 0.0015, "provider": "Google"},
    "gemini-1.0-pro-001": {"input": 0.0005, "output": 0.0015, "provider": "Google"},
    "gemini-pro": {"input": 0.0005, "output": 0.0015, "provider": "Google"},
    # Meta Llama Models (Updated June 2025)
    "llama-3.3-70b": {"input": 0.00035, "output": 0.0004, "provider": "Meta"},
    "llama-3.2-90b": {"input": 0.0003, "output": 0.0003, "provider": "Meta"},
    "llama-3.2-11b": {"input": 0.00006, "output": 0.00006, "provider": "Meta"},
    "llama-3.2-3b": {"input": 0.00006, "output": 0.00006, "provider": "Meta"},
    "llama-3.2-1b": {"input": 0.00004, "output": 0.00004, "provider": "Meta"},
    "llama-3.1-405b": {"input": 0.00095, "output": 0.00095, "provider": "Meta"},
    "llama-3.1-70b": {"input": 0.00035, "output": 0.0004, "provider": "Meta"},
    "llama-3.1-8b": {"input": 0.00006, "output": 0.00006, "provider": "Meta"},
    "llama-3-70b": {"input": 0.00035, "output": 0.0004, "provider": "Meta"},
    "llama-3-8b": {"input": 0.00006, "output": 0.00006, "provider": "Meta"},
    "llama-2-70b": {"input": 0.00035, "output": 0.0004, "provider": "Meta"},
    "llama-2-13b": {"input": 0.0001, "output": 0.0001, "provider": "Meta"},
    "llama-2-7b": {"input": 0.00006, "output": 0.00006, "provider": "Meta"},
    "llama-4-scout": {"input": 0.00025, "output": 0.00025, "provider": "Meta"},
    "llama-4-maverick": {"input": 0.0005, "output": 0.0005, "provider": "Meta"},
    "llama-4-behemoth": {"input": 0.001, "output": 0.001, "provider": "Meta"},
    # Mistral Models (Updated June 2025)
    "mistral-large": {"input": 0.002, "output": 0.006, "provider": "Mistral"},
    "mistral-large-2": {"input": 0.002, "output": 0.006, "provider": "Mistral"},
    "mistral-medium": {"input": 0.0014, "output": 0.0042, "provider": "Mistral"},
    "mistral-small": {"input": 0.0001, "output": 0.0003, "provider": "Mistral"},
    "mistral-8x7b": {"input": 0.00045, "output": 0.00045, "provider": "Mistral"},
    "mixtral-8x7b": {"input": 0.00045, "output": 0.00045, "provider": "Mistral"},
    "mixtral-8x22b": {"input": 0.00065, "output": 0.00065, "provider": "Mistral"},
    "mistral-7b": {"input": 0.00006, "output": 0.00006, "provider": "Mistral"},
    "codestral-latest": {"input": 0.0002, "output": 0.0006, "provider": "Mistral"},
    "codestral": {"input": 0.0002, "output": 0.0006, "provider": "Mistral"},
    "mistral-nemo": {"input": 0.00013, "output": 0.00013, "provider": "Mistral"},
    "pixtral": {"input": 0.0001, "output": 0.0003, "provider": "Mistral"},
    # Amazon Nova Models (December 2024)
    "amazon-nova-pro": {"input": 0.0008, "output": 0.0032, "provider": "Amazon"},
    "amazon-nova-lite": {"input": 0.00006, "output": 0.00024, "provider": "Amazon"},
    "amazon-nova-micro": {"input": 0.000035, "output": 0.00014, "provider": "Amazon"},
    # Cohere Models
    "command-r-plus": {"input": 0.0025, "output": 0.01, "provider": "Cohere"},
    "command-r": {"input": 0.00015, "output": 0.0006, "provider": "Cohere"},
    "command": {"input": 0.0005, "output": 0.0015, "provider": "Cohere"},
    "command-light": {"input": 0.00015, "output": 0.0006, "provider": "Cohere"},
    # DeepSeek Models
    "deepseek-r1": {"input": 0.00055, "output": 0.00216, "provider": "DeepSeek"},
    "deepseek-v3": {"input": 0.00027, "output": 0.00108, "provider": "DeepSeek"},
    "deepseek-v2": {"input": 0.00014, "output": 0.00028, "provider": "DeepSeek"},
    "deepseek-chat": {"input": 0.00014, "output": 0.00028, "provider": "DeepSeek"},
    "deepseek-coder": {"input": 0.00014, "output": 0.00028, "provider": "DeepSeek"},
    # xAI Grok Models
    "grok-2": {"input": 0.001, "output": 0.01, "provider": "xAI"},
    "grok-3": {"input": 0.0015, "output": 0.015, "provider": "xAI"},
    "grok-3-mini": {"input": 0.0005, "output": 0.005, "provider": "xAI"},
    "grok-3-fast": {"input": 0.00075, "output": 0.0075, "provider": "xAI"},
    # Qwen Models (Alibaba)
    "qwen-2.5-72b": {"input": 0.0003, "output": 0.0004, "provider": "Alibaba"},
    "qwen-2.5-32b": {"input": 0.00018, "output": 0.00018, "provider": "Alibaba"},
    "qwen-2.5-14b": {"input": 0.0001, "output": 0.0001, "provider": "Alibaba"},
    "qwen-2.5-7b": {"input": 0.00006, "output": 0.00006, "provider": "Alibaba"},
    "qwen-2-72b": {"input": 0.00035, "output": 0.00045, "provider": "Alibaba"},
    "qwen-2-57b": {"input": 0.00029, "output": 0.00029, "provider": "Alibaba"},
    "qwen-2-7b": {"input": 0.00007, "output": 0.00007, "provider": "Alibaba"},
    "qwen-3-235b": {"input": 0.0005, "output": 0.0005, "provider": "Alibaba"},
    # Perplexity Models
    "llama-3.1-sonar-small": {
        "input": 0.0002,
        "output": 0.0002,
        "provider": "Perplexity",
    },
    "llama-3.1-sonar-large": {
        "input": 0.001,
        "output": 0.001,
        "provider": "Perplexity",
    },
    "llama-3.1-sonar-huge": {"input": 0.005, "output": 0.005, "provider": "Perplexity"},
    "sonar-deep-research": {"input": 0.005, "output": 0.005, "provider": "Perplexity"},
    "sonar-reasoning": {"input": 0.001, "output": 0.001, "provider": "Perplexity"},
    "sonar-reasoning-pro": {"input": 0.003, "output": 0.003, "provider": "Perplexity"},
    # Nvidia Models
    "llama-3.1-nemotron-70b": {
        "input": 0.00035,
        "output": 0.00045,
        "provider": "Nvidia",
    },
    # Additional generic fallbacks
    "anthropic-default": {"input": 0.008, "output": 0.024, "provider": "Anthropic"},
    "openai-default": {"input": 0.002, "output": 0.002, "provider": "OpenAI"},
    "google-default": {"input": 0.001, "output": 0.002, "provider": "Google"},
}


class CostTracker:
    """A class for tracking and managing costs associated with LLM API usage.

    This class provides functionality to:
    - Track costs for individual model inference requests
    - Support custom cost rates for different models
    - Load cost rates from environment variables or custom files
    - Calculate cost summaries across models and providers
    - Track cost metrics for comprehensive monitoring
    - Handle various model providers (OpenAI, Anthropic, Mistral, etc.)

    The costs are calculated based on input and output tokens using predefined
    or custom rates per 1000 tokens.
    """

    def __init__(
        self,
        cost_rates: Optional[Dict[str, Dict[str, float]]] = None,
        custom_rates_path: Optional[str] = None,
    ):
        self.tracked_costs: List[Dict[str, Any]] = []
        self._lock = threading.Lock()

        # Use the correct DEFAULT_COST_RATES (not the wrong default_cost_rates)
        self.cost_rates = DEFAULT_COST_RATES.copy()

        # Override with custom rates if provided
        if cost_rates:
            self.cost_rates.update(cost_rates)

        # Try to load rates from file if it exists
        self._load_rates_from_file()

    def _load_rates_from_file(self):
        """Load cost rates from a JSON file if it exists."""
        rates_file = os.getenv("COST_RATES_FILE", "cost_rates.json")
        if os.path.exists(rates_file):
            try:
                with open(rates_file, "r") as f:
                    file_rates = json.load(f)
                    # Ensure each rate has a provider
                    for model, rates in file_rates.items():
                        if "provider" not in rates:
                            rates["provider"] = self._guess_provider(model)
                    self.cost_rates.update(file_rates)
                logger.info(f"Loaded cost rates from {rates_file}")
            except Exception as e:
                logger.warning(f"Failed to load cost rates from {rates_file}: {e}")

    def _guess_provider(self, model_name: str) -> str:
        """Guess the provider based on model name."""
        model_lower = model_name.lower()
        if any(
            name in model_lower
            for name in [
                "gpt",
                "openai",
                "o1",
                "o3",
                "o4",
                "davinci",
                "babbage",
                "whisper",
                "tts",
            ]
        ):
            return "OpenAI"
        elif any(name in model_lower for name in ["claude", "anthropic"]):
            return "Anthropic"
        elif any(name in model_lower for name in ["gemini", "google", "palm", "bard"]):
            return "Google"
        elif any(name in model_lower for name in ["llama", "meta"]):
            return "Meta"
        elif any(
            name in model_lower
            for name in ["mistral", "mixtral", "codestral", "pixtral"]
        ):
            return "Mistral"
        elif any(name in model_lower for name in ["nova", "amazon", "bedrock"]):
            return "Amazon"
        elif any(name in model_lower for name in ["deepseek"]):
            return "DeepSeek"
        elif any(name in model_lower for name in ["command", "cohere"]):
            return "Cohere"
        elif any(name in model_lower for name in ["grok", "xai"]):
            return "xAI"
        elif any(name in model_lower for name in ["qwen", "alibaba"]):
            return "Alibaba"
        elif any(name in model_lower for name in ["perplexity", "sonar"]):
            return "Perplexity"
        elif any(name in model_lower for name in ["nemotron", "nvidia"]):
            return "Nvidia"
        else:
            return "unknown"

    def clean_model_name(self, model_name: str) -> str:
        """Clean and normalize model name."""
        if not model_name:
            return "unknown"

        # Remove common prefixes and normalize
        cleaned = model_name.lower().strip()

        # Handle Azure OpenAI naming
        if cleaned.startswith("azure/"):
            cleaned = cleaned[6:]
        if cleaned.startswith("azure-"):
            cleaned = cleaned[6:]
        if cleaned.startswith("bedrock/"):
            cleaned = cleaned[8:]

        # Handle deployment names that might contain the actual model
        # OpenAI models
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
        elif "o4" in cleaned:
            if "mini" in cleaned:
                return "o4-mini"
            return "o4"
        elif "o3" in cleaned:
            if "mini" in cleaned:
                return "o3-mini"
            return "o3"
        elif "o1" in cleaned:
            if "mini" in cleaned:
                return "o1-mini"
            elif "preview" in cleaned:
                return "o1-preview"
            return "o1"

        # Anthropic models
        elif "claude" in cleaned:
            if "4" in cleaned or "opus-4" in cleaned or "sonnet-4" in cleaned:
                if "opus" in cleaned:
                    return "claude-4-opus"
                elif "sonnet" in cleaned:
                    return "claude-4-sonnet"
                return "claude-4-opus"
            elif "3.7" in cleaned or "3-7" in cleaned:
                return "claude-3.7-sonnet"
            elif "3.5" in cleaned or "3-5" in cleaned:
                if "haiku" in cleaned:
                    return "claude-3.5-haiku"
                return "claude-3.5-sonnet"
            elif "opus" in cleaned:
                return "claude-3-opus"
            elif "sonnet" in cleaned:
                return "claude-3-sonnet"
            elif "haiku" in cleaned:
                return "claude-3-haiku"
            elif "instant" in cleaned:
                return "claude-instant-1.2"
            elif "2" in cleaned:
                return "claude-2.1"
            return "claude-3-sonnet"  # Default Claude

        # Google models
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
            return "gemini-1.0-pro"

        # Meta Llama models
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
                elif "sonar" in cleaned:
                    if "small" in cleaned:
                        return "llama-3.1-sonar-small"
                    elif "large" in cleaned:
                        return "llama-3.1-sonar-large"
                    elif "huge" in cleaned:
                        return "llama-3.1-sonar-huge"
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

        # Mistral models
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
        elif "codestral" in cleaned:
            return "codestral"
        elif "pixtral" in cleaned:
            return "pixtral"

        # Other providers
        elif "deepseek" in cleaned:
            if "r1" in cleaned:
                return "deepseek-r1"
            elif "v3" in cleaned:
                return "deepseek-v3"
            elif "v2" in cleaned:
                return "deepseek-v2"
            elif "coder" in cleaned:
                return "deepseek-coder"
            return "deepseek-chat"
        elif "nova" in cleaned:
            if "pro" in cleaned:
                return "amazon-nova-pro"
            elif "lite" in cleaned:
                return "amazon-nova-lite"
            elif "micro" in cleaned:
                return "amazon-nova-micro"
        elif "command" in cleaned:
            if "r-plus" in cleaned or "r+" in cleaned:
                return "command-r-plus"
            elif "r" in cleaned:
                return "command-r"
            elif "light" in cleaned:
                return "command-light"
            return "command"
        elif "grok" in cleaned:
            if "3" in cleaned:
                if "mini" in cleaned:
                    return "grok-3-mini"
                elif "fast" in cleaned:
                    return "grok-3-fast"
                return "grok-3"
            elif "2" in cleaned:
                return "grok-2"
        elif "qwen" in cleaned:
            if "3" in cleaned:
                return "qwen-3-235b"
            elif "2.5" in cleaned:
                if "72b" in cleaned:
                    return "qwen-2.5-72b"
                elif "32b" in cleaned:
                    return "qwen-2.5-32b"
                elif "14b" in cleaned:
                    return "qwen-2.5-14b"
                elif "7b" in cleaned:
                    return "qwen-2.5-7b"
            elif "2" in cleaned:
                if "72b" in cleaned:
                    return "qwen-2-72b"
                elif "57b" in cleaned:
                    return "qwen-2-57b"
                elif "7b" in cleaned:
                    return "qwen-2-7b"
        elif "sonar" in cleaned:
            if "deep" in cleaned:
                return "sonar-deep-research"
            elif "reasoning" in cleaned:
                if "pro" in cleaned:
                    return "sonar-reasoning-pro"
                return "sonar-reasoning"
        elif "nemotron" in cleaned:
            return "llama-3.1-nemotron-70b"

        return model_name

    def track_cost(
        self,
        model_name: str,
        input_tokens: int,
        output_tokens: int,
        run_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> float:
        """Track cost for a single LLM call."""
        model_name = self.clean_model_name(model_name)

        # Get cost rates for this model
        rates = self.get_model_rates(model_name)

        # Calculate costs
        input_cost = (input_tokens / 1000.0) * rates["input"]
        output_cost = (output_tokens / 1000.0) * rates["output"]
        total_cost = input_cost + output_cost
        total_tokens = input_tokens + output_tokens

        # Create cost data record
        cost_data = {
            "timestamp": time.time(),
            "model": model_name,
            "provider": rates["provider"],
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
            "run_id": run_id,
            "metadata": metadata or {},
        }

        # Thread-safe append
        with self._lock:
            self.tracked_costs.append(cost_data)

        return total_cost

    def track_cost_detailed(
        self,
        model_name: str,
        input_tokens: int,
        output_tokens: int,
        run_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Track cost for a single LLM call and return detailed breakdown."""
        model_name = self.clean_model_name(model_name)

        # Get cost rates for this model
        rates = self.get_model_rates(model_name)

        # Calculate costs
        input_cost = (input_tokens / 1000.0) * rates["input"]
        output_cost = (output_tokens / 1000.0) * rates["output"]
        total_cost = input_cost + output_cost
        total_tokens = input_tokens + output_tokens

        # Create cost data record
        cost_data = {
            "timestamp": time.time(),
            "model": model_name,
            "provider": rates["provider"],
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
            "run_id": run_id,
            "metadata": metadata or {},
        }

        # Thread-safe append
        with self._lock:
            self.tracked_costs.append(cost_data)

        return cost_data

    def get_model_rates(self, model_name: str) -> Dict[str, float]:
        """Get cost rates for a model, with fallback handling."""
        model_name = self.clean_model_name(model_name)

        # Direct match
        if model_name in self.cost_rates:
            rates = self.cost_rates[model_name].copy()
            logger.debug(f"✅ Found exact cost rates for model: {model_name}")
            return rates

        # Prefix match - check if any known model is a prefix of this model
        for rate_model, rates in self.cost_rates.items():
            if model_name.startswith(rate_model):
                rates = rates.copy()
                logger.debug(f"✅ Found prefix match for {model_name} -> {rate_model}")
                return rates

        # Enhanced model matching for common variants
        model_lower = model_name.lower()

        # OpenAI models
        if "gpt-4.1" in model_lower:
            if "nano" in model_lower:
                rates = DEFAULT_COST_RATES.get(
                    "gpt-4.1-nano", {"input": 0.0001, "output": 0.0004}
                ).copy()
            elif "mini" in model_lower:
                rates = DEFAULT_COST_RATES.get(
                    "gpt-4.1-mini", {"input": 0.0004, "output": 0.0016}
                ).copy()
            else:
                rates = DEFAULT_COST_RATES.get(
                    "gpt-4.1", {"input": 0.002, "output": 0.008}
                ).copy()
            logger.info(f"🔄 Using GPT-4.1 rates for variant: {model_name}")
        elif "gpt-4o" in model_lower:
            rates = DEFAULT_COST_RATES.get(
                "gpt-4o", {"input": 0.001, "output": 0.004}
            ).copy()
            logger.info(f"🔄 Using gpt-4o rates for variant: {model_name}")
        elif "gpt-4" in model_lower:
            rates = DEFAULT_COST_RATES.get(
                "gpt-4", {"input": 0.03, "output": 0.06}
            ).copy()
            logger.info(f"🔄 Using gpt-4 rates for variant: {model_name}")
        elif "gpt-3.5" in model_lower or "gpt-35" in model_lower:
            rates = DEFAULT_COST_RATES.get(
                "gpt-3.5-turbo", {"input": 0.0005, "output": 0.0015}
            ).copy()
            logger.info(f"🔄 Using gpt-3.5-turbo rates for variant: {model_name}")
        elif any(o_model in model_lower for o_model in ["o4", "o3", "o1"]):
            if "o4" in model_lower:
                rates = DEFAULT_COST_RATES.get(
                    "o4-mini", {"input": 0.0006, "output": 0.0024}
                ).copy()
            elif "o3" in model_lower:
                if "mini" in model_lower:
                    rates = DEFAULT_COST_RATES.get(
                        "o3-mini", {"input": 0.0005, "output": 0.0015}
                    ).copy()
                else:
                    rates = DEFAULT_COST_RATES.get(
                        "o3", {"input": 0.001, "output": 0.004}
                    ).copy()
            elif "mini" in model_lower:
                rates = DEFAULT_COST_RATES.get(
                    "o1-mini", {"input": 0.003, "output": 0.012}
                ).copy()
            else:
                rates = DEFAULT_COST_RATES.get(
                    "o1", {"input": 0.015, "output": 0.06}
                ).copy()
            logger.info(f"🔄 Using o-series rates for variant: {model_name}")

        # Anthropic models
        elif "claude" in model_lower:
            if "4" in model_lower:
                if "opus" in model_lower:
                    rates = DEFAULT_COST_RATES.get(
                        "claude-4-opus", {"input": 0.015, "output": 0.075}
                    ).copy()
                else:
                    rates = DEFAULT_COST_RATES.get(
                        "claude-4-sonnet", {"input": 0.003, "output": 0.015}
                    ).copy()
                logger.info(f"🔄 Using Claude 4 rates for variant: {model_name}")
            elif "3.7" in model_lower or "3-7" in model_lower:
                rates = DEFAULT_COST_RATES.get(
                    "claude-3.7-sonnet", {"input": 0.003, "output": 0.015}
                ).copy()
                logger.info(f"🔄 Using Claude 3.7 rates for variant: {model_name}")
            elif "haiku" in model_lower and (
                "3.5" in model_lower or "3-5" in model_lower
            ):
                rates = DEFAULT_COST_RATES.get(
                    "claude-3.5-haiku", {"input": 0.0008, "output": 0.004}
                ).copy()
                logger.info(
                    f"🔄 Using claude-3.5-haiku rates for variant: {model_name}"
                )
            elif "3.5" in model_lower or "3-5" in model_lower:
                rates = DEFAULT_COST_RATES.get(
                    "claude-3.5-sonnet", {"input": 0.003, "output": 0.015}
                ).copy()
                logger.info(
                    f"🔄 Using claude-3.5-sonnet rates for variant: {model_name}"
                )
            else:
                rates = DEFAULT_COST_RATES.get(
                    "claude-3-sonnet", {"input": 0.003, "output": 0.015}
                ).copy()
                logger.info(f"🔄 Using claude-3-sonnet rates for variant: {model_name}")

        # Google models
        elif "gemini" in model_lower:
            if "2.5" in model_lower:
                if "flash" in model_lower:
                    if "lite" in model_lower:
                        rates = DEFAULT_COST_RATES.get(
                            "gemini-2.5-flash-lite", {"input": 0.0001, "output": 0.0004}
                        ).copy()
                    else:
                        rates = DEFAULT_COST_RATES.get(
                            "gemini-2.5-flash", {"input": 0.0003, "output": 0.0025}
                        ).copy()
                else:
                    rates = DEFAULT_COST_RATES.get(
                        "gemini-2.5-pro", {"input": 0.00125, "output": 0.01}
                    ).copy()
                logger.info(f"🔄 Using Gemini 2.5 rates for variant: {model_name}")
            elif "2.0" in model_lower or "2-0" in model_lower:
                if "flash" in model_lower:
                    if "lite" in model_lower:
                        rates = DEFAULT_COST_RATES.get(
                            "gemini-2.0-flash-lite",
                            {"input": 0.000075, "output": 0.0003},
                        ).copy()
                    else:
                        rates = DEFAULT_COST_RATES.get(
                            "gemini-2.0-flash", {"input": 0.00015, "output": 0.0006}
                        ).copy()
                else:
                    rates = DEFAULT_COST_RATES.get(
                        "gemini-2.0-pro", {"input": 0.00125, "output": 0.005}
                    ).copy()
                logger.info(f"🔄 Using Gemini 2.0 rates for variant: {model_name}")
            elif "1.5" in model_lower:
                if "flash" in model_lower:
                    rates = DEFAULT_COST_RATES.get(
                        "gemini-1.5-flash", {"input": 0.000075, "output": 0.0003}
                    ).copy()
                else:
                    rates = DEFAULT_COST_RATES.get(
                        "gemini-1.5-pro", {"input": 0.00125, "output": 0.005}
                    ).copy()
                logger.info(f"🔄 Using Gemini 1.5 rates for variant: {model_name}")
            else:
                rates = DEFAULT_COST_RATES.get(
                    "gemini-1.0-pro", {"input": 0.0005, "output": 0.0015}
                ).copy()
                logger.info(f"🔄 Using gemini-1.0-pro rates for variant: {model_name}")

        # Meta Llama models
        elif "llama" in model_lower:
            if "4" in model_lower:
                rates = DEFAULT_COST_RATES.get(
                    "llama-4-maverick", {"input": 0.0005, "output": 0.0005}
                ).copy()
            elif "3.3" in model_lower:
                rates = DEFAULT_COST_RATES.get(
                    "llama-3.3-70b", {"input": 0.00035, "output": 0.0004}
                ).copy()
            elif "3.2" in model_lower:
                rates = DEFAULT_COST_RATES.get(
                    "llama-3.2-11b", {"input": 0.00006, "output": 0.00006}
                ).copy()
            elif "3.1" in model_lower:
                if "405b" in model_lower:
                    rates = DEFAULT_COST_RATES.get(
                        "llama-3.1-405b", {"input": 0.00095, "output": 0.00095}
                    ).copy()
                else:
                    rates = DEFAULT_COST_RATES.get(
                        "llama-3.1-70b", {"input": 0.00035, "output": 0.0004}
                    ).copy()
            elif "3" in model_lower:
                rates = DEFAULT_COST_RATES.get(
                    "llama-3-70b", {"input": 0.00035, "output": 0.0004}
                ).copy()
            else:
                rates = DEFAULT_COST_RATES.get(
                    "llama-2-70b", {"input": 0.00035, "output": 0.0004}
                ).copy()
            logger.info(f"🔄 Using Llama rates for variant: {model_name}")

        # Mistral models
        elif "mistral" in model_lower or "mixtral" in model_lower:
            if "large" in model_lower:
                rates = DEFAULT_COST_RATES.get(
                    "mistral-large", {"input": 0.002, "output": 0.006}
                ).copy()
            elif "8x22b" in model_lower:
                rates = DEFAULT_COST_RATES.get(
                    "mixtral-8x22b", {"input": 0.00065, "output": 0.00065}
                ).copy()
            elif "8x7b" in model_lower:
                rates = DEFAULT_COST_RATES.get(
                    "mixtral-8x7b", {"input": 0.00045, "output": 0.00045}
                ).copy()
            else:
                rates = DEFAULT_COST_RATES.get(
                    "mistral-small", {"input": 0.0001, "output": 0.0003}
                ).copy()
            logger.info(f"🔄 Using Mistral rates for variant: {model_name}")

        # Other providers
        elif "deepseek" in model_lower:
            if "r1" in model_lower:
                rates = DEFAULT_COST_RATES.get(
                    "deepseek-r1", {"input": 0.00055, "output": 0.00216}
                ).copy()
            else:
                rates = DEFAULT_COST_RATES.get(
                    "deepseek-v3", {"input": 0.00027, "output": 0.00108}
                ).copy()
            logger.info(f"🔄 Using DeepSeek rates for variant: {model_name}")
        elif "nova" in model_lower:
            rates = DEFAULT_COST_RATES.get(
                "amazon-nova-lite", {"input": 0.00006, "output": 0.00024}
            ).copy()
            logger.info(f"🔄 Using Amazon Nova rates for variant: {model_name}")
        elif "command" in model_lower:
            rates = DEFAULT_COST_RATES.get(
                "command-r", {"input": 0.00015, "output": 0.0006}
            ).copy()
            logger.info(f"🔄 Using Cohere rates for variant: {model_name}")
        elif "grok" in model_lower:
            rates = DEFAULT_COST_RATES.get(
                "grok-2", {"input": 0.001, "output": 0.01}
            ).copy()
            logger.info(f"🔄 Using Grok rates for variant: {model_name}")
        elif "qwen" in model_lower:
            rates = DEFAULT_COST_RATES.get(
                "qwen-2.5-72b", {"input": 0.0003, "output": 0.0004}
            ).copy()
            logger.info(f"🔄 Using Qwen rates for variant: {model_name}")

        # Provider-based fallbacks
        else:
            provider = self._guess_provider(model_name)
            if provider == "OpenAI":
                rates = DEFAULT_COST_RATES.get(
                    "openai-default", {"input": 0.002, "output": 0.002}
                ).copy()
            elif provider == "Anthropic":
                rates = DEFAULT_COST_RATES.get(
                    "anthropic-default", {"input": 0.008, "output": 0.024}
                ).copy()
            elif provider == "Google":
                rates = DEFAULT_COST_RATES.get(
                    "google-default", {"input": 0.001, "output": 0.002}
                ).copy()
            else:
                # Final fallback to gpt-3.5-turbo (cheapest reasonable option)
                rates = DEFAULT_COST_RATES.get(
                    "gpt-3.5-turbo", {"input": 0.0005, "output": 0.0015}
                ).copy()
            logger.warning(
                f"❌ No cost rates found for model {model_name}, using {provider} fallback"
            )

        # Ensure provider is set
        if "provider" not in rates:
            rates["provider"] = self._guess_provider(model_name)

        return rates

    def get_cost_summary(self) -> Dict[str, Any]:
        """Get a summary of all tracked costs."""
        if not self.tracked_costs:
            return {
                "total_calls": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "by_model": {},
                "by_provider": {},
            }

        total_calls = len(self.tracked_costs)
        total_tokens = sum(cost["total_tokens"] for cost in self.tracked_costs)
        total_cost = sum(cost["total_cost"] for cost in self.tracked_costs)

        # Group by model
        by_model = {}
        for cost in self.tracked_costs:
            model = cost["model"]
            if model not in by_model:
                by_model[model] = {
                    "calls": 0,
                    "tokens": 0,
                    "cost": 0.0,
                }
            by_model[model]["calls"] += 1
            by_model[model]["tokens"] += cost["total_tokens"]
            by_model[model]["cost"] += cost["total_cost"]

        # Group by provider
        by_provider = {}
        for cost in self.tracked_costs:
            provider = cost.get("provider", "unknown")
            if provider not in by_provider:
                by_provider[provider] = {
                    "calls": 0,
                    "tokens": 0,
                    "cost": 0.0,
                }
            by_provider[provider]["calls"] += 1
            by_provider[provider]["tokens"] += cost["total_tokens"]
            by_provider[provider]["cost"] += cost["total_cost"]

        return {
            "total_calls": total_calls,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "by_model": by_model,
            "by_provider": by_provider,
            "cost_per_token": total_cost / total_tokens if total_tokens > 0 else 0.0,
        }

    def reset(self):
        """Reset tracked costs."""
        with self._lock:
            self.tracked_costs.clear()
