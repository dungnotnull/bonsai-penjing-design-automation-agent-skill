"""
Production-grade tool registry and execution system.

This module provides:
- Rich tool schemas with input/output validation
- Dynamic tool invocation
- Tool chaining and composition
- Error handling and timeout management
- Tool result caching

Tools can be invoked synchronously or asynchronously, with automatic
fallback chains and degradation support.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from functools import lru_cache
from typing import Any, Awaitable, Callable, Dict, List, Optional, Type, TypeVar, Union

from pydantic import BaseModel, Field, create_model


class ToolCategory(Enum):
    """Tool categories for organization."""

    DATA_FETCH = "data_fetch"
    ANALYSIS = "analysis"
    KNOWLEDGE = "knowledge"
    UTILITY = "utility"
    VALIDATION = "validation"


class ToolExecutionMode(Enum):
    """Tool execution modes."""

    SYNC = "sync"
    ASYNC = "async"
    PARALLEL = "parallel"


@dataclass
class ToolSchema:
    """Input/output schema for a tool."""

    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    category: ToolCategory = ToolCategory.UTILITY
    timeout_seconds: int = 30
    retry_attempts: int = 3
    cacheable: bool = False
    cache_ttl_seconds: int = 300

    def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate input against schema."""
        try:
            # Create Pydantic model from schema
            model = self._create_model("Input", self.input_schema)
            model(**data)
            return True
        except Exception:
            return False

    def validate_output(self, data: Dict[str, Any]) -> bool:
        """Validate output against schema."""
        try:
            model = self._create_model("Output", self.output_schema)
            model(**data)
            return True
        except Exception:
            return False

    def _create_model(self, prefix: str, schema: Dict[str, Any]) -> Type[BaseModel]:
        """Create a Pydantic model from JSON schema."""
        fields = {}
        for prop_name, prop_def in schema.get("properties", {}).items():
            field_type = self._get_python_type(prop_def)
            required = prop_name in schema.get("required", [])
            default = ... if required else None
            fields[prop_name] = (field_type, default)

        return create_model(f"{prefix}_{self.name}", **fields)

    def _get_python_type(self, prop_def: Dict[str, Any]) -> Type:
        """Convert JSON schema type to Python type."""
        type_map = {
            "string": str,
            "number": float,
            "integer": int,
            "boolean": bool,
            "array": List,
            "object": Dict,
        }
        json_type = prop_def.get("type", "string")
        if json_type in type_map:
            return type_map[json_type]
        return Any


@dataclass
class ToolResult:
    """Result from tool execution."""

    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    cached: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
            "cached": self.cached,
            "metadata": self.metadata,
        }


@dataclass
class ToolContext:
    """Context passed to tool handlers."""

    tool_name: str
    input_data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    trace_id: Optional[str] = None


T = TypeVar("T", bound=BaseModel)


class ToolHandler(ABC):
    """Base class for tool handlers."""

    def __init__(self, schema: ToolSchema) -> None:
        """Initialize the tool handler."""
        self.schema = schema
        self._logger = logging.getLogger(f"tool.{schema.name}")

    @abstractmethod
    async def execute_async(self, context: ToolContext) -> ToolResult:
        """Execute the tool asynchronously."""
        pass

    def execute(self, context: ToolContext) -> ToolResult:
        """Execute the tool synchronously."""
        # Run async in sync context
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.execute_async(context))

    def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate input data."""
        return self.schema.validate_input(data)

    def validate_output(self, data: Dict[str, Any]) -> bool:
        """Validate output data."""
        return self.schema.validate_output(data)

    def generate_cache_key(self, input_data: Dict[str, Any]) -> str:
        """Generate cache key for input data."""
        data_str = json.dumps(input_data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def log_execution(self, context: ToolContext, result: ToolResult) -> None:
        """Log tool execution."""
        self._logger.info(
            f"Tool {self.schema.name}: success={result.success}, "
            f"time={result.execution_time_ms:.2f}ms, cached={result.cached}"
        )


# Built-in tool schemas
WEB_SEARCH_SCHEMA = ToolSchema(
    name="web_search",
    description="Search the web for current information",
    category=ToolCategory.DATA_FETCH,
    input_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"},
            "max_results": {"type": "integer", "default": 10},
            "recency": {"type": "string", "enum": ["any", "day", "week", "month"], "default": "week"},
        },
        "required": ["query"],
    },
    output_schema={
        "type": "object",
        "properties": {
            "results": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "url": {"type": "string"},
                        "snippet": {"type": "string"},
                        "published_date": {"type": "string"},
                    },
                },
            },
            "total_results": {"type": "integer"},
        },
    },
    cacheable=True,
    cache_ttl_seconds=3600,  # 1 hour
)

WEB_FETCH_SCHEMA = ToolSchema(
    name="web_fetch",
    description="Fetch content from a URL",
    category=ToolCategory.DATA_FETCH,
    input_schema={
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "URL to fetch"},
            "timeout": {"type": "integer", "default": 30},
        },
        "required": ["url"],
    },
    output_schema={
        "type": "object",
        "properties": {
            "content": {"type": "string"},
            "status_code": {"type": "integer"},
            "content_type": {"type": "string"},
            "length": {"type": "integer"},
        },
    },
    cacheable=True,
    cache_ttl_seconds=86400,  # 24 hours
)

KNOWLEDGE_QUERY_SCHEMA = ToolSchema(
    name="knowledge_query",
    description="Query the knowledge base for domain evidence",
    category=ToolCategory.KNOWLEDGE,
    input_schema={
        "type": "object",
        "properties": {
            "keywords": {"type": "array", "items": {"type": "string"}},
            "max_results": {"type": "integer", "default": 5},
            "min_tier": {"type": "integer", "enum": [1, 2, 3, 4], "default": 3},
        },
        "required": ["keywords"],
    },
    output_schema={
        "type": "object",
        "properties": {
            "entries": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "authors": {"type": "array", "items": {"type": "string"}},
                        "year": {"type": "integer"},
                        "doi": {"type": "string"},
                        "tier": {"type": "integer"},
                        "relevance_score": {"type": "number"},
                    },
                },
            },
            "total_found": {"type": "integer"},
        },
    },
    cacheable=True,
)

IMAGE_ANALYSIS_SCHEMA = ToolSchema(
    name="image_analysis",
    description="Analyze an image for bonsai/penjing design assessment",
    category=ToolCategory.ANALYSIS,
    input_schema={
        "type": "object",
        "properties": {
            "image_path": {"type": "string"},
            "analysis_type": {
                "type": "string",
                "enum": ["form_detection", "health_assessment", "composition_analysis"],
            },
        },
        "required": ["image_path", "analysis_type"],
    },
    output_schema={
        "type": "object",
        "properties": {
            "detected_features": {"type": "array", "items": {"type": "string"}},
            "confidence_scores": {"type": "object"},
            "recommendations": {"type": "array", "items": {"type": "string"}},
        },
    },
)

VALIDATE_SCHEMA = ToolSchema(
    name="validate_report",
    description="Validate a harness report against quality gates",
    category=ToolCategory.VALIDATION,
    input_schema={
        "type": "object",
        "properties": {
            "report_data": {"type": "object"},
            "strict_mode": {"type": "boolean", "default": True},
        },
        "required": ["report_data"],
    },
    output_schema={
        "type": "object",
        "properties": {
            "valid": {"type": "boolean"},
            "gate_results": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "gate_id": {"type": "string"},
                        "passed": {"type": "boolean"},
                        "errors": {"type": "array", "items": {"type": "string"}},
                    },
                },
            },
        },
    },
)


class ToolRegistry:
    """
    Central registry for tool schemas and handlers.

    Supports tool registration, lookup, invocation, caching, and
    fallback chains.
    """

    def __init__(self) -> None:
        """Initialize the tool registry."""
        self._schemas: Dict[str, ToolSchema] = {}
        self._handlers: Dict[str, ToolHandler] = {}
        self._cache: Dict[str, tuple[Any, float]] = {}
        self._fallback_chains: Dict[str, List[str]] = {}
        self._logger = logging.getLogger(__name__)

    def register(self, schema: ToolSchema, handler: ToolHandler) -> None:
        """Register a tool with its schema and handler."""
        self._schemas[schema.name] = schema
        self._handlers[schema.name] = handler
        self._logger.info(f"Registered tool: {schema.name}")

    def register_fallback(self, primary: str, fallback: str) -> None:
        """Register a fallback tool."""
        if primary not in self._fallback_chains:
            self._fallback_chains[primary] = []
        self._fallback_chains[primary].append(fallback)
        self._logger.debug(f"Registered fallback: {primary} -> {fallback}")

    def get_schema(self, tool_name: str) -> Optional[ToolSchema]:
        """Get tool schema."""
        return self._schemas.get(tool_name)

    def list_tools(self, category: Optional[ToolCategory] = None) -> List[str]:
        """List available tools, optionally filtered by category."""
        if category is None:
            return list(self._schemas.keys())
        return [
            name for name, schema in self._schemas.items() if schema.category == category
        ]

    def invoke(
        self,
        tool_name: str,
        input_data: Dict[str, Any],
        context: Optional[ToolContext] = None,
        use_cache: bool = True,
    ) -> ToolResult:
        """
        Invoke a tool with input data.

        Handles caching, validation, and fallback chains.
        """
        if tool_name not in self._schemas:
            return ToolResult(
                success=False,
                error=f"Tool not found: {tool_name}",
            )

        schema = self._schemas[tool_name]
        handler = self._handlers[tool_name]

        # Validate input
        if not schema.validate_input(input_data):
            return ToolResult(
                success=False,
                error=f"Invalid input for tool: {tool_name}",
            )

        # Check cache
        if use_cache and schema.cacheable:
            cache_key = handler.generate_cache_key(input_data)
            if cache_key in self._cache:
                data, timestamp = self._cache[cache_key]
                if time.time() - timestamp < schema.cache_ttl_seconds:
                    return ToolResult(
                        success=True,
                        data=data,
                        cached=True,
                    )

        # Create context
        if context is None:
            context = ToolContext(tool_name=tool_name, input_data=input_data)

        # Execute
        start_time = time.time()
        try:
            result = handler.execute(context)
            result.execution_time_ms = (time.time() - start_time) * 1000

            # Cache result if successful and cacheable
            if result.success and schema.cacheable and result.data:
                cache_key = handler.generate_cache_key(input_data)
                self._cache[cache_key] = (result.data, time.time())

            # Validate output
            if result.data and not schema.validate_output(result.data):
                result.success = False
                result.error = "Output validation failed"

            handler.log_execution(context, result)
            return result

        except Exception as e:
            self._logger.error(f"Tool execution error: {e}")

            # Try fallback chain
            if tool_name in self._fallback_chains:
                for fallback_name in self._fallback_chains[tool_name]:
                    fallback_result = self.invoke(fallback_name, input_data, context, use_cache)
                    if fallback_result.success:
                        self._logger.info(f"Fallback successful: {tool_name} -> {fallback_name}")
                        return fallback_result

            return ToolResult(
                success=False,
                error=str(e),
                execution_time_ms=(time.time() - start_time) * 1000,
            )

    async def invoke_async(
        self,
        tool_name: str,
        input_data: Dict[str, Any],
        context: Optional[ToolContext] = None,
    ) -> ToolResult:
        """Invoke a tool asynchronously."""
        if tool_name not in self._schemas:
            return ToolResult(success=False, error=f"Tool not found: {tool_name}")

        schema = self._schemas[tool_name]
        handler = self._handlers[tool_name]

        if not schema.validate_input(input_data):
            return ToolResult(success=False, error=f"Invalid input for tool: {tool_name}")

        if context is None:
            context = ToolContext(tool_name=tool_name, input_data=input_data)

        start_time = time.time()
        try:
            result = await handler.execute_async(context)
            result.execution_time_ms = (time.time() - start_time) * 1000
            handler.log_execution(context, result)
            return result
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
                execution_time_ms=(time.time() - start_time) * 1000,
            )

    def invoke_parallel(
        self,
        invocations: List[tuple[str, Dict[str, Any]]],
    ) -> List[ToolResult]:
        """Invoke multiple tools in parallel."""
        async def run_all() -> List[ToolResult]:
            tasks = [
                self.invoke_async(tool_name, input_data)
                for tool_name, input_data in invocations
            ]
            return await asyncio.gather(*tasks, return_exceptions=True)

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        results = loop.run_until_complete(run_all())

        # Handle exceptions
        processed = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                tool_name = invocations[i][0]
                processed.append(
                    ToolResult(success=False, error=f"Exception: {result}")
                )
            else:
                processed.append(result)

        return processed

    def clear_cache(self, tool_name: Optional[str] = None) -> None:
        """Clear tool cache."""
        if tool_name is None:
            self._cache.clear()
        else:
            keys_to_remove = [
                k for k in self._cache.keys() if k.startswith(f"{tool_name}:")
            ]
            for key in keys_to_remove:
                del self._cache[key]


# Global tool registry instance
_global_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance."""
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry()
    return _global_registry


def reset_tool_registry() -> None:
    """Reset the global tool registry (useful for testing)."""
    global _global_registry
    _global_registry = None


# Export key types and functions
__all__ = [
    "ToolCategory",
    "ToolExecutionMode",
    "ToolSchema",
    "ToolResult",
    "ToolContext",
    "ToolHandler",
    "ToolRegistry",
    "get_tool_registry",
    "reset_tool_registry",
    "WEB_SEARCH_SCHEMA",
    "WEB_FETCH_SCHEMA",
    "KNOWLEDGE_QUERY_SCHEMA",
    "IMAGE_ANALYSIS_SCHEMA",
    "VALIDATE_SCHEMA",
]
