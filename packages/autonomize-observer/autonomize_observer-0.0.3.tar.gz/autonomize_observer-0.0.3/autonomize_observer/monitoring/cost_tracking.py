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

# Default cost rates per 1000 tokens (USD) as of December 2024.
# Prices are based on official provider documentation and Langfuse model registry.
# Updated with comprehensive model coverage including OpenAI, Anthropic, and Google models.
DEFAULT_COST_RATES = {
    # OpenAI Pricing (Updated December 2024)
    "gpt-4o": {"input": 0.0025, "output": 0.005, "provider": "OpenAI"},
    "gpt-4o-2024-11-20": {"input": 0.0025, "output": 0.005, "provider": "OpenAI"},
    "gpt-4o-2024-08-06": {"input": 0.0025, "output": 0.005, "provider": "OpenAI"},
    "gpt-4o-2024-05-13": {"input": 0.0025, "output": 0.005, "provider": "OpenAI"},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006, "provider": "OpenAI"},
    "gpt-4o-mini-2024-07-18": {
        "input": 0.00015,
        "output": 0.0006,
        "provider": "OpenAI",
    },
    "chatgpt-4o-latest": {"input": 0.0025, "output": 0.005, "provider": "OpenAI"},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03, "provider": "OpenAI"},
    "gpt-4-turbo-2024-04-09": {"input": 0.01, "output": 0.03, "provider": "OpenAI"},
    "gpt-4": {"input": 0.03, "output": 0.06, "provider": "OpenAI"},
    "gpt-4-32k": {"input": 0.06, "output": 0.12, "provider": "OpenAI"},
    "gpt-4-0125-preview": {"input": 0.01, "output": 0.03, "provider": "OpenAI"},
    "gpt-4-1106-preview": {"input": 0.01, "output": 0.03, "provider": "OpenAI"},
    "gpt-4-vision-preview": {"input": 0.01, "output": 0.03, "provider": "OpenAI"},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015, "provider": "OpenAI"},
    "gpt-3.5-turbo-0125": {"input": 0.0005, "output": 0.0015, "provider": "OpenAI"},
    "gpt-3.5-turbo-instruct": {"input": 0.0015, "output": 0.002, "provider": "OpenAI"},
    "gpt-3.5-turbo-1106": {"input": 0.001, "output": 0.002, "provider": "OpenAI"},
    "gpt-3.5-turbo-0613": {"input": 0.0015, "output": 0.002, "provider": "OpenAI"},
    "gpt-3.5-turbo-16k-0613": {"input": 0.003, "output": 0.004, "provider": "OpenAI"},
    "gpt-3.5-turbo-0301": {"input": 0.0015, "output": 0.002, "provider": "OpenAI"},
    "davinci-002": {"input": 0.02, "output": 0.02, "provider": "OpenAI"},
    "babbage-002": {"input": 0.0004, "output": 0.0004, "provider": "OpenAI"},
    "o3-mini": {"input": 0.0005, "output": 0.0015, "provider": "OpenAI"},
    "o1-preview": {"input": 0.015, "output": 0.06, "provider": "OpenAI"},
    "o1-preview-2024-09-12": {"input": 0.015, "output": 0.06, "provider": "OpenAI"},
    "o1": {"input": 0.015, "output": 0.06, "provider": "OpenAI"},
    "o1-mini": {"input": 0.003, "output": 0.012, "provider": "OpenAI"},
    "o1-mini-2024-09-12": {"input": 0.003, "output": 0.012, "provider": "OpenAI"},
    "ft:gpt-3.5-turbo": {"input": 0.003, "output": 0.006, "provider": "OpenAI"},
    "text-davinci-003": {"input": 0.02, "output": 0.02, "provider": "OpenAI"},
    "whisper": {"input": 0.1, "output": 0, "provider": "OpenAI"},
    "tts-1-hd": {"input": 0.03, "output": 0, "provider": "OpenAI"},
    "tts-1": {"input": 0.015, "output": 0, "provider": "OpenAI"},
    # Anthropic Pricing
    "claude-3-5-sonnet-20240620": {
        "input": 0.003,
        "output": 0.015,
        "provider": "Anthropic",
    },
    "claude-3-7-sonnet-20250219": {
        "input": 0.003,
        "output": 0.015,
        "provider": "Anthropic",
    },
    "claude-3-opus-20240229": {
        "input": 0.015,
        "output": 0.075,
        "provider": "Anthropic",
    },
    "claude-3-sonnet-20240229": {
        "input": 0.003,
        "output": 0.075,
        "provider": "Anthropic",
    },
    "claude-3-haiku-20240307": {
        "input": 0.00025,
        "output": 0.00125,
        "provider": "Anthropic",
    },
    "claude-2.1": {"input": 0.008, "output": 0.024, "provider": "Anthropic"},
    "claude-2.0": {"input": 0.008, "output": 0.024, "provider": "Anthropic"},
    "claude-instant-1.2": {"input": 0.0008, "output": 0.0024, "provider": "Anthropic"},
    "anthropic-default": {"input": 0.008, "output": 0.024, "provider": "Anthropic"},
    "claude-instant-1": {"input": 0.0008, "output": 0.0024, "provider": "Anthropic"},
    "claude-instant-v1": {"input": 0.0008, "output": 0.0024, "provider": "Anthropic"},
    "claude-1": {"input": 0.008, "output": 0.024, "provider": "Anthropic"},
    "claude-v1": {"input": 0.008, "output": 0.024, "provider": "Anthropic"},
    "claude-v2": {"input": 0.008, "output": 0.024, "provider": "Anthropic"},
    "claude-3-opus": {"input": 0.015, "output": 0.075, "provider": "Anthropic"},
    "claude-3-sonnet": {"input": 0.003, "output": 0.075, "provider": "Anthropic"},
    "claude-3-haiku": {"input": 0.00025, "output": 0.00125, "provider": "Anthropic"},
    "claude-3-5-sonnet": {"input": 0.003, "output": 0.015, "provider": "Anthropic"},
    "claude-3-5-haiku-20241022": {
        "input": 0.001,
        "output": 0.005,
        "provider": "Anthropic",
    },
    "claude-3-5-haiku-latest": {
        "input": 0.001,
        "output": 0.005,
        "provider": "Anthropic",
    },
    # Google Gemini Models (pricing converted from per-character to per-1K-tokens, assuming 1 token ≈ 4 chars)
    "gemini-1.0-pro": {"input": 0.0005, "output": 0.0015, "provider": "Google"},
    "gemini-1.0-pro-001": {"input": 0.0005, "output": 0.0015, "provider": "Google"},
    "gemini-1.0-pro-latest": {"input": 0.001, "output": 0.002, "provider": "Google"},
    "gemini-pro": {"input": 0.0005, "output": 0.0015, "provider": "Google"},
    "gemini-1.5-pro": {"input": 0.01, "output": 0.03, "provider": "Google"},
    "gemini-1.5-pro-latest": {"input": 0.01, "output": 0.03, "provider": "Google"},
    "gemini-1.5-flash": {
        "input": 0.00075,
        "output": 0.0015,
        "provider": "Google",
    },  # Estimated based on typical flash pricing
}


class CostTracker:
    """A class for tracking and managing costs associated with LLM API usage.

    This class provides functionality to:
    - Track costs for individual model inference requests
    - Support custom cost rates for different models
    - Load cost rates from environment variables or custom files
    - Calculate cost summaries across models and providers
    - Log cost metrics to MLflow for experiment tracking
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
        if any(name in model_lower for name in ["gpt", "openai", "o1", "o3"]):
            return "OpenAI"
        elif any(name in model_lower for name in ["claude", "anthropic"]):
            return "Anthropic"
        elif any(name in model_lower for name in ["gemini", "google"]):
            return "Google"
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

        # Handle deployment names that might contain the actual model
        if "gpt-4" in cleaned:
            if "gpt-4o" in cleaned:
                return "gpt-4o"
            return "gpt-4"
        elif "gpt-3.5" in cleaned or "gpt-35" in cleaned:
            return "gpt-3.5-turbo"
        elif "o1" in cleaned:
            if "mini" in cleaned:
                return "o1-mini"
            return "o1-preview"
        elif "claude" in cleaned:
            if "opus" in cleaned:
                return "claude-3-opus"
            elif "sonnet" in cleaned:
                if "3.5" in cleaned or "3-5" in cleaned:
                    return "claude-3-5-sonnet"
                return "claude-3-sonnet"
            elif "haiku" in cleaned:
                if "3.5" in cleaned or "3-5" in cleaned:
                    return "claude-3-5-haiku-latest"
                return "claude-3-haiku"
            return "claude-3-sonnet"  # Default Claude
        elif "gemini" in cleaned:
            if "1.5" in cleaned:
                if "flash" in cleaned:
                    return "gemini-1.5-flash"
                return "gemini-1.5-pro"
            return "gemini-1.0-pro"

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

        # Log to MLflow immediately if we have a run_id
        if run_id:
            try:
                self._log_individual_metrics_sync(cost_data, run_id)
            except Exception as e:
                logger.warning(f"Failed to log individual metrics: {e}")

        return total_cost

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
        if "gpt-4o" in model_name.lower():
            rates = DEFAULT_COST_RATES.get(
                "gpt-4o", {"input": 0.0025, "output": 0.005}
            ).copy()
            logger.info(f"🔄 Using gpt-4o rates for variant: {model_name}")
        elif "gpt-4" in model_name.lower():
            rates = DEFAULT_COST_RATES.get(
                "gpt-4", {"input": 0.03, "output": 0.06}
            ).copy()
            logger.info(f"🔄 Using gpt-4 rates for variant: {model_name}")
        elif "gpt-3.5" in model_name.lower() or "gpt-35" in model_name.lower():
            rates = DEFAULT_COST_RATES.get(
                "gpt-3.5-turbo", {"input": 0.0005, "output": 0.0015}
            ).copy()
            logger.info(f"🔄 Using gpt-3.5-turbo rates for variant: {model_name}")
        elif "claude" in model_name.lower():
            if "haiku" in model_name.lower() and "3.5" in model_name.lower():
                rates = DEFAULT_COST_RATES.get(
                    "claude-3-5-haiku-latest", {"input": 0.001, "output": 0.005}
                ).copy()
                logger.info(
                    f"🔄 Using claude-3-5-haiku rates for variant: {model_name}"
                )
            else:
                rates = DEFAULT_COST_RATES.get(
                    "claude-3-5-sonnet", {"input": 0.003, "output": 0.015}
                ).copy()
                logger.info(
                    f"🔄 Using claude-3-5-sonnet rates for variant: {model_name}"
                )
        elif "gemini" in model_name.lower():
            if "1.5" in model_name.lower():
                if "flash" in model_name.lower():
                    rates = DEFAULT_COST_RATES.get(
                        "gemini-1.5-flash", {"input": 0.00075, "output": 0.0015}
                    ).copy()
                    logger.info(
                        f"🔄 Using gemini-1.5-flash rates for variant: {model_name}"
                    )
                else:
                    rates = DEFAULT_COST_RATES.get(
                        "gemini-1.5-pro", {"input": 0.01, "output": 0.03}
                    ).copy()
                    logger.info(
                        f"🔄 Using gemini-1.5-pro rates for variant: {model_name}"
                    )
            else:
                rates = DEFAULT_COST_RATES.get(
                    "gemini-1.0-pro", {"input": 0.0005, "output": 0.0015}
                ).copy()
                logger.info(f"🔄 Using gemini-1.0-pro rates for variant: {model_name}")
        elif "o1" in model_name.lower():
            if "mini" in model_name.lower():
                rates = DEFAULT_COST_RATES.get(
                    "o1-mini", {"input": 0.003, "output": 0.012}
                ).copy()
                logger.info(f"🔄 Using o1-mini rates for variant: {model_name}")
            else:
                rates = DEFAULT_COST_RATES.get(
                    "o1-preview", {"input": 0.015, "output": 0.06}
                ).copy()
                logger.info(f"🔄 Using o1-preview rates for variant: {model_name}")
        else:
            # Final fallback to gpt-3.5-turbo (cheapest reasonable option)
            logger.warning(
                f"❌ No cost rates found for model {model_name}, using gpt-3.5-turbo fallback"
            )
            rates = DEFAULT_COST_RATES.get(
                "gpt-3.5-turbo", {"input": 0.0005, "output": 0.0015}
            ).copy()

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

    def _log_individual_metrics_sync(self, cost_data: dict, run_id: str):
        """Log individual metrics - respects existing run context."""
        try:
            import mlflow

            # Check if there's an active run
            active_run = mlflow.active_run()
            if active_run and active_run.info.run_id == run_id:
                # Use the existing active run context
                mlflow.log_metrics(
                    {
                        "input_tokens": cost_data["input_tokens"],
                        "output_tokens": cost_data["output_tokens"],
                        "total_tokens": cost_data["total_tokens"],
                        "input_cost": cost_data["input_cost"],
                        "output_cost": cost_data["output_cost"],
                        "total_cost": cost_data["total_cost"],
                    }
                )
            else:
                # Use specific run context
                with mlflow.start_run(run_id=run_id):
                    mlflow.log_metrics(
                        {
                            "input_tokens": cost_data["input_tokens"],
                            "output_tokens": cost_data["output_tokens"],
                            "total_tokens": cost_data["total_tokens"],
                            "input_cost": cost_data["input_cost"],
                            "output_cost": cost_data["output_cost"],
                            "total_cost": cost_data["total_cost"],
                        }
                    )

                    # Don't log model/provider params to avoid conflicts in multi-model runs
                    # The tracer or monitor should handle these parameters
                    pass

        except Exception as e:
            logger.warning(f"Failed to log individual metrics for run {run_id}: {e}")

    def log_cost_summary_to_mlflow(self, run_id: Optional[str] = None):
        """Log cost summary to MLflow - disabled to prevent random runs."""
        # COMPLETELY DISABLED to prevent random MLflow runs during shutdown
        # Cost summaries should be logged by the tracer during normal operation
        logger.debug("Cost summary logging is disabled to prevent random MLflow runs")
        return

    def reset(self):
        """Reset tracked costs."""
        with self._lock:
            self.tracked_costs.clear()
