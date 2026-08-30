import os
import requests

from agent.providers.base import AIProvider


class GroqProvider(AIProvider):
    """Провайдер Groq через OpenAI-compatible API."""

    name = "groq"

    URL = "https://api.groq.com/openai/v1/chat/completions"
    MODEL = "openai/gpt-oss-120b"
    DEFAULT_TIMEOUT = 10

    def ask(self, prompt: str, timeout: float | None = None) -> str:
        if timeout is None:
            timeout = self.DEFAULT_TIMEOUT

        api_key = os.getenv("GROQ_API_KEY", "").strip()

        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY не установлен"
            )

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "max_tokens": 1024,
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
                f"Groq network error: {e}"
            ) from e

        if response.status_code != 200:
            raise RuntimeError(
                f"Groq API error {response.status_code}: "
                f"{response.text}"
            )

        try:
            data = response.json()
            return data["choices"][0]["message"]["content"]

        except (ValueError, KeyError, IndexError, TypeError) as e:
            raise RuntimeError(
                f"Неожиданный ответ Groq API: "
                f"{response.text}"
            ) from e
