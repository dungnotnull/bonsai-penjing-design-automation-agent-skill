"""
Production-grade configuration management for bonsai-penjing-design-automation.

This package provides type-safe configuration management supporting:
- Environment variable overrides
- YAML configuration files
- LLM parameter management
- Feature flags
- Runtime validation

Configuration priority (highest to lowest):
1. Environment variables (BONSAI_*)
2. Local config file (~/.bonsai/config.yaml)
3. Project config file (config/defaults.yaml)
4. Code defaults
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from pydantic import BaseModel, Field, field_validator


class LLMConfig(BaseModel):
    """LLM model parameters."""

    model_name: str = Field(
        default="claude-3-7-sonnet-20250219",
        description="Primary model for analysis tasks"
    )
    temperature: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Sampling temperature"
    )
    max_tokens: int = Field(
        default=8192,
        ge=1,
        description="Maximum tokens per response"
    )
    timeout_seconds: int = Field(
        default=120,
        ge=1,
        description="Request timeout"
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        description="Maximum retry attempts"
    )
    enable_prompt_caching: bool = Field(
        default=True,
        description="Enable prompt caching for repeated contexts"
    )
    cache_ttl_seconds: int = Field(
        default=300,
        ge=0,
        description="Cache TTL in seconds"
    )

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        """Validate temperature is in valid range."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Temperature must be between 0.0 and 1.0")
        return v


class ContextConfig(BaseModel):
    """Context window management."""

    max_context_tokens: int = Field(
        default=200000,
        ge=1000,
        description="Maximum context window size"
    )
    reserve_tokens: int = Field(
        default=4096,
        ge=100,
        description="Reserved tokens for system prompts"
    )
    compression_threshold: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Compress when usage exceeds this ratio"
    )
    summary_model: str = Field(
        default="claude-3-haiku-20250305",
        description="Model for context compression"
    )


class FeatureFlags(BaseModel):
    """Feature flags for experimental features."""

    enable_vision_analysis: bool = Field(
        default=True,
        description="Enable image/vision analysis for specimen photos"
    )
    enable_crawlers: bool = Field(
        default=True,
        description="Enable web crawling for knowledge updates"
    )
    enable_auto_remediation: bool = Field(
        default=True,
        description="Enable automatic quality gate remediation"
    )
    enable_parallel_evidence: bool = Field(
        default=True,
        description="Enable parallel evidence collection"
    )
    enable_knowledge_cache: bool = Field(
        default=True,
        description="Enable knowledge base caching"
    )
    strict_quality_gates: bool = Field(
        default=True,
        description="Enforce all quality gates strictly"
    )
    experimental_multi_model: bool = Field(
        default=False,
        description="Enable multi-model routing (experimental)"
    )


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str = Field(
        default="INFO",
        description="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    json_format: bool = Field(
        default=False,
        description="Use JSON format for logs"
    )
    file_path: Optional[str] = Field(
        default=None,
        description="Log file path (None for stdout only)"
    )
    rotation_size_mb: int = Field(
        default=100,
        ge=1,
        description="Log file rotation size in MB"
    )
    retention_days: int = Field(
        default=30,
        ge=1,
        description="Log retention period in days"
    )


class KnowledgeConfig(BaseModel):
    """Knowledge pipeline configuration."""

    crawl_interval_hours: int = Field(
        default=168,
        ge=1,
        description="Interval between knowledge crawls (hours)"
    )
    max_new_entries_per_crawl: int = Field(
        default=20,
        ge=1,
        description="Maximum new entries per crawl"
    )
    dedup_enabled: bool = Field(
        default=True,
        description="Enable SHA256 deduplication"
    )
    scoring_weights: Dict[str, float] = Field(
        default={"recency": 0.4, "keyword_relevance": 0.4, "citation_count": 0.2},
        description="Scoring weights for knowledge entries"
    )
    min_confidence_score: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Minimum confidence score for citations"
    )

    @field_validator("scoring_weights")
    @classmethod
    def validate_weights(cls, v: Dict[str, float]) -> Dict[str, float]:
        """Validate weights sum to approximately 1.0."""
        total = sum(v.values())
        if not 0.9 <= total <= 1.1:
            raise ValueError("Scoring weights must sum to approximately 1.0")
        return v


class HarnessConfig(BaseModel):
    """Harness execution configuration."""

    max_retry_attempts_per_gate: int = Field(
        default=2,
        ge=0,
        description="Maximum retries per quality gate"
    )
    source_timeout_seconds: int = Field(
        default=30,
        ge=1,
        description="Timeout for evidence source requests"
    )
    max_clarifying_questions: int = Field(
        default=2,
        ge=0,
        description="Maximum clarifying questions to ask user"
    )
    degradation_timeout_ms: int = Field(
        default=5000,
        ge=100,
        description="Timeout before triggering degradation"
    )
    graceful_degradation: bool = Field(
        default=True,
        description="Enable graceful degradation on errors"
    )


class Settings(BaseModel):
    """Root configuration object."""

    llm: LLMConfig = Field(default_factory=LLMConfig)
    context: ContextConfig = Field(default_factory=ContextConfig)
    features: FeatureFlags = Field(default_factory=FeatureFlags)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    knowledge: KnowledgeConfig = Field(default_factory=KnowledgeConfig)
    harness: HarnessConfig = Field(default_factory=HarnessConfig)

    class Config:
        """Pydantic config."""

        validate_assignment = True
        extra = "forbid"


# Global settings instance
_settings: Optional[Settings] = None


def get_defaults_path() -> Path:
    """Get path to default configuration file."""
    return Path(__file__).parent / "defaults.yaml"


def get_local_config_path() -> Path:
    """Get path to local user configuration file."""
    return Path.home() / ".bonsai" / "config.yaml"


def load_yaml_config(path: Path) -> Dict[str, Any]:
    """Load YAML configuration from file."""
    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_env_config() -> Dict[str, Any]:
    """Load configuration from environment variables."""

    def _get_bool(key: str, default: bool = False) -> bool:
        val = os.getenv(key, str(default)).lower()
        return val in ("true", "1", "yes", "on")

    config: Dict[str, Any] = {}

    # LLM settings
    if llm_model := os.getenv("BONSAI_LLM_MODEL"):
        config.setdefault("llm", {})["model_name"] = llm_model
    if temp := os.getenv("BONSAI_LLM_TEMPERATURE"):
        config.setdefault("llm", {})["temperature"] = float(temp)
    if max_tok := os.getenv("BONSAI_LLM_MAX_TOKENS"):
        config.setdefault("llm", {})["max_tokens"] = int(max_tok)

    # Context settings
    if max_ctx := os.getenv("BONSAI_CONTEXT_MAX_TOKENS"):
        config.setdefault("context", {})["max_context_tokens"] = int(max_ctx)

    # Feature flags
    config.setdefault("features", {})["enable_vision_analysis"] = _get_bool(
        "BONSAI_ENABLE_VISION", True
    )
    config.setdefault("features", {})["enable_crawlers"] = _get_bool(
        "BONSAI_ENABLE_CRAWLERS", True
    )
    config.setdefault("features", {})["enable_auto_remediation"] = _get_bool(
        "BONSAI_ENABLE_AUTO_REMEDIATION", True
    )
    config.setdefault("features", {})["strict_quality_gates"] = _get_bool(
        "BONSAI_STRICT_QUALITY", True
    )

    # Logging
    if log_level := os.getenv("BONSAI_LOG_LEVEL"):
        config.setdefault("logging", {})["level"] = log_level.upper()
    if log_json := os.getenv("BONSAI_LOG_JSON"):
        config.setdefault("logging", {})["json_format"] = _get_bool(log_json, False)

    return config


def load_settings() -> Settings:
    """Load settings from all sources with proper priority."""
    global _settings

    if _settings is not None:
        return _settings

    # Load in priority order: defaults -> local config -> env vars
    defaults = load_yaml_config(get_defaults_path())
    local_config = load_yaml_config(get_local_config_path())
    env_config = load_env_config()

    # Merge configurations
    merged = defaults.copy()
    for config_dict in [local_config, env_config]:
        for section, values in config_dict.items():
            if section in merged:
                if isinstance(merged[section], dict) and isinstance(values, dict):
                    merged[section].update(values)
                else:
                    merged[section] = values
            else:
                merged[section] = values

    _settings = Settings(**merged)
    return _settings


def get_settings() -> Settings:
    """Get current settings instance."""
    if _settings is None:
        return load_settings()
    return _settings


def reset_settings() -> None:
    """Reset settings (useful for testing)."""
    global _settings
    _settings = None


# Export main settings accessor
__all__ = ["Settings", "get_settings", "load_settings", "reset_settings"]
