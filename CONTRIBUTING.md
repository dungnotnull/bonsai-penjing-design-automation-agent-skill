# Contributing to bonsai-penjing-design-automation

Thanks for your interest in contributing! This project automates Bonsai & Penjing design analysis across Japan, China, and Vietnam classical schools.

## Development Setup

```bash
# Clone and install
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=bonsai_penjing --cov-report=html
```

## Project Structure

```
bonsai_penjing/          # Python package
├── models.py            # Pydantic v2 data models
├── config.py            # Configuration, translations, logging
├── errors.py            # Error handling, degradation, retry
├── context.py           # AI agent context management
├── harness.py           # Main orchestrator (6-step pipeline)
├── cli.py               # Click CLI
└── services/            # 6 service modules (one per step)
skills/                  # Claude Code skill markdown files
tools/                   # Knowledge crawl pipeline
tests/                   # Pytest suite (99 tests)
```

## Adding a New Form

1. Add the form definition to `bonsai_penjing/services/domain_knowledge.py` in `FORM_MATCHING`
2. Add suitable species to the form's `suitable_species` list
3. Add a test in `tests/test_full_pipeline.py`
4. Update the `BonsaiForm` enum in `models.py` if needed

## Adding a New Species

1. Add the species profile to `SPECIES_PROFILES` in `domain_knowledge.py`
2. Include: scientific name, common names, watering, soil mix, repot cycle, fertilisation, pests, seasonal notes, pruning timing, wiring notes, apical dominance
3. Add a test case in `TestCoreAnalysis.test_species_identification`

## Quality Gates

All 10 gates must pass before a report is considered valid. Gates are enforced in `bonsai_penjing/services/quality_gates.py`.

## Testing

- All new features require tests
- Run `pytest tests/` before submitting
- Target: zero warnings, zero failures

## Code Style

- Type hints required on all public functions
- Use Pydantic models for all data structures
- Max line length: 120 characters
- Follow existing patterns in the codebase
