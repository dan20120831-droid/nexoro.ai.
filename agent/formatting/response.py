import re


def clean_markdown(text: str) -> str:
    """
    Очищает ответ AI от лишнего Markdown,
    который плохо выглядит в Telegram.
    """

    if not text:
        return ""

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Убираем HTML-код, если модель случайно его вернула.
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)

    # Убираем тройные Markdown-границы,
    # но сам код внутри сохраняем.
    text = re.sub(r"```(?:python|py)?\s*", "", text, flags=re.IGNORECASE)
    text = text.replace("```", "")

    # Убираем чрезмерные последовательности звёздочек.
    text = re.sub(r"\*{3,}", "", text)

    # Превращаем **заголовок** в обычный заголовок.
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)

    # Убираем одинарное выделение *текст*,
    # если это не похоже на математическое выражение.
    text = re.sub(r"(?<!\w)\*(.*?)\*(?!\w)", r"\1", text)

    # Убираем лишние пробелы перед переносом.
    text = re.sub(r"[ \t]+\n", "\n", text)

    # Не допускаем огромные пустые промежутки.
    text = re.sub(r"\n{4,}", "\n\n", text)

    # Убираем пробелы в начале и конце.
    return text.strip()


def format_response(text: str) -> str:
    """
    Приводит ответ NEXORA к аккуратному виду
    для Telegram.
    """

    text = clean_markdown(text)

    if not text:
        return "🤖 NEXORA не получила текстового ответа."

    lines = text.splitlines()

    formatted = []

    for line in lines:
        stripped = line.strip()

        if not stripped:
            formatted.append("")
            continue

        # Нормализуем простые списки.
        stripped = re.sub(
            r"^[•●▪◦]\s*",
            "• ",
            stripped,
        )

        stripped = re.sub(
            r"^[-–—]\s+",
            "• ",
            stripped,
        )

        formatted.append(stripped)

    text = "\n".join(formatted)

    # Повторно убираем лишние пустые строки.
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()
