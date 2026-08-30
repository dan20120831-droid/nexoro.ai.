import os
import requests

from agent.providers.base import AIProvider


class MistralProvider(AIProvider):
    name = "mistral"

    URL = "https://api.mistral.ai/v1/chat/completions"
    MODEL = "mistral-small-latest"
    DEFAULT_TIMEOUT = 10

    def ask(self, prompt: str, timeout: float | None = None) -> str:
        if timeout is None:
            timeout = self.DEFAULT_TIMEOUT

        api_key = os.getenv("MISTRAL_API_KEY", "").strip()

        if not api_key:
            raise RuntimeError("MISTRAL_API_KEY не установлен")

        response = requests.post(
            self.URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                "max_tokens": 1024,
            },
            timeout=timeout,
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"Mistral API error {response.status_code}: "
                f"{response.text}"
            )

        try:
            return response.json()["choices"][0]["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError) as e:
            raise RuntimeError(
                f"Неожиданный ответ Mistral API: {response.text}"
            ) from e
