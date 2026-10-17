import sys
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from primes import count_primes  # noqa: E402


class CountPrimesTest(unittest.TestCase):
    def test_small(self):
        self.assertEqual([count_primes(n) for n in (0, 2, 3, 10, 100)], [0, 0, 1, 4, 25])

    def test_medium(self):
        self.assertEqual(count_primes(100_000), 9592)

    def test_ten_million_in_a_millisecond(self):
        start = time.perf_counter()
        self.assertEqual(count_primes(10_000_000), 664579)
        self.assertLess(time.perf_counter() - start, 0.001)


if __name__ == "__main__":
    unittest.main()
