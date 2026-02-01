from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass(frozen=True)
class LLMConfig:
    api_key: str
    base_url: str
    model: str
    timeout_s: float = 20.0


class LLMClient:
    def __init__(self, config: LLMConfig) -> None:
        self._config = config

    @classmethod
    def from_env(cls) -> Optional["LLMClient"]:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com")
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        return cls(LLMConfig(api_key=api_key, base_url=base_url, model=model))

    def generate(self, messages: Iterable[dict[str, str]]) -> str:
        payload = {
            "model": self._config.model,
            "messages": list(messages),
            "temperature": 0.4,
        }
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self._config.base_url.rstrip('/')}/v1/chat/completions",
            data=data,
            headers={
                "Authorization": f"Bearer {self._config.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self._config.timeout_s) as response:
                body = response.read()
        except urllib.error.URLError as exc:
            raise RuntimeError("Échec de la requête LLM.") from exc

        parsed = json.loads(body)
        choices = parsed.get("choices", [])
        if not choices:
            raise RuntimeError("Réponse LLM vide.")
        message = choices[0].get("message", {})
        content = message.get("content")
        if not content:
            raise RuntimeError("Réponse LLM sans contenu.")
        return str(content).strip()
