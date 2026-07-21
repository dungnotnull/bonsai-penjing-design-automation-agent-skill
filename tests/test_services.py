"""Tests for requirements gathering service."""

from __future__ import annotations

import pytest

from bonsai_penjing.config import detect_language
from bonsai_penjing.models import AnalysisType, Language, RequirementInput, School
from bonsai_penjing.services.gather_requirements import RequirementsService


class TestRequirementsService:
    @pytest.fixture
    def service(self):
        return RequirementsService()

    def test_parse_english_basic(self, service):
        result = service.execute("Analyze a Japanese black pine bonsai in shakan style")
        assert "pine" in result.object_of_analysis.lower() or "black pine" in result.object_of_analysis.lower()
        assert result.language == Language.ENGLISH

    def test_parse_vietnamese(self, service):
        result = service.execute("Phân tích cây thông Nhật Bản dáng shakan")
        assert result.language == Language.VIETNAMESE
        assert "thông" in result.object_of_analysis.lower() or "shakan" in result.object_of_analysis.lower()

    def test_detect_school_japan(self, service):
        result = service.execute("Design a chokkan bonsai")
        assert result.school_preference == "japan"

    def test_detect_school_vietnam(self, service):
        result = service.execute("Thiết kế cây dáng chân thọ")
        assert result.school_preference == "vietnam"

    def test_detect_audience_researcher(self, service):
        result = service.execute("Research the pruning physiology of ficus")
        assert result.target_audience == "researcher"

    def test_detect_comparison(self, service):
        result = service.execute("Compare juniper vs pine bonsai designs")
        assert result.analysis_type == AnalysisType.COMPARISON

    def test_detect_risk_assessment(self, service):
        result = service.execute("Assess the risk of pruning this maple")
        assert result.analysis_type == AnalysisType.RISK_ASSESSMENT

    def test_detect_care_only(self, service):
        result = service.execute("How to water fertilise and repot juniper care schedule")
        assert result.analysis_type == AnalysisType.CARE_ONLY

    def test_default_to_combined(self, service):
        result = service.execute("Tell me something about trees")
        assert result.analysis_type == AnalysisType.COMBINED

    def test_empty_message(self, service):
        result = service.execute("")
        assert "unspecified" in result.object_of_analysis.lower()

    def test_extract_available_inputs(self, service):
        result = service.execute("Analyze this juniper photo with height 30cm of this species")
        assert "images" in result.available_inputs
        assert "measurements" in result.available_inputs
        assert "species_info" in result.available_inputs
