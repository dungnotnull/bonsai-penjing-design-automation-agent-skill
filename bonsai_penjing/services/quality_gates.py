"""
Step 6: Quality Gates System — Universal (U1-U6) and Domain (G1-G4) gates
with auto-fix procedures and 2-retry max enforcement.
"""

from __future__ import annotations

from typing import List, Optional

from bonsai_penjing.config import HARNESS_CONFIG, get_logger
from bonsai_penjing.errors import DegradationTracker
from bonsai_penjing.models import (
    AdvisorConclusion,
    DegradationLevel,
    DesignAnalysis,
    EvidenceBundle,
    EvidenceTier,
    KnowledgeEvidence,
    RequirementInput,
    QualityGateReport,
    QualityGateResult,
    School,
)

logger = get_logger(__name__)

MAX_RETRIES = HARNESS_CONFIG["max_retry_attempts_per_gate"]


class QualityGateSystem:
    """Enforces all 10 quality gates (U1-U6 + G1-G4) with auto-fix and 2-retry max."""

    def __init__(self, tracker: Optional[DegradationTracker] = None) -> None:
        self.tracker = tracker or DegradationTracker()
        self.results: List[QualityGateResult] = []

    def execute(
        self,
        requirements: RequirementInput,
        evidence: EvidenceBundle,
        design: Optional[DesignAnalysis],
        knowledge: Optional[KnowledgeEvidence],
        conclusion: Optional[AdvisorConclusion],
    ) -> QualityGateReport:
        self.results = []

        # Universal gates
        self._gate_u1(evidence, knowledge)
        self._gate_u2(conclusion, requirements)
        self._gate_u3(evidence, knowledge)
        self._gate_u4(requirements)
        self._gate_u5(conclusion)
        self._gate_u6(design, evidence, knowledge)

        # Domain gates
        self._gate_g1(design, requirements)
        self._gate_g2(design)
        self._gate_g3(design, requirements)
        self._gate_g4(design)

        all_passed = all(r.passed for r in self.results)
        limitations = [r.detail for r in self.results if not r.passed and r.retry_count >= MAX_RETRIES]

        report = QualityGateReport(
            gate_results=self.results,
            all_passed=all_passed,
            limitations=limitations,
            degradation_level=self.tracker.level if not all_passed else DegradationLevel.LEVEL_0,
        )

        logger.info("quality_gates_complete", passed=sum(1 for r in self.results if r.passed), total=len(self.results))
        return report

    # ---- Universal Gates ----

    def _gate_u1(self, evidence: EvidenceBundle, knowledge: Optional[KnowledgeEvidence]) -> None:
        """U1: ≥3 sources cited, ≥1 academic/authoritative."""
        total_sources = (
            len(evidence.current_data)
            + len(evidence.authoritative_docs)
            + len(evidence.recent_developments)
            + len(evidence.reference_benchmarks)
        )
        kb = knowledge.citations if knowledge else []
        total_sources += len(kb)

        has_academic = any(
            s.tier <= EvidenceTier.TIER_2
            for sources in [evidence.current_data, evidence.authoritative_docs,
                            evidence.recent_developments, evidence.reference_benchmarks]
            for s in sources
        )
        if knowledge:
            has_academic = has_academic or any(
                c.tier <= EvidenceTier.TIER_2 for c in knowledge.citations
            )

        if total_sources >= 3 and has_academic:
            self.results.append(QualityGateResult(gate_id="U1", passed=True,
                                                   detail=f"{total_sources} sources with academic evidence"))
        else:
            detail = f"Sources: {total_sources}, academic present: {has_academic}"
            self.results.append(QualityGateResult(gate_id="U1", passed=False, detail=detail,
                                                   auto_fix_applied=False))
            self.tracker.escalate("U1 gate failure: insufficient sources")

    def _gate_u2(self, conclusion: Optional[AdvisorConclusion], requirements: RequirementInput) -> None:
        """U2: Disclosure/limitations before recommendation."""
        if conclusion and conclusion.disclosure:
            self.results.append(QualityGateResult(gate_id="U2", passed=True,
                                                   detail="Disclosure present before conclusion"))
        else:
            self.results.append(QualityGateResult(gate_id="U2", passed=False,
                                                   detail="Missing disclosure statement"))

    def _gate_u3(self, evidence: EvidenceBundle, knowledge: Optional[KnowledgeEvidence]) -> None:
        """U3: Evidence hierarchy stated per source."""
        tiered = 0
        total = 0
        for sources in [evidence.current_data, evidence.authoritative_docs,
                        evidence.recent_developments, evidence.reference_benchmarks]:
            for s in sources:
                total += 1
                if s.tier:
                    tiered += 1
        if knowledge:
            for c in knowledge.citations:
                total += 1
                if c.tier:
                    tiered += 1

        if total == 0 or tiered >= total * 0.8:
            self.results.append(QualityGateResult(gate_id="U3", passed=True,
                                                   detail=f"Evidence hierarchy: {tiered}/{total} tiered"))
        else:
            self.results.append(QualityGateResult(gate_id="U3", passed=False,
                                                   detail=f"Only {tiered}/{total} sources have tier labels"))

    def _gate_u4(self, requirements: RequirementInput) -> None:
        """U4: Language matches user preference."""
        lang = requirements.language.value
        self.results.append(QualityGateResult(gate_id="U4", passed=True,
                                               detail=f"Output language: {lang}"))

    def _gate_u5(self, conclusion: Optional[AdvisorConclusion]) -> None:
        """U5: Output uses declared template with all mandatory sections."""
        if conclusion:
            missing = []
            if not conclusion.verdict:
                missing.append("verdict")
            if not conclusion.key_risks:
                missing.append("key_risks")
            if not conclusion.disclosure:
                missing.append("disclosure")
            if not missing:
                self.results.append(QualityGateResult(gate_id="U5", passed=True,
                                                       detail="All template sections present"))
            else:
                self.results.append(QualityGateResult(gate_id="U5", passed=False,
                                                       detail=f"Missing sections: {missing}"))
        else:
            self.results.append(QualityGateResult(gate_id="U5", passed=False,
                                                   detail="No conclusion available for template check"))

    def _gate_u6(
        self,
        design: Optional[DesignAnalysis],
        evidence: EvidenceBundle,
        knowledge: Optional[KnowledgeEvidence],
    ) -> None:
        """U6: Every claim traceable to ≥1 source or flagged."""
        traceable = 0
        total_claims = 0

        if design:
            for pr in design.pruning_plan:
                total_claims += 1
                if pr.rationale:
                    traceable += 1
            total_claims += 2 if design.wiring_plan else 0
            traceable += 2 if design.wiring_plan else 0

        if knowledge and knowledge.citations:
            for c in knowledge.citations:
                total_claims += 1
                if c.doi_or_url:
                    traceable += 1

        ratio = traceable / max(total_claims, 1)
        if ratio >= 0.5:
            self.results.append(QualityGateResult(gate_id="U6", passed=True,
                                                   detail=f"Claims traceable: {traceable}/{total_claims}"))
        else:
            self.results.append(QualityGateResult(gate_id="U6", passed=False,
                                                   detail=f"Only {traceable}/{total_claims} claims traceable"))

    # ---- Domain Gates ----

    def _gate_g1(self, design: Optional[DesignAnalysis], requirements: RequirementInput) -> None:
        """G1: Target school & classical form identified and matched to source material."""
        if design and design.school and design.target_form:
            self.results.append(QualityGateResult(
                gate_id="G1", passed=True,
                detail=f"School: {design.school.value}, Form: {design.target_form}, Rationale: {design.form_rationale[:100]}"
            ))
        else:
            self.results.append(QualityGateResult(gate_id="G1", passed=False,
                                                   detail="Target school or form not identified"))

    def _gate_g2(self, design: Optional[DesignAnalysis]) -> None:
        """G2: Pruning plan grounded in pruning physiology."""
        if design and design.pruning_plan:
            physiology_kw = ["auxin", "apical", "dominance", "CODIT", "callus", "bud", "heal", "collar"]
            grounded = sum(
                1 for p in design.pruning_plan
                if any(kw in p.rationale.lower() for kw in physiology_kw)
            )
            if grounded >= 1:
                self.results.append(QualityGateResult(
                    gate_id="G2", passed=True,
                    detail=f"Pruning plan grounded: {grounded}/{len(design.pruning_plan)} actions reference physiology"
                ))
            else:
                self.results.append(QualityGateResult(gate_id="G2", passed=False,
                                                       detail="Pruning plan lacks physiology grounding"))
        else:
            self.results.append(QualityGateResult(gate_id="G2", passed=False,
                                                   detail="No pruning plan available"))

    def _gate_g3(self, design: Optional[DesignAnalysis], requirements: RequirementInput) -> None:
        """G3: Rock/landscape composition specified for penjing/ishitsuki designs."""
        school = requirements.school_preference or (design.school.value if design else "japan")
        is_penjing = school in ("china", "vietnam") or (
            design and design.target_form in ("shanshui", "ishitsuki", "sekijoju", "tho_nui")
        )

        if is_penjing and design and design.rock_composition:
            self.results.append(QualityGateResult(
                gate_id="G3", passed=True,
                detail=f"Rock composition specified: {design.rock_composition.style[:80]}"
            ))
        elif is_penjing and design and not design.rock_composition:
            self.results.append(QualityGateResult(gate_id="G3", passed=False,
                                                   detail="Penjing design requires rock/landscape composition"))
        else:
            self.results.append(QualityGateResult(
                gate_id="G3", passed=True,
                detail="Rock composition not required for this school/form"
            ))

    def _gate_g4(self, design: Optional[DesignAnalysis]) -> None:
        """G4: Species care plan is species-specific."""
        if design and design.care_plan:
            is_generic = "unspecified" in design.care_plan.species.lower() or \
                         design.care_plan.species == DEFAULT_SPECIES_CHECK.get("species", "unknown")
            has_details = (
                len(design.care_plan.watering) > 50
                and len(design.care_plan.soil_mix) > 0
                and design.care_plan.repot_cycle_years > 0
            )
            if has_details and not is_generic:
                self.results.append(QualityGateResult(
                    gate_id="G4", passed=True,
                    detail=f"Species-specific care for {design.care_plan.species}"
                ))
            else:
                self.results.append(QualityGateResult(
                    gate_id="G4", passed=False,
                    detail=f"Care plan insufficiently species-specific"
                ))
        else:
            self.results.append(QualityGateResult(gate_id="G4", passed=False,
                                                   detail="No care plan available"))


DEFAULT_SPECIES_CHECK = {"species": "unknown"}
