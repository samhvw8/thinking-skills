import unittest
from duration import parse_duration


class TestParseDuration(unittest.TestCase):
    def test_valid(self):
        for text, want in [("90s", 90), ("1h30m", 5400), ("2h", 7200), ("1h2m3s", 3723),
                           (" 5m ", 300), ("0s", 0), ("10m5s", 605), ("100h", 360000)]:
            with self.subTest(text=text):
                self.assertEqual(parse_duration(text), want)

    def test_invalid(self):
        for text in ["", "5", "5x", "1m1h", "1h1h", "-5s", "1.5h", "h", "1 h", "1h 2m"]:
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    parse_duration(text)


if __name__ == "__main__":
    unittest.main()
