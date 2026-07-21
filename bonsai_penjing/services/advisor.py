"""
Step 5: sub-advisor — Synthesize all analysis into a risk-disclosed conclusion
with evidence chain and remediation actions.
"""

from __future__ import annotations

from typing import List, Optional

from bonsai_penjing.config import get_logger, translate
from bonsai_penjing.errors import DegradationTracker
from bonsai_penjing.models import (
    AdvisorConclusion,
    DesignAnalysis,
    EvidenceBundle,
    HarnessReport,
    KnowledgeEvidence,
    Language,
    RequirementInput,
    RiskItem,
    VerdictCategory,
)

logger = get_logger(__name__)


class AdvisorService:
    """Step 5: Synthesize harness outputs into a single risk-disclosed conclusion."""

    def __init__(self, tracker: Optional[DegradationTracker] = None) -> None:
        self.tracker = tracker or DegradationTracker()

    def execute(
        self,
        requirements: RequirementInput,
        design: Optional[DesignAnalysis],
        knowledge: Optional[KnowledgeEvidence],
        evidence: EvidenceBundle,
    ) -> AdvisorConclusion:
        verdict = self._determine_verdict(design, knowledge, evidence)
        risks = self._identify_risks(design, evidence, knowledge)
        evidence_chain = self._build_evidence_chain(design, knowledge)
        remediation = self._build_remediation(verdict, risks, design)
        disclosure = self._build_disclosure(verdict, evidence.degradation_level, requirements.language)

        conclusion = AdvisorConclusion(
            verdict=verdict,
            scenarios_best=self._scenario_text(design, "best"),
            scenarios_base=self._scenario_text(design, "base"),
            scenarios_worst=self._scenario_text(design, "worst"),
            key_risks=risks,
            evidence_chain=evidence_chain,
            remediation=remediation,
            disclosure=disclosure,
            degradation_level=evidence.degradation_level,
        )

        logger.info("advisor_conclusion_ready", verdict=verdict.value)
        return conclusion

    def _determine_verdict(
        self,
        design: Optional[DesignAnalysis],
        knowledge: Optional[KnowledgeEvidence],
        evidence: EvidenceBundle,
    ) -> VerdictCategory:
        if evidence.degradation_level.value >= 3:
            return VerdictCategory.INCONCLUSIVE

        if design is None:
            return VerdictCategory.NEEDS_REWORK

        has_pruning = len(design.pruning_plan) > 0
        has_wiring = len(design.wiring_plan) > 0
        has_care = design.care_plan is not None

        if not has_pruning or not has_wiring:
            return VerdictCategory.NEEDS_REWORK

        kb_coverage = knowledge.evidence_coverage if knowledge else "Weak"

        if kb_coverage == "Strong" and has_pruning and has_wiring and has_care:
            return VerdictCategory.AWARD_LEVEL
        elif kb_coverage in ("Strong", "Moderate") and has_pruning and has_wiring:
            return VerdictCategory.SOLID_REFINEMENTS
        elif has_pruning and has_wiring:
            return VerdictCategory.SOLID_REFINEMENTS
        else:
            return VerdictCategory.NEEDS_REWORK

    def _identify_risks(
        self,
        design: Optional[DesignAnalysis],
        evidence: EvidenceBundle,
        knowledge: Optional[KnowledgeEvidence],
    ) -> List[RiskItem]:
        risks: List[RiskItem] = []

        risks.append(RiskItem(
            description="Pruning timing mismatch — pruning at incorrect season can cause die-back, excessive sap loss, or reduced vigour",
            probability="medium",
            impact="high",
            mitigation="Always prune during species-appropriate window. Refer to SPECIES_PROFILES in domain knowledge for precise timing.",
        ))

        risks.append(RiskItem(
            description="Wire scarring — wire left too long bites into bark causing permanent trunk/branch damage",
            probability="medium",
            impact="medium",
            mitigation="Inspect wiring every 2-4 weeks during growing season. Remove immediately when wire begins to mark bark. Use raffia protection for thick bends.",
        ))

        risks.append(RiskItem(
            description="Soil/watering mismatch — incorrect soil composition or watering schedule can cause root rot or desiccation",
            probability="low",
            impact="high",
            mitigation="Use species-specific soil mix (see care plan). Adjust watering to climate and season. Ensure pot drainage is adequate.",
        ))

        if evidence.degradation_level.value >= 2:
            risks.append(RiskItem(
                description="Reduced evidence quality — analysis based on cached knowledge base rather than live authoritative sources",
                probability="high",
                impact="medium",
                mitigation="Cross-check design decisions against multiple authoritative sources when network access is restored.",
            ))

        if knowledge and knowledge.evidence_coverage == "Weak":
            risks.append(RiskItem(
                description="Knowledge base coverage weak — limited academic evidence available for specific species/form combination",
                probability="medium",
                impact="medium",
                mitigation="Flag for crawl pipeline. Search specialist databases for species-specific studies. Consult local bonsai societies for experiential knowledge.",
            ))

        return risks

    def _build_evidence_chain(self, design: Optional[DesignAnalysis], knowledge: Optional[KnowledgeEvidence]) -> List[str]:
        chain: List[str] = []

        if knowledge and knowledge.citations:
            for c in knowledge.citations[:5]:
                chain.append(
                    f"Form and pruning design ← {c.title} ({c.authors}, {c.year}) — Tier {c.tier.value}: {c.key_finding[:100]}"
                )
        else:
            chain.append("Design ← Domain knowledge base (practitioner reference, Tier 3)")

        chain.append(f"Design methodology ← Bonsai & Penjing Design Analysis & Automation v2 — structured harness")
        return chain

    def _build_remediation(
        self,
        verdict: VerdictCategory,
        risks: List[RiskItem],
        design: Optional[DesignAnalysis],
    ) -> List[str]:
        actions: List[str] = []

        if verdict in (VerdictCategory.AWARD_LEVEL, VerdictCategory.SOLID_REFINEMENTS):
            actions.append("Maintain documentation of all pruning dates and wiring schedules")
            actions.append("Photograph from 4 angles quarterly to track development")
            if design and design.care_plan:
                actions.append(f"Apply species-specific care: {design.care_plan.watering[:100]}")
            actions.append("Submit to local bonsai exhibition for peer review and judging feedback")
        elif verdict == VerdictCategory.NEEDS_REWORK:
            actions.append("Re-evaluate species-form compatibility")
            actions.append("Consult with experienced practitioner for hands-on assessment")
            actions.append("Start with structural pruning before attempting refinement")
            actions.append("Consider simpler form if species does not match target form well")
        else:
            actions.append("Provide species, age, and current form details for re-analysis")
            actions.append("Provide images of tree from 4 angles")
            actions.append("Verify network connectivity for live source access")

        return actions

    def _build_disclosure(self, verdict: VerdictCategory, deg_level, lang: Language) -> str:
        if lang == Language.VIETNAMESE:
            base = (
                "CÔNG BỐ / GIỚI HẠN PHÂN TÍCH:\n"
                f"Kết luận: {verdict.value}.\n"
                "Phân tích này được tạo bởi hệ thống tự động hóa thiết kế bonsai/penjing. "
                "Đây là công cụ hỗ trợ ra quyết định, không thay thế cho đánh giá của chuyên gia.\n"
                "Thiết kế cần được người có chuyên môn về bonsai/penjing xem xét trước khi thực hiện.\n"
                "Các điều kiện thực tế (khí hậu, sức khỏe cây, tay nghề) có thể làm thay đổi kết quả đáng kể.\n"
            )
        else:
            base = (
                "DISCLOSURE / LIMITATIONS:\n"
                f"Conclusion: {verdict.value}.\n"
                "This analysis was generated by the bonsai/penjing design automation harness. "
                "It is a decision-support tool, not a substitute for expert human judgment.\n"
                "Designs should be reviewed by a qualified bonsai/penjing practitioner before implementation.\n"
                "Actual conditions (climate, tree health, practitioner skill) may significantly alter outcomes.\n"
            )

        if deg_level.value >= 2:
            if lang == Language.VIETNAMESE:
                base += "DỮ LIỆU CÓ HẠN: Phân tích dựa trên dữ liệu bộ nhớ đệm. Kiểm tra chéo với nguồn hiện tại.\n"
            else:
                base += "LIMITED DATA: Analysis based on cached knowledge. Cross-check with current sources.\n"

        return base

    def _scenario_text(self, design: Optional[DesignAnalysis], level: str) -> str:
        if design and design.scenarios:
            for s in design.scenarios:
                if s.level == level:
                    return s.description
        return f"{level} scenario: Refer to design analysis scenarios for detailed outcome projections."
