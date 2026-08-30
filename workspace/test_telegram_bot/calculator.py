def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    if b == 0:
        raise ValueError("Деление на ноль невозможно")
    return a / b


if __name__ == "__main__":
    tests = [
        ("add(2, 3)", add(2, 3), 5),
        ("add(-4, 1)", add(-4, 1), -3),
        ("subtract(10, 4)", subtract(10, 4), 6),
        ("subtract(3, 8)", subtract(3, 8), -5),
        ("multiply(6, 7)", multiply(6, 7), 42),
        ("multiply(-3, 5)", multiply(-3, 5), -15),
        ("divide(20, 4)", divide(20, 4), 5.0),
        ("divide(7, 2)", divide(7, 2), 3.5),
    ]

    for expression, result, expected in tests:
        assert result == expected, f"Ошибка: {expression} вернул {result}, ожидалось {expected}"
        print(f"{expression} = {result}")

    try:
        divide(10, 0)
    except ValueError as error:
        print(f"divide(10, 0): {error}")
    else:
        raise AssertionError("Деление на ноль не вызвало ожидаемую ошибку")

    print("Все тесты успешно пройдены.")
