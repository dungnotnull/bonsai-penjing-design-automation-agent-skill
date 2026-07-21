"""Shared fixtures and configuration for bonsai-penjing tests."""

from __future__ import annotations

import pytest
from datetime import datetime

from bonsai_penjing.models import (
    AnalysisType,
    Language,
    RequirementInput,
    School,
)
from bonsai_penjing.errors import (
    DegradationTracker,
    ErrorCategory,
    HarnessError,
)


@pytest.fixture
def sample_english_query() -> str:
    return "Analyze a Japanese black pine bonsai in shakan style with current form imagery"


@pytest.fixture
def sample_vietnamese_query() -> str:
    return "Phân tích cây thông Nhật Bản theo trường phái bonsai Nhật Bản dáng shakan"


@pytest.fixture
def sample_requirements() -> RequirementInput:
    return RequirementInput(
        object_of_analysis="Japanese black pine in shakan style",
        scope="Full design analysis",
        available_inputs=["images", "species_info"],
        target_audience="practitioner",
        language=Language.ENGLISH,
        analysis_type=AnalysisType.COMBINED,
        school_preference=School.JAPAN,
    )


@pytest.fixture
def sample_requirements_vi() -> RequirementInput:
    return RequirementInput(
        object_of_analysis="cây thông Nhật Bản dáng shakan",
        scope="Phân tích thiết kế toàn diện",
        available_inputs=["ảnh", "thông tin loài"],
        target_audience="practitioner",
        language=Language.VIETNAMESE,
        analysis_type=AnalysisType.COMBINED,
        school_preference=School.JAPAN,
    )


@pytest.fixture
def degradation_tracker() -> DegradationTracker:
    return DegradationTracker()


@pytest.fixture
def mock_error() -> HarnessError:
    return HarnessError(
        message="Test error occurred",
        category=ErrorCategory.SOURCE_TIMEOUT,
        details={"attempt": 1},
    )
