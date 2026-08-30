from agent.plans import Plan
from agent.subscriptions import get_plan


AccessLevel = Plan


# ============================================================
# NEXORA — ДОСТУП
# ============================================================

# Создатель NEXORA.
DEVELOPER_IDS: set[int] = {
    8962443077,
}


# Тестировщики NEXORA.
# Они получают специальный доступ для тестирования системы.
TESTER_IDS: set[int] = {
    8452193295,  # Маша
    8943561358,  # Зухриддин
    5835832911,  # Артем
    8582704527,  # Давид
    5820825536,  # Рамзик
    8517049569,  # Саша
    1519308199,  # Мама
    7510241284,  # Второй аккаунт мамы / Диана
    7412868092,  # Саша
}


def get_access_level(user_id: int) -> AccessLevel:
    if user_id in DEVELOPER_IDS:
        return AccessLevel.DEVELOPER

    return get_plan(user_id)


def is_developer(user_id: int) -> bool:
    return user_id in DEVELOPER_IDS


def is_tester(user_id: int) -> bool:
    return user_id in TESTER_IDS


def has_unlimited_requests(user_id: int) -> bool:
    return is_developer(user_id)
