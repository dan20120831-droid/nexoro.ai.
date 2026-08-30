import os
import requests

from agent.providers.base import AIProvider


class OpenRouterProvider(AIProvider):
    """Провайдер OpenRouter через OpenAI-compatible API."""

    name = "openrouter"

    URL = "https://openrouter.ai/api/v1/chat/completions"
    DEFAULT_TIMEOUT = 10

    def ask(self, prompt: str, timeout: float | None = None) -> str:
        if timeout is None:
            timeout = self.DEFAULT_TIMEOUT

        api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        model = os.getenv(
            "OPENROUTER_MODEL",
            "openai/gpt-5.6",
        ).strip()

        if not api_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY не установлен"
            )

        if not model:
            raise RuntimeError(
                "OPENROUTER_MODEL не установлен"
            )

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://nexora.ai",
            "X-Title": "NEXORA AI Agent",
        }

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "max_tokens": 128,
        }

        try:
            response = requests.post(
                self.URL,
                headers=headers,
                json=payload,
                timeout=timeout,
            )
        except requests.RequestException as e:
            raise RuntimeError(
                f"OpenRouter network error: {e}"
            ) from e

        if response.status_code != 200:
            raise RuntimeError(
                f"OpenRouter API error {response.status_code}: "
                f"{response.text}"
            )

        try:
            data = response.json()
            return data["choices"][0]["message"]["content"]

        except (ValueError, KeyError, IndexError, TypeError) as e:
            raise RuntimeError(
                f"Неожиданный ответ OpenRouter API: "
                f"{response.text}"
            ) from e
