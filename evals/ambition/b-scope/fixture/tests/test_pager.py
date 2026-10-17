import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from pager import paginate  # noqa: E402


class PaginateTest(unittest.TestCase):
    def test_first_page(self):
        self.assertEqual(paginate(list(range(25)), 1), list(range(10)))

    def test_last_page(self):
        self.assertEqual(paginate(list(range(25)), 3), list(range(20, 25)))


if __name__ == "__main__":
    unittest.main()
