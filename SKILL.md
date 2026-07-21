---
name: bonsai-penjing-design-automation
description: Bonsai & Penjing Design Analysis & Automation (Japan, China, Vietnam Schools) — production-grade AI agent harness. Use this skill whenever the user asks about bonsai design, penjing art, horticultural pruning, tree shaping, wiring techniques, rock landscapes, plant care for artistic purposes, or needs analysis of specimen trees from classical art school perspectives. Also use for questions about bonsai forms (chokkan, shakan, moyogi, etc.), pruning physiology, apical dominance, ramification, or award-winning bonsai techniques. This skill provides evidenced, risk-disclosed analysis with academic citations and professional practitioner references.
---

# SKILL.md — bonsai-penjing-design-automation Registry

## Overview

`bonsai-penjing-design-automation` is a production-grade AI agent harness for the **Bonsai/Penjing Art & Botanical Pruning Design** domain. It implements a 6-step orchestrated workflow that combines real-time data aggregation, classical design analysis, and academic research into risk-disclosed, evidenced outputs.

## Skill Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  MAIN HARNESS (main.md)                     │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  1. Requirements Service (sub-gather-requirements)   │  │
│  │  2. Evidence Collector (sub-evidence-collector)      │  │
│  │  3. Core Analysis (sub-core-analysis)                │  │
│  │  4. Knowledge Updater (sub-knowledge-updater)        │  │
│  │  5. Advisor (sub-advisor)                            │  │
│  │  6. Quality Gate System (10 gates, auto-fix)         │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Skill Registration

### Primary Skill

**Name:** `bonsai-penjing-design-automation`

**Trigger Phrases:**
- "analyze bonsai" / "analyze penjing" / "design bonsai"
- "bonsai design advice" / "penjing design recommendation"
- "pruning plan for [species]" / "wiring strategy for [tree]"
- "bonsai form selection" / "classical bonsai school"
- "rock planting design" / "forest composition"
- "[species] bonsai care" / "repotting advice"

**Description:**
> Bonsai & Penjing Design Analysis & Automation (Japan, China, Vietnam Schools) — production-grade AI agent harness. Use this skill whenever the user asks about bonsai design, penjing art, horticultural pruning, tree shaping, wiring techniques, rock landscapes, plant care for artistic purposes, or needs analysis of specimen trees from classical art school perspectives.

### Sub-Skills

| Sub-Skill | File | Purpose | Trigger |
|-----------|------|---------|---------|
| Requirements Service | `sub-gather-requirements.md` | Clarify analysis object, constraints, language | Step 1 of harness |
| Evidence Collector | `sub-evidence-collector.md` | Fetch authoritative data and standards | Step 2 of harness |
| Core Analysis | `sub-core-analysis.md` | Design analysis from classical school perspective | Step 3 of harness |
| Knowledge Updater | `sub-knowledge-updater.md` | Query knowledge base for academic evidence | Step 4 of harness |
| Advisor | `sub-advisor.md` | Synthesize into risk-disclosed conclusion | Step 5 of harness |

## Skill Resolution

### Resolution Order

1. **User invokes main skill** → `/bonsai-penjing-design-automation [query]`
2. **Language detection** → Vietnamese or English (regex-based)
3. **Requirements gathering** → Structured input via conversation
4. **Sequential execution** → Steps 1-6 in order
5. **Quality gate enforcement** → All gates must pass with auto-fix

### Input Resolution

Skills resolve inputs via a **cascading priority**:

1. **Explicit user input** (highest priority)
2. **Clarifying questions** (max 2, then proceed with assumptions)
3. **Knowledge base defaults** (from SECOND-KNOWLEDGE-BRAIN.md)
4. **Hard-coded defaults** (lowest priority, well-documented)

## Skill Execution

### Execution Flow

```python
# Pseudo-code representation of execution flow
def execute_harness(user_input: str) -> HarnessReport:
    # Step 0: Pre-flight checks
    language = detect_language(user_input)
    logger = setup_logging()

    # Step 1: Gather requirements
    requirements = RequirementsService.gather(user_input, language)

    # Step 2: Collect evidence
    evidence = EvidenceCollectorService.collect(requirements)

    # Step 3: Core analysis
    analysis = CoreAnalysisService.analyze(requirements, evidence)

    # Step 4: Knowledge lookup
    knowledge = KnowledgeUpdaterService.query(analysis.topics)

    # Step 5: Synthesize
    advisory = AdvisorService.synthesize(analysis, evidence, knowledge)

    # Step 6: Quality gates
    report = QualityGateSystem.validate(advisory, max_retries=2)

    return report
```

### Graceful Degradation

The harness implements **5 degradation levels**:

| Level | Condition | Behavior |
|-------|-----------|----------|
| 0 | Full capability | All services operational |
| 1 | Web source timeout | Fall back to knowledge base |
| 2 | Knowledge base gap | Use cached benchmarks, flag limitation |
| 3 | Core analysis failure | Provide best-effort, warn user |
| 4 | Critical failure | Explicit LIMITATION banner, no recommendations |

### Error Handling

All service calls use **safe_execute wrapper**:

```python
from bonsai_penjing.errors import safe_execute

result = safe_execute(
    risky_function,
    arg1, arg2,
    default_return={},
    raise_on_error=False,
    on_error=lambda e: logger.warning(f"Failed: {e}")
)
```

## Input/Output JSON Schemas

### RequirementInput Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "RequirementInput",
  "type": "object",
  "properties": {
    "object_of_analysis": {
      "type": "string",
      "description": "The primary object being analyzed (e.g., specific tree, species, design concept)"
    },
    "scope": {
      "type": "string",
      "enum": ["full_design", "pruning_only", "wiring_only", "care_only", "rock_composition", "general"],
      "description": "Analysis scope"
    },
    "timeframe": {
      "type": "string",
      "description": "Target timeframe for design implementation (e.g., '3 months', '1 year')"
    },
    "available_inputs": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Available input materials (photos, measurements, current state descriptions)"
    },
    "target_audience": {
      "type": "string",
      "enum": ["practitioner", "researcher", "learner", "decision_maker"],
      "description": "Target audience for the analysis"
    },
    "language": {
      "type": "string",
      "enum": ["english", "vietnamese"],
      "description": "Output language"
    },
    "analysis_type": {
      "type": "string",
      "enum": ["design_advice", "feasibility", "risk_assessment", "educational", "method_explanation"],
      "description": "Type of analysis requested"
    },
    "constraints": {
      "type": "object",
      "properties": {
        "climate": {"type": "string"},
        "space_limitations": {"type": "string"},
        "skill_level": {"type": "string"},
        "budget": {"type": "string"}
      }
    }
  },
  "required": ["object_of_analysis", "scope", "language"]
}
```

### EvidenceBundle Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "EvidenceBundle",
  "type": "object",
  "properties": {
    "current_data": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "source": {"type": "string"},
          "data": {"type": "object"},
          "timestamp": {"type": "string", "format": "date-time"},
          "confidence": {"type": "number", "minimum": 0, "maximum": 1}
        }
      }
    },
    "authoritative_docs": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "title": {"type": "string"},
          "source": {"type": "string"},
          "url": {"type": "string"},
          "tier": {"type": "integer", "minimum": 1, "maximum": 4},
          "relevance": {"type": "number", "minimum": 0, "maximum": 1}
        }
      }
    },
    "recent_news": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "title": {"type": "string"},
          "source": {"type": "string"},
          "url": {"type": "string"},
          "published_date": {"type": "string"},
          "summary": {"type": "string"}
        }
      }
    }
  }
}
```

### CoreAnalysisOutput Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "CoreAnalysisOutput",
  "type": "object",
  "properties": {
    "school_selection": {
      "type": "object",
      "properties": {
        "school": {"type": "string", "enum": ["japanese", "chinese", "vietnamese"]},
        "rationale": {"type": "string"},
        "key_principles": {"type": "array", "items": {"type": "string"}}
      }
    },
    "form_analysis": {
      "type": "object",
      "properties": {
        "primary_form": {"type": "string"},
        "alternative_forms": {"type": "array", "items": {"type": "string"}},
        "suitability_score": {"type": "number", "minimum": 0, "maximum": 1}
      }
    },
    "pruning_plan": {
      "type": "object",
      "properties": {
        "immediate_actions": {"type": "array", "items": {"type": "string"}},
        "seasonal_schedule": {"type": "object"},
        "physiology_basis": {"type": "string"},
        "timing_justification": {"type": "string"}
      }
    },
    "wiring_plan": {
      "type": "object",
      "properties": {
        "technique": {"type": "string"},
        "priority_branches": {"type": "array", "items": {"type": "string"}},
        "timeline": {"type": "string"},
        "risk_considerations": {"type": "array", "items": {"type": "string"}}
      }
    },
    "care_plan": {
      "type": "object",
      "properties": {
        "watering": {"type": "string"},
        "soil_composition": {"type": "string"},
        "feeding_schedule": {"type": "string"},
        "repotting_interval": {"type": "string"}
      }
    }
  }
}
```

### HarnessReport Schema (Final Output)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "HarnessReport",
  "type": "object",
  "properties": {
    "metadata": {
      "type": "object",
      "properties": {
        "report_id": {"type": "string", "format": "uuid"},
        "generated_at": {"type": "string", "format": "date-time"},
        "language": {"type": "string"},
        "version": {"type": "string"}
      }
    },
    "executive_summary": {"type": "string"},
    "inputs_scope": {"type": "string"},
    "evidence_collected": {
      "type": "object",
      "properties": {
        "sources_count": {"type": "integer"},
        "academic_sources": {"type": "integer"},
        "tier_breakdown": {"type": "object"}
      }
    },
    "analysis_scorecard": {
      "type": "object",
      "properties": {
        "school_selection": {"type": "object"},
        "form_analysis": {"type": "object"},
        "pruning_plan": {"type": "object"},
        "wiring_plan": {"type": "object"},
        "care_plan": {"type": "object"}
      }
    },
    "action_plan": {"type": "string"},
    "academic_evidence": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "citation": {"type": "string"},
          "tier": {"type": "integer"},
          "relevance": {"type": "string"}
        }
      }
    },
    "disclosure": {"type": "string"},
    "recommendation": {
      "type": "string",
      "enum": [
        "award_level_design",
        "solid_design_refinements",
        "needs_significant_rework",
        "inconclusive"
      ]
    },
    "quality_gate_results": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "gate_id": {"type": "string"},
          "gate_name": {"type": "string"},
          "passed": {"type": "boolean"},
          "attempts": {"type": "integer"}
        }
      }
    }
  },
  "required": [
    "metadata",
    "executive_summary",
    "disclosure",
    "recommendation"
  ]
}
```

## Quality Gates

### Universal Gates (U1-U6)

| Gate | Criterion | Auto-Fix |
|------|-----------|----------|
| U1 | ≥3 sources cited, ≥1 academic/authoritative | Query knowledge base for additional sources |
| U2 | Safety/risk/limitation disclosure present | Prepend disclosure section |
| U3 | Evidence hierarchy stated per source | Label sources with Tier 1-4 |
| U4 | Language matches user preference | Translate/adjust output language |
| U5 | Output uses declared template | Restructure to template |
| U6 | Every claim traceable to source or flagged | Add "[Analyst judgment]" tags |

### Domain Gates (G1-G4)

| Gate | Criterion | Auto-Fix |
|------|-----------|----------|
| G1 | School & classical form identified | Add school selection section |
| G2 | Pruning/wiring grounded in physiology | Add physiology justification |
| G3 | Species-specific care provided | Add species profile reference |
| G4 | 3-scenario analysis present | Generate scenarios |

## Tool Definitions

### Built-in Tools

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `WebSearch` | Fetch recent domain news | Query string | Search results |
| `WebFetch` | Scrape authoritative sources | URL | Content |
| `Read` | Read knowledge base | File path | File contents |
| `Write` | Append knowledge entries | Path, content | Success |
| `Bash` | Run crawl pipeline | Command | Output |

### Dynamic Tool Invocation

Agents can dynamically invoke tools via the **ToolRegistry**:

```python
from bonsai_penjing.tools import ToolRegistry

registry = ToolRegistry()
result = registry.invoke(
    tool_name="web_search",
    params={"query": "bonsai pruning apical dominance research"}
)
```

## Validation

### Input Validation

All inputs are validated via **Pydantic models**:

```python
from bonsai_penjing.models import RequirementInput
from pydantic import ValidationError

try:
    requirements = RequirementInput(**user_data)
except ValidationError as e:
    # Handle validation error
    pass
```

### Output Validation

Final reports are validated against the **HarnessReport schema**:

```python
from bonsai_penjing.models import HarnessReport

try:
    report = HarnessReport(**analysis_result)
except ValidationError as e:
    # Trigger quality gate remediation
    pass
```

### Quality Gate Validation

All 10 gates are checked with **2-retry maximum**:

```python
from bonsai_penjing.services import QualityGateSystem

qgs = QualityGateSystem()
result = qgs.validate_all(report, max_retries=2)
```

## Extension Points

### Adding New Sub-Skills

1. Create `sub-new-skill.md` with required sections
2. Update `skills/main.md` to invoke new sub-skill
3. Add corresponding service in `bonsai_penjing/services/`
4. Add tests in `tests/`
5. Update this SKILL.md registry

### Adding New Quality Gates

1. Define gate in `PROJECT-detail.md`
2. Add gate logic to `bonsai_penjing/services/quality_gates.py`
3. Update gate table in `skills/main.md`
4. Add gate-specific tests

### Custom Knowledge Sources

Add to `config/defaults.yaml`:

```yaml
knowledge:
  custom_sources:
    - name: "My Bonsai Society"
      url: "https://mybonsaisociety.org"
      tier: 2
```

## CLI Usage

```bash
# Analyze a bonsai design
bonsai analyze --input "Design a Japanese maple formal upright"

# Validate a report
bonsai validate --report path/to/report.json

# Run knowledge crawl
bonsai crawl --dry-run

# Show system info
bonsai info
```

## Python API Usage

```python
from bonsai_penjing import HarnessOrchestrator
from bonsai_penjing.models import RequirementInput

# Create orchestrator
orchestrator = HarnessOrchestrator()

# Run analysis
requirements = RequirementInput(
    object_of_analysis="Japanese Maple",
    scope="full_design",
    language="english"
)

report = orchestrator.run(requirements)
print(report.executive_summary)
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test module
pytest tests/test_harness.py -v

# Run with coverage
pytest tests/ --cov=bonsai_penjing --cov-report=html
```

## License

MIT License — See LICENSE file for details.
