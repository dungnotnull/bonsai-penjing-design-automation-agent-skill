"""Tests for core data models."""

from __future__ import annotations

import pytest
from datetime import datetime
from pydantic import ValidationError

from bonsai_penjing.models import (
    AnalysisType,
    CarePlan,
    DegradationLevel,
    DesignAnalysis,
    DesignScenario,
    EvidenceBundle,
    EvidenceTier,
    HarnessReport,
    KnowledgeCitation,
    KnowledgeEvidence,
    Language,
    PruningAction,
    QualityGateReport,
    QualityGateResult,
    RequirementInput,
    RiskItem,
    School,
    SourceEntry,
    VerdictCategory,
    WiringAction,
    AdvisorConclusion,
    RiskLevel,
)


class TestRequirementInput:
    def test_default_values(self):
        req = RequirementInput(object_of_analysis="test tree")
        assert req.language == Language.ENGLISH
        assert req.analysis_type == AnalysisType.COMBINED
        assert req.target_audience == "practitioner"
        assert req.available_inputs == []

    def test_empty_object_raises(self):
        with pytest.raises(ValidationError):
            RequirementInput(object_of_analysis="")

    def test_vietnamese(self):
        req = RequirementInput(object_of_analysis="cây", language=Language.VIETNAMESE)
        assert req.language == Language.VIETNAMESE

    def test_all_fields(self):
        req = RequirementInput(
            object_of_analysis="juniper shakan",
            scope="full analysis",
            timeframe="2026 season",
            available_inputs=["images", "measurements"],
            target_audience="researcher",
            language=Language.ENGLISH,
            analysis_type=AnalysisType.COMPARISON,
            school_preference=School.JAPAN,
        )
        assert req.school_preference == School.JAPAN
        assert req.analysis_type == AnalysisType.COMPARISON
        assert len(req.available_inputs) == 2


class TestEvidenceModels:
    def test_source_entry(self):
        entry = SourceEntry(
            title="Test Source",
            source_url="https://example.com",
            source_name="Example",
            tier=EvidenceTier.TIER_1,
            content_summary="Test content",
        )
        assert entry.tier == EvidenceTier.TIER_1
        assert entry.is_cached is False

    def test_evidence_bundle_empty(self):
        bundle = EvidenceBundle()
        assert len(bundle.current_data) == 0
        assert bundle.degradation_level == DegradationLevel.LEVEL_0

    def test_evidence_bundle_with_degradation(self):
        bundle = EvidenceBundle(
            degradation_level=DegradationLevel.LEVEL_2,
            limitation_notes=["Source failed"],
        )
        assert bundle.degradation_level == DegradationLevel.LEVEL_2
        assert "Source failed" in bundle.limitation_notes


class TestDesignModels:
    def test_pruning_action(self):
        action = PruningAction(
            branch_id="P1",
            description="Cut apex",
            timing="Late winter",
            method="Diagonal cut",
            rationale="Auxin redistribution",
            healing_expected="6 months",
        )
        assert "auxin" in action.rationale.lower()

    def test_wiring_action(self):
        action = WiringAction(
            branch_id="W1",
            gauge_mm=2.5,
            material="aluminum",
            direction="Downward",
            duration_months=6,
            removal_criteria="Before bark bite",
        )
        assert action.gauge_mm == 2.5

    def test_care_plan(self):
        care = CarePlan(
            species="Juniperus chinensis",
            watering="Allow drying between watering",
            soil_mix={"akadama": 40, "pumice": 30, "lava_rock": 30},
            repot_cycle_years=2,
            fertilisation="Balanced 7-7-7",
            pest_disease_watch=["spider mites", "scale"],
            seasonal_notes={"spring": "Major pruning window"},
        )
        assert care.repot_cycle_years == 2
        assert "spider mites" in care.pest_disease_watch

    def test_design_analysis(self):
        analysis = DesignAnalysis(
            source_material={"species": "Pinus thunbergii"},
            school=School.JAPAN,
            target_form="shakan",
            form_rationale="Matching trunk lean",
        )
        assert analysis.school == School.JAPAN

    def test_design_scenario(self):
        scenario = DesignScenario(
            level="best",
            description="Award-level outcome",
            form_match="Perfect",
            key_risks=["over-wiring"],
            expected_outcome="Exhibition ready",
        )
        assert scenario.level == "best"


class TestKnowledgeModels:
    def test_knowledge_citation(self):
        citation = KnowledgeCitation(
            title="Test Paper",
            authors="Smith et al.",
            year=2024,
            venue="Journal of Horticulture",
            doi_or_url="https://doi.org/10.1234/test",
            tier=EvidenceTier.TIER_1,
            relevance="High",
            key_finding="Important result",
            category="pruning_physiology",
        )
        assert citation.tier == EvidenceTier.TIER_1
        assert citation.category == "pruning_physiology"

    def test_knowledge_evidence_empty(self):
        evidence = KnowledgeEvidence()
        assert evidence.evidence_coverage == "Weak"
        assert len(evidence.citations) == 0
        assert len(evidence.knowledge_gaps) == 0


class TestAdvisorModels:
    def test_risk_item(self):
        risk = RiskItem(
            description="Risk of dieback",
            probability="medium",
            impact="high",
            mitigation="Prune in correct season",
        )
        assert risk.probability == "medium"
        assert risk.impact == "high"

    def test_advisor_conclusion(self):
        conclusion = AdvisorConclusion(
            verdict=VerdictCategory.AWARD_LEVEL,
            scenarios_best="Best outcome",
            scenarios_base="Base outcome",
            scenarios_worst="Worst outcome",
            disclosure="Standard disclosure",
        )
        assert conclusion.verdict == VerdictCategory.AWARD_LEVEL


class TestQualityGateModels:
    def test_quality_gate_result(self):
        result = QualityGateResult(
            gate_id="U1",
            passed=True,
            detail="3 sources with academic evidence",
        )
        assert result.passed is True
        assert result.auto_fix_applied is False

    def test_quality_gate_report(self):
        report = QualityGateReport(
            gate_results=[
                QualityGateResult(gate_id="U1", passed=True, detail="ok"),
                QualityGateResult(gate_id="U2", passed=False, detail="missing"),
            ],
            all_passed=False,
            limitations=["Missing disclosure"],
        )
        assert report.has_limitations is True
        assert report.all_passed is False


class TestHarnessReport:
    def test_report_creation(self):
        from bonsai_penjing.models import EvidenceBundle, RequirementInput
        report = HarnessReport(
            language=Language.ENGLISH,
            requirements=RequirementInput(object_of_analysis="test"),
            evidence=EvidenceBundle(),
            degradation_level=DegradationLevel.LEVEL_0,
        )
        assert report.version == "2.0.0"
        markdown = report.to_markdown()
        assert "Bonsai" in markdown

    def test_report_with_errors(self):
        from bonsai_penjing.models import EvidenceBundle, RequirementInput
        report = HarnessReport(
            language=Language.ENGLISH,
            requirements=RequirementInput(object_of_analysis="test"),
            evidence=EvidenceBundle(),
            errors=[{"message": "test error", "category": "source_timeout"}],
        )
        markdown = report.to_markdown()
        assert "test error" in markdown
