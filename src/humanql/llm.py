"""OpenAI-compatible chat client for text generation."""

import os
from typing import Any

import requests


def config_from_env() -> dict[str, str]:
    """Read API_KEY, BASE_URL, MODEL from environment. Trim trailing slash from BASE_URL."""
    base_url = (os.getenv("BASE_URL") or "https://api.openai.com/v1").rstrip("/")
    api_key = os.getenv("API_KEY") or ""
    model = (os.getenv("MODEL") or "gpt-4o-mini").strip()
    return {"base_url": base_url, "api_key": api_key, "model": model}


class OpenAIClient:
    """OpenAI-compatible chat completions client. Implements TextGenerator protocol."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        timeout: int = 45,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._model = model
        self._timeout = timeout

    def generate(self, system: str, user: str) -> str:
        """Send system and user messages; return trimmed assistant content. Raises on error."""
        url = f"{self._base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}",
        }
        payload: dict[str, Any] = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=self._timeout)
        if resp.status_code != 200:
            raise RuntimeError(f"chat completion: {resp.status_code} {resp.text}")
        data = resp.json()
        choices = data.get("choices") or []
        if not choices:
            raise ValueError("chat completion: no choices in response")
        content = choices[0].get("message", {}).get("content") or ""
        return content.strip()
