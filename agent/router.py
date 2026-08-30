from agent.providers.groq import GroqProvider
from agent.providers.mistral import MistralProvider
from agent.providers.huggingface import HuggingFaceProvider
from agent.providers.base import AIProvider
from agent.providers.gemini import GeminiProvider
from agent.providers.openrouter import OpenRouterProvider


class AIRouter:
    """Маршрутизатор NEXORA между AI-провайдерами."""

    def __init__(self):
        self.providers: dict[str, AIProvider] = {
            "gemini": GeminiProvider(),
            "openrouter": OpenRouterProvider(),
            "groq": GroqProvider(),
            "mistral": MistralProvider(),
            "huggingface": HuggingFaceProvider(),
        }

        # Порядок резервных провайдеров для обычного чата.
        # Groq теперь основной (см. ask()), поэтому в fallback
        # он не нужен первым — используется только если явно
        # передан другой provider и он совпадёт с groq.
        self.fallback_order = [
            "mistral",
            "openrouter",
            "huggingface",
            "gemini",
        ]

    def available_providers(self) -> list[str]:
        return list(self.providers.keys())

    def ask(
        self,
        prompt: str,
        provider: str = "groq",
        fallback: bool = True,
        timeout: float | None = None,
    ) -> str:
        if provider not in self.providers:
            raise ValueError(
                f"AI provider не найден: {provider}"
            )

        try:
            return self.providers[provider].ask(prompt, timeout=timeout)

        except Exception as primary_error:
            if not fallback:
                raise

            errors = [
                f"{provider}: {primary_error}"
            ]

            for fallback_provider in self.fallback_order:
                if fallback_provider == provider:
                    continue

                try:
                    return self.providers[fallback_provider].ask(
                        prompt, timeout=timeout
                    )

                except Exception as fallback_error:
                    errors.append(
                        f"{fallback_provider}: {fallback_error}"
                    )

            raise RuntimeError(
                "Все доступные AI-провайдеры завершились ошибкой:\n"
                + "\n".join(errors)
            ) from primary_error


router = AIRouter()
