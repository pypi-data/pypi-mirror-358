"""
MCP client “model”: sends the prompt straight to a remote MCP-Host and
returns the assistant’s reply as-is.

The MCP Host is expected to expose an OpenAI-compatible
`/v1/chat/completions` endpoint (exactly what Wiz & MS Copilot do today).
"""

from __future__ import annotations

import os
import sys
from typing import Any, Dict, List

import requests

from cloudsecgpt.utils.cache import make_cache_path
from cloudsecgpt.utils.console import console


class MCPModel:
    def __init__(
        self,
        model_name: str,
        host_url: str | None = None,
        api_key: str | None = None,
    ):
        try:
            # e.g. https://mcp.acme.com/v1/chat/completions
            self.url = host_url or os.getenv("MCP_HOST_URL")
            if not self.url:
                raise RuntimeError("MCP host URL not provided (--host or MCP_HOST_URL)")
            self.model = model_name
            self.api_key = api_key or os.getenv("MCP_API_KEY")  # optional
        except Exception as e:
            console.log(f"[red]MCPModel error: {e}[/red]")
            sys.exit(1)

    # ------------------------------------------------------------------ #

    def _headers(self) -> Dict[str, str]:
        hdr = {"Content-Type": "application/json"}
        if self.api_key:
            hdr["Authorization"] = f"Bearer {self.api_key}"
        return hdr

    # ------------------------------------------------------------------ #

    def call(self, messages: List[Dict[str, Any]]) -> str:
        """
        POSTs the OpenAI-style payload to the MCP host and returns
        the assistant's content string.  A tiny on-disk cache avoids
        repeated calls during dev / slides.
        """
        try:
            cache_file = make_cache_path(key=f"mcp:{self.url}:{self.model}:{messages}")
            if cache_file.exists():
                return cache_file.read_text()

            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.2,
                "max_tokens": 1024,
            }

            try:
                r = requests.post(
                    self.url, json=payload, timeout=90, headers=self._headers()
                )
                r.raise_for_status()
                text = r.json()["choices"][0]["message"]["content"]
            except requests.RequestException as exc:
                console.log(f"[red]MCP API error: {exc}.[/red]")
                text = ""

            cache_file.write_text(text)
            return text
        except Exception as e:
            console.log(f"[red]MCPModel error: {e}[/red]")
            sys.exit(1)
