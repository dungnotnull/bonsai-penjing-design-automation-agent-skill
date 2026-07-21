# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] — 2026-07-11

### Added
- **Production-grade Python package** (`bonsai_penjing/`) with 15 source files
- **30+ Pydantic v2 data models** for all domain entities (models.py)
- **6-step harness pipeline** with HarnessOrchestrator
- **10 quality gates** (U1-U6 universal + G1-G4 domain) with auto-fix and 2-retry max
- **5-level graceful degradation** with explicit LIMITATION banners
- **7 species profiles** with pruning physiology, care plans, seasonal notes
- **10+ form templates** across Japan/China/Vietnam schools
- **8 DOI-cited academic references** with tier grading
- **Context management system** — token-aware windows, priority eviction, conversation memory
- **Click-based CLI** — `bonsai analyze`, `validate`, `crawl`, `info`
- **Full VI/EN bilingual support** with auto-detection
- **99-test pytest suite** across 7 test modules
- **MIT LICENSE**
- **pyproject.toml** with full dependency specification and entry points

### Changed
- Elevation from markdown-only skill templates to runnable Python package
- Knowledge base now has 8 DOI-cited references (was 4)
- Quality gates now auto-fix with proper enforcement logic

### Fixed
- Gate U1 now correctly counts knowledge citations in source total
- Harness report creation no longer fails on missing required fields
- Console encoding issues on Windows fixed with UTF-8 reconfig

## [1.0.0] — 2026-07-10

### Added
- Initial Claude Code skill with 5 sub-skills in markdown
- 6-step harness execution protocol
- SECOND-KNOWLEDGE-BRAIN.md knowledge base
- Tools: knowledge_updater.py, test_knowledge_updater.py, run_test_scenarios.py
- 5 test scenarios covering all gates and verdicts
- VI/EN language detection
