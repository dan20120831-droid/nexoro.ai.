def fibonacci(n):
    """Return the n-th Fibonacci number."""
    if n < 0:
        raise ValueError("n must be non-negative")

    current, following = 0, 1
    for _ in range(n):
        current, following = following, current + following
    return current
