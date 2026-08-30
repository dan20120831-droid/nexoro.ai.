import json
import os
import urllib.request
import urllib.error


GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

GEMINI_MODEL = "gemini-3.6-flash"

DEFAULT_TIMEOUT = 10

SYSTEM_PROMPT = """
Ты — NEXORA AI Coding Agent.

Ты являешься программирующим AI-агентом.

Твои задачи:
- понимать задачу пользователя;
- анализировать существующий проект;
- писать рабочий код;
- создавать новые файлы;
- изменять существующие файлы только когда это действительно необходимо;
- не уничтожать уже рабочий код без причины;
- исправлять ошибки;
- писать понятный и поддерживаемый код;
- использовать реальные библиотеки и API;
- учитывать результаты тестирования.

ВАЖНЫЕ ПРАВИЛА:
1. Не придумывай существование библиотек или API.
2. Не используй секреты непосредственно в исходном коде.
3. Старайся сохранять уже работающий код.
4. Перед изменением существующей архитектуры сначала анализируй её.
5. Если задача недостаточно понятна — задай уточняющий вопрос.
"""


def ask_ai(task: str, timeout: float | None = None) -> str:
    if timeout is None:
        timeout = DEFAULT_TIMEOUT

    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY не установлен")

    prompt = SYSTEM_PROMPT + "\n\nЗАДАЧА ПОЛЬЗОВАТЕЛЯ:\n" + task

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 4096
        }
    }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            result = json.loads(response.read().decode("utf-8"))

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Gemini API error {e.code}: {error_body}"
        ) from e

    try:
        return result["candidates"][0]["content"]["parts"][0]["text"]

    except (KeyError, IndexError, TypeError) as e:
        raise RuntimeError(
            f"Неожиданный ответ Gemini API: {result}"
        ) from e
