"""Tests for config, language detection, and logging."""

from __future__ import annotations

import pytest

from bonsai_penjing.config import (
    detect_language,
    get_logger,
    setup_logging,
    translate,
    HARNESS_CONFIG,
    KNOWLEDGE_SOURCES,
    BRAIN_PATH,
    SKILLS_DIR,
    LOGS_DIR,
)
from bonsai_penjing.models import Language


class TestLanguageDetection:
    def test_english_default(self):
        assert detect_language("Hello world") == Language.ENGLISH
        assert detect_language("Analyze this tree") == Language.ENGLISH

    def test_empty_string(self):
        assert detect_language("") == Language.ENGLISH

    def test_vietnamese_chars(self):
        assert detect_language("cây cảnh bonsai") == Language.VIETNAMESE
        assert detect_language("Phân tích thiết kế") == Language.VIETNAMESE

    def test_vietnamese_single_word(self):
        assert detect_language("bonsai cây") == Language.VIETNAMESE

    def test_three_vi_chars(self):
        assert detect_language("à á ả") == Language.VIETNAMESE

    def test_mixed_but_mostly_english(self):
        assert detect_language("Japanese bonsai tree analysis") == Language.ENGLISH


class TestTranslation:
    def test_english_translation(self):
        assert translate("analysis_report", Language.ENGLISH) == "Analysis Report"
        assert translate("executive_summary", Language.ENGLISH) == "Executive Summary"

    def test_vietnamese_translation(self):
        assert translate("analysis_report", Language.VIETNAMESE) == "Báo cáo phân tích"
        assert translate("executive_summary", Language.VIETNAMESE) == "Tóm tắt tổng quan"

    def test_missing_key(self):
        assert translate("nonexistent_key", Language.ENGLISH) == "nonexistent_key"


class TestConfig:
    def test_harness_config(self):
        assert "max_retry_attempts_per_gate" in HARNESS_CONFIG
        assert HARNESS_CONFIG["max_retry_attempts_per_gate"] == 2
        assert HARNESS_CONFIG["source_timeout_seconds"] == 30

    def test_knowledge_sources(self):
        assert "primary_sources" in KNOWLEDGE_SOURCES
        assert len(KNOWLEDGE_SOURCES["primary_sources"]) >= 5
        assert "academic_sources" in KNOWLEDGE_SOURCES
        assert any("HortScience" in s["name"] for s in KNOWLEDGE_SOURCES["academic_sources"])

    def test_paths_exist(self):
        assert SKILLS_DIR.exists()
        assert SKILLS_DIR.is_dir()
        assert LOGS_DIR.exists()
        assert LOGS_DIR.is_dir()

    def test_brain_path(self):
        assert "SECOND-KNOWLEDGE-BRAIN.md" in str(BRAIN_PATH)


class TestLogging:
    def test_setup_logging_console(self):
        setup_logging(level="INFO", json_format=False)

    def test_setup_logging_json(self):
        setup_logging(level="DEBUG", json_format=True)

    def test_get_logger(self):
        logger = get_logger("test_module")
        assert logger is not None
