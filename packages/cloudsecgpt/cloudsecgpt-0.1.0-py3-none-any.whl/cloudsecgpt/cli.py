"""
CLI entry point.
Example:
    cloudsecgpt analyze findings.json --provider openai
"""

import argparse
import signal
import time
from pathlib import Path

from rich import box
from rich.columns import Columns
from rich.progress import (
    BarColumn,
    Progress,
    ProgressBar,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.syntax import Syntax
from rich.table import Table

from cloudsecgpt.utils.console import console
from cloudsecgpt.utils.files import ANALYZED_FILENAME, GROUPED_FILENAME, HTML_FILENAME

from .core import analyze_file

VERSION = "v0.1.0"

BANNER = f"""
╭━━━┳╮╱╱╱╱╱╱╱╱╭┳━━━╮╱╱╱╱╱╭━━━┳━━━┳━━━━╮
┃╭━╮┃┃╱╱╱╱╱╱╱╱┃┃╭━╮┃╱╱╱╱╱┃╭━╮┃╭━╮┃╭╮╭╮┃
┃┃╱╰┫┃╭━━┳╮╭┳━╯┃╰━━┳━━┳━━┫┃╱╰┫╰━╯┣╯┃┃╰╯
┃┃╱╭┫┃┃╭╮┃┃┃┃╭╮┣━━╮┃┃━┫╭━┫┃╭━┫╭━━╯╱┃┃
┃╰━╯┃╰┫╰╯┃╰╯┃╰╯┃╰━╯┃┃━┫╰━┫╰┻━┃┃╱╱╱╱┃┃
╰━━━┻━┻━━┻━━┻━━┻━━━┻━━┻━━┻━━━┻╯╱╱╱╱╰╯[bold]{VERSION}[/bold]
"""

_rich_progress = None
_task_id = None
_interrupted = False
_signal_handler_registered = False


def _signal_handler(_, __):
    """Handle Ctrl+C gracefully"""
    global _rich_progress, _interrupted

    if _interrupted:
        return

    _interrupted = True
    console.log("[yellow]Interrupted by user (Ctrl+C)[/yellow]")

    if _rich_progress is not None:
        _rich_progress.stop()

    import os

    os._exit(1)


if not _signal_handler_registered:
    signal.signal(signal.SIGINT, _signal_handler)
    _signal_handler_registered = True


def _progress_callback(total_findings: int, processed: int, args: argparse.Namespace):
    """
    Callback that analyze_file will call after each batch
    with the total number of findings and the amount already processed.
    """
    global _rich_progress, _task_id, _interrupted

    if _interrupted:
        return

    if _rich_progress is None:
        _rich_progress = Progress(
            SpinnerColumn(),
            TextColumn("{task.description}", justify="right"),
            BarColumn(bar_width=None),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            "•",
            TextColumn("[cyan]{task.completed}/{task.total} findings"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=console,
            transient=True,
        )

        # Create description with provider and model info if available
        description = "[bold blue]Analyzing findings"
        description += (
            f" from {args.file}"
            if args.file
            else (
                " from Security Hub"
                if args.security_hub
                else (
                    " from GCP SCC"
                    if args.gcp_scc is not None
                    else (
                        " from Azure Defender"
                        if args.azure_defender is not None
                        else ""
                    )
                )
            )
        )
        if args.provider and args.model:
            description += f" with {args.provider}/{args.model}"
        elif args.provider:
            description += f" with {args.provider}"

        _task_id = _rich_progress.add_task(description, total=total_findings)
        _rich_progress.start()

    _rich_progress.update(_task_id, completed=processed)

    if processed >= total_findings:
        _rich_progress.stop()


def _run_analyze(args):
    global _interrupted

    if _interrupted:
        return

    try:
        start = time.time()

        # Create a wrapper callback that includes provider and model info
        def progress_wrapper(total_findings: int, processed: int):
            _progress_callback(total_findings, processed, args)

        findings = analyze_file(
            input_file=args.file,
            output_path=args.out,
            provider=args.provider,
            model_name=args.model,
            batch_size=args.batch,
            max_workers=args.workers,
            host=args.host,
            api_key=args.api_key,
            security_hub=args.security_hub,
            gcp_scc=args.gcp_scc,
            azure_defender=args.azure_defender,
            progress_callback=progress_wrapper,
        )

        if _interrupted:
            return

        if findings:
            console.print(
                f"[green]✔[/green][blue] [bold]Analysis completed in {time.time() - start:.1f}s -> 🌐 {args.provider}/{args.model}  | 🔍 {'Scanned file: ' + str(args.file) if args.file else 'Live pull from Security Hub' if args.security_hub else 'Live pull from GCP SCC' if args.gcp_scc is not None else 'Live pull from Azure Defender' if args.azure_defender is not None else ''} | {len(findings)} security findings[/]\n"
            )
            output_path_abs = Path(args.out).resolve()
            console.print(
                f" 🗂  Enriched findings → [link=file://{output_path_abs}/{ANALYZED_FILENAME}]{args.out}/{ANALYZED_FILENAME}[/link]\n"
                f" 🗂  Grouped findings → [link=file://{output_path_abs}/{GROUPED_FILENAME}]{args.out}/{GROUPED_FILENAME}[/link]\n"
                f" 🗂  HTML report → [blue][link=file://{output_path_abs}/{HTML_FILENAME}]{args.out}/{HTML_FILENAME}[/link][/blue]"
            )
            console.print()
            # ────────────────────── Severity bar chart ──────────────────────
            total = len(findings)
            buckets = [
                ("🔴 Critical (>9)", sum(1 for f in findings if f["risk_score"] >= 9)),
                (
                    "🟠 High    (7-8)",
                    sum(1 for f in findings if 7 <= f["risk_score"] <= 8),
                ),
                (
                    "🟡 Medium  (4-6)",
                    sum(1 for f in findings if 4 <= f["risk_score"] <= 6),
                ),
                (
                    "🟢 Low     (1-3)",
                    sum(1 for f in findings if 1 <= f["risk_score"] <= 3),
                ),
            ]

            sev_tbl = Table(
                box=box.ROUNDED,
                title="📊 Severity Distribution",
                title_justify="center",
            )
            sev_tbl.add_column("Severity", no_wrap=True)
            sev_tbl.add_column("Count", justify="right")
            sev_tbl.add_column("", no_wrap=True)

            for label, cnt in buckets:
                bar = ProgressBar(
                    total=total, completed=cnt, width=30, complete_style="bright_blue"
                )
                sev_tbl.add_row(label, str(cnt), bar)

            # ────────────── Resource-type horizontal bar chart ─────────────
            resource_type_counts = {}
            for f in findings:
                rt = f.get("resource_type", "Unknown")
                resource_type_counts[rt] = resource_type_counts.get(rt, 0) + 1

            top_rts = sorted(
                resource_type_counts.items(), key=lambda x: x[1], reverse=True
            )[:8]

            bar_tbl = Table(
                box=box.ROUNDED, title="🏗️  Resource Types", title_justify="center"
            )
            bar_tbl.add_column("Resource Type")
            bar_tbl.add_column("Count", justify="right")
            bar_tbl.add_column("")

            for rt, count in top_rts:
                # render static bar for each resource type
                bar = ProgressBar(
                    total=total,
                    completed=count,
                    width=20,
                    complete_style="bright_blue",
                )
                bar_tbl.add_row(rt, str(count), bar)

            # ────────────── Regions bar chart ─────────────
            regions_counts = {}
            for f in findings:
                region = f.get("region", "Unknown")
                regions_counts[region] = regions_counts.get(region, 0) + 1
            top_regions = sorted(
                regions_counts.items(), key=lambda x: x[1], reverse=True
            )[:8]

            region_tbl = Table(
                box=box.ROUNDED, title="🌍 Regions", title_justify="center"
            )
            region_tbl.add_column("Region")
            region_tbl.add_column("Count", justify="right")
            region_tbl.add_column("")

            for region, count in top_regions:
                bar = ProgressBar(
                    total=total, completed=count, width=20, complete_style="bright_blue"
                )
                region_tbl.add_row(region, str(count), bar)
            # Ensure all tables have the same height by padding the shorter one
            sev_rows = len(sev_tbl.rows)
            bar_rows = len(bar_tbl.rows)
            region_rows = len(region_tbl.rows)
            max_rows = max(sev_rows, bar_rows, region_rows)

            # Pad severity table if needed
            while len(sev_tbl.rows) < max_rows:
                sev_tbl.add_row("", "", "")

            # Pad resource type table if needed
            while len(bar_tbl.rows) < max_rows:
                bar_tbl.add_row("", "", "")
            # Pad region table if needed
            while len(region_tbl.rows) < max_rows:
                region_tbl.add_row("", "", "")
            console.print(Columns([sev_tbl, bar_tbl, region_tbl], align="center"))
            console.print()

            # ────────────── Top 5 Misconfigurations ─────────────
            sorted_findings = sorted(
                findings, key=lambda x: x["risk_score"], reverse=True
            )[:5]
            top_tbl = Table(
                box=box.ROUNDED,
                title="🔥 Top 5 Misconfigurations",
                title_justify="center",
                show_lines=True,
            )
            top_tbl.add_column("🆔 Account ID", justify="center", no_wrap=True)
            top_tbl.add_column("📝 Summary", overflow="fold")
            top_tbl.add_column("📊 Risk Score", justify="center")
            top_tbl.add_column("🔍 Why", overflow="fold")
            top_tbl.add_column("📦 Resource", overflow="fold")
            top_tbl.add_column("🌍 Region", justify="center")
            for c in sorted_findings:
                top_tbl.add_row(
                    c["account_id"],
                    c["summary"],
                    str(c["risk_score"]),
                    c["why"],
                    c["resource_uid"],
                    c["region"],
                )
            console.print(top_tbl)
            console.print()

            # ────────────── CLI Fix Commands ─────────────
            console.print("[bold blue]🔧 CLI Fix Commands:[/bold blue]")
            console.print()
            for i, c in enumerate(sorted_findings, 1):
                if c["cli_fix"]:
                    console.print(f"[bold]{i}.[/bold] {c['summary']}")
                    cli_syntax = Syntax(
                        c["cli_fix"], "bash", background_color="default", word_wrap=True
                    )
                    console.print(cli_syntax)
                    console.print()
        else:
            console.log("[yellow]No security findings found[/yellow]")
    except KeyboardInterrupt:
        console.print("\n[yellow]Analysis interrupted by user[/yellow]")
    except Exception as e:
        console.log(f"[red]Error: {e}[/red]")


def _run_chat(args):
    try:
        from cloudsecgpt.chat import chat_session

        chat_session(
            input_file=args.file,
            provider=args.provider,
            model_name=args.model,
            host=args.host,
            api_key=args.api_key,
            security_hub=args.security_hub,
            gcp_scc=args.gcp_scc,
            azure_defender=args.azure_defender,
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]Chat session interrupted by user[/yellow]")


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="cloudsecgpt")
    sub = ap.add_subparsers(dest="cmd", required=True)

    an = sub.add_parser(
        "analyze",
        help="Analyze JSON-OCSF/AWS Security Hub/GCP SCC/Azure Defender findings with an LLM",
    )
    an.add_argument("--file", type=Path, help="JSON-OCSF/JSON-ASFF/Parquet file")
    an.add_argument(
        "--security-hub",
        action="store_true",
        help="Fetch findings from AWS Security Hub",
    )
    an.add_argument(
        "--gcp-scc",
        nargs="?",
        const="",
        metavar="ORG/RESOURCE",
        help="Fetch findings from GCP SCC. Pass org/folder/project ID "
        "or leave empty to auto-detect if only one org is visible.",
    )
    an.add_argument(
        "--azure-defender",
        metavar="SUB_ID",
        nargs="?",
        const="",
        help="Fetch ACTIVE assessments from Azure Defender for Cloud. "
        'Pass "" to auto-detect single subscription.',
    )
    an.add_argument("--out", "-o", default="output", help="Output directory")
    an.add_argument(
        "--provider",
        "-p",
        choices=["openai", "ollama", "bedrock", "mcp"],
        default="openai",
        help="LLM backend: OpenAI, Ollama (local), Amazon Bedrock or a remote MCP host",
    )
    an.add_argument("--host", help="When --provider mcp: base URL of the MCP host")
    an.add_argument("--api-key", help="Optional bearer token for the MCP host")
    an.add_argument("--model", "-m", default="gpt-4o-mini", help="Model name")
    an.add_argument("--batch", "-b", type=int, default=10, help="Batch size")
    an.add_argument("--workers", "-w", type=int, default=8, help="Parallel calls")
    an.set_defaults(func=_run_analyze)
    ch = sub.add_parser("chat", help="Interactive Q&A over raw findings")
    ch.add_argument("--file", type=Path, help="JSON-OCSF file")
    ch.add_argument(
        "--security-hub",
        action="store_true",
        help="Fetch findings from AWS Security Hub",
    )
    ch.add_argument(
        "--gcp-scc",
        nargs="?",
        const="",
        metavar="ORG/RESOURCE",
        help="Fetch findings from GCP SCC. Pass org/folder/project ID "
        "or leave empty to auto-detect if only one org is visible.",
    )
    ch.add_argument(
        "--azure-defender",
        metavar="SUB_ID",
        nargs="?",
        const="",
        help="Fetch ACTIVE assessments from Azure Defender for Cloud. "
        'Pass "" to auto-detect single subscription.',
    )
    ch.add_argument(
        "--provider",
        "-p",
        choices=["openai", "ollama", "bedrock", "mcp"],
        default="openai",
    )
    ch.add_argument("--model", "-m", default="gpt-4o-mini", help="Model name")
    ch.add_argument("--host", default="", help="MCP host URL (if provider=mcp)")
    ch.add_argument("--api-key", default="", help="MCP / vendor API key")
    ch.set_defaults(func=_run_chat)
    return ap


def main():
    console.print(BANNER, highlight=False)
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
