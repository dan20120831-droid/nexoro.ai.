from abc import ABC, abstractmethod


class AIProvider(ABC):
    """Базовый интерфейс любого AI-провайдера."""

    name = "unknown"

    @abstractmethod
    def ask(self, prompt: str, timeout: float | None = None) -> str:
        """Отправляет запрос AI и возвращает ответ.

        timeout — необязательный таймаут в секундах.
        Если не передан, провайдер использует свой DEFAULT_TIMEOUT.
        """
        raise NotImplementedError
