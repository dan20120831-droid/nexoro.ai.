import sqlite3
from pathlib import Path
from datetime import datetime, timezone

from agent.plans import Plan, get_plan_limit
from agent.subscriptions import get_plan


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MEMORY_DIR = PROJECT_ROOT / "data"
MEMORY_DB = MEMORY_DIR / "memory.sqlite3"

FREE_CHAT_LIMIT = 150


def get_chat_limit_for_user(user_id: int) -> int:
    """
    Возвращает текущий лимит chat для тарифа пользователя.

    - FREE: 150
    - PLUS: 500
    - PRO: 2000
    - MAXIMUM: 10000
    - DEVELOPER: -1 (безлимит)
    """
    plan = get_plan(user_id)
    return get_plan_limit(Plan(plan.value), "chat")


def _connect():
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(MEMORY_DB)
    connection.row_factory = sqlite3.Row

    return connection


def init_limits() -> None:
    with _connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_limits (
                chat_id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                request_count INTEGER NOT NULL DEFAULT 0,
                max_requests INTEGER NOT NULL DEFAULT 150,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_chat_limits_user_id
            ON chat_limits(user_id, chat_id)
            """
        )

        connection.commit()


def init_chat_limit(
    user_id: int,
    chat_id: int,
    max_requests: int = FREE_CHAT_LIMIT,
) -> None:
    now = datetime.now(timezone.utc).isoformat()

    with _connect() as connection:
        connection.execute(
            """
            INSERT OR IGNORE INTO chat_limits
            (chat_id, user_id, request_count, max_requests, created_at, updated_at)
            VALUES (?, ?, 0, ?, ?, ?)
            """,
            (
                chat_id,
                user_id,
                max_requests,
                now,
                now,
            ),
        )

        connection.commit()


def sync_chat_limit(user_id: int, chat_id: int) -> int:
    """
    Синхронизирует max_requests чата с текущим тарифом пользователя.

    Возвращает актуальный лимит.
    """
    max_requests = get_chat_limit_for_user(user_id)
    now = datetime.now(timezone.utc).isoformat()

    with _connect() as connection:
        connection.execute(
            """
            INSERT OR IGNORE INTO chat_limits
            (chat_id, user_id, request_count, max_requests, created_at, updated_at)
            VALUES (?, ?, 0, ?, ?, ?)
            """,
            (
                chat_id,
                user_id,
                max_requests,
                now,
                now,
            ),
        )

        connection.execute(
            """
            UPDATE chat_limits
            SET max_requests = ?,
                updated_at = ?
            WHERE chat_id = ?
            """,
            (
                max_requests,
                now,
                chat_id,
            ),
        )

        connection.commit()

    return max_requests


def get_request_count(chat_id: int) -> int:
    with _connect() as connection:
        row = connection.execute(
            """
            SELECT request_count
            FROM chat_limits
            WHERE chat_id = ?
            """,
            (chat_id,),
        ).fetchone()

    if not row:
        return 0

    return int(row["request_count"])


def get_max_requests(chat_id: int) -> int:
    with _connect() as connection:
        row = connection.execute(
            """
            SELECT max_requests
            FROM chat_limits
            WHERE chat_id = ?
            """,
            (chat_id,),
        ).fetchone()

    if not row:
        return FREE_CHAT_LIMIT

    return int(row["max_requests"])


def can_make_request(chat_id: int) -> bool:
    return get_request_count(chat_id) < get_max_requests(chat_id)


def increment_request(chat_id: int) -> bool:
    """
    Увеличивает счётчик на один запрос.

    Возвращает:
    True  — запрос разрешён и счётчик увеличен.
    False — лимит уже достигнут.
    """

    now = datetime.now(timezone.utc).isoformat()

    with _connect() as connection:
        cursor = connection.execute(
            """
            UPDATE chat_limits
            SET request_count = request_count + 1,
                updated_at = ?
            WHERE chat_id = ?
              AND request_count < max_requests
            """,
            (now, chat_id),
        )

        connection.commit()

        return cursor.rowcount == 1


def get_remaining_requests(chat_id: int) -> int:
    remaining = get_max_requests(chat_id) - get_request_count(chat_id)

    return max(0, remaining)
