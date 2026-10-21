"""Tests for ambition's card dealer and deck. Standard library only.

Run: python3 -m unittest discover -s skills/ambition/tests
"""
import contextlib
import io
import json
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))
import deal as D  # noqa: E402

DECK = json.loads(D.DECK.read_text())


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPTS / "deal.py"), *args], capture_output=True, text=True)


class DeckTest(unittest.TestCase):
    def test_every_visible_pattern_deals_a_fitted_model(self):
        # An empty pattern makes the dealer fall back to cards unrelated to the task.
        for p in DECK["patterns"]:
            usable = [m for m in p["models"] if m != "cynefin-framework"]
            if not p.get("hidden"):
                self.assertGreaterEqual(len(usable), 2, p["id"])

    def test_cards_have_a_move_and_a_receipt(self):
        ids = {m["id"] for m in DECK["models"]}
        self.assertEqual(len(ids), len(DECK["models"]), "model ids are unique")
        for m in DECK["models"]:
            self.assertTrue(m["move"] and m["receipt"], m["id"])
        for f in DECK["fields"]:
            for k in ("verbs", "method", "instruments", "receipt"):
                self.assertTrue(f[k], (f["id"], k))

    def test_lenses_include_a_challenger(self):
        self.assertIn("challenger", {l["family"] for l in DECK["lenses"]})


class DealTest(unittest.TestCase):
    def test_stemmer_matches_word_forms(self):
        self.assertEqual(D.words("failing failed fails"), {"fail"})
        self.assertEqual(D.words("limiter limits"), {"limit"})

    def test_second_pattern_still_contributes_when_its_top_model_is_taken(self):
        # Both patterns list pre-mortem; the second must give its next model instead of nothing.
        _, _, models, _, _ = D.deal("decide whether to migrate the billing database",
                                    pattern_ids=["pre-decision-adversarial-review", "reversibility-gate"])
        reasons = [why for _, why in models]
        self.assertIn("pattern: reversibility-gate", reasons)
        self.assertEqual(len({m["id"] for m, _ in models}), 3)

    def test_fill_cards_without_overlap_are_labelled(self):
        _, _, models, _, _ = D.deal("zzz qqq", pattern_ids=["structural-communication"], seed=1)
        fills = [why for _, why in models if why.startswith("fill")]
        self.assertTrue(all("no fit" in w for w in fills), fills)

    def test_auto_patterns_say_when_nothing_matched(self):
        _, note, _, _, _ = D.deal("zzz qqq")
        self.assertIn("no pattern shares a word", note)

    def test_lenses_seat_a_challenger_and_differ_by_family(self):
        _, _, _, _, lenses = D.deal("rate limiter lets bursts through", seed=3)
        fams = [l["family"] for l in lenses]
        self.assertIn("challenger", fams)
        self.assertEqual(len(fams), len(set(fams)))

    def test_fields_rank_by_verbs(self):
        top = D.rank_fields(DECK, "reconcile the totals and audit for manipulation")[0][1]
        self.assertEqual(top["id"], "forensic-accounting")

    def test_same_task_and_seed_deal_the_same_cards(self):
        a = D.deal("cut checkout latency", seed=7)
        b = D.deal("cut checkout latency", seed=7)
        self.assertEqual([m["id"] for m, _ in a[2]], [m["id"] for m, _ in b[2]])


class CliTest(unittest.TestCase):
    def test_patterns_listing_shows_counts_and_hides_meta_patterns(self):
        out = run("patterns").stdout
        self.assertIn("models)", out)
        self.assertNotIn("classify-before-solving", out)

    def test_bad_arguments_fail_with_usage_not_a_traceback(self):
        for args in (["deal", "x", "--seed"], ["deal", "x", "--seed", "abc"]):
            r = run(*args)
            self.assertNotEqual(r.returncode, 0)
            self.assertNotIn("Traceback", r.stderr)

    def test_deal_prints_every_section(self):
        out = run("deal", "find why signups halved", "--patterns", "symptom-vs-structure-trap").stdout
        for h in ("## Patterns", "## Models", "## Range fields", "## Lenses", "Receipt:", "Instruments:"):
            self.assertIn(h, out)


if __name__ == "__main__":
    unittest.main()
