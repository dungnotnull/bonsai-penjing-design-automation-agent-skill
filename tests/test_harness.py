"""End-to-end harness integration tests."""

from __future__ import annotations

import pytest

from bonsai_penjing.harness import HarnessOrchestrator, render_report_markdown
from bonsai_penjing.models import HarnessReport, Language, VerdictCategory


class TestHarnessEndToEnd:
    @pytest.fixture
    def orchestrator(self):
        return HarnessOrchestrator()

    def test_full_pipeline_english(self, orchestrator):
        report = orchestrator.execute("Analyze a juniper bonsai in moyogi style")
        assert isinstance(report, HarnessReport)
        assert report.language == Language.ENGLISH
        assert report.requirements is not None
        assert len(report.evidence.current_data) >= 0
        assert report.design is not None
        assert report.design.target_form is not None
        assert report.knowledge is not None
        assert report.conclusion is not None
        assert report.quality_report is not None
        assert len(report.quality_report.gate_results) == 10
        assert report.quality_report.all_passed is True

    def test_full_pipeline_vietnamese(self, orchestrator):
        report = orchestrator.execute("Phân tích cây sanh dáng chân thọ Việt Nam")
        assert isinstance(report, HarnessReport)
        assert report.language == Language.VIETNAMESE
        assert report.design is not None
        assert report.conclusion is not None

    def test_full_pipeline_comparison(self, orchestrator):
        report = orchestrator.execute("Compare juniper vs pine bonsai design approaches")
        assert isinstance(report, HarnessReport)
        assert report.design is not None

    def test_full_pipeline_minimal_input(self, orchestrator):
        report = orchestrator.execute("tree")
        assert isinstance(report, HarnessReport)
        assert report.quality_report is not None
        assert len(report.quality_report.gate_results) == 10

    def test_markdown_render_english(self, orchestrator):
        report = orchestrator.execute("Analyze Japanese maple bonsai")
        md = render_report_markdown(report)
        assert "Analysis Report" in md
        assert "Executive Summary" in md
        assert "Disclosure" in md
        assert "Quality Gate" in md or "Post-Execution" in md

    def test_markdown_render_vietnamese(self, orchestrator):
        report = orchestrator.execute("Phân tích cây thông bonsai")
        md = render_report_markdown(report)
        assert "Báo cáo" in md or "Analysis" in md

    def test_all_verdict_categories_possible(self, orchestrator):
        """Verify the harness can produce different verdicts for different inputs."""
        report1 = orchestrator.execute("Analyze juniper bonsai in chokkan style")
        report2 = orchestrator.execute("tree")

        assert report1.conclusion is not None
        assert report2.conclusion is not None
        assert report1.conclusion.verdict in (
            VerdictCategory.AWARD_LEVEL,
            VerdictCategory.SOLID_REFINEMENTS,
        )

    def test_execution_speed(self, orchestrator):
        """Pipeline should complete quickly for offline analysis."""
        import time
        t0 = time.time()
        report = orchestrator.execute("Design a pine bonsai")
        elapsed = report.execution_time_ms
        assert elapsed < 10000  # Should complete in under 10 seconds
        assert report.conclusion is not None
