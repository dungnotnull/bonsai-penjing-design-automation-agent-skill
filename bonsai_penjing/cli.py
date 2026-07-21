"""
CLI entry point for bonsai-penjing-design-automation.
Provides the `bonsai` command with full harness execution and `bonsai-crawl` for knowledge base updates.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import click

from bonsai_penjing import __version__
from bonsai_penjing.config import setup_logging, BRAIN_PATH
from bonsai_penjing.harness import HarnessOrchestrator, render_report_markdown

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass


@click.group()
@click.version_option(version=__version__, prog_name="bonsai-penjing-design-automation")
@click.option("--log-level", default="INFO", help="Logging level")
@click.option("--json-log", is_flag=True, help="Output logs as JSON")
@click.pass_context
def main(ctx: click.Context, log_level: str, json_log: bool) -> None:
    """Bonsai & Penjing Design Analysis & Automation — Japan, China, Vietnam Schools.

    Production-grade AI agent harness for evidence-backed bonsai/penjing design analysis.
    """
    ctx.ensure_object(dict)
    setup_logging(level=log_level, json_format=json_log)


@main.command("analyze")
@click.argument("query", nargs=-1)
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output file path (markdown or json)")
@click.option("--format", "-f", "output_format", type=click.Choice(["markdown", "json"]), default="markdown",
              help="Output format")
@click.option("--language", "-l", "forced_lang", type=click.Choice(["en", "vi"]), help="Force output language")
@click.option("--context-tokens", type=int, default=180_000, help="Context window budget in tokens")
@click.pass_context
def analyze(
    ctx: click.Context,
    query: tuple[str, ...],
    output: Optional[Path],
    output_format: str,
    forced_lang: Optional[str],
    context_tokens: int,
) -> None:
    """Run the full bonsai/penjing analysis harness on a query.

    \b
    Examples:
        bonsai analyze "Analyze a juniper bonsai in shakan style"
        bonsai analyze "Thiết kế cây thông Nhật Bản theo trường phái Nhật"
        bonsai analyze --output report.md "Design a ficus penjing landscape"
    """
    user_message = " ".join(query)
    if not user_message.strip():
        click.echo("Error: Please provide a query to analyze.", err=True)
        click.echo("Example: bonsai analyze \"Design a juniper in moyogi style\"", err=True)
        sys.exit(1)

    click.echo(f"Analyzing: {user_message[:100]}...")
    click.echo("Running 6-step harness pipeline...")

    orchestrator = HarnessOrchestrator(context_budget_tokens=context_tokens)
    report = orchestrator.execute(user_message)

    if output_format == "json":
        result_text = report.model_dump_json(indent=2)
    else:
        result_text = render_report_markdown(report)

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        ext = ".json" if output_format == "json" else ".md"
        path = output if output.suffix else output.with_suffix(ext)
        path.write_text(result_text, encoding="utf-8")
        click.echo(f"Report saved to: {path}")
    else:
        click.echo(result_text)

    if report.errors:
        click.echo(f"\n⚠️  Completed with {len(report.errors)} error(s)")
    else:
        verdict = report.conclusion.verdict.value if report.conclusion else "N/A"
        quality = "PASS" if (report.quality_report and report.quality_report.all_passed) else "LIMITATIONS"
        click.echo(f"\n✅ Analysis complete | Verdict: {verdict} | Quality Gates: {quality}")


@main.command("validate")
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.pass_context
def validate(ctx: click.Context, path: Path) -> None:
    """Validate a saved analysis report for completeness and gate compliance."""
    click.echo(f"Validating report: {path}")
    content = path.read_text(encoding="utf-8")

    checks = {
        "Executive Summary": any(h in content for h in ["Executive Summary", "Tóm tắt tổng quan"]),
        "Inputs & Scope": any(h in content for h in ["Inputs & Scope", "Đầu vào & Phạm vi"]),
        "Evidence Collected": any(h in content for h in ["Evidence Collected", "Bằng chứng thu thập"]),
        "Analysis / Scorecard": any(h in content for h in ["Analysis", "Scorecard", "Phân tích", "Bảng điểm"]),
        "Disclosure": any(h in content for h in ["Disclosure", "Limitations", "Công bố", "Giới hạn"]),
        "Conclusion": any(h in content for h in ["Recommendation", "Conclusion", "Kết luận"]),
        "Quality Gate Checklist": any(h in content for h in ["Gate Checklist", "Kiểm tra chất lượng"]),
    }

    passed = sum(1 for v in checks.values() if v)
    total = len(checks)

    for name, ok in checks.items():
        status = "✓" if ok else "✗"
        click.echo(f"  {status} {name}")

    click.echo(f"\n{passed}/{total} sections present")
    if passed == total:
        click.echo("✅ Report is structurally complete")
    elif passed >= total - 2:
        click.echo("⚠️  Report is mostly complete but missing some sections")
    else:
        click.echo("❌ Report is incomplete")
        sys.exit(1)


@main.command("crawl")
@click.option("--dry-run", is_flag=True, help="Preview without writing")
@click.option("--keywords", "-k", multiple=True, help="Additional keywords for crawl")
@click.pass_context
def crawl(ctx: click.Context, dry_run: bool, keywords: tuple[str, ...]) -> None:
    """Run the knowledge base crawl pipeline to fetch latest research.

    Updates SECOND-KNOWLEDGE-BRAIN.md with new academic papers and practitioner references.
    """
    click.echo("Running knowledge base crawl pipeline...")
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
        import knowledge_updater as ku
        all_entries = []
        if keywords:
            all_kw = list(ku.KNOWLEDGE_CONFIG["keywords"]) + list(keywords)
        else:
            all_kw = list(ku.KNOWLEDGE_CONFIG["keywords"])

        all_entries += ku.fetch_arxiv(all_kw)
        all_entries += ku.fetch_semantic_scholar(all_kw)
        all_entries += ku.fetch_rss()

        click.echo(f"Found {len(all_entries)} candidates")
        n = ku.append_to_brain(all_entries, dry_run=dry_run)
        if dry_run:
            click.echo(f"[DRY RUN] Would append {n} entries")
        else:
            click.echo(f"✅ Appended {n} new entries to {ku.BRAIN_PATH}")
    except Exception as exc:
        click.echo(f"❌ Crawl failed: {exc}", err=True)
        sys.exit(1)


@main.command("info")
@click.pass_context
def info(ctx: click.Context) -> None:
    """Show project information and knowledge base statistics."""
    click.echo(f"bonsai-penjing-design-automation v{__version__}")
    click.echo("Bonsai & Penjing Design Analysis & Automation")
    click.echo("Japan, China, Vietnam Schools — Production-grade AI agent harness")
    click.echo("")

    if BRAIN_PATH.exists():
        brain = BRAIN_PATH.read_text(encoding="utf-8")
        size_kb = BRAIN_PATH.stat().st_size / 1024
        sections = brain.count("### ")
        dois = brain.count("DOI/URL")
        click.echo(f"Knowledge Base: {BRAIN_PATH}")
        click.echo(f"  Size: {size_kb:.1f} KB | Sections: {sections} | Citations: {dois}")
    else:
        click.echo(f"Knowledge Base: {BRAIN_PATH} (not found)")

    skill_dir = Path(__file__).resolve().parent.parent / "skills"
    if skill_dir.exists():
        skills = list(skill_dir.glob("*.md"))
        click.echo(f"\nSkills: {len(skills)} files in {skill_dir}")
        for s in sorted(skills):
            click.echo(f"  - {s.name}")


if __name__ == "__main__":
    main()
