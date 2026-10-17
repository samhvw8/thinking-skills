import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from money import split_bill  # noqa: E402


class SplitBillTest(unittest.TestCase):
    def test_even(self):
        self.assertEqual(split_bill(10, 2), [5, 5])

    def test_extra_cents_go_first(self):
        self.assertEqual(split_bill(10, 3), [4, 3, 3])

    def test_sum_is_exact(self):
        for total in range(0, 200):
            for people in range(1, 8):
                self.assertEqual(sum(split_bill(total, people)), total)

    def test_zero_people(self):
        with self.assertRaises(ValueError):
            split_bill(10, 0)

    def test_three_way_dinner(self):
        self.assertEqual(split_bill(100, 3), [34, 34, 33])


if __name__ == "__main__":
    unittest.main()
