"""
Production-grade hooks system for lifecycle management and event emission.

This module provides a clean, reusable hooks framework for:
- Lifecycle events (startup, shutdown, before/after operations)
- State synchronization
- Event emission and subscription
- Error handling hooks

Hooks follow the publish-subscribe pattern with async support.
"""

from __future__ import annotations

import asyncio
import inspect
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
from threading import Lock
from typing import Any, Awaitable, Callable, Dict, List, Optional, Set

from bonsai_penjing.errors import safe_execute


class HookEvent(Enum):
    """Standard hook events."""

    # Lifecycle events
    HARNESS_START = "harness_start"
    HARNESS_COMPLETE = "harness_complete"
    HARNESS_ERROR = "harness_error"

    # Step events
    STEP_START = "step_start"
    STEP_COMPLETE = "step_complete"
    STEP_ERROR = "step_error"

    # Data events
    BEFORE_GATHER = "before_gather"
    AFTER_GATHER = "after_gather"
    BEFORE_EVIDENCE = "before_evidence"
    AFTER_EVIDENCE = "after_evidence"
    BEFORE_ANALYSIS = "before_analysis"
    AFTER_ANALYSIS = "after_analysis"
    BEFORE_ADVISOR = "before_advisor"
    AFTER_ADVISOR = "after_advisor"

    # Quality gate events
    BEFORE_QUALITY_GATE = "before_quality_gate"
    AFTER_QUALITY_GATE = "after_quality_gate"
    QUALITY_GATE_FAIL = "quality_gate_fail"
    QUALITY_GATE_RETRY = "quality_gate_retry"

    # Knowledge events
    KNOWLEDGE_QUERY = "knowledge_query"
    KNOWLEDGE_UPDATE = "knowledge_update"

    # Degradation events
    DEGRADATION_TRIGGERED = "degradation_triggered"
    DEGRADATION_RECOVERED = "degradation_recovered"

    # Custom events (string-based)
    CUSTOM = "custom"


@dataclass
class HookContext:
    """Context passed to hook subscribers."""

    event: HookEvent
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0

    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if self.timestamp == 0.0:
            import time

            self.timestamp = time.time()


@dataclass
class HookSubscriber:
    """A registered hook subscriber."""

    callback: Callable[[HookContext], Any]
    name: str
    priority: int = 0  # Higher priority runs first
    once: bool = False  # Remove after first execution
    async_mode: bool = False  # Run in async context if available

    def __hash__(self) -> int:
        """Hash based on name for uniqueness."""
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        """Equality based on name."""
        if not isinstance(other, HookSubscriber):
            return NotImplemented
        return self.name == other.name


class HookSystem:
    """
    Central hook registry and dispatcher.

    Thread-safe, supports sync and async subscribers, priority ordering,
    and one-time execution.
    """

    def __init__(self) -> None:
        """Initialize the hook system."""
        self._subscribers: Dict[HookEvent, List[HookSubscriber]] = defaultdict(list)
        self._custom_subscribers: Dict[str, List[HookSubscriber]] = defaultdict(list)
        self._lock = Lock()
        self._logger = logging.getLogger(__name__)
        self._once_executed: Set[str] = set()

    def subscribe(
        self,
        event: HookEvent | str,
        callback: Callable[[HookContext], Any],
        name: Optional[str] = None,
        priority: int = 0,
        once: bool = False,
    ) -> HookSubscriber:
        """
        Subscribe to a hook event.

        Args:
            event: Event to subscribe to (HookEvent enum or custom string)
            callback: Function to call when event is triggered
            name: Unique name for this subscriber (defaults to function name)
            priority: Higher priority subscribers run first
            once: Remove subscriber after first execution

        Returns:
            The registered HookSubscriber object
        """
        if name is None:
            name = callback.__name__

        # Detect if callback is async
        async_mode = inspect.iscoroutinefunction(callback)

        subscriber = HookSubscriber(
            callback=callback,
            name=name,
            priority=priority,
            once=once,
            async_mode=async_mode,
        )

        with self._lock:
            if isinstance(event, str):
                self._custom_subscribers[event].append(subscriber)
            else:
                self._subscribers[event].append(subscriber)

            # Sort by priority (descending)
            target_list = (
                self._custom_subscribers[event]
                if isinstance(event, str)
                else self._subscribers[event]
            )
            target_list.sort(key=lambda s: s.priority, reverse=True)

        self._logger.debug(f"Registered hook subscriber: {name} -> {event}")
        return subscriber

    def unsubscribe(self, event: HookEvent | str, name: str) -> bool:
        """
        Unsubscribe a named subscriber from an event.

        Args:
            event: Event to unsubscribe from
            name: Name of the subscriber to remove

        Returns:
            True if subscriber was found and removed, False otherwise
        """
        with self._lock:
            target_list = (
                self._custom_subscribers[event]
                if isinstance(event, str)
                else self._subscribers.get(event, [])
            )

            for i, subscriber in enumerate(target_list):
                if subscriber.name == name:
                    target_list.pop(i)
                    self._logger.debug(f"Unregistered hook subscriber: {name} from {event}")
                    return True

        return False

    def emit(
        self,
        event: HookEvent | str,
        context: Optional[HookContext] = None,
        **kwargs: Any,
    ) -> List[Any]:
        """
        Emit a hook event to all subscribers.

        Args:
            event: Event to emit
            context: Hook context (created if not provided)
            **kwargs: Additional context data

        Returns:
            List of results from all subscribers (in priority order)
        """
        if context is None:
            context = HookContext(event=event, data=kwargs)

        # Get subscribers for this event
        with self._lock:
            if isinstance(event, str):
                subscribers = list(self._custom_subscribers.get(event, []))
            else:
                subscribers = list(self._subscribers.get(event, []))

        if not subscribers:
            return []

        results = []
        to_remove: List[HookSubscriber] = []

        for subscriber in subscribers:
            # Skip if once-only and already executed
            if subscriber.once and subscriber.name in self._once_executed:
                to_remove.append(subscriber)
                continue

            # Execute subscriber
            result = safe_execute(
                subscriber.callback,
                context,
                default_return=None,
                raise_on_error=False,
            )

            results.append(result)

            # Track once-only execution
            if subscriber.once:
                self._once_executed.add(subscriber.name)
                to_remove.append(subscriber)

        # Remove one-time subscribers
        with self._lock:
            for subscriber in to_remove:
                self.unsubscribe(event, subscriber.name)

        return results

    async def emit_async(
        self,
        event: HookEvent | str,
        context: Optional[HookContext] = None,
        **kwargs: Any,
    ) -> List[Any]:
        """
        Emit a hook event asynchronously.

        Handles both sync and async subscribers appropriately.
        """
        if context is None:
            context = HookContext(event=event, data=kwargs)

        with self._lock:
            if isinstance(event, str):
                subscribers = list(self._custom_subscribers.get(event, []))
            else:
                subscribers = list(self._subscribers.get(event, []))

        if not subscribers:
            return []

        results = []
        to_remove: List[HookSubscriber] = []

        for subscriber in subscribers:
            # Skip if once-only and already executed
            if subscriber.once and subscriber.name in self._once_executed:
                to_remove.append(subscriber)
                continue

            # Execute based on async mode
            if subscriber.async_mode:
                result = await safe_execute(
                    subscriber.callback,
                    context,
                    default_return=None,
                    raise_on_error=False,
                )
            else:
                result = safe_execute(
                    subscriber.callback,
                    context,
                    default_return=None,
                    raise_on_error=False,
                )

            results.append(result)

            # Track once-only execution
            if subscriber.once:
                self._once_executed.add(subscriber.name)
                to_remove.append(subscriber)

        # Remove one-time subscribers
        with self._lock:
            for subscriber in to_remove:
                self.unsubscribe(event, subscriber.name)

        return results

    def clear(self) -> None:
        """Clear all subscribers."""
        with self._lock:
            self._subscribers.clear()
            self._custom_subscribers.clear()
            self._once_executed.clear()

    def list_subscribers(self, event: Optional[HookEvent | str] = None) -> Dict[str, List[str]]:
        """
        List all registered subscribers.

        Args:
            event: If provided, only list subscribers for this event

        Returns:
            Dictionary mapping event names to lists of subscriber names
        """
        with self._lock:
            if event is not None:
                if isinstance(event, str):
                    subscribers = self._custom_subscribers.get(event, [])
                else:
                    subscribers = self._subscribers.get(event, [])
                return {str(event): [s.name for s in subscribers]}

            result: Dict[str, List[str]] = {}
            for evt, subs in self._subscribers.items():
                result[str(evt.value)] = [s.name for s in subs]
            for evt, subs in self._custom_subscribers.items():
                result[evt] = [s.name for s in subs]
            return result


# Global hook system instance
_global_hooks: Optional[HookSystem] = None


def get_hooks() -> HookSystem:
    """Get the global hook system instance."""
    global _global_hooks
    if _global_hooks is None:
        _global_hooks = HookSystem()
    return _global_hooks


def reset_hooks() -> None:
    """Reset the global hook system (useful for testing)."""
    global _global_hooks
    _global_hooks = None


# Decorator for hook subscription
def on_event(
    event: HookEvent | str,
    name: Optional[str] = None,
    priority: int = 0,
    once: bool = False,
) -> Callable:
    """
    Decorator to register a function as a hook subscriber.

    Usage:
        @on_event(HookEvent.STEP_COMPLETE)
        def log_step(context: HookContext) -> None:
            print(f"Step completed: {context.data.get('step_name')}")
    """

    def decorator(func: Callable[[HookContext], Any]) -> Callable[[HookContext], Any]:
        hooks = get_hooks()
        hooks.subscribe(event, func, name=name, priority=priority, once=once)
        return func

    return decorator


# Export key types and functions
__all__ = [
    "HookEvent",
    "HookContext",
    "HookSubscriber",
    "HookSystem",
    "get_hooks",
    "reset_hooks",
    "on_event",
]
