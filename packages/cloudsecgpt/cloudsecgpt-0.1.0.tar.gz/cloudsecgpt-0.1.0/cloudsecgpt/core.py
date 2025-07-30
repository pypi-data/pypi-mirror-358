import hashlib
import pathlib
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import pandas as pd

from cloudsecgpt.core_helpers import load_findings_auto
from cloudsecgpt.models.bedrock_model import BedrockModel
from cloudsecgpt.models.mcp_model import MCPModel
from cloudsecgpt.models.ollama_model import OllamaModel
from cloudsecgpt.models.openai_model import OpenAIModel
from cloudsecgpt.protocols.triage import TriageProtocol
from cloudsecgpt.report import generate_report
from cloudsecgpt.utils.console import console
from cloudsecgpt.utils.files import ANALYZED_FILENAME, GROUPED_FILENAME, HTML_FILENAME


def get_model(provider: str, model_name: str, namespace: str, host: str, api_key: str):
    try:
        if provider == "openai":
            return OpenAIModel(model_name, namespace)
        if provider == "bedrock":
            return BedrockModel(model_name, namespace)
        if provider == "ollama":
            return OllamaModel(model_name, namespace)
        if provider == "mcp":
            return MCPModel(model_name, host, api_key)
        raise ValueError(f"Unknown provider: {provider}")
    except Exception as e:
        console.log(f"[red]Error getting model: {e}[/red]")
        sys.exit(1)


def _cluster_findings(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Cluster findings by resource_type + summary.
    Aggregates:
      - count       : number of occurrences
      - max_score   : highest risk_score
      - providers   : unique providers
      - accounts    : unique accounts
      - regions     : unique regions
      - remediation : remediation text from the highest-risk item
      - why         : the 'why' from the highest-risk item
      - cli_fix : the cli_fix from the highest-risk item
    """
    try:
        df = pd.DataFrame(rows)
        groups = []

        for (r_type, summary), group in df.groupby(
            ["resource_type", "summary"], dropna=False
        ):
            count = len(group)
            max_score = int(group["risk_score"].max())
            providers = ",".join(sorted(group["provider"].dropna().unique()))
            accounts = ",".join(sorted(group["account_id"].dropna().unique()))
            regions = ",".join(sorted(group["region"].dropna().unique()))
            # Ensure resources is always a string, even if empty
            resource_uids = group["resource_uid"].dropna().unique()
            resources = (
                ",".join(sorted(resource_uids)) if len(resource_uids) > 0 else ""
            )

            top = group.loc[group["risk_score"].idxmax()]
            groups.append(
                {
                    "resource_type": r_type,
                    "summary": summary,
                    "count": count,
                    "max_score": max_score,
                    "providers": providers,
                    "accounts": accounts,
                    "regions": regions,
                    "resources": resources,
                    "why": top["why"],
                    "remediation": top["remediation"],
                    "cli_fix": top["cli_fix"],
                }
            )

        return pd.DataFrame(groups)
    except Exception as e:
        console.log(f"[red]Error clustering findings: {e}[/red]")
        sys.exit(1)


def analyze_file(
    input_file: Optional[str | Path],
    output_path: str = "output",
    provider: str = "openai",
    model_name: str = "gpt-4o-mini",
    batch_size: int = 10,
    max_workers: int = 8,
    host: str = "",
    api_key: str = "",
    security_hub: bool = False,
    gcp_scc: str | None = None,
    azure_defender: str | None = None,
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> List[Dict[str, Any]]:
    try:
        # 1) load raw findings
        findings = load_findings_auto(input_file, security_hub, gcp_scc, azure_defender)
        # 2) normalize & batch
        if type(findings) is not list:
            findings = [findings]
        # If findings is a list with several empty dicts, return 0
        if not findings or all(f == {} for f in findings):
            return []
        if progress_callback:
            progress_callback(len(findings), 0)
        batches = [
            findings[i : i + batch_size] for i in range(0, len(findings), batch_size)
        ]

        total_findings = len(findings)
        processed_count = 0
    except Exception as e:
        console.log(f"[red]Error analyzing file: {e}[/red]")
        sys.exit(1)

    # 3) define worker
    def worker(batch):
        try:
            if input_file:
                file_bytes = pathlib.Path(input_file).read_bytes()
                namespace = hashlib.sha1(file_bytes, usedforsecurity=False).hexdigest()
            else:
                namespace = "security-hub"
            mdl = get_model(provider, model_name, namespace, host, api_key)
            prt = TriageProtocol()
            prompt = prt.build_prompt(batch)
            reply = mdl.call(prompt)
            parsed = prt.parse_response(reply)

            out = []
            for entry in parsed:
                ctx = {}
                for f in batch:
                    if entry["id"] in f["id"]:
                        ctx = f
                        break
                if ctx:
                    entry.update(
                        {
                            "provider": ctx.get("provider", ""),
                            "account_id": ctx.get("account_id", ""),
                            "region": ctx.get("region", ""),
                            "resource_type": ctx.get("resource_type", ""),
                            "resource_uid": ctx.get("resource_uid", ""),
                        }
                    )
                    out.append(entry)
            return out
        except Exception as e:
            console.log(f"[red]Error in worker: {e}[/red]")
            return []

    try:
        all_rows: List[Dict[str, Any]] = []

        # 4) process batches (threaded for OpenAI, serial for Ollama)
        if provider == "ollama":
            for batch in batches:
                try:
                    rows = worker(batch)
                    all_rows.extend(rows)
                    processed_count += len(batch)
                    if progress_callback:
                        progress_callback(total_findings, processed_count)
                except KeyboardInterrupt:
                    console.print("\n[yellow]Processing interrupted by user[/yellow]")
                    return all_rows
        else:
            from concurrent.futures import ThreadPoolExecutor, as_completed

            with ThreadPoolExecutor(max_workers=max_workers) as pool:
                futures = {pool.submit(worker, b): b for b in batches}
                try:
                    for fut in as_completed(futures):
                        batch = futures[fut]
                        rows = fut.result()
                        all_rows.extend(rows)
                        processed_count += len(batch)
                        if progress_callback:
                            progress_callback(total_findings, processed_count)
                except KeyboardInterrupt:
                    console.print("\n[yellow]Processing interrupted by user[/yellow]")
                    # Cancel remaining futures and shutdown pool
                    for future in futures:
                        future.cancel()
                    pool.shutdown(wait=False)
                    # Return what we have so far
                    return all_rows

        # 5) write flat CSV sorted by risk_score desc
        out_dir = Path(output_path)

        # Check if output_path already exists as a file
        if out_dir.exists() and not out_dir.is_dir():
            console.log(
                f"[red]Error: '{output_path}' already exists as a file. Please specify a different output directory or remove the existing file.[/red]"
            )
            return []

        out_dir.mkdir(parents=True, exist_ok=True)

        flat_csv = out_dir / ANALYZED_FILENAME
        cluster_csv = out_dir / GROUPED_FILENAME
        html_report = out_dir / HTML_FILENAME
        if not all_rows:
            return []
        df_flat = pd.DataFrame(all_rows).sort_values("risk_score", ascending=False)
        df_flat.to_csv(
            flat_csv,
            index=False,
            columns=[
                "id",
                "provider",
                "account_id",
                "region",
                "resource_type",
                "resource_uid",
                "risk_score",
                "summary",
                "why",
                "cli_fix",
                "remediation",
            ],
        )

        # 6) write clustered CSV sorted by max_score desc
        df_cluster = _cluster_findings(all_rows).sort_values(
            "max_score", ascending=False
        )
        df_cluster.to_csv(cluster_csv, index=False)

        # 7) Generate HTML report
        generate_report(input_path=out_dir, output_path=html_report)
        return all_rows
    except KeyboardInterrupt:
        console.print("\n[yellow]Analysis interrupted by user[/yellow]")
        return all_rows if "all_rows" in locals() else []
    except Exception as e:
        console.log(f"[red]Error writing CSV: {e}[/red]")
        return []
