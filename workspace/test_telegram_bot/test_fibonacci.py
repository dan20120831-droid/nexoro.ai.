import unittest

from fibonacci import fibonacci


class FibonacciTests(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(fibonacci(0), 0)

    def test_one(self):
        self.assertEqual(fibonacci(1), 1)

    def test_ten(self):
        self.assertEqual(fibonacci(10), 55)

    def test_negative_number(self):
        with self.assertRaises(ValueError):
            fibonacci(-1)


if __name__ == "__main__":
    unittest.main()
