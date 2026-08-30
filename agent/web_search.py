import html
import re
import urllib.parse
import urllib.request


def web_search(query: str, max_results: int = 5) -> list[dict[str, str]]:
    """
    Простой веб-поиск для NEXORA AI.
    Использует DuckDuckGo HTML без отдельного API-ключа.
    """

    encoded_query = urllib.parse.quote_plus(query)

    url = (
        "https://html.duckduckgo.com/html/"
        f"?q={encoded_query}"
    )

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "(Linux; Android 12) "
                "AppleWebKit/537.36 "
                "Chrome/131 Mobile Safari/537.36"
            )
        },
    )

    with urllib.request.urlopen(request, timeout=15) as response:
        page = response.read().decode("utf-8", errors="replace")

    results = []

    pattern = re.compile(
        r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
        re.S,
    )

    for match in pattern.finditer(page):
        if len(results) >= max_results:
            break

        raw_url = html.unescape(match.group(1))
        raw_title = re.sub(r"<[^>]+>", "", match.group(2))
        title = html.unescape(raw_title).strip()

        url = raw_url

        if "uddg=" in url:
            parsed = urllib.parse.urlparse(url)
            params = urllib.parse.parse_qs(parsed.query)

            if "uddg" in params:
                url = params["uddg"][0]

        if title and url:
            results.append(
                {
                    "title": title,
                    "url": url,
                }
            )

    return results


def format_search_results(results: list[dict[str, str]]) -> str:
    if not results:
        return "Поиск не вернул результатов."

    lines = ["РЕЗУЛЬТАТЫ ПОИСКА В ИНТЕРНЕТЕ:"]

    for index, item in enumerate(results, 1):
        lines.append(
            f"{index}. {item['title']}\n"
            f"URL: {item['url']}"
        )

    return "\n\n".join(lines)
