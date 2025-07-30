from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.markdown import Markdown

from cloudsecgpt.core_helpers import load_findings_auto
from cloudsecgpt.models.bedrock_model import BedrockModel
from cloudsecgpt.models.mcp_model import MCPModel
from cloudsecgpt.models.ollama_model import OllamaModel
from cloudsecgpt.models.openai_model import OpenAIModel
from cloudsecgpt.utils.console import console


def _get_model(provider: str, model: str, host: str, api_key: str):
    try:
        if provider == "openai":
            return OpenAIModel(model, namespace="chat")
        if provider == "ollama":
            return OllamaModel(model, namespace="chat")
        if provider == "bedrock":
            return BedrockModel(model, namespace="chat")
        if provider == "mcp":
            return MCPModel(model, host, api_key)
        raise ValueError(f"Unknown provider {provider!r}")
    except Exception as e:
        console.log(f"[red]Error getting model: {e}[/red]")
        sys.exit(1)


def _compress_toc(findings: List[Dict[str, Any]]) -> str:
    """Return a tiny, one-line-per-finding summary for the prompt."""
    try:
        lines = []
        for f in findings:
            lines.append(
                f"{f['id']} | {f.get('provider', '-')} | {f.get('title', '-')} | {f.get('description', '-')} | {f['resource_type']} | {f['severity']} | score={f.get('risk_score', '?')} | {f.get('region', '-')} | {f.get('account_id', '-')} | {f.get('resource_uid', '-')}"
            )
        return "\n".join(lines[:200])  # keep prompt bounded
    except Exception as e:
        console.log(f"[red]Error compressing TOC: {e}[/red]")
        sys.exit(1)


def chat_session(
    input_file: Optional[Path | str],
    provider: str,
    model_name: str,
    host: str,
    api_key: str,
    security_hub: bool,
    gcp_scc: str | None,
    azure_defender: str | None,
):
    try:
        # 1) load raw findings
        findings = load_findings_auto(input_file, security_hub, gcp_scc, azure_defender)

        # 2) normalize & batch
        if type(findings) is not list:
            findings = [findings]
        toc = _compress_toc(findings)

        # 2) initialise model
        model = _get_model(provider, model_name, host, api_key)

        system_msg = (
            "You are CloudSecGPT, a senior cloud-security analyst. "
            "You have full knowledge of the following findings (table of contents below). "
            "Answer the user's questions concisely. "
            "If you reference any finding, quote its id and resource uid."
        )
        messages: list[dict] = [
            {"role": "system", "content": system_msg},
            {"role": "system", "content": f"Findings TOC:\n{toc}"},
        ]
        console.log("[bold cyan]CloudSecGPT chat - type /exit to quit[/]\n")
        while True:
            try:
                user_input = console.input("[blue]user > [/]")
                console.print()
            except EOFError:  # Ctrl-D
                console.print()
                break
            except KeyboardInterrupt:  # Ctrl-C
                console.print("\n[yellow]Chat session interrupted by user[/yellow]")
                break
            if user_input.strip().lower() in {"/exit", "quit", "q"}:
                break
            if not user_input.strip():
                continue

            messages.append({"role": "user", "content": user_input})

            try:
                reply = model.call(messages)
                messages.append({"role": "assistant", "content": reply})

                console.print("[green]cloudsecgpt  >[/]")
                console.print(Markdown(reply, justify="left"))
                console.print()
            except KeyboardInterrupt:
                console.print(
                    "\n[yellow]Response generation interrupted by user[/yellow]"
                )
                break
    except Exception as e:
        console.log(f"[red]Error in chat session: {e}[/red]")
        sys.exit(1)
