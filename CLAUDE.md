# CLAUDE.md — Skill 170: bonsai-penjing-design-automation

## Skill Identity
- **Skill Name:** `bonsai-penjing-design-automation`
- **Tagline:** Bonsai & Penjing Design Analysis & Automation (Japan, China, Vietnam Schools) — Bonsai/Penjing Art & Botanical Pruning Design analysis & decision-support harness.
- **Current Version:** v3.0.0 — PRODUCTION READY
- **Folder:** `D:\972026\170-bonsai-penjing-design-automation\`

---

## Problem This Skill Solves

This skill provides a structured, evidence-backed analytical workflow for
**Bonsai/Penjing Art & Botanical Pruning Design**. It gathers authoritative real-time and reference data, applies
recognized domain methods, cross-references academic research, and delivers
actionable outputs that are fully evidenced, risk/limitation-disclosed, and
traceable to authoritative sources — continuously self-improving through an
automated knowledge crawl pipeline.

---

## Harness Flow Summary

```
/bonsai-penjing-design-automation invoked
│
├─ Step 1: RequirementsService          → Parse inputs, detect language, produce RequirementInput
├─ Step 2: EvidenceCollectorService     → Fetch authoritative data from primary + academic sources
├─ Step 3: CoreAnalysisService          → Select school/form, design pruning/wiring/care with physiology grounding
├─ Step 4: KnowledgeUpdaterService      → Query knowledge base, grade citations by tier, flag gaps
├─ Step 5: AdvisorService               → Synthesize into verdict + risks + evidence chain + disclosure
└─ Step 6: QualityGateSystem            → Enforce U1-U6 + G1-G4 with auto-fix + 2-retry max
```

## Python Package

The skill is implemented as a production-grade Python package:

```
bonsai_penjing/
├── models.py           # 30+ Pydantic models (RequirementInput through HarnessReport)
├── config.py           # Structured config, VI/EN translations, structured logging
├── errors.py           # HarnessError, DegradationTracker, retry, safe_execute
├── context.py          # ContextWindow, ConversationMemory, ContextPipeline
├── harness.py          # HarnessOrchestrator + render_report_markdown
├── cli.py              # Click CLI: bonsai analyze/validate/crawl/info
└── services/
    ├── gather_requirements.py   # Step 1
    ├── evidence_collector.py    # Step 2
    ├── domain_knowledge.py      # 7 species profiles, 10+ forms, pruning physiology
    ├── core_analysis.py         # Step 3
    ├── knowledge_updater.py     # Step 4 (8 DOI-cited references)
    ├── advisor.py               # Step 5
    └── quality_gates.py         # Step 6 (10 gates)
```

## Sub-Skills

| `skills/sub-gather-requirements.md` | Step 1 — Clarify the object of analysis, constraints, timeframe, available inputs, target audience, and language before any data fetching. |
| `skills/sub-evidence-collector.md` | Step 2 — Fetch authoritative real-time and reference data for the object: current status/parameters, authoritative documents/standards, and recent developments from domain and academic sources. |
| `skills/sub-core-analysis.md` | Step 3 — Analyze and design a bonsai/penjing artwork from a classical-school perspective, proposing pruning, wiring, rock/landscape composition, and care grounded in pruning physiology and award-winning practitioner references. |
| `skills/sub-knowledge-updater.md` | Step 4 — Query SECOND-KNOWLEDGE-BRAIN.md for authoritative academic and professional evidence; surface citations with tier labels and flag gaps for the crawl pipeline. |
| `skills/sub-advisor.md` | Step 5 — Synthesize all prior analysis into a risk-disclosed conclusion with a full evidence chain and recommended actions. |

## Tools Required

- **WebSearch** — live domain news, reports, standards updates
- **WebFetch** — scrape Bonsai/Penjing Art & Botanical Pruning Design authoritative sources
- **Read / Write** — read SECOND-KNOWLEDGE-BRAIN.md; append knowledge entries
- **Bash** — run `tools/knowledge_updater.py` for periodic crawl
- **Skill** — invoke sub-skills sequentially through the harness
- **CLI** — `bonsai analyze/validate/crawl/info`

## Knowledge Sources

### Domain Authoritative Sources
- Bonsai Clubs International — bonsai-bci.com
- National Bonsai Foundation — bonsai-nbf.org
- Bonsai Empire — bonsaiempire.com
- American Bonsai Society — absbonsai.org
- Ueki Bonsai (Vietnam) / Vietnam Bonsai Association
- Royal Horticultural Society (RHS) pruning references
- International Shohin Bonsai Association

### Academic & Research Sources
- HortScience / HortTechnology — ASHS
- Scientia Horticulturae — Elsevier
- Trees — Springer (arboriculture & pruning physiology)
- Journal of Horticulture & Forestry
- Environmental & Experimental Botany — Elsevier
- Frontiers in Plant Science (pruning physiology)

### Academic Crawl Targets
- Semantic Scholar / Google Scholar for "Bonsai/Penjing Art & Botanical Pruning Design" keyword clusters
- ArXiv API for relevant categories
- RSS feeds from domain sources

---

## Supporting Python Tools

| File | Purpose |
|------|---------|
| `tools/knowledge_updater.py` | Crawl pipeline: fetches latest papers + news → scores → appends to SECOND-KNOWLEDGE-BRAIN.md |
| `tools/test_knowledge_updater.py` | Unit tests for hash, scoring, entry formatting |
| `tools/run_test_scenarios.py` | Structural & content validator for 8-File Contract |

---

## Automated Knowledge Update Schedule

```cron
# Weekly academic update (Mondays 8:00 AM)
0 8 * * 1 python D:/972026/170-bonsai-penjing-design-automation/tools/knowledge_updater.py >> logs/knowledge_update.log 2>&1

# Daily news update (Daily 7:00 AM)
0 7 * * * python D:/972026/170-bonsai-penjing-design-automation/tools/knowledge_updater.py --news-only >> logs/knowledge_news.log 2>&1
```

Manual: `python tools/knowledge_updater.py --dry-run` | `--keywords "..."` | `--news-only`

---

## Active Development Tasks

- [x] Phase 0: Architecture & source map (CLAUDE.md, PROJECT-detail.md, PDPT.md)
- [x] Phase 1: Core sub-skills (5 production-grade .md files)
- [x] Phase 2: Main harness + quality gates + degradation (10 gates)
- [x] Phase 3: Knowledge pipeline + species profiles + tests
- [x] Phase 4: Testing & validation (99 tests pass)
- [x] Phase 5: Integration & polish — PRODUCTION READY v2.0.0
- [x] Phase 6: Production architecture upgrade — PRODUCTION READY v3.0.0
  - Modular directories: /config, /scripts, /references, /assets
  - Hooks system for lifecycle events
  - Tool registry with schema validation
  - SKILL.md registry documentation
  - Automation scripts (setup, seed, batch)
  - Domain references (species profiles, form templates)
  - System diagrams and report templates

---

## Testing

```bash
pytest tests/ -v                           # All 99 tests
python tools/test_knowledge_updater.py     # Knowledge updater unit tests
python tools/run_test_scenarios.py         # Structural validation
```

---

## References

- `PROJECT-detail.md` — full technical specification
- `PROJECT-DEVELOPMENT-PHASE-TRACKING.md` — build roadmap (100% complete)
- `SECOND-KNOWLEDGE-BRAIN.md` — self-improving knowledge base
- `pyproject.toml` — package metadata and dependencies
