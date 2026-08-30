from pathlib import Path

from agent.tools import (
    create_python_file,
    read_python_file,
    edit_python_file,
    test_python_file,
)


WORKSPACE = Path(__file__).resolve().parent.parent / "workspace"


def _normalize_filename(filename: str) -> str:
    """
    Приводит путь к виду относительно workspace.
    """

    path = str(filename).strip().replace("\\", "/")

    while path.startswith("./"):
        path = path[2:]

    if path == "workspace":
        return ""

    if path.startswith("workspace/"):
        path = path[len("workspace/"):]

    return path


def list_workspace() -> str:
    """Возвращает список файлов в workspace."""

    files = []

    for path in sorted(WORKSPACE.rglob("*")):
        if path.is_file():
            files.append(str(path.relative_to(WORKSPACE)))

    if not files:
        return "WORKSPACE пуст."

    return "\n".join(files)


def read_file(filename: str) -> str:
    """Читает файл из workspace."""

    return read_python_file(
        _normalize_filename(filename)
    )


def create_file(filename: str, code: str) -> str:
    """Создаёт Python-файл."""

    filename = _normalize_filename(filename)

    if not filename.endswith(".py"):
        raise ValueError(
            "На этом этапе разрешены только .py файлы."
        )

    return create_python_file(filename, code)


def edit_file(filename: str, code: str) -> str:
    """Изменяет существующий Python-файл."""

    filename = _normalize_filename(filename)

    if not filename.endswith(".py"):
        raise ValueError(
            "На этом этапе разрешены только .py файлы."
        )

    return edit_python_file(filename, code)


def test_file(filename: str) -> str:
    """Запускает Python-файл."""

    return test_python_file(
        _normalize_filename(filename)
    )


def execute(action: str, **kwargs) -> str:
    """Единая точка выполнения инструментов NEXORA."""

    if action == "list_workspace":
        return list_workspace()

    if action == "read_file":
        return read_file(kwargs["filename"])

    if action == "create_file":
        return create_file(
            kwargs["filename"],
            kwargs["code"],
        )

    if action == "edit_file":
        return edit_file(
            kwargs["filename"],
            kwargs["code"],
        )

    if action == "test_file":
        return test_file(kwargs["filename"])

    raise ValueError(
        f"Неизвестное действие: {action}"
    )
