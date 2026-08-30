import os
import requests

from agent.providers.base import AIProvider


class QwenProvider(AIProvider):
    """Провайдер Qwen через Alibaba Cloud Model Studio."""

    name = "qwen"

    URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions"
    MODEL = "qwen3.8-flash"

    def ask(self, prompt: str) -> str:
        api_key = os.getenv("DASHSCOPE_API_KEY", "").strip()

        if not api_key:
            raise RuntimeError(
                "DASHSCOPE_API_KEY не установлен"
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
        }

        try:
            response = requests.post(
                self.URL,
                headers=headers,
                json=payload,
                timeout=120,
            )
        except requests.RequestException as e:
            raise RuntimeError(
                f"Qwen network error: {e}"
            ) from e

        if response.status_code != 200:
            raise RuntimeError(
                f"Qwen API error {response.status_code}: "
                f"{response.text}"
            )

        try:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError) as e:
            raise RuntimeError(
                f"Неожиданный ответ Qwen API: {response.text}"
            ) from e
