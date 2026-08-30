import json
import os
import time
import urllib.parse
import urllib.request

BOT_TOKEN = os.getenv("BOT_TOKEN")
HELP_TEXT = "Доступные команды:\n/help — показать доступные команды"


def telegram_request(method, data=None):
    if not BOT_TOKEN:
        raise RuntimeError("Переменная окружения BOT_TOKEN не задана")

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    encoded_data = urllib.parse.urlencode(data or {}).encode("utf-8")

    with urllib.request.urlopen(url, data=encoded_data, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def send_message(chat_id, text):
    return telegram_request("sendMessage", {"chat_id": chat_id, "text": text})


def handle_message(message):
    text = message.get("text", "").strip()
    chat_id = message.get("chat", {}).get("id")

    if chat_id is not None and text.split("@", 1)[0] == "/help":
        send_message(chat_id, HELP_TEXT)


def run_bot():
    offset = None

    while True:
        try:
            data = {"timeout": 25}
            if offset is not None:
                data["offset"] = offset

            response = telegram_request("getUpdates", data)
            for update in response.get("result", []):
                offset = update["update_id"] + 1
                if "message" in update:
                    handle_message(update["message"])
        except Exception as error:
            print(f"Ошибка: {error}")
            time.sleep(3)


if __name__ == "__main__":
    run_bot()
