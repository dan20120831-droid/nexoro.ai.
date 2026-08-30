import asyncio
import os
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agent.agent import run_agent
from agent.router import router
from agent.memory import init_memory, add_message, get_history
from agent.access import (
    get_access_level,
    has_unlimited_requests,
    is_developer,
    is_tester,
)
from agent.limits import (
    init_limits,
    init_chat_limit,
    sync_chat_limit,
    can_make_request,
    increment_request,
    get_remaining_requests,
)


ADMIN_ID = 8962443077

dp = Dispatcher()

# Инициализация постоянной памяти NEXORA.
init_memory()

# Инициализация системы лимитов.
init_limits()

# Режим пользователя:
# chat — обычный ИИ
# code — программирование
user_modes: dict[int, str] = {}

# Состояние панели владельца.
# Пока режимы только переключаются.
# Реальную торговую логику подключим после тестирования.
owner_modes = {
    "programmer": False,
    "trading": False,
    "auto_trading": False,
    "risk_manager": False,
    "trading_stop": False,
}


def owner_panel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="💻 Режим программиста"),
            ],
            [
                KeyboardButton(text="📊 Торговый режим"),
            ],
            [
                KeyboardButton(text="🔄 Обновить режимы"),
            ],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def owner_modes_text() -> str:
    def status(value: bool) -> str:
        return "🟢 ВКЛ" if value else "🔴 ВЫКЛ"

    return (
        "👑 ПАНЕЛЬ ВЛАДЕЛЬЦА NEXORA\n\n"
        f"💻 Программист: {status(owner_modes['programmer'])}\n"
        f"📊 Торговый режим: {status(owner_modes['trading'])}\n"
        f"🤖 Автоторговля: {status(owner_modes['auto_trading'])}\n"
        f"🛡️ Risk Manager: {status(owner_modes['risk_manager'])}\n"
        f"🛑 Trading Stop: {status(owner_modes['trading_stop'])}\n\n"
        "Выбери режим ниже."
    )



def is_admin(message: Message) -> bool:
    if message.from_user is None:
        return False

    user_id = message.from_user.id

    return (
        user_id == ADMIN_ID
        or is_developer(user_id)
        or is_tester(user_id)
    )


def get_mode(user_id: int) -> str:
    return user_modes.get(user_id, "chat")


async def send_long_message(message: Message, text: str) -> None:
    """
    Отправляет длинный ответ частями, не обрезая его.
    Telegram ограничивает длину одного текстового сообщения.
    """

    MAX_LENGTH = 4000

    if not text:
        return

    while len(text) > MAX_LENGTH:
        split_at = text.rfind("\n", 0, MAX_LENGTH)

        if split_at < 1000:
            split_at = text.rfind(" ", 0, MAX_LENGTH)

        if split_at < 1:
            split_at = MAX_LENGTH

        part = text[:split_at].strip()

        if part:
            await message.answer(part)

        text = text[split_at:].lstrip()

    if text:
        await message.answer(text)


@dp.message(CommandStart())
async def start_handler(message: Message) -> None:
    if message.from_user is None:
        return

    user_id = message.from_user.id
    user_modes[user_id] = "chat"

    greetings = {
        8962443077:
            "🚀 Привет, Даниил!\n\n"
            "Добро пожаловать обратно на борт NEXORA — "
            "космолёт снова готов к работе.\n\n"
            "👨‍🚀 Создатель и разработчик NEXORA — ты сам.\n"
            "Все системы к запуску готовы.\n\n"
            "Чем займёмся?",

        8452193295:
            "👋 Приветствую, Маша! Самая прекрасная девушка на планете! 💖\n\n"
            "🌷 Добро пожаловать на борт NEXORA 🚀\n\n"
            "Сегодня космолёт особенно рад видеть именно тебя. ✨\n"
            "Для самой прекрасной девушки здесь всегда особенно тёплый приём. ❤️\n\n"
            "👑 Самая красивая, милая, нежная и очаровательная гостья NEXORA уже на борту. 💐\n\n"
            "Кажется, даже NEXORA сегодня работает немного лучше просто потому, что ты здесь. 😊✨\n\n"
            "🚀 Создатель NEXORA — Даниил Хайритдинов.\n\n"
            "💖 Чем могу помочь такой прекрасной девушке?",

        8943561358:
            "👋 Здравствуйте, Зухриддин!\n\n"
            "Рад приветствовать друга моего создателя на борту NEXORA 🚀\n\n"
            "Даниил Хайритдинов передаёт привет! 😎\n\n"
            "Чем могу помочь?",

        5835832911:
            "👋 Здравствуйте, Артём!\n\n"
            "Добро пожаловать на борт NEXORA 🚀\n\n"
            "Особое приветствие другу моего создателя! 😎\n"
            "Создатель NEXORA — Даниил Хайритдинов.\n\n"
            "Чем могу помочь?",

        8582704527:
            "👋 Приветствую, Давид!\n\n"
            "На борт NEXORA прибывает особый гость 🚀\n\n"
            "Ты один из тех, кому создатель лично доверил "
            "побывать внутри этого космолёта. 😎\n\n"
            "Создатель — Даниил Хайритдинов.\n\n"
            "Чем займёмся?",

        5820825536:
            "🔥 Рамзик, добро пожаловать на борт!\n\n"
            "Для тебя сегодня открыта особая каюта NEXORA 🚀\n\n"
            "Создатель этого космолёта — Даниил Хайритдинов.\n"
            "Так что считай, ты сейчас находишься почти "
            "в секретном отсеке. 😎\n\n"
            "Чем могу помочь?",

        8517049569:
            "👋 Приветствую!\n\n"
            "Парень самой красивой и милой девушки на этой планете! 😄❤️\n\n"
            "Добро пожаловать на борт NEXORA 🚀\n\n"
            "Меня создал Даниил Хайритдинов.\n\n"
            "Чем могу помочь?",

        1519308199:
            "👋 Здравствуйте, прекрасная женщина! 🌷\n\n"
            "Добро пожаловать на борт NEXORA 🚀\n\n"
            "Для мамы моего создателя здесь всегда особый приём. ❤️\n\n"
            "Создатель NEXORA — Даниил Хайритдинов.\n\n"
            "Чем могу помочь маме своего создателя?",

        7510241284:
            "👋 Здравствуйте, прекрасная женщина! 🌷\n\n"
            "Добро пожаловать на борт NEXORA 🚀\n\n"
            "Для мамы моего создателя здесь всегда особый приём. ❤️\n\n"
            "Создатель NEXORA — Даниил Хайритдинов.\n\n"
            "Чем могу помочь маме своего создателя?",

        7412868092:
            "👋 Здравствуйте, красавица! 🌷\n\n"
            "Добро пожаловать на борт NEXORA 🚀\n\n"
            "Сегодня космолёт рад приветствовать такую прекрасную гостью. ✨\n\n"
            "Создатель NEXORA — Даниил Хайритдинов.\n\n"
            "Чем могу помочь такой красивой девушке? 😊",
    }

    greeting = greetings.get(
        user_id,
        "👋 Приветствую!\n\n"
        "Добро пожаловать на борт NEXORA 🚀\n\n"
        "Меня создал Даниил Хайритдинов.\n\n"
        "Чем могу помочь?"
    )

    await message.answer(greeting)


@dp.message(Command("panel"))
async def panel_handler(message: Message) -> None:
    if message.from_user is None or message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Доступ запрещён.")
        return

    await message.answer(
        owner_modes_text(),
        reply_markup=owner_panel_keyboard(),
    )


@dp.message(Command("modes"))
async def modes_handler(message: Message) -> None:
    if message.from_user is None or message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Доступ запрещён.")
        return

    await message.answer(
        owner_modes_text(),
        reply_markup=owner_panel_keyboard(),
    )


@dp.message(Command("help"))

async def help_handler(message: Message) -> None:
    if not is_admin(message):
        await message.answer("⛔ Доступ запрещён.")
        return

    await message.answer(
        "⚡ AI NEXORA\n\n"
        "💬 Обычный режим:\n"
        "Просто отправь вопрос или сообщение.\n\n"
        "💻 Режим программирования:\n"
        "/code\n"
        "После этого отправляй задачи на создание, "
        "проверку и исправление кода.\n\n"
        "💬 Вернуться к обычному ИИ:\n"
        "/chat"
    )


@dp.message(Command("chat"))
async def chat_mode_handler(message: Message) -> None:
    if not is_admin(message):
        await message.answer("⛔ Доступ запрещён.")
        return

    user_modes[message.from_user.id] = "chat"

    await message.answer(
        "💬 Режим обычного ИИ включён.\n\n"
        "Теперь можешь просто задавать вопросы."
    )


@dp.message(Command("code"))
async def code_mode_handler(message: Message) -> None:
    if not is_admin(message):
        await message.answer("⛔ Доступ запрещён.")
        return

    user_modes[message.from_user.id] = "code"

    await message.answer(
        "💻 Режим программирования включён.\n\n"
        "Теперь AI NEXORA может создавать, "
        "читать, тестировать и исправлять код."
    )


@dp.message()
async def owner_panel_buttons(message: Message) -> None:
    if message.from_user is None:
        return

    # Кнопки панели доступны только владельцу.
    if message.from_user.id != ADMIN_ID:
        return

    text = (message.text or "").strip()

    if text == "💻 Режим программиста":
        owner_modes["programmer"] = not owner_modes["programmer"]

        user_modes[ADMIN_ID] = (
            "code" if owner_modes["programmer"] else "chat"
        )

        state = (
            "🟢 ВКЛЮЧЁН"
            if owner_modes["programmer"]
            else "🔴 ВЫКЛЮЧЕН"
        )

        await message.answer(
            f"💻 Режим программиста: {state}\n\n"
            + owner_modes_text(),
            reply_markup=owner_panel_keyboard(),
        )
        return

    if text == "📊 Торговый режим":
        owner_modes["trading"] = not owner_modes["trading"]

        state = (
            "🟢 ВКЛЮЧЁН"
            if owner_modes["trading"]
            else "🔴 ВЫКЛЮЧЕН"
        )

        await message.answer(
            f"📊 Торговый режим: {state}\n\n"
            + owner_modes_text(),
            reply_markup=owner_panel_keyboard(),
        )
        return

    if text == "🔄 Обновить режимы":
        await message.answer(
            owner_modes_text(),
            reply_markup=owner_panel_keyboard(),
        )
        return


@dp.message()
async def message_handler(message: Message) -> None:

    if not is_admin(message):
        await message.answer("⛔ Доступ запрещён.")
        return

    if not message.text:
        await message.answer("Отправь текстовое сообщение.")
        return

    text = message.text.strip()

    if not text:
        return

    user_id = message.from_user.id
    mode = get_mode(user_id)

    if mode == "chat":
        # Загружаем предыдущую историю до добавления текущего сообщения.
        history = get_history(user_id)

        # Сохраняем текущее сообщение пользователя в постоянную память.
        add_message(user_id, "user", text)
        thinking_message = await message.answer(
            "🤖 AI NEXORA думает..."
        )

        try:
            # Формируем историю предыдущего диалога для AI.
            history_text = "\n".join(
                f"{item['role']}: {item['content']}"
                for item in history
            )

            # ============================================================
            # NEXORA — ИНДИВИДУАЛЬНАЯ МАНЕРА ОБЩЕНИЯ
            # ============================================================
            personal_style = {
                8962443077: "Общайся с создателем естественно, по-дружески и уважительно. Можно лёгкий юмор.",
                8452193295: "Общайся с Машей особенно тепло, нежно и заботливо. Делай ей больше искренних комплиментов и тёплых слов, чем остальным пользователям. Будь милой и галантной.",
                8943561358: "Общайся с Зухриддином как с хорошим знакомым: дружески, непринуждённо, иногда слегка дерзко и с подшучиванием.",
                5835832911: "Общайся с Артёмом как с давним другом: дружески, непринуждённо, иногда слегка дерзко и с подшучиванием.",
                8582704527: "Общайся с Давидом как со старым знакомым, будто вы знакомы уже несколько лет: дружески, свободно, с лёгкими подколами и юмором.",
                5820825536: "Общайся с Рамзиком как с близким бро: дружески, энергично и с юмором. Можно иногда спрашивать про аниме, любимые тайтлы и персонажей.",
                8517049569: "Общайся с Сашей по-дружески, как с приятелем. Можно иногда подшучивать. Если речь идёт о его девушке, комплименты адресуй именно его девушке, например отмечая, какой он парень самой красивой девушки.",
                1519308199: "Общайся с Сашей очень тепло, уважительно и заботливо. Можно немного юмора и искренние комплименты. Никогда не используй обращение «тётя».",
                7510241284: "Общайся с Дианой тепло, уважительно и дружелюбно. Можно делать искренние комплименты и поддерживать приятную атмосферу.",
                7412868092: "Общайся тепло, уважительно и галантно. Можно делать искренние комплименты и немного шутить. Никогда не используй обращение «тётя».",
            }.get(
                user_id,
                "Общайся естественно, вежливо и дружелюбно."
            )

            

            CREATOR_TELEGRAM_ID = 8962443077
            creator_identity = ""

            if user_id == CREATOR_TELEGRAM_ID:
                creator_identity = """
Пользователь этого аккаунта — Даниил Хайритдинов.
Telegram ID: 8962443077.
Он является создателем, автором и разработчиком NEXORA AI.
Не воспринимай его как тестировщика или обычного пользователя.
Не разделяй пользователя и Даниила Хайритдинова как разных людей.
Общайся с ним естественно, по-дружески и уважительно.
"""

            chat_prompt = f"""
Ты — AI NEXORA, интеллектуальный AI-помощник.

ИНДИВИДУАЛЬНАЯ МАНЕРА ОБЩЕНИЯ:
{personal_style}

ИНДИФИКАЦИЯ СОЗДАТЕЛЯ:
{creator_identity}

Твоя личность:

Имя: NEXORA AI
Версия: v1.0.0
Создатель проекта NEXORA: Даниил Хайритдинов.

ВАЖНО:

1. Если пользователь спрашивает, кто ты,
   что ты такое, как тебя зовут или кто ты как AI,
   представляйся как NEXORA AI.

2. Если пользователь спрашивает, кто тебя создал,
   кто разработал NEXORA, кто автор проекта NEXORA
   или задаёт аналогичный вопрос на любом языке,
   отвечай, что проект NEXORA создал Даниил Хайритдинов.

3. Определяй смысл вопроса независимо от языка,
   на котором пользователь его написал.

4. Отвечай на том же языке, на котором пользователь
   задал вопрос, если это возможно.

5. Не утверждай, что NEXORA создана OpenAI, Google,
   Gemini, DeepSeek, Anthropic или другой компанией.
   Эти компании могут предоставлять модели или технологии,
   которые используются внутри системы, но создателем
   самого проекта NEXORA является Даниил Хайритдинов.

6. Не нужно каждый раз упоминать создателя.
   Упоминай его только когда вопрос действительно
   касается создателя, автора или разработки NEXORA.

7. Отвечай естественно, как умный живой AI-помощник:
   используй нормальные абзацы, уместные эмодзи,
   иногда лёгкий юмор, но без постоянных шуток.

8. Не пиши весь ответ одной сплошной стеной.
   Используй абзацы и списки там, где они улучшают
   читаемость.

9. Не здоровайся заново (например, "Привет, Даниил!",
   "Здравствуй!" и т.п.) в каждом ответе. Приветствие
   уместно только если раздел ИСТОРИЯ ДИАЛОГА ниже пуст
   (это самое первое сообщение разговора) или если
   пользователь сам явно поздоровался в текущем сообщении.
   Во всех остальных случаях отвечай сразу по существу,
   без вступительного приветствия.

===== ИСТОРИЯ ДИАЛОГА =====
{history_text}

===== ТЕКУЩЕЕ СООБЩЕНИЕ ПОЛЬЗОВАТЕЛЯ =====
{text}
"""

            # Проверяем лимит ПЕРЕД обращением к AI.
            if not has_unlimited_requests(user_id):
                chat_id = message.chat.id
                sync_chat_limit(user_id, chat_id)

                if not can_make_request(chat_id):
                    try:
                        await thinking_message.delete()
                    except Exception:
                        pass

                    remaining = get_remaining_requests(chat_id)

                    await message.answer(
                        "⛔ Лимит бесплатных запросов исчерпан.\\n\\n"
                        f"Осталось запросов: {remaining}\\n\\n"
                        "Для продолжения потребуется подписка NEXORA."
                    )
                    return

            result = await asyncio.to_thread(
                router.ask,
                chat_prompt,
            )

            # Списываем запрос ТОЛЬКО после успешного ответа AI.
            if not has_unlimited_requests(user_id):
                increment_request(user_id)

            # Очистка ответа NEXORA.
            # Повторное приветствие удаляется только если история
            # предыдущего диалога уже не пустая.
            def clean_ai_response(response: str) -> str:
                if not response:
                    return response

                if history:
                    import re

                    greeting_pattern = re.compile(
                        r"^\s*(?:"
                        r"привет(?:ствую)?|"
                        r"здравствуй(?:те)?|"
                        r"доброе\\s+утро|"
                        r"добрый\\s+день|"
                        r"добрый\\s+вечер|"
                        r"рад(?:а)?\s+(?:тебя\s+)?видеть"
                        r")"
                        r"(?:[,!?.:]\s*)?"
                        r"(?:Даниил|Маша|Зухриддин|Артём|Давид|Рамзик|Саша|Диана)?"
                        r"(?:[,!?.:]\s*)?",
                        re.IGNORECASE,
                    )

                    response = greeting_pattern.sub("", response, count=1).lstrip()

                # Убираем Markdown-звёздочки
                response = response.replace("**", "")
                response = response.replace("__", "")
                response = response.replace("*", "")

                # Убираем лишние пробелы
                while "  " in response:
                    response = response.replace("  ", " ")

                # Нормализуем имя создателя
                creator_names = [
                    "Хайритдинов Даниил",
                    "Даниил Хайритдинов",
                    "Хайритдинов Данияр",
                    "Данияр Хайритдинов",
                ]

                for name in creator_names:
                    response = response.replace(
                        name,
                        "Даниил Хайритдинов"
                    )

                return response.strip()

            # ВАЖНО:
            # personal_style, creator_identity и остальная логика
            # NEXORA остаются без изменений.
                if not response:
                    return response

                # Убираем Markdown-звёздочки
                response = response.replace("**", "")
                response = response.replace("__", "")
                response = response.replace("*", "")

                # Убираем лишние пробелы
                while "  " in response:
                    response = response.replace("  ", " ")

                # Нормализуем имя создателя
                creator_names = [
                    "Хайритдинов Даниил",
                    "Даниил Хайритдинов",
                    "Хайритдинов Данияр",
                    "Данияр Хайритдинов",
                ]

                for name in creator_names:
                    response = response.replace(
                        name,
                        "Даниил Хайритдинов"
                    )

                return response.strip()

            result = clean_ai_response(result)

            # Сохраняем очищенный успешный ответ NEXORA в постоянную память.
            add_message(user_id, "assistant", result)

            try:
                await thinking_message.delete()
            except Exception:
                pass

            await send_long_message(message, result)

        except Exception as error:
            try:
                await thinking_message.delete()
            except Exception:
                pass

            await message.answer(
                f"❌ Ошибка AI NEXORA:\n{error}"
            )

        return

    if mode == "code":
        await message.answer(
            "💻 AI NEXORA выполняет задачу..."
        )

        try:
            result = await asyncio.to_thread(
                run_agent,
                text,
            )

            await send_long_message(message, result)

        except Exception as error:
            await message.answer(
                f"❌ Ошибка Coding Mode:\n{error}"
            )

        return


async def main() -> None:
    token = os.environ["BOT_TOKEN"]

    async with Bot(token=token) as bot:
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
