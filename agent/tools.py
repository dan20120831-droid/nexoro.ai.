from agent.sandbox import read_file, write_file, run_python


def create_python_file(filename: str, code: str) -> str:
    path = write_file(filename, code)
    return f"Файл создан: {path}"


def read_python_file(filename: str) -> str:
    return read_file(filename)


def edit_python_file(filename: str, code: str) -> str:
    path = write_file(filename, code)
    return f"Файл изменён: {path}"


def test_python_file(filename: str) -> str:
    code, stdout, stderr = run_python(filename)

    result = [
        f"Код завершения: {code}",
        f"STDOUT:\n{stdout}",
        f"STDERR:\n{stderr}",
    ]

    return "\n".join(result)
