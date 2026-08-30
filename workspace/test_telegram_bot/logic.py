import unittest


def is_even(n):
    return n % 2 == 0


class TestIsEven(unittest.TestCase):
    def test_two(self):
        self.assertTrue(is_even(2))

    def test_seven(self):
        self.assertFalse(is_even(7))

    def test_zero(self):
        self.assertTrue(is_even(0))

    def test_negative_four(self):
        self.assertTrue(is_even(-4))


if __name__ == "__main__":
    unittest.main()
