"""
Core Pydantic data models for the bonsai-penjing design automation harness.
All domain entities, enums, and transmission types are defined here.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class Language(str, Enum):
    ENGLISH = "en"
    VIETNAMESE = "vi"


class School(str, Enum):
    JAPAN = "japan"
    CHINA = "china"
    VIETNAM = "vietnam"


class BonsaiForm(str, Enum):
    CHOKKAN = "chokkan"
    SHAKAN = "shakan"
    MOYOGI = "moyogi"
    KENGAI = "kengai"
    HAN_KENGAI = "han_kengai"
    BUNJINGI = "bunjingi"
    SOKAN = "sokan"
    KABUDACHI = "kabudachi"
    NEAGARI = "neagari"
    FUKINAGASHI = "fukinagashi"
    YOSE_UE = "yose_ue"
    SEKJOJU = "sekijoju"
    ISHITSUKI = "ishitsuki"
    NEARAI = "nearai"


class PenjingForm(str, Enum):
    SHUMU = "shumu"
    SHANSHUI = "shanshui"
    SHUIHAN = "shuihan"


class VietnameseForm(str, Enum):
    THO_NUI = "tho_nui"
    CHAN_THO = "chan_tho"
    DA_LON = "da_lon"
    TIEN_CAY_DOI = "tien_cay_doi"


class EvidenceTier(int, Enum):
    TIER_1 = 1  # Systematic review / meta-analysis / official standard
    TIER_2 = 2  # Peer-reviewed academic paper / RCT
    TIER_3 = 3  # Industry report / professional association guideline
    TIER_4 = 4  # News / blog / vendor material


class VerdictCategory(str, Enum):
    AWARD_LEVEL = "Award-Level Design"
    SOLID_REFINEMENTS = "Solid Design (refinements)"
    NEEDS_REWORK = "Needs Significant Rework"
    INCONCLUSIVE = "Inconclusive"


class AnalysisType(str, Enum):
    COMBINED = "combined"
    DESIGN_ONLY = "design_only"
    CARE_ONLY = "care_only"
    COMPARISON = "comparison"
    RISK_ASSESSMENT = "risk_assessment"


class DegradationLevel(int, Enum):
    LEVEL_0 = 0  # All primary sources reachable
    LEVEL_1 = 1  # Some primary sources fail — use secondary
    LEVEL_2 = 2  # Most live sources fail — knowledge base only
    LEVEL_3 = 3  # Required input variable missing — proceed with flags
    LEVEL_4 = 4  # All sources AND knowledge base fail — no output without notice


class RiskLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# --- Input & Output Models ---


class RequirementInput(BaseModel):
    object_of_analysis: str = Field(..., min_length=1, description="Tree/plant specimen or design case")
    scope: Optional[str] = Field(default=None, description="Scope constraints")
    timeframe: Optional[str] = Field(default=None, description="Time constraints or season")
    available_inputs: List[str] = Field(default_factory=list, description="Images, measurements, notes available")
    target_audience: str = Field(default="practitioner", description="practitioner, researcher, decision_maker, learner")
    language: Language = Field(default=Language.ENGLISH)
    analysis_type: AnalysisType = Field(default=AnalysisType.COMBINED)
    school_preference: Optional[School] = Field(default=None)
    form_preference: Optional[str] = Field(default=None)


class SourceEntry(BaseModel):
    title: str
    source_url: str
    source_name: str
    retrieval_date: datetime = Field(default_factory=datetime.now)
    tier: EvidenceTier
    content_summary: str
    is_cached: bool = False


class EvidenceBundle(BaseModel):
    current_data: List[SourceEntry] = Field(default_factory=list)
    authoritative_docs: List[SourceEntry] = Field(default_factory=list)
    recent_developments: List[SourceEntry] = Field(default_factory=list)
    reference_benchmarks: List[SourceEntry] = Field(default_factory=list)
    degradation_level: DegradationLevel = DegradationLevel.LEVEL_0
    limitation_notes: List[str] = Field(default_factory=list)


class PruningAction(BaseModel):
    branch_id: str
    description: str
    timing: str
    method: str
    rationale: str
    healing_expected: str


class WiringAction(BaseModel):
    branch_id: str
    gauge_mm: float
    material: str
    direction: str
    duration_months: int
    removal_criteria: str


class CarePlan(BaseModel):
    species: str
    watering: str
    soil_mix: Dict[str, int] = Field(default_factory=dict, description="Component -> percentage")
    repot_cycle_years: int
    fertilisation: str
    pest_disease_watch: List[str] = Field(default_factory=list)
    seasonal_notes: Dict[str, str] = Field(default_factory=dict)


class RockComposition(BaseModel):
    style: str
    rock_type: str
    placement: str
    soil_level: str
    moss_ground_cover: Optional[str] = None


class DesignScenario(BaseModel):
    level: str  # best, base, worst
    description: str
    form_match: str
    key_risks: List[str] = Field(default_factory=list)
    expected_outcome: str


class DesignAnalysis(BaseModel):
    source_material: Dict[str, Any] = Field(default_factory=dict)
    school: School
    target_form: str
    form_rationale: str
    pruning_plan: List[PruningAction] = Field(default_factory=list)
    wiring_plan: List[WiringAction] = Field(default_factory=list)
    rock_composition: Optional[RockComposition] = None
    care_plan: Optional[CarePlan] = None
    scenarios: List[DesignScenario] = Field(default_factory=list)


class KnowledgeCitation(BaseModel):
    title: str
    authors: str
    year: int
    venue: str
    doi_or_url: str
    tier: EvidenceTier
    relevance: str
    key_finding: str
    category: str


class KnowledgeEvidence(BaseModel):
    citations: List[KnowledgeCitation] = Field(default_factory=list)
    knowledge_gaps: List[str] = Field(default_factory=list)
    evidence_coverage: str = "Weak"  # Strong, Moderate, Weak


class RiskItem(BaseModel):
    description: str
    probability: str  # high, medium, low
    impact: str      # high, medium, low
    mitigation: str


class AdvisorConclusion(BaseModel):
    verdict: VerdictCategory
    scenarios_best: str
    scenarios_base: str
    scenarios_worst: str
    key_risks: List[RiskItem] = Field(default_factory=list)
    evidence_chain: List[str] = Field(default_factory=list)
    remediation: List[str] = Field(default_factory=list)
    disclosure: str
    degradation_level: DegradationLevel = DegradationLevel.LEVEL_0


class QualityGateResult(BaseModel):
    gate_id: str
    passed: bool
    detail: str
    auto_fix_applied: bool = False
    retry_count: int = 0


class QualityGateReport(BaseModel):
    gate_results: List[QualityGateResult] = Field(default_factory=list)
    all_passed: bool = False
    limitations: List[str] = Field(default_factory=list)
    degradation_level: DegradationLevel = DegradationLevel.LEVEL_0

    @property
    def has_limitations(self) -> bool:
        return len(self.limitations) > 0


class HarnessReport(BaseModel):
    """The final, complete analysis report from the harness."""
    report_id: str = Field(default_factory=lambda: datetime.now().strftime("BPD-%Y%m%d-%H%M%S"))
    date: datetime = Field(default_factory=datetime.now)
    version: str = __import__("bonsai_penjing").__version__
    language: Language
    requirements: RequirementInput
    evidence: EvidenceBundle
    design: Optional[DesignAnalysis] = None
    knowledge: Optional[KnowledgeEvidence] = None
    conclusion: Optional[AdvisorConclusion] = None
    quality_report: Optional[QualityGateReport] = None
    degradation_level: DegradationLevel = DegradationLevel.LEVEL_0
    execution_time_ms: float = 0.0
    errors: List[Dict[str, Any]] = Field(default_factory=list)

    def to_markdown(self) -> str:
        lang = self.language
        labels = _get_labels(lang)
        lines = [
            f"# {labels['title']}",
            f"**{labels['date_label']}:** {self.date.strftime('%Y-%m-%d')} | "
            f"**{labels['analyst']}:** bonsai-penjing-design-automation v{self.version} | "
            f"**{labels['language']}:** {lang.value}",
            f"**{labels['degradation']}:** {self.degradation_level.name}",
            "",
        ]
        if self.errors:
            lines.append(f"## {labels['errors']}")
            for e in self.errors:
                lines.append(f"- {e.get('message', str(e))}")
            lines.append("")
        return "\n".join(lines)


_LABELS_EN = {
    "title": "Bonsai & Penjing Design Analysis & Automation — Report",
    "date_label": "Date",
    "analyst": "Analyst",
    "language": "Language",
    "degradation": "Degradation Level",
    "errors": "Errors Encountered",
}
_LABELS_VI = {
    "title": "Phân Tích & Tự Động Hóa Thiết Kế Bonsai, Cây Cảnh Nghệ Thuật — Báo Cáo",
    "date_label": "Ngày",
    "analyst": "Phân tích viên",
    "language": "Ngôn ngữ",
    "degradation": "Mức suy giảm",
    "errors": "Lỗi gặp phải",
}


def _get_labels(lang: Language) -> Dict[str, str]:
    return _LABELS_VI if lang == Language.VIETNAMESE else _LABELS_EN
