"""Tests for error handling, degradation tracker, and retry logic."""

from __future__ import annotations

import pytest

from bonsai_penjing.errors import (
    DegradationTracker,
    ErrorCategory,
    HarnessError,
    categorize_error,
    retry_with_fallback,
    safe_execute,
    ERROR_RECOVERY_TABLE,
)
from bonsai_penjing.models import DegradationLevel


class TestHarnessError:
    def test_basic_error(self):
        err = HarnessError("test message")
        assert str(err) == "test message"
        assert err.category == ErrorCategory.UNKNOWN

    def test_error_with_category(self):
        err = HarnessError("timeout", category=ErrorCategory.SOURCE_TIMEOUT, details={"attempt": 1})
        assert err.category == ErrorCategory.SOURCE_TIMEOUT
        assert err.details == {"attempt": 1}

    def test_error_to_dict(self):
        err = HarnessError("test", category=ErrorCategory.NETWORK_ERROR)
        d = err.to_dict()
        assert d["message"] == "test"
        assert d["category"] == "network_error"
        assert d["recoverable"] is True


class TestDegradationTracker:
    def test_initial_state(self):
        tracker = DegradationTracker()
        assert tracker.level == DegradationLevel.LEVEL_0
        assert len(tracker.failed_sources) == 0

    def test_escalate_level_1(self):
        tracker = DegradationTracker()
        tracker.failed_sources.append("source1")
        tracker.escalate("First source failed")
        assert tracker.level.value >= 1

    def test_escalate_level_2(self):
        tracker = DegradationTracker()
        tracker.failed_sources = ["s1", "s2", "s3"]
        tracker.escalate("Multiple sources failed")
        assert tracker.level.value >= 2

    def test_missing_inputs_escalate(self):
        tracker = DegradationTracker()
        tracker.missing_inputs.append("species")
        tracker.escalate("Missing required input")
        assert tracker.level.value >= 3

    def test_lim_banner_level_0(self):
        tracker = DegradationTracker()
        assert tracker.lim_banner() == ""

    def test_lim_banner_level_2(self):
        tracker = DegradationTracker()
        tracker.failed_sources = ["s1", "s2", "s3"]
        tracker.escalate("Failed")
        banner = tracker.lim_banner()
        assert "LIMITATION NOTICE" in banner
        assert "Level" in banner


class TestCategorizeError:
    def test_timeout_error(self):
        class MockTimeoutError(Exception):
            pass
        err = MockTimeoutError("connection timed out")
        cat = categorize_error(err)
        assert cat == ErrorCategory.NETWORK_ERROR

    def test_parse_error(self):
        class ParseException(ValueError):
            pass
        err = ParseException("failed to parse XML document")
        cat = categorize_error(err)
        assert cat == ErrorCategory.PARSE_ERROR

    def test_unknown_error(self):
        err = ValueError("something happened")
        cat = categorize_error(err)
        assert cat == ErrorCategory.UNKNOWN


class TestRetryWithFallback:
    def test_success_first_try(self):
        call_count = [0]

        def succeed():
            call_count[0] += 1
            return 42

        result, error = retry_with_fallback(succeed, category=ErrorCategory.UNKNOWN)
        assert result == 42
        assert error is None
        assert call_count[0] == 1

    def test_retry_then_succeed(self):
        calls = [0]

        def fail_then_succeed():
            calls[0] += 1
            if calls[0] < 2:
                raise ValueError("failed")
            return 99

        result, error = retry_with_fallback(
            fail_then_succeed, category=ErrorCategory.UNKNOWN, max_retries=2
        )
        assert result == 99
        assert error is None
        assert calls[0] >= 2

    def test_all_fail_with_fallback(self):
        def always_fail():
            raise RuntimeError("always fails")

        def fallback_func():
            return 77

        result, error = retry_with_fallback(
            always_fail,
            category=ErrorCategory.SOURCE_TIMEOUT,
            max_retries=1,
            fallback=fallback_func,
        )
        assert result == 77
        assert error is not None

    def test_none_result(self):
        def returns_none():
            return None

        result, error = retry_with_fallback(returns_none, category=ErrorCategory.UNKNOWN)
        assert result is None


class TestSafeExecute:
    def test_success(self):
        def ok():
            return "result"

        result, error = safe_execute(ok)
        assert result == "result"
        assert error is None

    def test_harness_error(self):
        def raise_he():
            raise HarnessError("planned error", category=ErrorCategory.KNOWLEDGE_BASE_MISS)

        result, error = safe_execute(raise_he)
        assert result is None
        assert isinstance(error, HarnessError)
        assert error.category == ErrorCategory.KNOWLEDGE_BASE_MISS

    def test_regular_exception(self):
        def raise_normal():
            raise ValueError("normal error")

        result, error = safe_execute(raise_normal, error_category=ErrorCategory.PARSE_ERROR)
        assert result is None
        assert isinstance(error, HarnessError)
        assert error.category == ErrorCategory.PARSE_ERROR


class TestErrorRecoveryTable:
    def test_all_categories_have_recovery(self):
        for cat in ErrorCategory:
            assert cat in ERROR_RECOVERY_TABLE
            assert "recovery" in ERROR_RECOVERY_TABLE[cat]
            assert "retry_limit" in ERROR_RECOVERY_TABLE[cat]
