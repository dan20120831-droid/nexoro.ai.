import asyncio

from agent.router import router
from agent.web_search import web_search, format_search_results


def needs_web_search(text: str) -> bool:
    """
    Определяет, нужен ли поиск в интернете.
    """

    text_lower = text.lower()

    triggers = (
        "сейчас",
        "сегодня",
        "вчера",
        "завтра",
        "последние",
        "последний",
        "последняя",
        "новости",
        "актуальн",
        "кто сейчас",
        "что сейчас",
        "курс",
        "цена",
        "стоимость",
        "произошло",
        "произошёл",
        "вернётся",
        "ушёл",
        "ушла",
        "новый",
        "новая",
        "2026",
        "2025",
    )

    return any(trigger in text_lower for trigger in triggers)


def ask_with_web(text: str) -> str:
    """
    Отвечает на вопрос через NEXORA.
    При необходимости сначала выполняет веб-поиск.
    """

    if not needs_web_search(text):
        return router.ask(text)

    results = web_search(text, max_results=5)
    search_context = format_search_results(results)

    prompt = f"""
Ты — AI NEXORA.

Пользователь задал вопрос:
{text}

Перед ответом был выполнен поиск в интернете.

Данные поиска:
{search_context}

Правила:
1. Используй найденную информацию для ответа.
2. Отдавай предпочтение более надёжным и официальным источникам.
3. Не выдавай неподтверждённые сведения за факты.
4. Если источники противоречат друг другу, сообщи об этом.
5. Не придумывай информацию, которой нет в результатах.
6. Ответь пользователю естественно и понятно.
7. В конце укажи краткий список использованных источников.

Ответ:
"""

    return router.ask(prompt)


async def ask_with_web_async(text: str) -> str:
    return await asyncio.to_thread(ask_with_web, text)
