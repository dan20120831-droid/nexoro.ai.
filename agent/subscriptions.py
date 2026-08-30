import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from agent.plans import Plan as AccessLevel


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SUBSCRIPTIONS_DB = DATA_DIR / "subscriptions.sqlite3"


def _connect():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(SUBSCRIPTIONS_DB)
    connection.row_factory = sqlite3.Row

    return connection


def init_subscriptions() -> None:
    with _connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS subscriptions (
                user_id INTEGER PRIMARY KEY,
                plan TEXT NOT NULL,
                expires_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        connection.commit()


def set_plan(
    user_id: int,
    plan: AccessLevel,
    expires_at: str | None = None,
) -> None:
    now = datetime.now(timezone.utc).isoformat()

    with _connect() as connection:
        connection.execute(
            """
            INSERT INTO subscriptions
                (user_id, plan, expires_at, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                plan = excluded.plan,
                expires_at = excluded.expires_at,
                updated_at = excluded.updated_at
            """,
            (
                user_id,
                plan.value,
                expires_at,
                now,
                now,
            ),
        )

        connection.commit()


def get_plan(user_id: int) -> AccessLevel:
    with _connect() as connection:
        row = connection.execute(
            """
            SELECT plan, expires_at
            FROM subscriptions
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()

    if not row:
        return AccessLevel.FREE

    plan = AccessLevel(row["plan"])
    expires_at = row["expires_at"]

    if plan == AccessLevel.DEVELOPER:
        return plan

    if expires_at:
        try:
            expiration = datetime.fromisoformat(expires_at)

            if expiration <= datetime.now(timezone.utc):
                return AccessLevel.FREE

        except ValueError:
            return AccessLevel.FREE

    return plan


def get_subscription_info(user_id: int) -> dict:
    with _connect() as connection:
        row = connection.execute(
            """
            SELECT plan, expires_at, created_at, updated_at
            FROM subscriptions
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()

    if not row:
        return {
            "plan": AccessLevel.FREE.value,
            "expires_at": None,
            "created_at": None,
            "updated_at": None,
        }

    return dict(row)


print("✅ NEXORA subscriptions.py загружен")
