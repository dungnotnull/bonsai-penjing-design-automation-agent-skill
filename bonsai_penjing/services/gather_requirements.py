"""
Step 1: sub-gather-requirements — Parse and validate user inputs, detect language,
and produce a structured RequirementInput object for the rest of the pipeline.
"""

from __future__ import annotations

from typing import Optional

from bonsai_penjing.config import get_logger
from bonsai_penjing.models import AnalysisType, Language, RequirementInput

logger = get_logger(__name__)

MINIMAL_SCHOOL_KEYWORDS = {
    "japan": ["japan", "japanese", "nhat", "nhật", "bản", "chokkan", "shakan", "moyogi", "kengai"],
    "china": ["china", "chinese", "trung", "quốc", "hoa", "penjing", "shanshui", "shumu"],
    "vietnam": ["vietnam", "việt", "nam", "tho", "nui", "núi", "chan", "chân", "tho nui", "chan tho"],
}

AUDIENCE_KEYWORDS = {
    "practitioner": ["practice", "design", "style", "prune", "wire", "care", "thiết kế", "tạo dáng"],
    "researcher": ["research", "study", "paper", "academic", "nghiên cứu", "học thuật"],
    "decision_maker": ["assess", "risk", "feasibility", "đánh giá", "rủi ro", "quyết định"],
    "learner": ["learn", "explain", "how to", "what is", "học", "giải thích", "thế nào"],
}


class RequirementsService:
    """Parse raw user queries into structured requirement objects."""

    def __init__(self) -> None:
        self.max_clarifying_questions = 2

    def execute(self, user_message: str, language: Optional[Language] = None) -> RequirementInput:
        if language is None:
            from bonsai_penjing.config import detect_language
            language = detect_language(user_message)

        obj = self._extract_object(user_message)
        scope = self._extract_scope(user_message)
        audience = self._detect_audience(user_message)
        analysis_type = self._detect_analysis_type(user_message)
        school = self._detect_school(user_message)
        available_inputs = self._extract_available_inputs(user_message)

        req = RequirementInput(
            object_of_analysis=obj or "unspecified bonsai/penjing specimen or design case",
            scope=scope,
            timeframe=None,
            available_inputs=available_inputs,
            target_audience=audience,
            language=language,
            analysis_type=analysis_type,
            school_preference=school,
        )
        logger.info("requirements_parsed", object=req.object_of_analysis, language=language.value)
        return req

    def _extract_object(self, text: str) -> Optional[str]:
        """Extract the primary object of analysis from user text."""
        # Remove common filler and question words
        stripped = text.strip().rstrip(".?!")
        filler_words = ["analyze", "analyse", "analyzing", "phân tích", "design", "please", "help", "hãy", "xin"]
        for fw in filler_words:
            if stripped.lower().startswith(fw):
                stripped = stripped[len(fw):].strip()
                if stripped.startswith((":", "-", " ", "\t")):
                    stripped = stripped[1:].strip()
                break

        if not stripped:
            return None

        if "compare" in stripped.lower() or "so sánh" in stripped.lower():
            parts = _split_comparison(stripped)
            if parts:
                return " vs ".join(parts[:2])
            return stripped

        return stripped[:200]

    def _extract_scope(self, text: str) -> Optional[str]:
        lower = text.lower()
        scope_markers = [
            ("scope:", None), ("phạm vi:", None),
            ("focus on", None), ("specifically", None),
            ("in terms of", None),
        ]
        for marker, _ in scope_markers:
            if marker in lower:
                idx = lower.index(marker)
                fragment = text[idx + len(marker):].strip().rstrip(".?!")
                return fragment[:150] if fragment else None
        return None

    def _detect_audience(self, text: str) -> str:
        lower = text.lower()
        scores = {aud: sum(1 for kw in kws if kw in lower) for aud, kws in AUDIENCE_KEYWORDS.items()}
        max_score = max(scores.values())
        if max_score == 0:
            return "practitioner"
        for aud, score in scores.items():
            if score == max_score:
                return aud
        return "practitioner"

    def _detect_analysis_type(self, text: str) -> AnalysisType:
        lower = text.lower()
        if any(kw in lower for kw in ["compare", "comparison", "so sánh", "vs"]):
            return AnalysisType.COMPARISON
        if any(kw in lower for kw in ["risk", "feasibility", "rủi ro", "khả thi"]):
            return AnalysisType.RISK_ASSESSMENT
        if any(kw in lower for kw in ["care", "watering", "soil", "repot", "chăm sóc", "tưới", "đất"]):
            return AnalysisType.CARE_ONLY
        if any(kw in lower for kw in ["design", "style", "form", "prune", "wire", "thiết kế", "tạo dáng"]):
            return AnalysisType.DESIGN_ONLY
        return AnalysisType.COMBINED

    def _detect_school(self, text: str) -> Optional[str]:
        lower = text.lower()
        for school, keywords in MINIMAL_SCHOOL_KEYWORDS.items():
            if any(kw in lower for kw in keywords):
                return school
        return None

    def _extract_available_inputs(self, text: str) -> list:
        inputs = []
        if any(kw in text.lower() for kw in ["image", "photo", "picture", "ảnh", "hình"]):
            inputs.append("images")
        if any(kw in text.lower() for kw in ["measure", "size", "height", "width", "kích thước", "chiều cao"]):
            inputs.append("measurements")
        if any(kw in text.lower() for kw in ["species", "loài", "giống"]):
            inputs.append("species_info")
        if any(kw in text.lower() for kw in ["age", "tuổi", "năm tuổi"]):
            inputs.append("age_info")
        return inputs


def _split_comparison(text: str) -> list:
    separators = [" vs ", " versus ", " compared to ", " and ", " với ", " so với "]
    lower = text.lower()
    for sep in separators:
        if sep in lower:
            idx = lower.index(sep)
            left = text[:idx].strip()
            right = text[idx + len(sep):].strip()
            return [left, right]
    return []
