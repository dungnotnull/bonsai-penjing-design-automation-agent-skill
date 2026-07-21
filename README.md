# bonsai-penjing-design-automation

**Bonsai & Penjing Design Analysis & Automation (Japan, China, Vietnam Schools) v3.0.0**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-99%20passed-brightgreen.svg)](tests/)
[![Production Ready](https://img.shields.io/badge/production--ready-brightgreen.svg)](#production-grade-features)

A production-grade Python package and Claude Code harness for **Bonsai/Penjing Art & Botanical Pruning Design** — gathers authoritative data, applies classical domain methods, integrates academic research, and delivers evidence-backed, risk-disclosed outputs through a 6-step quality-gated pipeline with modular architecture, hooks system, and tool registry.

## Features

### Core Capabilities
- **6-Step Harness Pipeline**: Requirements → Evidence → Design Analysis → Knowledge → Advisor → Quality Gates
- **10 Quality Gates**: U1-U6 (universal) + G1-G4 (domain-specific) with auto-fix and 2-retry max
- **Multi-School Support**: Japan (chokkan, shakan, moyogi, kengai, bunjingi, sokan, neagari), China (penjing shanshui/shumu), Vietnam (tho nui, chan tho)
- **8+ Species Profiles**: Juniper, Pine, Maple, Ficus, Azalea, Elm, Bougainvillea with species-specific care plans
- **Pruning Physiology**: Auxin/apical dominance, CODIT wound healing, ramification techniques
- **Evidence Grading**: Tier 1 (systematic review) through Tier 4 (news), with DOI-cited references
- **Graceful Degradation**: 5 levels (0-4) with explicit limitation banners
- **Vietnamese/English**: Full bilingual support with auto-detection
- **CLI Interface**: `bonsai analyze`, `bonsai validate`, `bonsai crawl`, `bonsai info`
- **99 Passing Tests**: Comprehensive pytest suite with E2E harness validation

### Production-Grade Features (v3.0.0)
- **Modular Architecture**: `/config`, `/scripts`, `/references`, `/assets` with type-safe configuration management
- **Hooks System**: 15+ lifecycle events with priority ordering, one-time execution, and async support
- **Tool Registry**: JSON schema validation, automatic caching, fallback chains, parallel execution
- **Context Management**: Token-aware context windows, priority-based eviction, compression
- **Structured Logging**: Correlation IDs, performance tracking, JSON/console output modes
- **Error Fallback System**: Retry with exponential backoff, alternative execution paths, degraded mode
- **Performance Monitoring**: Execution timing, success/failure rates, percentiles (p50/p95/p99)
- **Configuration System**: Pydantic-based settings with environment variable overrides and YAML config

## Installation

```bash
# Standard install
pip install -e .

# With dev dependencies
pip install -e ".[dev]"

# With crawl dependencies
pip install -e ".[crawl]"
```

## Usage

### CLI

```bash
# Run full analysis pipeline
bonsai analyze "Analyze a Japanese black pine bonsai in shakan style"

# Vietnamese analysis
bonsai analyze "Thiết kế cây thông Nhật Bản theo trường phái Nhật"

# Output to file
bonsai analyze --output report.md "Design a ficus penjing landscape"
bonsai analyze --format json -o report.json "Compare juniper vs pine designs"

# Validate an existing report
bonsai validate report.md

# Update knowledge base
bonsai crawl --dry-run
bonsai crawl -k "shohin bonsai technique"

# Project info
bonsai info
```

### Python API

```python
from bonsai_penjing.harness import HarnessOrchestrator, render_report_markdown

orchestrator = HarnessOrchestrator()
report = orchestrator.execute("Analyze a juniper bonsai in moyogi style")

# Access structured data
print(report.conclusion.verdict.value)  # "Solid Design (refinements)"
print(report.design.target_form)        # "moyogi"
print(report.design.pruning_plan)       # List[PruningAction]

# Render markdown
markdown = render_report_markdown(report)
```

## Architecture

```
bonsai-penjing-design-automation/
├── config/                    # Modular configuration & production systems
│   ├── __init__.py           # Settings management (Pydantic + env + YAML)
│   ├── defaults.yaml         # Default configuration values
│   ├── hooks.py              # Hooks system (15+ lifecycle events)
│   ├── tools.py              # Tool registry (schema validation, caching)
│   └── production.py         # Production best practices (context, logging)
├── scripts/                   # Automation utilities
│   ├── setup.py              # Installation wizard
│   ├── seed_knowledge.py     # Knowledge base seeding
│   └── batch_analyze.py      # Batch analysis processing
├── references/                # Domain knowledge
│   ├── species_profiles.md   # Species profile templates
│   └── form_templates.md     # Classical form templates
├── assets/                    # Static resources
│   ├── diagrams/             # Mermaid system diagrams
│   └── templates/            # Report templates (Markdown + JSON)
├── bonsai_penjing/           # Core Python package
│   ├── services/             # 7 service modules
│   ├── models.py             # 30+ Pydantic models
│   ├── harness.py            # Harness orchestrator
│   └── cli.py                # Click CLI
├── skills/                    # Claude Code skill definitions
│   ├── main.md               # Main harness skill
│   └── sub-*.md              # 5 sub-skills
└── tests/                     # 99 passing tests
```

### Execution Flow

```
USER INPUT
    │
    ▼
[Config System] → Load settings (env + YAML + defaults)
    │
    ▼
[Hook System] → Emit harness_start event
    │
    ▼
[main.md / HarnessOrchestrator]
    │
    ├─► Step 1: RequirementsService     → RequirementInput
    ├─► Step 2: EvidenceCollectorService → EvidenceBundle (via Tool Registry)
    ├─► Step 3: CoreAnalysisService      → DesignAnalysis
    ├─► Step 4: KnowledgeUpdaterService  → KnowledgeEvidence
    ├─► Step 5: AdvisorService           → AdvisorConclusion
    └─► Step 6: QualityGateSystem        → QualityGateReport
            │
            ▼
    [Hook System] → Emit harness_complete event
            │
            ▼
    [Performance Monitor] → Record metrics
            │
            ▼
    [HarnessReport → Markdown/JSON output]
```

## Quality Gates

| Gate | Check |
|------|-------|
| U1 | ≥3 sources cited, ≥1 academic/authoritative |
| U2 | Disclosure/limitations before recommendation |
| U3 | Evidence hierarchy stated (Tier 1-4) per source |
| U4 | Language matches user preference |
| U5 | Output uses declared template (all sections) |
| U6 | Every claim traceable to ≥1 source or flagged |
| G1 | Target school & classical form identified |
| G2 | Pruning plan grounded in pruning physiology |
| G3 | Rock/landscape composition for penjing designs |
| G4 | Species care plan is species-specific |

## Data Sources

- Bonsai Clubs International — bonsai-bci.com
- National Bonsai Foundation — bonsai-nbf.org
- Bonsai Empire — bonsaiempire.com
- American Bonsai Society — absbonsai.org
- Ueki Bonsai (Vietnam) / Vietnam Bonsai Association
- Royal Horticultural Society (RHS) pruning references
- International Shohin Bonsai Association
- Academic: HortScience, Scientia Horticulturae, Trees (Springer), Frontiers in Plant Science

## Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=bonsai_penjing --cov-report=html

# Run specific module
pytest tests/test_harness.py -v

# Run knowledge updater tests
python tools/test_knowledge_updater.py
python tools/run_test_scenarios.py
```

## Knowledge Base

`SECOND-KNOWLEDGE-BRAIN.md` is auto-updated via `tools/knowledge_updater.py` with:
- Weekly academic crawl (ArXiv + Semantic Scholar)
- Daily news crawl (RSS feeds)
- SHA256 deduplication
- Composite scoring (recency + relevance + citations)

## Roadmap

- [x] Phase 0: Architecture & Research
- [x] Phase 1: Core Sub-Skills (5 files)
- [x] Phase 2: Main Harness + Quality Gates (10 gates)
- [x] Phase 3: Knowledge Pipeline (8+ DOI references, species profiles)
- [x] Phase 4: Testing & Validation (99 tests)
- [x] Phase 5: Integration & Polish (Python package v2.0.0, CLI, context management)
- [x] Phase 6: Production Architecture Upgrade (v3.0.0 — modular architecture, hooks, tools, production best practices)

**Status:** ✅ **COMPLETE** — All phases finished, production-ready v3.0.0

## License

MIT — see [LICENSE](LICENSE).

## Citation

```bibtex
@software{bonsai-penjing-design-automation,
  title = {bonsai-penjing-design-automation: Bonsai & Penjing Design Analysis & Automation},
  author = {{bonsai-penjing-design-automation contributors}},
  year = {2026},
  version = {3.0.0},
  url = {https://github.com/example/bonsai-penjing-design-automation},
  doi = {10.5281/zenodo.XXXXXXX}
}
```

## Production-Grade Features

This v3.0.0 release includes enterprise-ready production features:

### Configuration Management
- **Type-safe settings** with Pydantic validation
- **Environment variable overrides** (`BONSAI_*` prefix)
- **YAML configuration files** (`~/.bonsai/config.yaml`, `config/defaults.yaml`)
- **Feature flags** for experimental capabilities
- **Hot-reload capable** with validation on change

### Hooks System
- **15+ lifecycle events** for extensibility
- **Priority-based ordering** for subscriber execution
- **One-time execution** for fire-and-forget handlers
- **Async support** for non-blocking operations
- **Context propagation** with trace/span IDs

### Tool Registry
- **JSON schema validation** for inputs/outputs
- **Automatic caching** with TTL and cache invalidation
- **Fallback chains** for resilient execution
- **Parallel execution** for independent tools
- **Performance monitoring** per tool

### Production Best Practices
- **Context window management** with token counting and compression
- **Structured logging** with correlation IDs and JSON output
- **Error fallback system** with exponential backoff
- **Performance monitoring** with percentile tracking
- **Graceful degradation** with explicit limitation banners

### Documentation
- **SKILL.md** — Complete skill registry with JSON schemas
- **Mermaid diagrams** — 11 system flow diagrams in `/assets/diagrams/`
- **Report templates** — Standard templates in `/assets/templates/`
- **Domain references** — Species profiles and form templates in `/references/`
- **Comprehensive README** — Installation, usage, architecture, testing

## Why This Project

Bonsai/Penjing practitioners face fragmented data, inconsistent methodology, and tools that do not self-improve. This project unifies authoritative data, recognized domain methods, and a continuously-updated academic knowledge base into one evidence-backed, risk-disclosed, production-grade AI agent harness.
