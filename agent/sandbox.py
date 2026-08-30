from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE = PROJECT_ROOT / "workspace"


def safe_path(filename: str) -> Path:
    """
    Разрешает агенту работать только внутри workspace.
    """
    path = (WORKSPACE / filename).resolve()

    if not path.is_relative_to(WORKSPACE.resolve()):
        raise ValueError("Доступ за пределы workspace запрещён")

    return path


def write_file(filename: str, content: str) -> Path:
    """
    Создаёт или перезаписывает файл внутри workspace.
    """
    path = safe_path(filename)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

    return path


def read_file(filename: str) -> str:
    """
    Читает файл только из workspace.
    """
    path = safe_path(filename)

    if not path.exists():
        raise FileNotFoundError(filename)

    return path.read_text(encoding="utf-8")


def run_python(filename: str) -> tuple[int, str, str]:
    """
    Запускает Python-файл внутри workspace.

    Если программа работает дольше 20 секунд,
    процесс принудительно останавливается и
    возвращается понятная ошибка вместо traceback.
    """
    path = safe_path(filename)

    if not path.exists():
        raise FileNotFoundError(filename)

    try:
        result = subprocess.run(
            [sys.executable, str(path)],
            cwd=str(WORKSPACE),
            capture_output=True,
            text=True,
            timeout=20,
        )

        return (
            result.returncode,
            result.stdout,
            result.stderr,
        )

    except subprocess.TimeoutExpired as error:
        stdout = error.stdout or ""
        stderr = error.stderr or ""

        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")

        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")

        timeout_message = (
            "Процесс остановлен: превышен лимит выполнения "
            "20 секунд. Возможно, программа является "
            "долгоживущим процессом (например, Telegram polling)."
        )

        return (
            124,
            stdout,
            f"{stderr}\n{timeout_message}".strip(),
        )


if __name__ == "__main__":
    print("NEXORA AI Agent sandbox: OK")
    print(f"Workspace: {WORKSPACE}")
