"""
Production-grade error handling and graceful degradation for the bonsai-penjing harness.
Supports retry logic, fallback chains, degradation level escalation, and limitation banners.
"""

from __future__ import annotations

import time
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar

from pydantic import BaseModel, Field

from bonsai_penjing.config import HARNESS_CONFIG, get_logger
from bonsai_penjing.models import DegradationLevel

logger = get_logger(__name__)
T = TypeVar("T")


class ErrorCategory(str, Enum):
    SOURCE_TIMEOUT = "source_timeout"
    INVALID_INPUT = "invalid_input"
    MISSING_INPUT = "missing_input"
    STALE_READING = "stale_reading"
    KNOWLEDGE_BASE_MISS = "knowledge_base_miss"
    CONFLICTING_ACTIONS = "conflicting_actions"
    ENVELOPE_UNAVAILABLE = "envelope_unavailable"
    OBJECT_AMBIGUOUS = "object_ambiguous"
    NETWORK_ERROR = "network_error"
    PARSE_ERROR = "parse_error"
    UNKNOWN = "unknown"


ERROR_RECOVERY_TABLE: Dict[ErrorCategory, Dict[str, Any]] = {
    ErrorCategory.SOURCE_TIMEOUT: {
        "recovery": "retry alternate source",
        "retry_limit": 3,
        "base_delay": 2.0,
    },
    ErrorCategory.INVALID_INPUT: {
        "recovery": "ask user to confirm",
        "retry_limit": 2,
        "base_delay": 0.0,
    },
    ErrorCategory.MISSING_INPUT: {
        "recovery": "proceed with available + flag",
        "retry_limit": 0,
        "base_delay": 0.0,
    },
    ErrorCategory.STALE_READING: {
        "recovery": "flag, request refresh",
        "retry_limit": 1,
        "base_delay": 0.0,
    },
    ErrorCategory.KNOWLEDGE_BASE_MISS: {
        "recovery": "WebSearch gap-fill + queue for crawl",
        "retry_limit": 2,
        "base_delay": 1.0,
    },
    ErrorCategory.CONFLICTING_ACTIONS: {
        "recovery": "apply stated precedence",
        "retry_limit": 0,
        "base_delay": 0.0,
    },
    ErrorCategory.ENVELOPE_UNAVAILABLE: {
        "recovery": "use genus/category fallback + flag",
        "retry_limit": 1,
        "base_delay": 0.0,
    },
    ErrorCategory.OBJECT_AMBIGUOUS: {
        "recovery": "ask user to confirm",
        "retry_limit": 2,
        "base_delay": 0.0,
    },
    ErrorCategory.NETWORK_ERROR: {
        "recovery": "retry alternate source",
        "retry_limit": 3,
        "base_delay": 2.0,
    },
    ErrorCategory.PARSE_ERROR: {
        "recovery": "use fallback parsing + flag",
        "retry_limit": 2,
        "base_delay": 0.5,
    },
    ErrorCategory.UNKNOWN: {
        "recovery": "log, escalate, flag limitation",
        "retry_limit": 1,
        "base_delay": 1.0,
    },
}


class HarnessError(Exception):
    """Base exception for harness errors."""

    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        details: Optional[Dict[str, Any]] = None,
        recoverable: bool = True,
    ) -> None:
        super().__init__(message)
        self.category = category
        self.details = details or {}
        self.recoverable = recoverable
        self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message": str(self),
            "category": self.category.value,
            "details": self.details,
            "recoverable": self.recoverable,
            "timestamp": self.timestamp,
        }


class DegradationTracker(BaseModel):
    """Tracks degradation state through the harness pipeline."""
    level: DegradationLevel = DegradationLevel.LEVEL_0
    failed_sources: List[str] = Field(default_factory=list)
    substituted_sources: List[Dict[str, str]] = Field(default_factory=list)
    missing_inputs: List[str] = Field(default_factory=list)
    limitation_notes: List[str] = Field(default_factory=list)

    def escalate(self, reason: str) -> None:
        """Escalate degradation level based on accumulated failures."""
        current = self.level.value
        self.limitation_notes.append(reason)

        if len(self.failed_sources) >= 3 or len(self.substituted_sources) >= 2:
            new_level = max(current, 2)
        elif len(self.failed_sources) >= 2:
            new_level = max(current, 2)
        elif len(self.failed_sources) >= 1:
            new_level = max(current, 1)
        else:
            new_level = current

        if self.missing_inputs:
            new_level = max(new_level, 3)

        if new_level >= 4:
            new_level = 4

        self.level = DegradationLevel(new_level)

    def lim_banner(self) -> str:
        """Generate the LIMITATION banner for the current degradation level."""
        if self.level == DegradationLevel.LEVEL_0:
            return ""
        return (
            "---\n"
            f"⚠️  LIMITATION NOTICE\n"
            f"This output was generated with reduced data availability (Level {self.level.value}). "
            f"Cross-check with current data before acting on it. "
            f"Substituted/missing sources are flagged inline.\n"
            "---\n"
        )


def retry_with_fallback(
    func: Callable[..., T],
    *args: Any,
    category: ErrorCategory = ErrorCategory.UNKNOWN,
    max_retries: Optional[int] = None,
    fallback: Optional[Callable[..., T]] = None,
    **kwargs: Any,
) -> Tuple[Optional[T], Optional[str]]:
    """Execute a function with retry logic and optional fallback."""
    recovery = ERROR_RECOVERY_TABLE.get(category, ERROR_RECOVERY_TABLE[ErrorCategory.UNKNOWN])
    retries = max_retries if max_retries is not None else recovery["retry_limit"]
    base_delay = recovery["base_delay"]

    last_error: Optional[str] = None
    for attempt in range(retries + 1):
        try:
            if attempt > 0:
                delay = base_delay * (2 ** (attempt - 1))
                time.sleep(delay)
            result = func(*args, **kwargs)
            if result is not None:
                return result, None
            last_error = "Function returned None"
        except Exception as exc:
            last_error = str(exc)
            logger.warning(
                "retry_attempt",
                attempt=attempt,
                max_retries=retries,
                category=category.value,
                error=last_error,
            )
    if fallback:
        try:
            result = fallback(*args, **kwargs)
            if result is not None:
                return result, f"Used fallback after {retries + 1} failed attempts: {last_error}"
        except Exception as exc:
            logger.error("fallback_failed", error=str(exc))
    return None, last_error


def categorize_error(exc: Exception) -> ErrorCategory:
    """Map an exception to its ErrorCategory."""
    msg = str(exc).lower()
    if any(kw in msg for kw in ("timeout", "timed out", "connection", "httpx.")):
        return ErrorCategory.NETWORK_ERROR
    if any(kw in msg for kw in ("parse", "decode", "json", "xml")):
        return ErrorCategory.PARSE_ERROR
    return ErrorCategory.UNKNOWN


def safe_execute(
    func: Callable[..., T],
    *args: Any,
    error_category: Optional[ErrorCategory] = None,
    default: Optional[T] = None,
    **kwargs: Any,
) -> Tuple[Optional[T], Optional[HarnessError]]:
    """Execute a function safely, returning result or HarnessError."""
    try:
        result = func(*args, **kwargs)
        return result, None
    except HarnessError as he:
        logger.error("harness_error", category=he.category.value, error=str(he))
        return default, he
    except Exception as exc:
        cat = error_category or categorize_error(exc)
        he = HarnessError(str(exc), category=cat, details={"original_type": type(exc).__name__})
        logger.error("safe_execute_error", category=cat.value, error=str(exc), exc_info=True)
        return default, he
