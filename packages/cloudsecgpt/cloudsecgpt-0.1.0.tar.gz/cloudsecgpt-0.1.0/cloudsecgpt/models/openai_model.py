import sys
from typing import Any, Dict, List

from openai import OpenAI, OpenAIError

from cloudsecgpt.utils.cache import make_cache_path
from cloudsecgpt.utils.console import console


class OpenAIModel:
    """
    OpenAI ≥1.x client with on-disk caching.
    """

    def __init__(self, model_name: str, namespace: str):
        try:
            self.client = OpenAI()  # reads OPENAI_API_KEY from env
            self.model = model_name
            self.namespace = namespace
        except Exception as e:
            console.log(f"[red]OpenAIModel error: {e}[/red]")
            sys.exit(1)

    def call(self, messages: List[Dict[str, Any]]) -> str:
        """
        Send 'messages' to the OpenAI chat API and return the response text.
        Caches results to avoid duplicate calls.
        """
        try:
            prompt_str = str(messages)
            cache_path = make_cache_path(
                namespace=self.namespace,
                provider="openai",
                model=self.model,
                prompt=prompt_str,
            )
            # Return cached response if available
            if cache_path.exists():
                return cache_path.read_text()

            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=10000,
                    temperature=0.1,
                )
                text = response.choices[0].message.content
            except OpenAIError as e:
                console.log(f"[red]OpenAI error: {e}[/red]")
                text = ""

            cache_path.write_text(text)
            return text
        except Exception as e:
            console.log(f"[red]OpenAIModel error: {e}[/red]")
            sys.exit(1)
