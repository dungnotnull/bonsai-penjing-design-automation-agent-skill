# Report Templates

## Analysis Report Template (Markdown)

This is the standard template for bonsai-penjing analysis reports.

```markdown
# {analysis_report}

## {executive_summary}

{Brief summary of the analysis, key findings, and recommendation}

## {inputs_scope}

**Object of Analysis:** {object_of_analysis}
**Scope:** {scope}
**Timeframe:** {timeframe}
**Target Audience:** {target_audience}
**Language:** {language}

**Provided Inputs:**
- {input_item_1}
- {input_item_2}

**Constraints:**
- {constraint_1}
- {constraint_2}

---

## {evidence_collected}

### Current Data Sources
| Source | URL | Tier | Recency |
|--------|-----|------|---------|
| {source_1} | {url_1} | {tier_1} | {date_1} |
| {source_2} | {url_2} | {tier_2} | {date_2} |

### Authoritative Documents
| Document | Source | Tier |
|----------|--------|------|
| {doc_1} | {source_1} | {tier_1} |
| {doc_2} | {source_2} | {tier_2} |

### Evidence Tier Breakdown
- **Tier 1 (Peer-reviewed):** {count} sources
- **Tier 2 (Professional):** {count} sources
- **Tier 3 (Industry):** {count} sources
- **Tier 4 (General):** {count} sources

---

## {analysis_scorecard}

### School Selection
**Primary School:** {school_name}
**Rationale:** {school_rationale}

**Key Principles Applied:**
- {principle_1}
- {principle_2}

### Form Analysis
**Primary Form:** {form_name}
**Suitability Score:** {score}/1.0

**Form Characteristics:**
- {characteristic_1}
- {characteristic_2}

**Alternative Forms Considered:**
- {alt_form_1}: {reasoning}
- {alt_form_2}: {reasoning}

### Pruning Plan
**Immediate Actions:**
1. {action_1} - {timing}
2. {action_2} - {timing}

**Seasonal Schedule:**
- {season_1}: {activity}
- {season_2}: {activity}

**Physiology Basis:**
{physiology_justification - referencing apical dominance, CODIT, etc.}

**Timing Justification:**
{timing_reasoning - referencing dormancy, sap flow, etc.}

### Wiring Plan
**Technique:** {wiring_technique}
**Best Timing:** {wiring_timing}

**Priority Branches:**
1. {branch_1}: {direction}
2. {branch_2}: {direction}

**Timeline:** {duration_months} months maximum wire duration

**Risk Considerations:**
- {risk_1}
- {risk_2}

### Care Plan
**Watering:**
- Frequency: {watering_frequency}
- Method: {watering_method}

**Soil Composition:**
- Akadama: {percent}%
- Pumice: {percent}%
- Lava Rock: {percent}%
- Organic: {percent}%

**Feeding Schedule:**
- {season_1}: {fertilizer_type}
- {season_2}: {fertilizer_type}

**Repotting Interval:**
- Young trees: Every {young_years} years
- Old trees: Every {old_years} years

---

## {action_plan}

### Recommended Actions
**Priority 1 (Immediate):**
1. {action_1}

**Priority 2 (Short-term):**
1. {action_2}

**Priority 3 (Long-term):**
1. {action_3}

### Timeline
| Phase | Duration | Key Activities |
|-------|----------|----------------|
| {phase_1} | {duration_1} | {activities_1} |
| {phase_2} | {duration_2} | {activities_2} |

### Resource Requirements
- {resource_1}
- {resource_2}

---

## {academic_evidence}

### Key Citations

1. **{citation_1_title}**
   - Authors: {authors}
   - Year: {year}
   - Tier: {tier}
   - Relevance: {relevance_summary}
   - DOI: {doi}

2. **{citation_2_title}**
   - Authors: {authors}
   - Year: {year}
   - Tier: {tier}
   - Relevance: {relevance_summary}
   - DOI: {doi}

### Evidence Synthesis
{synthesis of how academic evidence supports the analysis}

### Knowledge Gaps Identified
- {gap_1}: {suggested_research}
- {gap_2}: {suggested_research}

---

## {disclosure}

### Analysis Limitations
{limitation_statement}

### Risk Factors
1. {risk_1}: {mitigation}
2. {risk_2}: {mitigation}

### Professional Disclaimers
{disclaimer_content}

---

## {recommendation}

**Verdict:** {recommendation_category}

**Confidence Level:** {confidence_level}/1.0

### Scenarios

**Scenario 1: Best Case**
- Conditions: {best_case_conditions}
- Outcome: {best_case_outcome}
- Probability: {probability}%

**Scenario 2: Expected Case**
- Conditions: {expected_case_conditions}
- Outcome: {expected_case_outcome}
- Probability: {probability}%

**Scenario 3: Worst Case**
- Conditions: {worst_case_conditions}
- Outcome: {worst_case_outcome}
- Probability: {probability}%

### Recommended Actions
{final_action_recommendations}

---

## {post_gate_checklist}

### Quality Gate Results
| Gate | Status | Attempts |
|------|--------|----------|
| U1: Source Count (≥3, ≥1 academic) | {status_U1} | {attempts_U1} |
| U2: Disclosure Present | {status_U2} | {attempts_U2} |
| U3: Evidence Tier Stated | {status_U3} | {attempts_U3} |
| U4: Language Match | {status_U4} | {attempts_U4} |
| U5: Template Format | {status_U5} | {attempts_U5} |
| U6: Claims Traceable | {status_U6} | {attempts_U6} |
| G1: School/Form ID | {status_G1} | {attempts_G1} |
| G2: Physiology Grounding | {status_G2} | {attempts_G2} |
| G3: Species-Specific Care | {status_G3} | {attempts_G3} |
| G4: Scenario Analysis | {status_G4} | {attempts_G4} |

### Auto-Fixes Applied
{list_of_any_auto_fixes_applied_during_generation}

---

**Report Generated:** {timestamp}
**Report ID:** {report_id}
**Version:** {version}
**Analysis Duration:** {duration_seconds} seconds
```

## JSON Schema for Reports

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "BonsaiPenjingAnalysisReport",
  "type": "object",
  "required": [
    "metadata",
    "executive_summary",
    "inputs_scope",
    "evidence_collected",
    "analysis_scorecard",
    "action_plan",
    "academic_evidence",
    "disclosure",
    "recommendation"
  ],
  "properties": {
    "metadata": {
      "type": "object",
      "required": ["report_id", "generated_at", "language", "version"],
      "properties": {
        "report_id": {"type": "string", "format": "uuid"},
        "generated_at": {"type": "string", "format": "date-time"},
        "language": {"type": "string", "enum": ["english", "vietnamese"]},
        "version": {"type": "string"},
        "duration_seconds": {"type": "number"}
      }
    },
    "executive_summary": {"type": "string", "minLength": 50},
    "inputs_scope": {
      "type": "object",
      "properties": {
        "object_of_analysis": {"type": "string"},
        "scope": {"type": "string"},
        "timeframe": {"type": "string"},
        "target_audience": {"type": "string"},
        "provided_inputs": {"type": "array", "items": {"type": "string"}},
        "constraints": {"type": "array", "items": {"type": "string"}}
      }
    },
    "evidence_collected": {
      "type": "object",
      "properties": {
        "sources": {"type": "array", "items": {"$ref": "#/definitions/source"}},
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
    "action_plan": {
      "type": "object",
      "properties": {
        "recommended_actions": {"type": "array", "items": {"type": "string"}},
        "timeline": {"type": "array", "items": {"$ref": "#/definitions/phase"}},
        "resource_requirements": {"type": "array", "items": {"type": "string"}}
      }
    },
    "academic_evidence": {
      "type": "array",
      "items": {"$ref": "#/definitions/citation"}
    },
    "disclosure": {
      "type": "object",
      "properties": {
        "limitations": {"type": "array", "items": {"type": "string"}},
        "risk_factors": {"type": "array", "items": {"$ref": "#/definitions/risk"}},
        "disclaimers": {"type": "array", "items": {"type": "string"}}
      }
    },
    "recommendation": {
      "type": "object",
      "properties": {
        "verdict": {
          "type": "string",
          "enum": ["award_level_design", "solid_design_refinements", "needs_significant_rework", "inconclusive"]
        },
        "confidence_level": {"type": "number", "minimum": 0, "maximum": 1},
        "scenarios": {"type": "array", "items": {"$ref": "#/definitions/scenario"}},
        "recommended_actions": {"type": "array", "items": {"type": "string"}}
      }
    },
    "quality_gate_results": {
      "type": "array",
      "items": {"$ref": "#/definitions/gate_result"}
    }
  },
  "definitions": {
    "source": {
      "type": "object",
      "properties": {
        "name": {"type": "string"},
        "url": {"type": "string"},
        "tier": {"type": "integer", "minimum": 1, "maximum": 4},
        "recency": {"type": "string"}
      }
    },
    "citation": {
      "type": "object",
      "properties": {
        "title": {"type": "string"},
        "authors": {"type": "array", "items": {"type": "string"}},
        "year": {"type": "integer"},
        "tier": {"type": "integer"},
        "relevance": {"type": "string"},
        "doi": {"type": "string"}
      }
    },
    "risk": {
      "type": "object",
      "properties": {
        "description": {"type": "string"},
        "mitigation": {"type": "string"}
      }
    },
    "scenario": {
      "type": "object",
      "properties": {
        "name": {"type": "string"},
        "conditions": {"type": "string"},
        "outcome": {"type": "string"},
        "probability": {"type": "number"}
      }
    },
    "phase": {
      "type": "object",
      "properties": {
        "name": {"type": "string"},
        "duration": {"type": "string"},
        "activities": {"type": "array", "items": {"type": "string"}}
      }
    },
    "gate_result": {
      "type": "object",
      "properties": {
        "gate_id": {"type": "string"},
        "gate_name": {"type": "string"},
        "passed": {"type": "boolean"},
        "attempts": {"type": "integer"}
      }
    }
  }
}
```
