from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE = PROJECT_ROOT / "workspace"

MAX_FILE_SIZE = 50000
MAX_FILES = 40

IGNORED_DIRS = {
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "node_modules",
}


def _is_ignored(path: Path) -> bool:
    return any(
        part in IGNORED_DIRS
        for part in path.parts
    )


def list_project_files() -> list[str]:
    """Возвращает доступные файлы проекта."""

    if not WORKSPACE.exists():
        return []

    files = []

    for path in sorted(WORKSPACE.rglob("*")):
        if not path.is_file():
            continue

        if _is_ignored(path):
            continue

        try:
            relative = path.relative_to(WORKSPACE)
        except ValueError:
            continue

        files.append(str(relative))

        if len(files) >= MAX_FILES:
            break

    return files


def read_project_file(filename: str) -> str:
    """Безопасно читает файл проекта."""

    path = (WORKSPACE / filename).resolve()

    if not path.is_relative_to(WORKSPACE.resolve()):
        raise ValueError(
            "Доступ за пределы workspace запрещён."
        )

    if not path.exists():
        raise FileNotFoundError(filename)

    if not path.is_file():
        raise ValueError(
            f"{filename} не является файлом."
        )

    size = path.stat().st_size

    if size > MAX_FILE_SIZE:
        return (
            f"[Файл слишком большой: {size} байт. "
            f"Максимум: {MAX_FILE_SIZE} байт.]"
        )

    try:
        return path.read_text(
            encoding="utf-8"
        )
    except UnicodeDecodeError:
        return (
            "[Файл не является обычным UTF-8 текстом.]"
        )


def build_project_context() -> str:
    """
    Создаёт компактный контекст проекта:
    список файлов + содержимое небольших текстовых файлов.
    """

    files = list_project_files()

    if not files:
        return "WORKSPACE пуст."

    sections = [
        "===== PROJECT FILES =====",
        *files,
        "",
        "===== PROJECT CONTENT =====",
    ]

    for filename in files:
        path = WORKSPACE / filename

        # Пока анализируем текстовые файлы.
        if path.suffix.lower() not in {
            ".py",
            ".txt",
            ".json",
            ".md",
            ".html",
            ".css",
            ".js",
            ".ts",
            ".yaml",
            ".yml",
        }:
            continue

        content = read_project_file(filename)

        sections.extend(
            [
                "",
                f"===== {filename} =====",
                content,
            ]
        )

    return "\n".join(sections)


if __name__ == "__main__":
    print(build_project_context())
