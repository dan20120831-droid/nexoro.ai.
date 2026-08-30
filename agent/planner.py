import json
import re

from agent.router import router


ALLOWED_ACTIONS = {
    "create_file",
    "edit_file",
    "read_file",
    "test_file",
    "list_workspace",
}


PLANNER_PROMPT = """
Ты — Planner системы NEXORA AI Coding Agent.

Твоя задача — превратить задачу пользователя в точный
последовательный план действий.

РАЗРЕШЁННЫЕ ДЕЙСТВИЯ:

CREATE_FILE:
{
  "action": "create_file",
  "filename": "example.py",
  "code": "print('Hello')"
}

EDIT_FILE:
{
  "action": "edit_file",
  "filename": "example.py",
  "code": "print('Hello NEXORA')"
}

READ_FILE:
{
  "action": "read_file",
  "filename": "example.py"
}

TEST_FILE:
{
  "action": "test_file",
  "filename": "example.py"
}

LIST_WORKSPACE:
{
  "action": "list_workspace"
}

ПРАВИЛА:

1. Ответ должен быть только валидным JSON.
2. Корневой объект должен содержать "steps".
3. "steps" должен быть непустым массивом.
4. Используй только разрешённые действия.
5. Пути должны быть относительными к workspace.
6. Никогда не добавляй workspace/ в filename.
7. Python-файлы должны иметь расширение .py.
8. Если нужно изменить существующий файл:
   сначала используй read_file.
9. После анализа существующего файла используй edit_file.
10. Не создавай новый файл вместо существующего,
    если пользователь просит изменить существующий.
11. После create_file добавляй test_file.
12. После edit_file добавляй test_file.
13. Для сложной задачи используй несколько последовательных шагов.
14. Не удаляй существующий функционал без необходимости.
15. Сохраняй исходную задачу программы.
16. Если пользователь явно указал имя файла,
    используй именно это имя.
17. Если пользователь явно указал переменную,
    функцию, команду или другой идентификатор,
    не переименовывай его без необходимости.
18. Если пользователь указал BOT_TOKEN,
    используй именно BOT_TOKEN.
19. Никогда не помещай API-ключи, токены или пароли
    непосредственно в исходный код.
20. Не выполняй действия сам — только составляй план.
21. Не добавляй комментарии вне JSON.
"""


def clean_json(response: str) -> str:
    response = response.strip()

    response = re.sub(
        r"^```(?:json)?\s*",
        "",
        response,
        flags=re.IGNORECASE,
    )

    response = re.sub(
        r"\s*```$",
        "",
        response,
    )

    return response.strip()


def plan(task: str) -> dict:
    if not task or not task.strip():
        raise ValueError("Задача не указана.")

    prompt = (
        PLANNER_PROMPT
        + "\n\nЗАДАЧА ПОЛЬЗОВАТЕЛЯ:\n"
        + task.strip()
    )

    # Coding-agent: план может быть длинным, оставляем больше
    # времени, чем у обычного чата (не быстрый дефолт 10 сек).
    response = clean_json(router.ask(prompt, timeout=60))

    try:
        result = json.loads(response)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"Planner вернул невалидный JSON:\n{response}"
        ) from e

    if not isinstance(result, dict):
        raise RuntimeError(
            "План должен быть JSON-объектом."
        )

    steps = result.get("steps")

    if not isinstance(steps, list):
        raise RuntimeError(
            "В плане отсутствует массив steps."
        )

    if not steps:
        raise RuntimeError(
            "Planner вернул пустой план."
        )

    for index, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            raise RuntimeError(
                f"Шаг {index} должен быть JSON-объектом."
            )

        action = step.get("action")

        if action not in ALLOWED_ACTIONS:
            raise RuntimeError(
                f"Недопустимое действие в шаге {index}: {action}"
            )

    return result
