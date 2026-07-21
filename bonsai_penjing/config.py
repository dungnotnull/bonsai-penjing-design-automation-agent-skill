"""
Configuration, structured logging, and language detection for the bonsai-penjing harness.
"""

from __future__ import annotations

import logging
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import structlog

from bonsai_penjing.models import Language

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills"
TESTS_DIR = PROJECT_ROOT / "tests"
TOOLS_DIR = PROJECT_ROOT / "tools"
LOGS_DIR = PROJECT_ROOT / "logs"
BRAIN_PATH = PROJECT_ROOT / "SECOND-KNOWLEDGE-BRAIN.md"

LOGS_DIR.mkdir(exist_ok=True)

# --- Vietnamese character sets for language detection ---
_VI_CHARS = re.compile(
    r"[àáảãạăắằẳẵặâấầẩẫậđèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựýỳỷỹỵ]"
)
_VI_WORDS = {
    "cây", "cảnh", "bon", "sai", "tạo", "dáng", "thế", "cắt", "tỉa",
    "thiết", "kế", "nghệ", "thuật", "trường", "phái", "nhật", "bản",
    "trung", "hoa", "việt", "nam", "phân", "tích", "báo", "cáo",
    "tự", "động", "hóa", "kiến", "thức", "nguồn", "dữ", "liệu",
}

# --- Translation tables ---
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        "analysis_report": "Analysis Report",
        "executive_summary": "Executive Summary",
        "inputs_scope": "Inputs & Scope",
        "evidence_collected": "Evidence Collected",
        "analysis_scorecard": "Analysis / Scorecard",
        "action_plan": "Action / Control Plan",
        "academic_evidence": "Academic & Research Evidence",
        "disclosure": "Disclosure / Limitations",
        "recommendation": "Recommendation / Conclusion",
        "post_gate_checklist": "Post-Execution Gate Checklist",
        "key_risks": "Key Risks",
        "evidence_chain": "Evidence Chain",
        "recommended_actions": "Recommended Actions",
        "optimal": "Optimal / Recommended",
        "conditional": "Adjust Required / Conditional",
        "critical": "Critical Alert / Not Recommended",
        "inconclusive": "Inconclusive",
    },
    "vi": {
        "analysis_report": "Báo cáo phân tích",
        "executive_summary": "Tóm tắt tổng quan",
        "inputs_scope": "Đầu vào & Phạm vi",
        "evidence_collected": "Bằng chứng thu thập",
        "analysis_scorecard": "Phân tích / Bảng điểm",
        "action_plan": "Kế hoạch hành động",
        "academic_evidence": "Bằng chứng học thuật",
        "disclosure": "Công bố / Giới hạn phân tích",
        "recommendation": "Kết luận",
        "post_gate_checklist": "Danh sách kiểm tra chất lượng",
        "key_risks": "Rủi ro chính",
        "evidence_chain": "Chuỗi bằng chứng",
        "recommended_actions": "Hành động đề xuất",
        "optimal": "Tối ưu / Khuyến nghị",
        "conditional": "Cần điều chỉnh / Có điều kiện",
        "critical": "Cảnh báo nghiêm trọng / Không khuyến nghị",
        "inconclusive": "Chưa đủ cơ sở kết luận",
    },
}

# --- Knowledge source configuration ---
KNOWLEDGE_SOURCES: Dict[str, Any] = {
    "domain": "Bonsai/Penjing Art & Botanical Pruning Design",
    "primary_sources": [
        {"name": "Bonsai Clubs International", "url": "https://bonsai-bci.com", "tier": 3},
        {"name": "National Bonsai Foundation", "url": "https://bonsai-nbf.org", "tier": 3},
        {"name": "Bonsai Empire", "url": "https://www.bonsaiempire.com", "tier": 3},
        {"name": "American Bonsai Society", "url": "https://absbonsai.org", "tier": 3},
        {"name": "Ueki Bonsai Vietnam", "url": "https://uekibonsai.vn", "tier": 3},
        {"name": "Royal Horticultural Society", "url": "https://www.rhs.org.uk", "tier": 2},
        {"name": "International Shohin Bonsai Association", "url": "https://shohin-bonsai.com", "tier": 3},
    ],
    "academic_sources": [
        {"name": "HortScience / HortTechnology", "url": "https://journals.ashs.org", "tier": 1},
        {"name": "Scientia Horticulturae", "url": "https://www.sciencedirect.com/journal/scientia-horticulturae", "tier": 1},
        {"name": "Trees — Springer", "url": "https://link.springer.com/journal/468", "tier": 1},
        {"name": "Journal of Horticulture & Forestry", "url": "https://academicjournals.org/journal/JHF", "tier": 2},
        {"name": "Environmental & Experimental Botany", "url": "https://www.sciencedirect.com/journal/environmental-and-experimental-botany", "tier": 1},
        {"name": "Frontiers in Plant Science", "url": "https://www.frontiersin.org/journals/plant-science", "tier": 1},
    ],
    "crawl_keywords": [
        "bonsai penjing design school",
        "bonsai pruning technique apical dominance",
        "bonsai wiring shaping technique",
        "penjing rock landscape composition",
        "bonsai form chokkan shakan moyogi",
        "bonsai species care repotting soil",
        "CODIT compartmentalization wound healing trees",
        "auxin apical dominance pruning response",
        "bonsai ramification technique pinching",
    ],
    "scoring_weights": {"recency": 0.4, "keyword_relevance": 0.4, "citation_count": 0.2},
}

# --- Harness settings ---
HARNESS_CONFIG: Dict[str, Any] = {
    "max_retry_attempts_per_gate": 2,
    "max_source_retries": 3,
    "source_timeout_seconds": 30,
    "stale_data_threshold_days": 365,
    "max_clarifying_questions": 2,
    "max_knowledge_citations": 5,
    "max_web_search_gap_fill": 2,
    "min_sources_required": 3,
    "min_academic_sources": 1,
    "max_new_entries_per_crawl": 20,
    "max_results_per_source": 10,
    "degradation_timeout_ms": 5000,
}


def detect_language(text: str) -> Language:
    """Detect if input text is Vietnamese or English."""
    if not text:
        return Language.ENGLISH
    lower = text.lower()
    vi_char_count = len(_VI_CHARS.findall(text))
    vi_word_count = sum(1 for w in _VI_WORDS if w in lower)
    if vi_char_count > 0 and vi_word_count >= 1:
        return Language.VIETNAMESE
    if vi_char_count >= 3:
        return Language.VIETNAMESE
    return Language.ENGLISH


def translate(key: str, lang: Language) -> str:
    """Get translated label for the given key."""
    codes = TRANSLATIONS.get(lang.value, TRANSLATIONS["en"])
    return codes.get(key, key)


def setup_logging(level: str = "INFO", json_format: bool = False) -> None:
    """Configure structured logging via structlog."""
    timestamper = structlog.processors.TimeStamper(fmt="iso")
    pre_chain = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        timestamper,
        structlog.processors.CallsiteParameterAdder(
            {
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            }
        ),
    ]

    if json_format:
        structlog.configure(
            processors=pre_chain + [structlog.processors.JSONRenderer()],
            wrapper_class=structlog.stdlib.BoundLogger,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
    else:
        structlog.configure(
            processors=pre_chain + [structlog.dev.ConsoleRenderer()],
            wrapper_class=structlog.stdlib.BoundLogger,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper(), logging.INFO),
    )


def get_logger(name: Optional[str] = None) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name or "bonsai_penjing")
