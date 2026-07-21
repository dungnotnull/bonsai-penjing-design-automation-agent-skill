#!/usr/bin/env python3
"""
Batch analysis script for bonsai-penjing-design-automation.

This script:
- Processes multiple analysis requests from a file
- Generates reports in bulk
- Supports JSON/CSV input formats
- Outputs results to specified directory
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import click

# Import harness components
try:
    from bonsai_penjing import HarnessOrchestrator
    from bonsai_penjing.models import RequirementInput
    from bonsai_penjing.config import get_settings
except ImportError:
    click.echo("Error: bonsai_penjing package not found. Run setup.py first.", err=True)
    sys.exit(1)


def load_input_file(input_path: Path) -> List[Dict[str, Any]]:
    """Load analysis requests from input file."""
    suffix = input_path.suffix.lower()

    if suffix == ".json":
        with open(input_path) as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and "requests" in data:
                return data["requests"]
            else:
                raise ValueError("Invalid JSON format")

    elif suffix == ".csv":
        import csv

        requests = []
        with open(input_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                requests.append(dict(row))
        return requests

    else:
        raise ValueError(f"Unsupported file format: {suffix}")


def validate_request(request: Dict[str, Any]) -> bool:
    """Validate a single request."""
    required_fields = ["object_of_analysis", "scope", "language"]

    for field in required_fields:
        if field not in request:
            click.echo(f"Error: Missing required field: {field}", err=True)
            return False

    return True


@click.command()
@click.option(
    "--input",
    "-i",
    "input_path",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Input file with analysis requests (JSON/CSV)",
)
@click.option(
    "--output",
    "-o",
    "output_dir",
    type=click.Path(path_type=Path),
    default="output",
    help="Output directory for reports",
)
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["markdown", "json", "both"]),
    default="both",
    help="Output format for reports",
)
@click.option(
    "--parallel",
    "-p",
    "parallel_jobs",
    type=int,
    default=1,
    help="Number of parallel analysis jobs",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Verbose output",
)
def batch_analyze(
    input_path: Path,
    output_dir: Path,
    output_format: str,
    parallel_jobs: int,
    verbose: bool,
) -> None:
    """Run batch analysis on multiple requests."""
    click.echo(f"Loading input from: {input_path}")

    try:
        requests = load_input_file(input_path)
        click.echo(f"Found {len(requests)} analysis requests")
    except Exception as e:
        click.echo(f"Error loading input: {e}", err=True)
        sys.exit(1)

    # Create output directory
    output_dir = output_dir / f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize orchestrator
    click.echo("Initializing harness...")
    settings = get_settings()
    orchestrator = HarnessOrchestrator()

    # Process requests
    results = []
    failed = []

    for i, request in enumerate(requests, 1):
        click.echo(f"[{i}/{len(requests)}] Processing: {request.get('object_of_analysis', 'Unknown')}")

        # Validate request
        if not validate_request(request):
            failed.append((i, request, "Validation failed"))
            continue

        try:
            # Create requirement input
            requirements = RequirementInput(**request)

            # Run analysis
            report = orchestrator.run(requirements)

            # Save report
            report_name = f"report_{i:03d}_{request['object_of_analysis'][:30].replace(' ', '_')}"
            report_path = output_dir / report_name

            if output_format in ["markdown", "both"]:
                md_path = report_path.with_suffix(".md")
                md_path.write_text(report.to_markdown(), encoding="utf-8")
                if verbose:
                    click.echo(f"  Saved: {md_path}")

            if output_format in ["json", "both"]:
                json_path = report_path.with_suffix(".json")
                json_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
                if verbose:
                    click.echo(f"  Saved: {json_path}")

            results.append((i, request, report))

        except Exception as e:
            click.echo(f"  Error: {e}", err=True)
            failed.append((i, request, str(e)))

    # Generate summary
    summary_path = output_dir / "summary.json"
    summary = {
        "timestamp": datetime.utcnow().isoformat(),
        "total_requests": len(requests),
        "successful": len(results),
        "failed": len(failed),
        "output_format": output_format,
        "failed_details": [
            {"index": i, "request": req, "error": err} for i, req, err in failed
        ],
    }

    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # Print summary
    click.echo()
    click.echo("=" * 60)
    click.echo("Batch Analysis Summary")
    click.echo("=" * 60)
    click.echo(f"Total requests: {len(requests)}")
    click.echo(f"Successful: {len(results)}")
    click.echo(f"Failed: {len(failed)}")
    click.echo(f"Output directory: {output_dir}")
    click.echo("=" * 60)

    if failed:
        click.echo("\nFailed requests:")
        for i, req, err in failed:
            click.echo(f"  [{i}] {req.get('object_of_analysis', 'Unknown')}: {err}")


if __name__ == "__main__":
    batch_analyze()
