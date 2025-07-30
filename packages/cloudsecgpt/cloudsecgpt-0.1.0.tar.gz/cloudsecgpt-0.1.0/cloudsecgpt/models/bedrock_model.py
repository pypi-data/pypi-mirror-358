import json
import os
import sys
from typing import Any, Dict, List, Tuple

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from cloudsecgpt.utils.cache import make_cache_path
from cloudsecgpt.utils.console import console


class BedrockModel:
    """
    AWS Bedrock client supporting:
      - Anthropic Claude (Messages API)
      - Amazon Titan (Text)
      - Meta LLaMA (Text)
      - Mistral (Text)
    via a single invoke_model call.
    """

    MAX_TOKENS = 4096
    TEMPERATURE = 0

    def __init__(
        self,
        model_name: str = "anthropic.claude-3-7-sonnet-20250219-v1:0",
        namespace: str = "",
    ):
        try:
            self.region = os.getenv("AWS_REGION", "us-east-1")
            self.client = boto3.client(
                "bedrock-runtime",
                region_name=self.region,
                config=Config(retries={"max_attempts": 3}),
            )
            self.model = model_name
            self.namespace = namespace
        except Exception as e:
            console.log(f"[red]Failed to initialize BedrockModel: {e}[/red]")
            sys.exit(1)

    def call(self, messages: List[Dict[str, Any]]) -> str:
        """
        Build and invoke model payload based on selected model.
        """
        cache_key = json.dumps(messages, sort_keys=True)
        cache_path = make_cache_path(
            namespace=self.namespace,
            provider="bedrock",
            model=self.model,
            prompt=cache_key,
        )
        if cache_path.exists():
            return cache_path.read_text()

        system, user, combined = self._prepare_prompt(messages)
        payload = self._build_payload(system, user, combined)
        body = json.dumps(payload).encode("utf-8")

        try:
            resp = self.client.invoke_model(
                modelId=self.model,
                body=body,
                contentType="application/json",
                accept="application/json",
                performanceConfigLatency="standard",
            )
            raw = resp["body"].read().decode("utf-8")
            data = json.loads(raw)
            result = self._parse_response(data)
            cache_path.write_text(result)
            return result

        except (BotoCoreError, ClientError) as err:
            console.log(f"[red]Bedrock invoke_model error: {err}[/red]")
            return ""
        except Exception as e:
            console.log(f"[red]Unexpected error: {e}[/red]")
            sys.exit(1)

    def _prepare_prompt(self, messages: List[Dict[str, Any]]) -> Tuple[str, str, str]:
        """
        Extract system & user messages and combine into a single prompt.
        """
        try:
            system = messages[0]["content"]
            user = messages[1]["content"]
            combined = f"{system}\n\n{user}"
            return system, user, combined
        except Exception as e:
            console.log(f"[red]Error preparing prompt: {e}[/red]")
            sys.exit(1)

    def _build_payload(self, system: str, user: str, combined: str) -> Dict[str, Any]:
        """
        Construct model-specific payload:
        - Titan: inputText + textGenerationConfig.maxTokenCount
        - LLaMA: prompt + max_gen_len
        - Mistral: prompt + max_tokens
        - Claude: messages + maxTokensToSample
        """
        name = self.model.lower()
        if name.startswith("amazon.titan"):
            return self._titan_payload(combined)

        if "llama" in name:
            return self._llama_payload(combined)

        if "mistral" in name:
            return self._mistral_payload(combined)

        return self._claude_payload(system, user)

    def _titan_payload(self, prompt: str) -> Dict[str, Any]:
        return {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": self.MAX_TOKENS,
                "temperature": self.TEMPERATURE,
            },
        }

    def _llama_payload(self, prompt: str) -> Dict[str, Any]:
        return {
            "prompt": prompt,
            "max_gen_len": self.MAX_TOKENS,
            "temperature": self.TEMPERATURE,
        }

    def _mistral_payload(self, prompt: str) -> Dict[str, Any]:
        return {
            "prompt": prompt,
            "max_tokens": self.MAX_TOKENS,
            "temperature": self.TEMPERATURE,
        }

    def _claude_payload(self, system: str, user: str) -> Dict[str, Any]:
        return {
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "maxTokensToSample": self.MAX_TOKENS,
            "temperature": self.TEMPERATURE,
        }

    def _parse_response(self, data: Dict[str, Any]) -> str:
        """
        Extract model output:
        - Titan: data["results"][0]["outputText"]
        - Llama: data["generation"]
        - Mistral: data["outputs"][0]["text"]
        - Claude: data["messages"][0]["content"]
        """
        name = self.model.lower()
        if name.startswith("amazon.titan"):
            return data["results"][0]["outputText"]
        elif "llama" in name:
            return data["generation"]

        elif "mistral" in name:
            return data["outputs"][0]["text"]
        else:
            return data["messages"][0]["content"]
