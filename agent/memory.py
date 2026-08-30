import sqlite3
from pathlib import Path
from datetime import datetime, timezone


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MEMORY_DIR = PROJECT_ROOT / "data"
MEMORY_DB = MEMORY_DIR / "memory.sqlite3"

MAX_MESSAGES = 30


def _connect():
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(MEMORY_DB)
    connection.row_factory = sqlite3.Row

    return connection


def init_memory() -> None:
    with _connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT,
                created_at TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_chats_user_id
            ON chats(user_id, id)
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                chat_id INTEGER NOT NULL DEFAULT 0,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_messages_user_id
            ON messages(user_id, id)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_messages_chat_id
            ON messages(chat_id, id)
            """
        )

        connection.commit()


def create_chat(user_id: int, title: str | None = None) -> int:
    with _connect() as connection:
        connection.execute(
            """
            UPDATE chats
            SET is_active = 0
            WHERE user_id = ?
            """,
            (user_id,),
        )

        cursor = connection.execute(
            """
            INSERT INTO chats
            (user_id, title, created_at, is_active)
            VALUES (?, ?, ?, 1)
            """,
            (
                user_id,
                title,
                datetime.now(timezone.utc).isoformat(),
            ),
        )

        connection.commit()

        return int(cursor.lastrowid)


def get_active_chat_id(user_id: int) -> int:
    with _connect() as connection:
        row = connection.execute(
            """
            SELECT id
            FROM chats
            WHERE user_id = ?
              AND is_active = 1
            ORDER BY id DESC
            LIMIT 1
            """,
            (user_id,),
        ).fetchone()

        if row:
            return int(row["id"])

    return create_chat(user_id)


def get_chat_history(
    user_id: int,
    chat_id: int,
    limit: int = MAX_MESSAGES,
) -> list[dict[str, str]]:
    limit = max(1, min(limit, MAX_MESSAGES))

    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT role, content
            FROM messages
            WHERE user_id = ?
              AND chat_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, chat_id, limit),
        ).fetchall()

    rows.reverse()

    return [
        {
            "role": row["role"],
            "content": row["content"],
        }
        for row in rows
    ]


def add_message(
    user_id: int,
    role: str,
    content: str,
) -> None:
    if not content or not content.strip():
        return

    with _connect() as connection:
        connection.execute(
            """
            INSERT INTO messages
            (user_id, role, content, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                user_id,
                role,
                content.strip(),
                datetime.now(timezone.utc).isoformat(),
            ),
        )

        connection.execute(
            """
            DELETE FROM messages
            WHERE user_id = ?
            AND id NOT IN (
                SELECT id
                FROM messages
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT ?
            )
            """,
            (user_id, user_id, MAX_MESSAGES),
        )

        connection.commit()



def add_chat_message(
    user_id: int,
    chat_id: int,
    role: str,
    content: str,
) -> None:
    if not content or not content.strip():
        return

    with _connect() as connection:
        connection.execute(
            """
            INSERT INTO messages
            (user_id, chat_id, role, content, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user_id,
                chat_id,
                role,
                content.strip(),
                datetime.now(timezone.utc).isoformat(),
            ),
        )

        connection.execute(
            """
            DELETE FROM messages
            WHERE user_id = ?
              AND chat_id = ?
              AND id NOT IN (
                  SELECT id
                  FROM messages
                  WHERE user_id = ?
                    AND chat_id = ?
                  ORDER BY id DESC
                  LIMIT ?
              )
            """,
            (
                user_id,
                chat_id,
                user_id,
                chat_id,
                MAX_MESSAGES,
            ),
        )

        connection.commit()

    print("✅ add_chat_message добавлена")

def get_history(
    user_id: int,
    limit: int = MAX_MESSAGES,
) -> list[dict[str, str]]:
    limit = max(1, min(limit, MAX_MESSAGES))

    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT role, content
            FROM messages
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()

    rows.reverse()

    return [
        {
            "role": row["role"],
            "content": row["content"],
        }
        for row in rows
    ]


def clear_history(user_id: int) -> None:
    with _connect() as connection:
        connection.execute(
            "DELETE FROM messages WHERE user_id = ?",
            (user_id,),
        )
        connection.commit()


if __name__ == "__main__":
    init_memory()

    print("===== NEXORA MEMORY =====")
    print(f"База: {MEMORY_DB}")
    print("✅ SQLite-память инициализирована")
