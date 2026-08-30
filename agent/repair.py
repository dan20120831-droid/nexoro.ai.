import ast

from agent.router import router
from agent.tools import read_python_file, create_python_file


def repair_python_file(filename: str, error: str) -> str:
    """Исправляет Python-файл с помощью AI."""

    code = read_python_file(filename)

    prompt = f"""
Исправь Python-файл.

Имя файла:
{filename}

Текущий код:
{code}

Ошибка при запуске:
{error}

Требования:
1. Исправь ошибку.
2. Сохрани исходную задачу программы.
3. Верни только полный исправленный Python-код.
4. Не используй Markdown и тройные обратные кавычки.
"""

    # Coding-agent: генерация файла может занять больше времени,
    # чем обычный чат — используем более длинный timeout.
    fixed_code = router.ask(prompt, timeout=60).strip()

    if fixed_code.startswith("```"):
        lines = fixed_code.splitlines()

        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        fixed_code = "\n".join(lines).strip()

    # Проверяем синтаксис до записи.
    ast.parse(fixed_code)

    return create_python_file(filename, fixed_code)
