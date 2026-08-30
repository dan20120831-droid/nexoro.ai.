from enum import Enum


class Plan(str, Enum):
    FREE = "free"
    PLUS = "plus"
    PRO = "pro"
    MAXIMUM = "maximum"
    DEVELOPER = "developer"


# Базовые лимиты.
# Коммерческие значения можно будет изменить позже
# без переделки остальной системы.
PLAN_LIMITS = {
    Plan.FREE: {
        "chat": 150,
        "code": 0,
        "images": 0,
    },
    Plan.PLUS: {
        "chat": 500,
        "code": 100,
        "images": 0,
    },
    Plan.PRO: {
        "chat": 2000,
        "code": 500,
        "images": 0,
    },
    Plan.MAXIMUM: {
        "chat": 10000,
        "code": 2000,
        "images": 0,
    },
    Plan.DEVELOPER: {
        "chat": -1,
        "code": -1,
        "images": -1,
    },
}


def get_plan_limits(plan: Plan) -> dict[str, int]:
    return PLAN_LIMITS[plan].copy()


def get_plan_limit(plan: Plan, feature: str) -> int:
    limits = PLAN_LIMITS.get(plan)

    if limits is None:
        limits = PLAN_LIMITS[Plan.FREE]

    return limits.get(feature, 0)


def is_unlimited(plan: Plan, feature: str) -> bool:
    return get_plan_limit(plan, feature) == -1


def has_feature_access(plan: Plan, feature: str) -> bool:
    limit = get_plan_limit(plan, feature)

    return limit != 0


def get_all_plans() -> list[str]:
    return [plan.value for plan in Plan]


print("✅ NEXORA plans.py загружен")
