from agent.planner import plan
from agent.executor import execute
from agent.repair import repair_python_file
from agent.tools import test_python_file
from agent.project_context import build_project_context


MAX_REPAIR_ATTEMPTS = 3


def _run_test_and_repair(
    filename: str,
    results: list[str],
) -> None:
    """
    Проверяет Python-файл и автоматически исправляет ошибки.
    """

    for attempt in range(1, MAX_REPAIR_ATTEMPTS + 1):
        test_result = test_python_file(filename)

        if "Код завершения: 0" in test_result:
            results.append(
                f"🧪 Проверка {filename}: успешно "
                f"(попытка {attempt})"
            )
            return

        if "Код завершения: 124" in test_result:
            results.append(
                f"⏱️ {filename}: обнаружен "
                f"долгоживущий процесс. "
                f"Автоисправление остановлено."
            )
            return

        results.append(
            f"❌ Ошибка {filename} "
            f"(попытка {attempt})"
        )

        if attempt == MAX_REPAIR_ATTEMPTS:
            results.append(
                f"🔴 Не удалось автоматически исправить "
                f"{filename} после "
                f"{MAX_REPAIR_ATTEMPTS} попыток.\n"
                f"{test_result}"
            )
            return

        try:
            repair_python_file(
                filename,
                test_result,
            )

            results.append(
                f"🔧 NEXORA исправляет {filename} "
                f"(попытка {attempt})"
            )

        except Exception as error:
            results.append(
                f"⚠️ Ошибка AI-исправления "
                f"{filename}: {error}"
            )
            return


def run_agent(task: str) -> str:
    """
    Основной многошаговый цикл NEXORA AI Coding Agent.
    """

    if not task or not task.strip():
        return "Задача не указана."

    project_context = build_project_context()

    planning_task = f'''
ЗАДАЧА ПОЛЬЗОВАТЕЛЯ:
{task.strip()}

ТЕКУЩИЙ КОНТЕКСТ ПРОЕКТА:
{project_context}

Используй контекст проекта, чтобы понять существующую
архитектуру и определить, какие файлы действительно
нужно создать, прочитать или изменить.
'''

    planned = plan(planning_task)

    steps = planned.get("steps")

    if not isinstance(steps, list) or not steps:
        raise RuntimeError(
            "Planner не вернул steps."
        )

    results = []

    for index, step in enumerate(steps, start=1):
        action_name = step.get("action")

        if not action_name:
            raise RuntimeError(
                f"В шаге {index} отсутствует action."
            )

        parameters = {
            key: value
            for key, value in step.items()
            if key != "action"
        }

        results.append(
            f"📍 Шаг {index}: {action_name}"
        )

        result = execute(
            action_name,
            **parameters,
        )

        results.append(result)

        if action_name in {
            "create_file",
            "edit_file",
        }:
            filename = parameters["filename"]

            _run_test_and_repair(
                filename,
                results,
            )

    return "\n\n".join(results)


if __name__ == "__main__":
    print("NEXORA AI Agent запущен.")
    print("Введите задачу или 'exit' для выхода.")

    while True:
        try:
            task = input("\nNEXORA > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nВыход.")
            break

        if task.lower() in {
            "exit",
            "quit",
            "выход",
        }:
            print("Выход.")
            break

        if not task:
            continue

        try:
            print("\nNEXORA AI:\n")
            print(run_agent(task))

        except Exception as error:
            print(
                f"\n❌ Ошибка агента: {error}"
            )
