"""
Production best practices for context management and token optimization.

This module provides:
- Context window management with compression
- Token counting and optimization
- Structured logging with correlation
- Graceful error fallbacks
- Performance monitoring

Designed for production deployment with Claude Code's harness system.
"""

from __future__ import annotations

import logging
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Deque, Dict, List, Optional, Tuple

from bonsai_penjing.errors import safe_execute


class LogLevel(Enum):
    """Log levels for structured logging."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class LogEntry:
    """Structured log entry."""

    timestamp: datetime
    level: LogLevel
    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    exception: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "message": self.message,
            "context": self.context,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "exception": self.exception,
        }


class StructuredLogger:
    """
    Production-grade structured logger.

    Provides:
    - Correlation IDs for request tracing
    - Context-aware logging
    - Performance tracking
    - Error aggregation
    """

    def __init__(self, name: str, level: LogLevel = LogLevel.INFO) -> None:
        """Initialize the structured logger."""
        self.name = name
        self.level = level
        self._logger = logging.getLogger(name)
        self._entries: Deque[LogEntry] = deque(maxlen=10000)

    def _log(self, level: LogLevel, message: str, **context: Any) -> None:
        """Internal logging method."""
        if level.value < self.level.value:
            return

        entry = LogEntry(
            timestamp=datetime.utcnow(),
            level=level,
            message=message,
            context=context,
            trace_id=self._get_trace_id(),
            span_id=self._get_span_id(),
        )
        self._entries.append(entry)

        # Also log to standard logger
        log_func = getattr(self._logger, level.value.lower())
        log_func(message, extra={"structured": entry.to_dict()})

    def debug(self, message: str, **context: Any) -> None:
        """Log debug message."""
        self._log(LogLevel.DEBUG, message, **context)

    def info(self, message: str, **context: Any) -> None:
        """Log info message."""
        self._log(LogLevel.INFO, message, **context)

    def warning(self, message: str, **context: Any) -> None:
        """Log warning message."""
        self._log(LogLevel.WARNING, message, **context)

    def error(self, message: str, exception: Optional[Exception] = None, **context: Any) -> None:
        """Log error message."""
        entry = LogEntry(
            timestamp=datetime.utcnow(),
            level=LogLevel.ERROR,
            message=message,
            context=context,
            trace_id=self._get_trace_id(),
            span_id=self._get_span_id(),
            exception=str(exception) if exception else None,
        )
        self._entries.append(entry)
        self._logger.error(message, exc_info=exception is not None, extra={"structured": entry.to_dict()})

    def critical(self, message: str, **context: Any) -> None:
        """Log critical message."""
        self._log(LogLevel.CRITICAL, message, **context)

    def get_recent_entries(self, count: int = 100) -> List[LogEntry]:
        """Get recent log entries."""
        return list(self._entries)[-count:]

    def _get_trace_id(self) -> Optional[str]:
        """Get trace ID from context."""
        # Implementation would use contextvars
        return None

    def _get_span_id(self) -> Optional[str]:
        """Get span ID from context."""
        # Implementation would use contextvars
        return None


@dataclass
class ContextToken:
    """A token in the context window."""

    content: str
    token_count: int
    priority: float = 1.0  # Higher priority = less likely to compress
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def age_seconds(self) -> float:
        """Get age of token in seconds."""
        return (datetime.utcnow() - self.created_at).total_seconds()


class ContextWindow:
    """
    Context window manager for token optimization.

    Features:
    - Token counting and tracking
    - Priority-based compression
    - Age-based eviction
    - Summary generation
    """

    def __init__(
        self,
        max_tokens: int = 200000,
        reserve_tokens: int = 4096,
        compression_threshold: float = 0.8,
    ) -> None:
        """Initialize the context window."""
        self.max_tokens = max_tokens
        self.reserve_tokens = reserve_tokens
        self.compression_threshold = compression_threshold
        self._tokens: List[ContextToken] = []
        self._logger = StructuredLogger("context_window")

    def add_token(self, content: str, priority: float = 1.0, **metadata: Any) -> int:
        """Add content to context window."""
        token_count = self.estimate_tokens(content)
        token = ContextToken(
            content=content,
            token_count=token_count,
            priority=priority,
            metadata=metadata,
        )
        self._tokens.append(token)

        current_usage = self.usage_ratio()
        if current_usage > self.compression_threshold:
            self._logger.info(
                f"Context usage at {current_usage:.1%}, triggering compression"
            )
            self.compress()

        return token_count

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Approximate: 1 token ≈ 4 characters for English text.
        More accurate would use a tokenizer.
        """
        return len(text) // 4

    def current_size(self) -> int:
        """Get current token count."""
        return sum(t.token_count for t in self._tokens)

    def usage_ratio(self) -> float:
        """Get current usage as ratio of max tokens."""
        usable = self.max_tokens - self.reserve_tokens
        return min(1.0, self.current_size() / usable) if usable > 0 else 1.0

    def get_content(self) -> str:
        """Get concatenated content."""
        return "\n\n".join(t.content for t in self._tokens)

    def compress(self, target_ratio: Optional[float] = None) -> None:
        """
        Compress context window by removing low-priority or old tokens.

        Strategy:
        1. Remove tokens below priority threshold
        2. Remove old tokens if still over threshold
        3. Summarize remaining content if needed
        """
        target = target_ratio or self.compression_threshold
        target_tokens = int(self.max_tokens * target)

        # Sort by priority (ascending) and age (descending)
        sorted_tokens = sorted(
            self._tokens,
            key=lambda t: (t.priority, -t.age_seconds()),
        )

        # Remove tokens until under target
        removed_count = 0
        new_tokens = []

        for token in reversed(sorted_tokens):
            if sum(t.token_count for t in new_tokens) + token.token_count <= target_tokens:
                new_tokens.insert(0, token)
            else:
                removed_count += 1

        self._tokens = new_tokens
        self._logger.info(
            f"Compressed context: removed {removed_count} tokens, "
            f"now at {self.usage_ratio():.1%} capacity"
        )

    def clear(self) -> None:
        """Clear all tokens."""
        self._tokens.clear()

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        return {
            "current_tokens": self.current_size(),
            "max_tokens": self.max_tokens,
            "usage_ratio": self.usage_ratio(),
            "token_count": len(self._tokens),
            "average_priority": sum(t.priority for t in self._tokens) / len(self._tokens) if self._tokens else 0,
        }


class PerformanceMonitor:
    """
    Performance monitoring for production operations.

    Tracks:
    - Execution time
    - Success/failure rates
    - Token usage
    - Cache hit rates
    """

    def __init__(self) -> None:
        """Initialize the performance monitor."""
        self._metrics: Dict[str, Deque[float]] = {}
        self._counts: Dict[str, Dict[str, int]] = {}
        self._logger = StructuredLogger("performance_monitor")

    def record_execution(
        self,
        operation: str,
        duration_ms: float,
        success: bool = True,
        **metadata: Any,
    ) -> None:
        """Record an operation execution."""
        if operation not in self._metrics:
            self._metrics[operation] = deque(maxlen=1000)
            self._counts[operation] = {"success": 0, "failure": 0}

        self._metrics[operation].append(duration_ms)

        if success:
            self._counts[operation]["success"] += 1
        else:
            self._counts[operation]["failure"] += 1

        self._logger.debug(
            f"Recorded execution: {operation}={duration_ms:.2f}ms, success={success}"
        )

    def get_statistics(self, operation: str) -> Optional[Dict[str, Any]]:
        """Get statistics for an operation."""
        if operation not in self._metrics:
            return None

        durations = list(self._metrics[operation])
        if not durations:
            return None

        counts = self._counts[operation]
        total = sum(counts.values())

        return {
            "operation": operation,
            "count": len(durations),
            "avg_ms": sum(durations) / len(durations),
            "min_ms": min(durations),
            "max_ms": max(durations),
            "p50_ms": self._percentile(durations, 50),
            "p95_ms": self._percentile(durations, 95),
            "p99_ms": self._percentile(durations, 99),
            "success_rate": counts["success"] / total if total > 0 else 0,
            "failure_rate": counts["failure"] / total if total > 0 else 0,
        }

    def _percentile(self, data: List[float], p: int) -> float:
        """Calculate percentile."""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * p / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]

    def get_all_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all operations."""
        return {
            op: stats for op in self._metrics if (stats := self.get_statistics(op)) is not None
        }


@dataclass
class ErrorFallback:
    """Error fallback configuration."""

    error_type: Type[Exception]
    fallback_handler: Callable[[Exception], Any]
    max_attempts: int = 3
    backoff_seconds: float = 1.0
    exponential_backoff: bool = True


class ErrorFallbackSystem:
    """
    Graceful error fallback system.

    Provides:
    - Retry with exponential backoff
    - Alternative execution paths
    - Degraded mode operation
    - Error aggregation and reporting
    """

    def __init__(self) -> None:
        """Initialize the error fallback system."""
        self._fallbacks: List[ErrorFallback] = []
        self._error_counts: Dict[str, int] = {}
        self._last_error_time: Dict[str, datetime] = {}
        self._logger = StructuredLogger("error_fallback")

    def register_fallback(self, fallback: ErrorFallback) -> None:
        """Register an error fallback."""
        self._fallbacks.append(fallback)
        self._logger.info(f"Registered fallback for: {fallback.error_type.__name__}")

    def execute_with_fallback(
        self,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute a function with automatic fallback on error.

        Args:
            func: Function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result from func or fallback handler

        Raises:
            Exception: If all fallbacks fail
        """
        func_name = func.__name__
        current_attempt = 0
        last_exception = None

        # Try primary function with retry
        while current_attempt < 3:  # Default retry attempts
            try:
                result = func(*args, **kwargs)
                self._error_counts[func_name] = 0  # Reset on success
                return result
            except Exception as e:
                last_exception = e
                current_attempt += 1
                self._error_counts[func_name] = self._error_counts.get(func_name, 0) + 1
                self._last_error_time[func_name] = datetime.utcnow()

                self._logger.warning(
                    f"Execution failed (attempt {current_attempt}/3): {func_name} - {e}"
                )

                # Find fallback for this error type
                for fallback in self._fallbacks:
                    if isinstance(e, fallback.error_type):
                        if current_attempt < fallback.max_attempts:
                            # Exponential backoff
                            if fallback.exponential_backoff:
                                wait_time = fallback.backoff_seconds * (2 ** (current_attempt - 1))
                            else:
                                wait_time = fallback.backoff_seconds

                            self._logger.info(f"Retrying after {wait_time:.1f}s...")
                            time.sleep(wait_time)
                            break

                        # Use fallback handler
                        try:
                            fallback_result = fallback.fallback_handler(e)
                            self._logger.info(f"Fallback executed: {fallback.error_type.__name__}")
                            return fallback_result
                        except Exception as fallback_error:
                            self._logger.error(f"Fallback failed: {fallback_error}")
                            last_exception = fallback_error

        # All attempts failed
        self._logger.critical(f"All execution attempts failed: {func_name}")
        raise last_exception or Exception("Execution failed with no fallback available")

    def get_error_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get error statistics."""
        return {
            func_name: {
                "count": count,
                "last_error": (
                    self._last_error_time[func_name].isoformat()
                    if func_name in self._last_error_time
                    else None
                ),
            }
            for func_name, count in self._error_counts.items()
        }


class TokenOptimizer:
    """
    Token optimization utilities.

    Provides:
    - Token counting
    - Content compression
    - Efficient representation
    - Caching strategies
    """

    @staticmethod
    def count_tokens(text: str) -> int:
        """Count tokens in text (approximate)."""
        return len(text) // 4

    @staticmethod
    def compress_text(text: str, target_ratio: float = 0.5) -> str:
        """
        Compress text by removing redundancy while preserving meaning.

        Strategy:
        1. Remove duplicate lines
        2. Summarize long passages
        3. Remove excessive whitespace
        """
        lines = text.split("\n")
        seen = set()
        unique_lines = []

        for line in lines:
            stripped = line.strip()
            if stripped and stripped not in seen:
                seen.add(stripped)
                unique_lines.append(line)

        result = "\n".join(unique_lines)

        # Further compression if needed
        if len(result) > len(text) * target_ratio:
            # Simple truncation for now
            result = result[: int(len(text) * target_ratio)]

        return result

    @staticmethod
    def optimize_json(data: Dict[str, Any], remove_optional: bool = True) -> Dict[str, Any]:
        """Optimize JSON structure for token efficiency."""
        optimized = {}

        for key, value in data.items():
            # Skip None values
            if value is None:
                continue

            # Skip empty collections
            if isinstance(value, (list, dict)) and len(value) == 0:
                continue

            # Recurse into nested structures
            if isinstance(value, dict):
                optimized[key] = TokenOptimizer.optimize_json(value, remove_optional)
            elif isinstance(value, list):
                optimized[key] = [
                    TokenOptimizer.optimize_json(item, remove_optional) if isinstance(item, dict) else item
                    for item in value
                    if item is not None
                ]
            else:
                optimized[key] = value

        return optimized


# Global instances
_performance_monitor: Optional[PerformanceMonitor] = None
_error_fallback: Optional[ErrorFallbackSystem] = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def get_error_fallback_system() -> ErrorFallbackSystem:
    """Get the global error fallback system instance."""
    global _error_fallback
    if _error_fallback is None:
        _error_fallback = ErrorFallbackSystem()
    return _error_fallback


# Export key types and functions
__all__ = [
    "LogLevel",
    "LogEntry",
    "StructuredLogger",
    "ContextToken",
    "ContextWindow",
    "PerformanceMonitor",
    "ErrorFallback",
    "ErrorFallbackSystem",
    "TokenOptimizer",
    "get_performance_monitor",
    "get_error_fallback_system",
]
