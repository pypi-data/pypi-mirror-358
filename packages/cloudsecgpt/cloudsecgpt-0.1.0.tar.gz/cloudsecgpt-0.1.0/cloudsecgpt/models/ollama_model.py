import os
import sys
from typing import Any, Dict, List

import requests

from cloudsecgpt.utils.cache import make_cache_path
from cloudsecgpt.utils.console import console


class OllamaModel:
    """
    Local LLM backend using the Ollama HTTP API.
    Expects an Ollama server running (`ollama serve`)
    on localhost:11434 speaking OpenAI-compatible endpoints.
    Responses are cached to ~/.cgpt_cache.
    """

    def __init__(
        self,
        model_name: str = "mistral:7b",
        namespace: str = "",  # file-specific namespace
        api_url: str | None = None,
    ):
        try:
            self.model = model_name
            self.namespace = namespace
            self.api_url = api_url or os.getenv(
                "OLLAMA_API_URL", "http://localhost:11434/v1/chat/completions"
            )
        except Exception as e:
            console.log(f"[red]OllamaModel error: {e}[/red]")
            sys.exit(1)

    def call(self, messages: List[Dict[str, Any]]) -> str:
        """
        Send a list of OpenAI-style chat messages to Ollama via HTTP POST.
        Caches replies in ~/.cgpt_cache so repeated prompts (with same
        namespace/provider/model) return instantly.
        """
        try:
            prompt_str = str(messages)
            cache_path = make_cache_path(
                namespace=self.namespace,
                provider="ollama",
                model=self.model,
                prompt=prompt_str,
            )
            if cache_path.exists():
                return cache_path.read_text()

            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.1,
                "max_tokens": 1024,
            }
            try:
                resp = requests.post(self.api_url, json=payload, timeout=60)
                resp.raise_for_status()
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
            except requests.RequestException as e:
                console.log(f"[red]Ollama API error: {e}")
                content = ""

            cache_path.write_text(content)
            return content
        except Exception as e:
            console.log(f"[red]OllamaModel error: {e}[/red]")
            sys.exit(1)
