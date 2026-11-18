import unittest

from numerical import (
    derivative,
    gradient,
    integral,
    integral_1d,
    monte_carlo_1d,
    monte_carlo_integral,
    sparse_integral,
    sum_of_squares,
)


class TestNumerical(unittest.TestCase):
    def test_derivative(self):
        cube = lambda x: x ** 3
        for method in ("central", "forward", "backward"):
            with self.subTest(method=method):
                self.assertAlmostEqual(derivative(cube, 2.0, method=method), 12.0, places=3)
        self.assertAlmostEqual(derivative(cube, 2.0, method="central"), 12.0, places=8)

    def test_gradient(self):
        g = gradient(sum_of_squares, (1.0,) * 100)
        self.assertEqual(len(g), 100)
        for value in g:
            self.assertAlmostEqual(value, 2.0, places=8)

        g = gradient(sum_of_squares, (0.5,) * 5)
        for value in g:
            self.assertAlmostEqual(value, 1.0, places=8)

    def test_integral_1d_methods(self):
        exact = 1 / 3
        self.assertAlmostEqual(integral_1d(lambda x: x * x, 0, 1, 10_000), exact, places=8)
        self.assertAlmostEqual(integral_1d(lambda x: x * x, 0, 1, 1000, "left"), exact, places=2)
        self.assertAlmostEqual(integral_1d(lambda x: x * x, 0, 1, 1000, "right"), exact, places=2)
        self.assertAlmostEqual(integral_1d(lambda x: x * x, 0, 1, 1000, "trapezoid"), exact, places=6)
        self.assertAlmostEqual(integral_1d(lambda x: x * x, 0, 1, 1000, "simpson"), exact, places=12)
        self.assertAlmostEqual(integral_1d(lambda x: 4 * x ** 3, 0, 2, 1000, "simpson"), 16.0, places=8)

    def test_integral_nd_riemann(self):
        cases = {1: 10_000, 2: 200, 5: 10}
        for n, steps in cases.items():
            with self.subTest(n=n):
                low, high = (0.0,) * n, (1.0,) * n
                value = integral(sum_of_squares, low, high, steps=steps, method="grid")
                self.assertAlmostEqual(value, n / 3, delta=0.01)

    def test_integral_non_unit_box(self):
        value = integral(sum_of_squares, (0.0, 0.0), (2.0, 3.0), steps=400, method="grid")
        self.assertAlmostEqual(value, 3 * (8 / 3) + 2 * 9, delta=0.02)

    def test_grid_cursee_of_dimensionality(self):
        with self.assertRaises(ValueError):
            integral(sum_of_squares, (0.0,) * 100, (1.0,) * 100, steps=2, method="grid")

    def test_sparse_integral_100d(self):
        low, high = (0.0,) * 100, (1.0,) * 100
        self.assertAlmostEqual(sparse_integral(sum_of_squares, low, high), 100 / 3, places=9)
        self.assertAlmostEqual(integral(sum_of_squares, low, high), 100 / 3, places=9)

    def test_monte_carlo_1d(self):
        for seed in (0, 1, 42):
            with self.subTest(seed=seed):
                value = monte_carlo_1d(lambda x: x * x, 0, 1, samples=100_000, seed=seed)
                self.assertAlmostEqual(value, 1 / 3, delta=0.01)

    def test_monte_carlo_nd(self):
        for n in (1, 2, 5, 100):
            with self.subTest(n=n):
                low, high = (0.0,) * n, (1.0,) * n
                value, error = monte_carlo_integral(
                    sum_of_squares, low, high, samples=100_000, seed=42, with_error=True
                )
                self.assertGreater(error, 0)
                self.assertAlmostEqual(value, n / 3, delta=max(5 * error, 0.02))

    def test_sum_of_squares(self):
        self.assertEqual(sum_of_squares(3), 9)
        self.assertEqual(sum_of_squares((1, 2, 3)), 14)


if __name__ == "__main__":
    unittest.main(verbosity=2)
