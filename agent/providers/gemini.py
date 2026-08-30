from agent.ai import ask_ai
from agent.providers.base import AIProvider


class GeminiProvider(AIProvider):
    """Провайдер Gemini."""

    name = "gemini"

    def ask(self, prompt: str, timeout: float | None = None) -> str:
        return ask_ai(prompt, timeout=timeout)
