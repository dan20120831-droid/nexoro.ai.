import os
import requests

from agent.providers.base import AIProvider


class HuggingFaceProvider(AIProvider):
    name = "huggingface"

    URL = "https://router.huggingface.co/v1/chat/completions"
    MODEL = "openai/gpt-oss-120b"
    DEFAULT_TIMEOUT = 10

    def ask(self, prompt: str, timeout: float | None = None) -> str:
        if timeout is None:
            timeout = self.DEFAULT_TIMEOUT

        api_key = os.getenv("HF_TOKEN", "").strip()

        if not api_key:
            raise RuntimeError("HF_TOKEN не установлен")

        try:
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
        except requests.RequestException as e:
            raise RuntimeError(
                f"Hugging Face network error: {e}"
            ) from e

        if response.status_code != 200:
            raise RuntimeError(
                f"Hugging Face API error {response.status_code}: "
                f"{response.text}"
            )

        try:
            return response.json()["choices"][0]["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError) as e:
            raise RuntimeError(
                f"Неожиданный ответ Hugging Face API: {response.text}"
            ) from e
