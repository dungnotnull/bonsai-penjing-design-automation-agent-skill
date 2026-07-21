"""
Step 3: sub-core-analysis — Analyze and design bonsai/penjing artwork.
Applies classical school forms, pruning physiology, wiring, and rock composition.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from bonsai_penjing.config import get_logger
from bonsai_penjing.errors import DegradationTracker
from bonsai_penjing.models import (
    CarePlan,
    DesignAnalysis,
    DesignScenario,
    EvidenceBundle,
    PruningAction,
    RequirementInput,
    RockComposition,
    School,
    WiringAction,
)
from bonsai_penjing.services.domain_knowledge import (
    DEFAULT_SPECIES,
    FORM_MATCHING,
    PRUNING_PHYSIOLOGY,
    ROCK_COMPOSITION_TEMPLATES,
    SPECIES_PROFILES,
    WIRING_REFERENCE,
)

logger = get_logger(__name__)


class CoreAnalysisService:
    """Step 3: Analyse and produce a complete bonsai/penjing design."""

    def __init__(self, tracker: Optional[DegradationTracker] = None) -> None:
        self.tracker = tracker or DegradationTracker()

    def execute(self, requirements: RequirementInput, evidence: EvidenceBundle) -> DesignAnalysis:
        species_key = self._identify_species(requirements.object_of_analysis)
        species = SPECIES_PROFILES.get(species_key, DEFAULT_SPECIES)

        school, form_key = self._select_form(requirements, species_key)
        form_info = FORM_MATCHING.get(form_key, FORM_MATCHING.get("moyogi", {}))

        pruning = self._design_pruning(species, form_key, requirements.object_of_analysis)
        wiring = self._design_wiring(form_key)
        rock_composition = self._design_rock_composition(form_key, school)

        care = CarePlan(
            species=species.get("scientific", requirements.object_of_analysis),
            watering=species.get("water", DEFAULT_SPECIES["water"]),
            soil_mix=species.get("soil", DEFAULT_SPECIES["soil"]),
            repot_cycle_years=species.get("repot_years", DEFAULT_SPECIES["repot_years"]),
            fertilisation=species.get("fertilisation", DEFAULT_SPECIES["fertilisation"]),
            pest_disease_watch=species.get("pests", DEFAULT_SPECIES["pests"]),
            seasonal_notes=species.get("seasonal", DEFAULT_SPECIES["seasonal"]),
        )

        scenarios = self._build_scenarios(school, form_key, species_key, form_info)

        analysis = DesignAnalysis(
            source_material={
                "species": species.get("scientific", "Unknown"),
                "common_name": requirements.object_of_analysis,
                "identified_key": species_key,
            },
            school=School(school),
            target_form=form_key,
            form_rationale=form_info.get("description", "Classical bonsai/penjing form"),
            pruning_plan=pruning,
            wiring_plan=wiring,
            rock_composition=rock_composition,
            care_plan=care,
            scenarios=scenarios,
        )

        logger.info("design_complete", school=school, form=form_key, species=species_key)
        return analysis

    def _identify_species(self, text: str) -> str:
        lower = text.lower()
        for key, profile in SPECIES_PROFILES.items():
            for name in profile["common_names"]:
                if name in lower:
                    return key
        if "pine" in lower or "thông" in lower:
            return "pine"
        if "maple" in lower or "phong" in lower:
            return "maple"
        if "juniper" in lower or "tùng" in lower or "bách" in lower:
            return "juniper"
        if "ficus" in lower or "fig" in lower or "đa" in lower or "si" in lower:
            return "ficus"
        if "azalea" in lower or "đỗ" in lower or "satsuki" in lower:
            return "azalea"
        if "elm" in lower or "du" in lower or "zelkova" in lower:
            return "elm"
        if "bougainvillea" in lower or "hoa giấy" in lower or "bông giấy" in lower:
            return "bougainvillea"
        return "juniper"

    def _select_form(self, requirements: RequirementInput, species_key: str) -> Tuple[str, str]:
        school = "japan"
        if requirements.school_preference:
            school = requirements.school_preference

        if school not in ["japan", "china", "vietnam"]:
            school = "japan"

        if school == "vietnam":
            form_key = "chan_tho" if species_key in ("ficus", "juniper", "elm") else "tho_nui"
        elif school == "china":
            form_key = "shanshui"
        else:
            jap_forms = [k for k, v in FORM_MATCHING.items() if v.get("school") == "japan"
                         and species_key in v.get("suitable_species", [])]
            if not jap_forms:
                jap_forms = ["moyogi", "shakan"]
            form_key = jap_forms[0]

        return school, form_key

    def _design_pruning(self, species: dict, form_key: str, obj: str) -> List[PruningAction]:
        actions = []
        timing = species.get("pruning_timing", "Late winter for structural, growing season for maintenance")
        apex_strength = species.get("apical_dominance", "moderate")

        actions.append(PruningAction(
            branch_id="P1-apex",
            description=f"Reduce apical leader by 1/3 to redirect auxin flow and stimulate lateral budding. "
                        f"Species apical dominance: {apex_strength}.",
            timing="Late winter / early spring before bud break",
            method="Clean diagonal cut above outward-facing bud at desired new apex position",
            rationale=PRUNING_PHYSIOLOGY["apical_dominance"]["description"],
            healing_expected="Callus formation within one growing season with proper cut paste application",
        ))

        actions.append(PruningAction(
            branch_id="P2-lower-branches",
            description="Select primary branches for the form. Remove crossing, inward-growing, and weak branches. "
                        f"Keep branches that match {form_key} branch structure requirements.",
            timing="Concurrent with P1 — same late winter/early spring session",
            method="Clean cuts at branch collar. Seal cuts > 5mm with cut paste. Follow CODIT principles.",
            rationale="Establishing the structural branch framework for the form. "
                      "Branches retained must serve the design and not compete with the trunk line.",
            healing_expected="Healing within 6-12 months for cuts under 10mm diameter. Larger cuts may take 2+ years.",
        ))

        actions.append(PruningAction(
            branch_id="P3-ramification",
            description="Seasonal pinching and pruning to develop secondary and tertiary branching. "
                        "Build foliage pad density through repeated apical control.",
            timing=timing,
            method="Pinch new shoots to 2-3 nodes after extension. Partial defoliation of outer canopy "
                    "where species-appropriate to stimulate interior back-budding.",
            rationale="Auxin redistribution from pinching stimulates dormant buds along branches. "
                      "Repeated cycles build ramification density over multiple growing seasons.",
            healing_expected="Small pinch wounds heal within days. Defoliation wounds heal within 1-2 weeks.",
        ))

        return actions

    def _design_wiring(self, form_key: str) -> List[WiringAction]:
        actions = []
        form_info = FORM_MATCHING.get(form_key, {})

        actions.append(WiringAction(
            branch_id="W1-primary-branches",
            gauge_mm=2.5,
            material="anodized aluminum",
            direction="Wire outward and slightly downward on primary branches to create aged appearance",
            duration_months=6,
            removal_criteria="Remove when wire begins to bite into bark — check every 2-4 weeks during growing season",
        ))

        actions.append(WiringAction(
            branch_id="W2-secondary-branches",
            gauge_mm=1.5,
            material="anodized aluminum",
            direction="Wire secondary branches to create foliage pads. Position to avoid shading lower branches.",
            duration_months=4,
            removal_criteria="Remove when position is set. Deciduous species may set faster than conifers.",
        ))

        return actions

    def _design_rock_composition(self, form_key: str, school: str) -> Optional[RockComposition]:
        if school == "china":
            template = ROCK_COMPOSITION_TEMPLATES.get("shanshui_penjing", {})
        elif school == "vietnam":
            template = ROCK_COMPOSITION_TEMPLATES.get("ishitsuki", {})
        elif form_key in ("ishitsuki", "sekijoju"):
            template = ROCK_COMPOSITION_TEMPLATES.get("ishitsuki", {})
        elif form_key in ("shanshui",):
            template = ROCK_COMPOSITION_TEMPLATES.get("saikei", {"description": ""})
        else:
            return None

        return RockComposition(
            style=template.get("description", ""),
            rock_type=template.get("rock_selection", ""),
            placement=template.get("technique", ""),
            soil_level="Soil level reaching the lower third of the rock for root establishment",
            moss_ground_cover="Apply moss to soil surface around rock base for moisture retention and aesthetic finish",
        )

    def _build_scenarios(self, school: str, form_key: str, species_key: str, form_info: dict) -> List[DesignScenario]:
        scenarios = []
        species_name = SPECIES_PROFILES.get(species_key, {}).get(
            "scientific", SPECIES_PROFILES.get(species_key, {}).get("common_names", [species_key])[0]
        )

        scenarios.append(DesignScenario(
            level="best",
            description=f"Award-level {school} {form_key} design with {species_name}. "
                        f"All pruning cuts clean and healing well. Branch structure develops as planned. "
                        f"Ramification achieved in 3-5 years with consistent technique.",
            form_match=f"Perfect match — {form_info.get('description', form_key)}",
            key_risks=["Over-wiring causing scars", "Pest infestation during development"],
            expected_outcome="Exhibition-ready specimen within 5-7 years of consistent development",
        ))

        scenarios.append(DesignScenario(
            level="base",
            description=f"Solid {school} {form_key} design. Major structure established correctly. "
                        f"Some refinement needed in secondary branching. Functional and presentable.",
            form_match=f"Good match — {form_key} structure present with room for refinement",
            key_risks=["Uneven ramification", "Wire scarring on primary branches"],
            expected_outcome="Presentable bonsai within 3-5 years. Continues improving with refinement.",
        ))

        scenarios.append(DesignScenario(
            level="worst",
            description=f"Design fails if foundational pruning is incorrect or species is mismatched to {form_key}. "
                        f"Poor wound healing or die-back could require complete redesign.",
            form_match=f"Poor match — may need to reconsider form or species combination",
            key_risks=["Die-back from over-pruning", "Permanent reverse taper from poor branch selection",
                       "Root rot from incorrect soil or watering"],
            expected_outcome="Redesign may be necessary. Reassess species-form match and horticultural conditions.",
        ))

        return scenarios
