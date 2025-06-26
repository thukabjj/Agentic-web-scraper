#!/usr/bin/env python3
"""
Token Usage Logging System

Comprehensive logging for LLM API calls including:
- Input/output token tracking
- Tokens per second calculation
- Cost tracking per provider
- Performance metrics
- Integration with existing logging infrastructure
"""

import json
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog

# Ensure structlog logs to stderr, not stdout
structlog.configure(
    processors=[
        structlog.processors.KeyValueRenderer(key_order=["event"])
    ],
    logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
)

class ProviderType(Enum):
    """Supported LLM providers"""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    OLLAMA = "ollama"
    PERPLEXITY = "perplexity"
    GOOGLE = "google"
    MISTRAL = "mistral"
    AZURE_OPENAI = "azure_openai"
    OPENROUTER = "openrouter"
    XAI = "xai"


@dataclass
class TokenUsage:
    """Token usage metrics for a single API call"""
    timestamp: str
    session_id: str
    provider: str
    model: str
    operation: str  # e.g., "scrape_url", "research", "analyze_url"
    input_tokens: int
    output_tokens: int
    total_tokens: int
    duration_seconds: float
    tokens_per_second: float
    cost_usd: float
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


@dataclass
class TokenMetrics:
    """Aggregated token metrics"""
    total_requests: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    average_tokens_per_second: float = 0.0
    total_duration_seconds: float = 0.0
    error_count: int = 0

    def update(self, usage: TokenUsage) -> None:
        """Update metrics with new usage data"""
        self.total_requests += 1
        self.total_input_tokens += usage.input_tokens
        self.total_output_tokens += usage.output_tokens
        self.total_tokens += usage.total_tokens
        self.total_cost_usd += usage.cost_usd
        self.total_duration_seconds += usage.duration_seconds

        if usage.error:
            self.error_count += 1

        # Recalculate average tokens per second
        if self.total_duration_seconds > 0:
            self.average_tokens_per_second = self.total_tokens / self.total_duration_seconds

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


class TokenLogger:
    """
    Comprehensive token usage logger with multiple output formats
    """

    # Provider cost per 1M tokens (input, output) in USD
    PROVIDER_COSTS = {
        ProviderType.ANTHROPIC: {
            "claude-3-5-sonnet-20241022": (3.00, 15.00),
            "claude-3-5-haiku-20241022": (1.00, 5.00),
            "claude-3-opus-20240229": (15.00, 75.00),
        },
        ProviderType.OPENAI: {
            "gpt-4": (30.00, 60.00),
            "gpt-4-turbo": (10.00, 30.00),
            "gpt-3.5-turbo": (0.50, 1.50),
        },
        ProviderType.PERPLEXITY: {
            "sonar-pro": (1.00, 1.00),
            "sonar-medium": (0.60, 0.60),
        },
        ProviderType.OLLAMA: {
            # Local models - no cost
            "default": (0.00, 0.00),
        },
        ProviderType.GOOGLE: {
            "gemini-pro": (0.50, 1.50),
            "gemini-pro-vision": (0.50, 1.50),
        },
        ProviderType.MISTRAL: {
            "mistral-large": (8.00, 24.00),
            "mistral-medium": (2.70, 8.10),
        }
    }

    def __init__(self, storage_path: str = "./storage/logs",
                 enable_file_logging: bool = True):
        """
        Initialize token logger

        Args:
            storage_path: Directory to store log files
            enable_file_logging: Whether to write logs to files
        """
        self.storage_path = Path(storage_path)
        self.enable_file_logging = enable_file_logging
        self.session_metrics: Dict[str, TokenMetrics] = {}
        self.global_metrics = TokenMetrics()

        # Ensure storage directory exists
        if self.enable_file_logging:
            self.storage_path.mkdir(parents=True, exist_ok=True)
            self.log_file = self.storage_path / "token_usage.jsonl"
            self.metrics_file = self.storage_path / "token_metrics.json"

        # Initialize structured logger
        self.logger = structlog.get_logger("token_logger")

        self.logger.info(
            "Token logger initialized",
            storage_path=str(self.storage_path),
            file_logging_enabled=self.enable_file_logging
        )

    def start_operation(self,
                       provider: str,
                       model: str,
                       operation: str,
                       session_id: Optional[str] = None,
                       user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Start tracking an LLM operation

        Returns a context dict to pass to end_operation
        """
        context = {
            "start_time": time.time(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "provider": provider,
            "model": model,
            "operation": operation,
            "session_id": session_id or f"session_{int(time.time())}",
            "user_id": user_id,
            "request_id": f"req_{int(time.time() * 1000)}"
        }

        self.logger.debug("Started LLM operation", **context)
        return context

    def end_operation(self,
                     context: Dict[str, Any],
                     input_tokens: int,
                     output_tokens: int,
                     error: Optional[str] = None) -> TokenUsage:
        """
        End tracking an LLM operation and log the results

        Args:
            context: Context dict from start_operation
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens generated
            error: Error message if operation failed

        Returns:
            TokenUsage object with calculated metrics
        """
        end_time = time.time()
        duration = end_time - context["start_time"]
        total_tokens = input_tokens + output_tokens

        # Calculate tokens per second
        tokens_per_second = total_tokens / duration if duration > 0 else 0

        # Calculate cost
        cost = self._calculate_cost(
            context["provider"],
            context["model"],
            input_tokens,
            output_tokens
        )

        # Create usage record
        usage = TokenUsage(
            timestamp=context["timestamp"],
            session_id=context["session_id"],
            provider=context["provider"],
            model=context["model"],
            operation=context["operation"],
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            duration_seconds=duration,
            tokens_per_second=tokens_per_second,
            cost_usd=cost,
            request_id=context.get("request_id"),
            user_id=context.get("user_id"),
            error=error
        )

        # Log the usage
        self._log_usage(usage)

        # Update metrics
        self._update_metrics(usage)

        return usage

    def _calculate_cost(self, provider: str, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost in USD for the token usage"""
        try:
            provider_enum = ProviderType(provider.lower())

            # Get provider costs
            provider_costs = self.PROVIDER_COSTS.get(provider_enum, {})

            # Find model costs (exact match first, then default)
            model_costs = provider_costs.get(model)
            if not model_costs:
                model_costs = provider_costs.get("default", (0.00, 0.00))

            input_cost_per_1m, output_cost_per_1m = model_costs

            # Calculate cost
            input_cost = (input_tokens / 1_000_000) * input_cost_per_1m
            output_cost = (output_tokens / 1_000_000) * output_cost_per_1m

            return input_cost + output_cost

        except (ValueError, KeyError) as e:
            self.logger.warning("Could not calculate cost",
                              provider=provider,
                              model=model,
                              error=str(e))
            return 0.0

    def _log_usage(self, usage: TokenUsage) -> None:
        """Log usage to structured logger and file"""
        log_data = usage.to_dict()

        # Log to structured logger
        if usage.error:
            self.logger.error("LLM operation failed", **log_data)
        else:
            self.logger.info("LLM operation completed", **log_data)

        # Log to file (JSONL format)
        if self.enable_file_logging:
            try:
                with open(self.log_file, "a") as f:
                    f.write(json.dumps(log_data) + "\n")
            except Exception as e:
                self.logger.error("Failed to write to log file", error=str(e))

    def _update_metrics(self, usage: TokenUsage) -> None:
        """Update session and global metrics"""
        # Update session metrics
        session_id = usage.session_id
        if session_id not in self.session_metrics:
            self.session_metrics[session_id] = TokenMetrics()

        self.session_metrics[session_id].update(usage)

        # Update global metrics
        self.global_metrics.update(usage)

        # Save metrics to file
        if self.enable_file_logging:
            self._save_metrics()

    def _save_metrics(self) -> None:
        """Save current metrics to file"""
        try:
            metrics_data = {
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "global_metrics": self.global_metrics.to_dict(),
                "session_metrics": {
                    session_id: metrics.to_dict()
                    for session_id, metrics in self.session_metrics.items()
                }
            }

            with open(self.metrics_file, "w") as f:
                json.dump(metrics_data, f, indent=2)

        except Exception as e:
            self.logger.error("Failed to save metrics", error=str(e))

    def get_session_metrics(self, session_id: str) -> Optional[TokenMetrics]:
        """Get metrics for a specific session"""
        return self.session_metrics.get(session_id)

    def get_global_metrics(self) -> TokenMetrics:
        """Get global metrics across all sessions"""
        return self.global_metrics

    def get_recent_usage(self, limit: int = 100) -> List[TokenUsage]:
        """Get recent usage records from log file"""
        if not self.enable_file_logging or not self.log_file.exists():
            return []

        usage_records = []
        try:
            with open(self.log_file, "r") as f:
                lines = f.readlines()

            # Get last N lines
            recent_lines = lines[-limit:] if len(lines) > limit else lines

            for line in recent_lines:
                try:
                    data = json.loads(line.strip())
                    usage_records.append(TokenUsage(**data))
                except json.JSONDecodeError:
                    continue

        except Exception as e:
            self.logger.error("Failed to read usage records", error=str(e))

        return usage_records

    def generate_report(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive usage report

        Args:
            session_id: If provided, generate report for specific session

        Returns:
            Dictionary containing usage report
        """
        if session_id:
            metrics = self.get_session_metrics(session_id)
            if not metrics:
                return {"error": f"No metrics found for session {session_id}"}

            recent_usage = [u for u in self.get_recent_usage(1000) if u.session_id == session_id]
        else:
            metrics = self.global_metrics
            recent_usage = self.get_recent_usage(100)

        # Calculate additional statistics
        provider_breakdown = {}
        operation_breakdown = {}

        for usage in recent_usage:
            # Provider breakdown
            if usage.provider not in provider_breakdown:
                provider_breakdown[usage.provider] = TokenMetrics()
            provider_breakdown[usage.provider].update(usage)

            # Operation breakdown
            if usage.operation not in operation_breakdown:
                operation_breakdown[usage.operation] = TokenMetrics()
            operation_breakdown[usage.operation].update(usage)

        return {
            "report_generated_at": datetime.now(timezone.utc).isoformat(),
            "session_id": session_id,
            "overall_metrics": metrics.to_dict(),
            "provider_breakdown": {
                provider: metrics.to_dict()
                for provider, metrics in provider_breakdown.items()
            },
            "operation_breakdown": {
                operation: metrics.to_dict()
                for operation, metrics in operation_breakdown.items()
            },
            "recent_usage_count": len(recent_usage),
            "cost_efficiency": {
                "cost_per_token": metrics.total_cost_usd / metrics.total_tokens if metrics.total_tokens > 0 else 0,
                "cost_per_request": metrics.total_cost_usd / metrics.total_requests if metrics.total_requests > 0 else 0,
                "average_request_size": metrics.total_tokens / metrics.total_requests if metrics.total_requests > 0 else 0
            }
        }


# Global token logger instance
_token_logger: Optional[TokenLogger] = None


def get_token_logger() -> TokenLogger:
    """Get or create the global token logger instance"""
    global _token_logger
    if _token_logger is None:
        _token_logger = TokenLogger()
    return _token_logger


def log_llm_usage(provider: str,
                  model: str,
                  operation: str,
                  input_tokens: int,
                  output_tokens: int,
                  duration_seconds: float,
                  session_id: Optional[str] = None,
                  user_id: Optional[str] = None,
                  error: Optional[str] = None) -> TokenUsage:
    """
    Convenience function to log LLM usage without context tracking

    Args:
        provider: LLM provider name
        model: Model identifier
        operation: Operation name (e.g., "scrape_url")
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        duration_seconds: Operation duration in seconds
        session_id: Optional session identifier
        user_id: Optional user identifier
        error: Optional error message

    Returns:
        TokenUsage object with calculated metrics
    """
    logger = get_token_logger()

    # Create mock context
    context = {
        "start_time": time.time() - duration_seconds,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "provider": provider,
        "model": model,
        "operation": operation,
        "session_id": session_id or f"session_{int(time.time())}",
        "user_id": user_id,
        "request_id": f"req_{int(time.time() * 1000)}"
    }

    return logger.end_operation(context, input_tokens, output_tokens, error)
