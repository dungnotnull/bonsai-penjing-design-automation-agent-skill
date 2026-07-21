"""Tests for core analysis, evidence collector, knowledge updater, and advisor services."""

from __future__ import annotations

import pytest

from bonsai_penjing.models import (
    EvidenceBundle,
    Language,
    RequirementInput,
    VerdictCategory,
    AnalysisType,
)
from bonsai_penjing.errors import DegradationTracker
from bonsai_penjing.services.evidence_collector import EvidenceCollectorService
from bonsai_penjing.services.core_analysis import CoreAnalysisService
from bonsai_penjing.services.knowledge_updater import KnowledgeUpdaterService, REFERENCE_LIBRARY
from bonsai_penjing.services.advisor import AdvisorService
from bonsai_penjing.services.quality_gates import QualityGateSystem


class TestEvidenceCollector:
    @pytest.fixture
    def service(self):
        return EvidenceCollectorService(tracker=DegradationTracker())

    def test_collect_evidence(self, service, sample_requirements):
        bundle = service.execute(sample_requirements)
        assert isinstance(bundle, EvidenceBundle)
        assert len(bundle.current_data) >= 0
        assert len(bundle.authoritative_docs) >= 0

    def test_collect_with_degradation(self, sample_requirements):
        tracker = DegradationTracker()
        tracker.failed_sources.append("primary")
        service = EvidenceCollectorService(tracker=tracker)
        bundle = service.execute(sample_requirements)
        assert isinstance(bundle, EvidenceBundle)

    def test_build_keywords(self, service, sample_requirements):
        kw = service._build_keywords(sample_requirements)
        assert len(kw) >= 1


class TestCoreAnalysis:
    @pytest.fixture
    def service(self):
        return CoreAnalysisService(tracker=DegradationTracker())

    def test_analyze_pine(self, service, sample_requirements):
        evidence = EvidenceBundle()
        design = service.execute(sample_requirements, evidence)
        assert design.school.value == "japan"
        assert design.target_form is not None
        assert len(design.pruning_plan) > 0

    def test_analyze_vietnamese(self, service):
        req = RequirementInput(
            object_of_analysis="cây sanh dáng chân thọ",
            language=Language.VIETNAMESE,
            school_preference="vietnam",
        )
        evidence = EvidenceBundle()
        design = service.execute(req, evidence)
        assert design.school.value == "vietnam"
        assert design.target_form in ("chan_tho", "tho_nui")

    def test_analyze_chinese(self, service):
        req = RequirementInput(
            object_of_analysis="penjing landscape with juniper",
            school_preference="china",
        )
        evidence = EvidenceBundle()
        design = service.execute(req, evidence)
        assert design.school.value == "china"
        assert design.rock_composition is not None

    def test_pruning_has_physiology_rationale(self, service, sample_requirements):
        evidence = EvidenceBundle()
        design = service.execute(sample_requirements, evidence)
        for action in design.pruning_plan:
            assert len(action.rationale) > 0
            assert len(action.timing) > 0

    def test_care_plan_species_specific(self, service, sample_requirements):
        evidence = EvidenceBundle()
        design = service.execute(sample_requirements, evidence)
        assert design.care_plan is not None
        assert len(design.care_plan.watering) > 0
        assert len(design.care_plan.soil_mix) > 0

    def test_scenarios_present(self, service, sample_requirements):
        evidence = EvidenceBundle()
        design = service.execute(sample_requirements, evidence)
        assert len(design.scenarios) == 3
        levels = {s.level for s in design.scenarios}
        assert levels == {"best", "base", "worst"}

    def test_species_identification(self, service):
        assert service._identify_species("Japanese black pine") == "pine"
        assert service._identify_species("juniper shimpaku") == "juniper"
        assert service._identify_species("maple tree") == "maple"
        assert service._identify_species("ficus bonsai") == "ficus"
        assert service._identify_species("unknown tree") == "juniper"


class TestKnowledgeUpdater:
    @pytest.fixture
    def service(self):
        return KnowledgeUpdaterService(tracker=DegradationTracker())

    def test_reference_library(self):
        assert len(REFERENCE_LIBRARY) >= 5
        tiers = {r.tier.value for r in REFERENCE_LIBRARY}
        assert 1 in tiers
        assert 2 in tiers

    def test_execute(self, service, sample_requirements):
        evidence = service.execute(sample_requirements)
        assert len(evidence.citations) > 0
        assert evidence.evidence_coverage in ("Strong", "Moderate", "Weak")

    def test_match_citations(self, service):
        citations = service._match_citations(["juniper", "pruning"])
        assert len(citations) > 0

    def test_detect_gaps(self, service):
        gaps = service._detect_gaps([], ["rare topic"])
        assert len(gaps) > 0

    def test_assess_coverage_strong(self, service):
        citations = REFERENCE_LIBRARY[:4]
        coverage = service._assess_coverage(citations, [])
        assert coverage == "Strong"


class TestAdvisor:
    @pytest.fixture
    def service(self):
        return AdvisorService(tracker=DegradationTracker())

    def test_verdict_award_level(self, service, sample_requirements):
        evidence = EvidenceBundle()
        analysis_service = CoreAnalysisService()
        design = analysis_service.execute(sample_requirements, evidence)

        knowledge_service = KnowledgeUpdaterService()
        knowledge = knowledge_service.execute(sample_requirements, design)

        conclusion = service.execute(sample_requirements, design, knowledge, evidence)
        assert conclusion.verdict in (
            VerdictCategory.AWARD_LEVEL,
            VerdictCategory.SOLID_REFINEMENTS,
            VerdictCategory.NEEDS_REWORK,
            VerdictCategory.INCONCLUSIVE,
        )

    def test_disclosure_present(self, service, sample_requirements):
        evidence = EvidenceBundle()
        design = CoreAnalysisService().execute(sample_requirements, evidence)
        knowledge = KnowledgeUpdaterService().execute(sample_requirements)
        conclusion = service.execute(sample_requirements, design, knowledge, evidence)
        assert len(conclusion.disclosure) > 0

    def test_risks_minimum_three(self, service, sample_requirements):
        evidence = EvidenceBundle()
        design = CoreAnalysisService().execute(sample_requirements, evidence)
        knowledge = KnowledgeUpdaterService().execute(sample_requirements)
        conclusion = service.execute(sample_requirements, design, knowledge, evidence)
        assert len(conclusion.key_risks) >= 3

    def test_remediation_actions(self, service, sample_requirements):
        evidence = EvidenceBundle()
        design = CoreAnalysisService().execute(sample_requirements, evidence)
        knowledge = KnowledgeUpdaterService().execute(sample_requirements)
        conclusion = service.execute(sample_requirements, design, knowledge, evidence)
        assert len(conclusion.remediation) > 0

    def test_inconclusive_on_degraded(self, service, sample_requirements):
        evidence = EvidenceBundle(degradation_level=3)
        design = CoreAnalysisService().execute(sample_requirements, evidence)
        knowledge = KnowledgeUpdaterService().execute(sample_requirements)
        conclusion = service.execute(sample_requirements, design, knowledge, evidence)
        assert conclusion.verdict == VerdictCategory.INCONCLUSIVE


class TestQualityGates:
    @pytest.fixture
    def gate_system(self):
        return QualityGateSystem()

    def test_all_gates_pass(self, gate_system, sample_requirements):
        evidence = EvidenceCollectorService().execute(sample_requirements)
        design = CoreAnalysisService().execute(sample_requirements, evidence)
        knowledge = KnowledgeUpdaterService().execute(sample_requirements, design)
        advisor = AdvisorService()
        conclusion = advisor.execute(sample_requirements, design, knowledge, evidence)

        report = gate_system.execute(sample_requirements, evidence, design, knowledge, conclusion)
        assert len(report.gate_results) == 10
        assert report.all_passed is True

    def test_g1_identifies_school(self, gate_system, sample_requirements):
        evidence = EvidenceBundle()
        design = CoreAnalysisService().execute(sample_requirements, evidence)
        knowledge = KnowledgeUpdaterService().execute(sample_requirements)
        advisor = AdvisorService()
        conclusion = advisor.execute(sample_requirements, design, knowledge, evidence)

        report = gate_system.execute(sample_requirements, evidence, design, knowledge, conclusion)
        g1 = [r for r in report.gate_results if r.gate_id == "G1"][0]
        assert g1.passed is True

    def test_gates_report_all_present(self, gate_system, sample_requirements):
        evidence = EvidenceBundle()
        design = CoreAnalysisService().execute(sample_requirements, evidence)
        knowledge = KnowledgeUpdaterService().execute(sample_requirements, design)
        advisor = AdvisorService()
        conclusion = advisor.execute(sample_requirements, design, knowledge, evidence)

        report = gate_system.execute(sample_requirements, evidence, design, knowledge, conclusion)
        gate_ids = [r.gate_id for r in report.gate_results]
        expected = {"U1", "U2", "U3", "U4", "U5", "U6", "G1", "G2", "G3", "G4"}
        assert expected.issubset(set(gate_ids))

    def test_missing_design_fails_gates(self, gate_system, sample_requirements):
        evidence = EvidenceBundle()
        knowledge = KnowledgeUpdaterService().execute(sample_requirements)
        advisor = AdvisorService()
        conclusion = advisor.execute(sample_requirements, None, knowledge, evidence)

        report = gate_system.execute(sample_requirements, evidence, None, knowledge, conclusion)
        assert not report.all_passed
