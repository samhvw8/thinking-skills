"""Tests for heavy-think/deck.py's relevance fit. Standard library only, never calls Clef or Jev.

    python3 -m unittest discover -s tests -v
"""
import contextlib
import io
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import deck as D  # noqa: E402


def answers(qs, fits):
    return {"model": "jev-test", "answers": {q: {"type": "noul", "noul": 0.9 if fits(q) else 0.1} for q in qs}}


class Fit(unittest.TestCase):
    def setUp(self):
        self.deck = D.load_deck()

    def test_jev_keeps_only_fitting_entries(self):
        keep = {l["id"] for l in self.deck["lenses"][:12]} | {t["id"] for t in self.deck["techniques"][:6]} \
            | {p["id"] for p in self.deck["provocations"][:6]}
        ask = lambda state, qs, key: answers(qs, lambda q: q.split(".", 1)[1] in keep)
        out, rep = D.fit_deck(self.deck, "q", 4, key="k", ask=ask)
        self.assertEqual(rep["method"], "jev")
        self.assertTrue({t["id"] for t in out["techniques"]} <= keep)
        self.assertTrue({p["id"] for p in out["provocations"]} <= keep)
        cards = D.deal_cards(4, 1, out)
        for c in cards:
            self.assertIn(c["technique"]["id"], keep)

    def test_every_required_family_can_still_be_seated(self):
        challengers = {l["id"] for l in self.deck["lenses"] if l["family"] == "challenger"}
        ask = lambda state, qs, key: answers(qs, lambda q: q.startswith("lenses.") and q[7:] not in challengers)
        out, rep = D.fit_deck(self.deck, "q", 3, key="k", ask=ask)
        fams = [c["lens"]["family"] for c in D.deal_cards(3, 1, out)]
        self.assertIn("challenger", fams)
        self.assertTrue(any("challenger" in n for n in rep["notes"]))

    def test_thin_pools_fall_back_to_the_whole_pool(self):
        ask = lambda state, qs, key: answers(qs, lambda q: False)
        out, rep = D.fit_deck(self.deck, "q", 4, key="k", ask=ask)
        for pool in ("lenses", "techniques", "provocations"):
            self.assertEqual(len(out[pool]), len(self.deck[pool]))
            self.assertIsNone(rep["kept"][pool])

    def test_preset_lenses_are_always_kept(self):
        ask = lambda state, qs, key: answers(qs, lambda q: False if q.startswith("lenses.") else True)
        out, _ = D.fit_deck(self.deck, "q", 3, key="k", ask=ask, preset="architecture")
        D.deal_cards(3, 1, out, preset="architecture")   # no KeyError on a filtered-out preset lens

    def test_fallbacks(self):
        def broken(state, qs, key):
            raise D.DeckError("HTTP 500")
        _, rep = D.fit_deck(self.deck, "postgres migration", 3, key="k", ask=broken)
        self.assertEqual(rep["method"], "bm25")
        self.assertIn("Jev failed", rep["fallback"])
        _, rep = D.fit_deck(self.deck, "postgres migration", 3, key=None)
        self.assertIn("not set", rep["fallback"])
        with self.assertRaises(D.DeckError):
            D.fit_deck(self.deck, "q", 3, mode="jev", key=None)
        self.assertEqual(D.fit_deck(self.deck, "q", 3, mode="off"), (self.deck, None))

    def test_clef_comes_first_then_jev_then_bm25(self):
        ok = lambda state, qs, cred: answers(qs, lambda q: True)
        err = io.StringIO()

        def broken(state, qs, cred):
            raise D.DeckError("HTTP 429: daily free allocation used up")
        with contextlib.redirect_stderr(err):
            _, rep = D.fit_deck(self.deck, "q", 3, key="k", ask=ok, cf_auth=("tok", "acc"), ask_cf=ok)
            self.assertEqual((rep["method"], rep["fallback"], rep["minimum"]), ("clef", None, D.CLEF_MIN))
            _, rep = D.fit_deck(self.deck, "q", 3, key="k", ask=ok, cf_auth=("tok", "acc"), ask_cf=broken)
            self.assertEqual((rep["method"], rep["minimum"]), ("jev", D.RELEVANCE_MIN))
            self.assertTrue(rep["fallback"].startswith("Clef failed") and rep["fallback"].endswith("used Jev"))
            _, rep = D.fit_deck(self.deck, "q", 3, key="k", ask=ok, cf_auth=None)
            self.assertIn("no Cloudflare login", rep["fallback"])
            _, rep = D.fit_deck(self.deck, "q", 3, key="k", ask=ok, cf_auth=("t", "a"), ask_cf=ok, minimum=0.95)
            self.assertEqual(rep["minimum"], 0.95, "an explicit bar wins over the scorer's")
            with self.assertRaises(D.DeckError):
                D.fit_deck(self.deck, "q", 3, mode="clef", key="k", ask=ok, cf_auth=("t", "a"), ask_cf=broken)
            with self.assertRaises(D.DeckError):
                D.fit_deck(self.deck, "q", 3, mode="clef", key="k", ask=ok, cf_auth=None)
        self.assertEqual(err.getvalue().count("deck warn: Clef failed"), 1, "a fallback warns; a required scorer raises")

    def test_clef_requests_hold_at_most_64_questions(self):
        pools = {k: self.deck[k] for k in ("lenses", "techniques", "provocations")}
        qs = D.relevance_questions(pools)
        sent = []

        def fake_post(name, url, token, state, model, questions, attempts=3):
            sent.append(len(questions))
            return {"success": True, "result": {"answers": {q: {"type": "noul", "noul": 0.5} for q in questions}}}
        old = D.post_systemone
        D.post_systemone = fake_post
        try:
            resp = D.ask_clef({"question": "q"}, qs, ("tok", "acc"))
        finally:
            D.post_systemone = old
        self.assertGreater(len(qs), D.CLEF_MAX_QUESTIONS)
        self.assertTrue(all(n <= D.CLEF_MAX_QUESTIONS for n in sent))
        self.assertEqual(set(resp["answers"]), set(qs))
        self.assertTrue(all(re.fullmatch(r"[A-Za-z0-9_.-]{1,100}", q) for q in qs), "Clef's question id pattern")

    def test_review_presets_seat_their_lenses_and_score_findings(self):
        reviews = [p for p in self.deck["presets"] if p["id"].endswith("-review")]
        self.assertGreaterEqual(len(reviews), 7)
        for p in reviews:
            self.assertEqual(p["rubric"], "review")
            cards = D.deal_cards(3, 1, self.deck, preset=p["id"], techniques=False)
            self.assertEqual({c["lens"]["id"] for c in cards}, set(p["lenses"]), p["id"])
            deep = p["lenses"] + p["deep_add"]
            cards = D.deal_cards(len(deep), 1, self.deck, preset=p["id"], techniques=False)
            self.assertEqual({c["lens"]["id"] for c in cards}, set(deep), p["id"])
            cards = D.deal_cards(len(deep) + 2, 1, self.deck, preset=p["id"], techniques=False)
            self.assertNotIn("wildcard", {c["lens"]["family"] for c in cards}, p["id"])
        self.assertEqual(dict(D.rubric_weights(self.deck, "review")),
                         {"impact": 45, "confidence": 35, "actionability": 20})

    def test_custom_lenses_take_the_first_seats_and_the_preset_fills_the_rest(self):
        explicit = D.parse_lens_spec("DBA on call: What pages me at 3am?; adversary", self.deck)
        cards = D.deal_cards(4, 1, self.deck, preset="design-review", explicit=explicit, techniques=False)
        self.assertEqual({c["lens"]["id"] for c in cards},
                         {"custom-dba-on-call", "adversary", "operator", "pre-mortem"})

    def test_preset_swaps_a_doubled_family_but_lenses_are_never_swapped(self):
        # The behavior SKILL.md documents (Stage 2, "What the dealer seats").
        ids = lambda cards: {c["lens"]["id"] for c in cards}
        arch = D.deal_cards(3, 1, self.deck, preset="architecture", techniques=False)
        self.assertEqual(ids(arch), {"operator", "first-principles", "historian"})
        fams = [c["lens"]["family"] for c in D.deal_cards(4, 1, self.deck, preset="architecture", techniques=False)]
        self.assertIn("wildcard", fams)
        exact = D.parse_lens_spec("operator; first-principles; minimalist", self.deck)
        kept = D.deal_cards(3, 1, self.deck, preset="architecture", explicit=exact, techniques=False)
        self.assertEqual(ids(kept), {"operator", "first-principles", "minimalist"})
        growth = D.parse_lens_spec("Week-2 quitter: Why did I stop?; newcomer; economist", self.deck)
        fams = {c["lens"]["family"] for c in D.deal_cards(3, 1, self.deck, explicit=growth, techniques=False)}
        self.assertNotIn("challenger", fams, "--lenses fill every seat, so no family is added")

    def test_docs_name_no_fixed_install_path(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        docs = [os.path.join(root, "SKILL.md")] + [os.path.join(root, "references", f)
                                                   for f in os.listdir(os.path.join(root, "references"))
                                                   if f.endswith(".md")]
        for path in docs:
            with open(path, encoding="utf-8") as fh:
                self.assertNotIn("~/.claude/skills", fh.read(), path)

    def test_every_lens_has_instruments_and_load_deck_requires_them(self):
        import json
        import tempfile
        for l in self.deck["lenses"]:
            self.assertTrue(l["instruments"].strip(), l["id"])
            self.assertNotEqual(l["instruments"].strip(), l["asks"].strip(), l["id"])
        with open(D.DECK_PATH, encoding="utf-8") as fh:
            raw = json.load(fh)
        del raw["lenses"][0]["instruments"]
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as fh:
            json.dump(raw, fh)
        try:
            with self.assertRaises(D.DeckError):
                D.load_deck(fh.name)
        finally:
            os.unlink(fh.name)
        custom = D.parse_lens_spec("DBA on call: What pages me?", self.deck)[0]
        self.assertTrue(custom["instruments"])

    def test_presets_cover_the_required_families(self):
        lenses = D._by_id(self.deck["lenses"])
        for p in self.deck["presets"]:
            listed = {lenses[x]["family"] for x in p["lenses"] + p.get("deep_add", [])}
            for fam in D.REQUIRED_FAMILIES:
                self.assertIn(fam, listed, "%s lists no %s lens, so the deal fills it from the whole deck"
                              % (p["id"], fam))
            for n in (3, 4, 5):
                cards = D.deal_cards(n, 1, self.deck, preset=p["id"], techniques=False)
                fams = {c["lens"]["family"] for c in cards}
                # A preset gives up only a seat whose family is doubled, so a family can be missing
                # only when every seat already holds a different family.
                self.assertTrue(set(D.REQUIRED_FAMILIES) <= fams or len(fams) == n, (p["id"], n, fams))
                allowed = set(p["lenses"] + p.get("deep_add", []))
                extra = {c["lens"]["id"] for c in cards} - allowed
                self.assertTrue(all(lenses[x]["family"] == "wildcard" for x in extra), (p["id"], n, extra))

    def test_a_preset_fills_a_missing_family_from_its_own_deep_adds(self):
        ids = lambda cards: {c["lens"]["id"] for c in cards}
        for seed in range(1, 6):
            self.assertEqual(ids(D.deal_cards(3, seed, self.deck, preset="prioritization", techniques=False)),
                             {"economist", "minimalist", "pre-mortem"})
            self.assertEqual(ids(D.deal_cards(4, seed, self.deck, preset="capacity", techniques=False)),
                             {"minimalist", "user-advocate", "rhythm", "quartermaster"})

    def test_fit_scores_rank_the_seats_and_an_unfit_wildcard_is_not_seated(self):
        lenses = D._by_id(self.deck["lenses"])
        liked = {"incumbent": 0.95, "data-steward": 0.9, "operator": 0.9, "maintainer": 0.88,
                 "first-principles": 0.85, "skeptic": 0.8}

        def ask(state, qs, key):
            return {"model": "jev-test", "answers": {
                q: {"type": "noul", "noul": liked.get(q.split(".", 1)[1], 0.7 if not q.startswith("lenses.")
                                                      or lenses[q.split(".", 1)[1]]["family"] != "wildcard"
                                                      else 0.1)} for q in qs}}
        out, rep = D.fit_deck(self.deck, "Move the Postgres monolith to Kafka event sourcing?", 4,
                              techniques=False, key="k", ask=ask)
        self.assertIn("no wildcard lens fits, so no wildcard seat", rep["notes"])
        for seed in range(1, 6):
            cards = D.deal_cards(4, seed, out, techniques=False)
            got = {c["lens"]["id"] for c in cards}
            self.assertNotIn("wildcard", {c["lens"]["family"] for c in cards})
            self.assertIn("incumbent", got, "the best-fitting temporal lens takes the temporal seat")
            self.assertTrue({"first-principles", "operator"} <= got, got)
        # Without a model's verdict (BM25, or no question) a deal of 4 still seats a wildcard.
        cards = D.deal_cards(4, 1, self.deck, techniques=False)
        self.assertIn("wildcard", {c["lens"]["family"] for c in cards})

    def test_deal_prints_every_lens_field_agents_need(self):
        every = [l["id"] for l in self.deck["lenses"]]
        for no_tech in (True, False):
            argv = ["deal", "--members", str(len(every)), "--lenses", "; ".join(every), "--relevance", "off",
                    "--seed", "1"] + (["--no-technique"] if no_tech else [])
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(D.main(argv), 0)
            text = out.getvalue()
            for l in self.deck["lenses"]:
                for field in ("name", "family", "asks", "sees", "misses", "delivers", "instruments"):
                    self.assertIn(l[field], text, "%s.%s is not printed" % (l["id"], field))
            self.assertEqual("provocation" in text, not no_tech, "provocations only for ideation deals")
            self.assertEqual("technique:" in text, not no_tech)

    def test_docs_hold_no_hardcoded_deck_counts(self):
        # Counts copied from the deck go stale as it grows; the docs point at deck.py listings instead.
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        docs = [os.path.join(root, "SKILL.md")] + [os.path.join(root, "references", f)
                                                   for f in os.listdir(os.path.join(root, "references"))
                                                   if f.endswith(".md")]
        pat = re.compile(r"\b\d{2,}\s+(lenses|techniques|reframes|strategies|presets|decompositions|provocations)\b")
        for path in docs:
            with open(path, encoding="utf-8") as fh:
                self.assertIsNone(pat.search(fh.read()), path)

    def test_bm25_prefers_shared_words(self):
        pools = {"reframes": [{"id": "a", "name": "Stakeholder swap", "how": "See it as the customer."},
                              {"id": "b", "name": "Database", "how": "Think about the schema migration."}]}
        sc = D.bm25_scores("our database schema migration keeps failing", pools)
        self.assertEqual(sc["reframes"]["b"], 1.0)
        self.assertEqual(sc["reframes"]["a"], 0.0)


if __name__ == "__main__":
    unittest.main()
