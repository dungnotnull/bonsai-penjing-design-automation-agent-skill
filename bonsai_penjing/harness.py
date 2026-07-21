"""
Main harness orchestrator — wires all 6 steps together with pre-flight language detection,
graceful degradation, context management, and comprehensive error handling.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from bonsai_penjing.config import detect_language, get_logger, translate
from bonsai_penjing.context import ContextPipeline
from bonsai_penjing.errors import DegradationTracker, HarnessError, safe_execute
from bonsai_penjing.models import (
    AdvisorConclusion,
    DegradationLevel,
    DesignAnalysis,
    EvidenceBundle,
    HarnessReport,
    KnowledgeEvidence,
    Language,
    QualityGateReport,
    RequirementInput,
)
from bonsai_penjing.services.advisor import AdvisorService
from bonsai_penjing.services.core_analysis import CoreAnalysisService
from bonsai_penjing.services.evidence_collector import EvidenceCollectorService
from bonsai_penjing.services.gather_requirements import RequirementsService
from bonsai_penjing.services.knowledge_updater import KnowledgeUpdaterService
from bonsai_penjing.services.quality_gates import QualityGateSystem

logger = get_logger(__name__)


class HarnessOrchestrator:
    """Orchestrates the 6-step bonsai/penjing analysis pipeline."""

    def __init__(self, context_budget_tokens: int = 180_000) -> None:
        self.tracker = DegradationTracker()
        self.context_pipeline = ContextPipeline(budget_tokens=context_budget_tokens)
        self.errors: List[Dict[str, Any]] = []

    def execute(self, user_message: str) -> HarnessReport:
        """Run the full 6-step pipeline and return a complete HarnessReport."""
        t0 = time.time()
        errors: List[Dict[str, Any]] = []

        # Pre-flight: language detection
        lang = detect_language(user_message)
        self.context_pipeline.memory.add_turn("user", user_message)

        report = HarnessReport(
            language=lang,
            requirements=RequirementInput(object_of_analysis=user_message[:200], language=lang),
            evidence=EvidenceBundle(),
            degradation_level=DegradationLevel.LEVEL_0,
        )

        # Step 1: Gather requirements
        requirements, req_err = self._step_gather_requirements(user_message, lang)
        if req_err:
            errors.append(req_err.to_dict())
            report.requirements = RequirementInput(
                object_of_analysis=user_message[:200],
                language=lang,
            )
        else:
            report.requirements = requirements  # type: ignore[assignment]

        if self.tracker.level.value >= 4:
            report.errors = errors
            report.degradation_level = self.tracker.level
            report.execution_time_ms = (time.time() - t0) * 1000
            logger.warning("pipeline_aborted_early", level=self.tracker.level.value)
            return report

        # Step 2: Collect evidence
        evidence, ev_err = self._step_collect_evidence(report.requirements)
        if ev_err:
            errors.append(ev_err.to_dict())
            evidence = EvidenceBundle(degradation_level=DegradationLevel.LEVEL_2)
        report.evidence = evidence

        # Step 3: Core analysis
        design, design_err = self._step_core_analysis(report.requirements, evidence)
        if design_err:
            errors.append(design_err.to_dict())
        report.design = design

        # Step 4: Knowledge evidence
        knowledge, know_err = self._step_knowledge_evidence(report.requirements, design)
        if know_err:
            errors.append(know_err.to_dict())
        report.knowledge = knowledge

        # Step 5: Advisor conclusion
        conclusion, conc_err = self._step_advisor(report.requirements, design, knowledge, evidence)
        if conc_err:
            errors.append(conc_err.to_dict())
        report.conclusion = conclusion

        # Step 6: Quality gates
        quality_report, qg_err = self._step_quality_gates(
            report.requirements, evidence, design, knowledge, conclusion
        )
        if qg_err:
            errors.append(qg_err.to_dict())
        report.quality_report = quality_report

        report.errors = errors
        report.degradation_level = self.tracker.level
        report.execution_time_ms = (time.time() - t0) * 1000

        self.context_pipeline.memory.add_turn(
            "assistant",
            f"Analysis complete. Verdict: {conclusion.verdict.value if conclusion else 'N/A'}. "
            f"Quality gates: {quality_report.all_passed if quality_report else 'N/A'}.",
        )

        logger.info("harness_complete",
                     elapsed_ms=round(report.execution_time_ms, 0),
                     degradation=self.tracker.level.value,
                     verdict=conclusion.verdict.value if conclusion else "N/A")
        return report

    def _step_gather_requirements(self, user_message: str, lang: Language) -> tuple:
        service = RequirementsService()
        result, error = safe_execute(service.execute, user_message, language=lang)
        if error:
            self.tracker.escalate(f"Requirements gathering error: {error}")
            return None, error
        return result, None

    def _step_collect_evidence(self, requirements: RequirementInput) -> tuple:
        service = EvidenceCollectorService(tracker=self.tracker)
        result, error = safe_execute(service.execute, requirements)
        if error:
            self.tracker.escalate(f"Evidence collection error: {error}")
            return None, error
        return result, None

    def _step_core_analysis(self, requirements: RequirementInput, evidence: EvidenceBundle) -> tuple:
        service = CoreAnalysisService(tracker=self.tracker)
        result, error = safe_execute(service.execute, requirements, evidence)
        if error:
            self.tracker.escalate(f"Core analysis error: {error}")
            return None, error
        return result, None

    def _step_knowledge_evidence(self, requirements: RequirementInput, design: Optional[DesignAnalysis]) -> tuple:
        service = KnowledgeUpdaterService(tracker=self.tracker)
        result, error = safe_execute(service.execute, requirements, design=design)
        if error:
            self.tracker.escalate(f"Knowledge updater error: {error}")
            return None, error
        return result, None

    def _step_advisor(
        self,
        requirements: RequirementInput,
        design: Optional[DesignAnalysis],
        knowledge: Optional[KnowledgeEvidence],
        evidence: EvidenceBundle,
    ) -> tuple:
        service = AdvisorService(tracker=self.tracker)
        result, error = safe_execute(
            service.execute, requirements, design, knowledge, evidence
        )
        if error:
            self.tracker.escalate(f"Advisor synthesis error: {error}")
            return None, error
        return result, None

    def _step_quality_gates(
        self,
        requirements: RequirementInput,
        evidence: EvidenceBundle,
        design: Optional[DesignAnalysis],
        knowledge: Optional[KnowledgeEvidence],
        conclusion: Optional[AdvisorConclusion],
    ) -> tuple:
        service = QualityGateSystem(tracker=self.tracker)
        result, error = safe_execute(
            service.execute, requirements, evidence, design, knowledge, conclusion
        )
        if error:
            self.tracker.escalate(f"Quality gate error: {error}")
            return None, error
        return result, None


def render_report_markdown(report: HarnessReport) -> str:
    """Render a HarnessReport to a complete markdown string."""
    lang = report.language
    t = lambda key: translate(key, lang)

    lines: List[str] = []
    lim_banner = report.degradation_level.value >= 1

    # Header
    lines.append(f"# {t('analysis_report')}")
    lines.append(f"**{t('analysis_report').split(' — ')[0] if ' — ' in t('analysis_report') else 'Report'} ID:** "
                 f"{report.report_id} | **Date:** {report.date.strftime('%Y-%m-%d')} | "
                 f"**Version:** v{report.version} | **Language:** {lang.value}")
    lines.append("")

    # Limitation banner
    if lim_banner:
        lines.append("---")
        lines.append(f"⚠️  LIMITATION NOTICE — Degradation Level {report.degradation_level.value}")
        if report.errors:
            for e in report.errors:
                lines.append(f"- Error: {e.get('message', str(e))[:120]}")
        lines.append("---")
        lines.append("")

    # Executive Summary
    lines.append(f"## {t('executive_summary')}")
    if report.conclusion:
        lines.append(f"**Verdict:** {report.conclusion.verdict.value}")
        lines.append(report.conclusion.scenarios_base[:300] if report.conclusion.scenarios_base else "No base scenario available.")
        lines.append("")
    else:
        lines.append("Analysis incomplete — see errors section.")
        lines.append("")

    # Inputs & Scope
    lines.append(f"## {t('inputs_scope')}")
    lines.append(f"- **Object of Analysis:** {report.requirements.object_of_analysis}")
    if report.requirements.scope:
        lines.append(f"- **Scope:** {report.requirements.scope}")
    lines.append(f"- **Analysis Type:** {report.requirements.analysis_type.value}")
    lines.append(f"- **Target Audience:** {report.requirements.target_audience}")
    if report.requirements.school_preference:
        lines.append(f"- **School Preference:** {report.requirements.school_preference}")
    lines.append("")

    # Evidence
    lines.append(f"## {t('evidence_collected')}")
    lines.append(f"- Current data sources: {len(report.evidence.current_data)}")
    lines.append(f"- Authoritative documents: {len(report.evidence.authoritative_docs)}")
    lines.append(f"- Recent developments: {len(report.evidence.recent_developments)}")
    lines.append(f"- Reference benchmarks: {len(report.evidence.reference_benchmarks)}")
    if report.evidence.limitation_notes:
        for note in report.evidence.limitation_notes[:3]:
            lines.append(f"- ⚠️ {note}")
    lines.append("")

    # Analysis / Scorecard
    if report.design:
        lines.append(f"## {t('analysis_scorecard')}")
        lines.append(f"- **School:** {report.design.school.value}")
        lines.append(f"- **Target Form:** {report.design.target_form}")
        lines.append(f"- **Form Rationale:** {report.design.form_rationale[:200]}")
        lines.append("")
        lines.append("### Pruning Plan")
        for p in report.design.pruning_plan:
            lines.append(f"- **{p.branch_id}:** {p.description[:150]} (Timing: {p.timing})")
        lines.append("")
        lines.append("### Wiring Plan")
        for w in report.design.wiring_plan:
            lines.append(f"- **{w.branch_id}:** {w.gauge_mm}mm {w.material}, {w.duration_months} months")
        lines.append("")

        if report.design.rock_composition:
            lines.append("### Rock/Landscape Composition")
            lines.append(f"- Style: {report.design.rock_composition.style[:100]}")
            lines.append(f"- Rock: {report.design.rock_composition.rock_type[:100]}")
            lines.append("")

        if report.design.care_plan:
            lines.append("### Species Care")
            lines.append(f"- Watering: {report.design.care_plan.watering[:150]}")
            lines.append(f"- Soil mix: {report.design.care_plan.soil_mix}")
            lines.append(f"- Repot cycle: {report.design.care_plan.repot_cycle_years} years")
            lines.append(f"- Pests to watch: {', '.join(report.design.care_plan.pest_disease_watch[:5])}")
            lines.append("")

    # Academic Evidence
    if report.knowledge and report.knowledge.citations:
        lines.append(f"## {t('academic_evidence')}")
        for i, c in enumerate(report.knowledge.citations, 1):
            lines.append(f"{i}. **{c.title}** — {c.authors} ({c.year}), {c.venue}")
            lines.append(f"   Tier {c.tier.value} | Relevance: {c.relevance}")
            lines.append(f"   {c.key_finding[:200]}")
            lines.append(f"   DOI/URL: {c.doi_or_url}")
            lines.append("")
        if report.knowledge.knowledge_gaps:
            lines.append("### Knowledge Gaps")
            for g in report.knowledge.knowledge_gaps:
                lines.append(f"- {g}")
            lines.append("")

    # Disclosure
    if report.conclusion:
        lines.append(f"## ⚠️  {t('disclosure')}")
        lines.append(report.conclusion.disclosure)
        lines.append("")

    # Recommendation
    if report.conclusion:
        lines.append(f"## {t('recommendation')}")
        lines.append(f"**{t('optimal')}:** {report.conclusion.verdict.value}")
        lines.append("")
        lines.append("### Scenarios")
        lines.append(f"- **Best:** {report.conclusion.scenarios_best[:200]}")
        lines.append(f"- **Base:** {report.conclusion.scenarios_base[:200]}")
        lines.append(f"- **Worst:** {report.conclusion.scenarios_worst[:200]}")
        lines.append("")

        if report.conclusion.key_risks:
            lines.append(f"### {t('key_risks')}")
            for r in report.conclusion.key_risks:
                lines.append(f"- [{r.probability}/{r.impact}] {r.description[:150]} → {r.mitigation[:100]}")
            lines.append("")

        if report.conclusion.remediation:
            lines.append(f"### {t('recommended_actions')}")
            for a in report.conclusion.remediation:
                lines.append(f"- {a}")
            lines.append("")

        if report.conclusion.evidence_chain:
            lines.append(f"### {t('evidence_chain')}")
            for c in report.conclusion.evidence_chain:
                lines.append(f"- {c}")
            lines.append("")

    # Quality Gate Checklist
    if report.quality_report:
        lines.append(f"## {t('post_gate_checklist')}")
        for r in report.quality_report.gate_results:
            status = "✓" if r.passed else "✗"
            lines.append(f"- {status} {r.gate_id}: {r.detail[:120]}")
        if report.quality_report.limitations:
            lines.append(f"\nLimitations: {report.quality_report.limitations}")
        lines.append("")

    # Errors
    if report.errors:
        lines.append("## Errors Encountered")
        for e in report.errors:
            lines.append(f"- [{e.get('category', 'unknown')}] {e.get('message', str(e))[:200]}")
        lines.append("")

    lines.append(f"---\n*Report generated by bonsai-penjing-design-automation v{report.version} "
                 f"in {report.execution_time_ms:.0f}ms*")
    return "\n".join(lines)
