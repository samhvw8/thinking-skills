"""Tests for council.py. Standard library only; never calls Clef, Jev or an agent.

    python3 -m unittest discover -s skills/council/tests -v
"""
import contextlib
import copy
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import council as C  # noqa: E402

D = C.D


def run(argv):
    """main(argv) -> (exit code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = C.main(argv)
    return code, out.getvalue(), err.getvalue()


class InTempDir(unittest.TestCase):
    """Every test runs in its own empty folder, since council writes .council/ in the cwd."""

    def setUp(self):
        self.old = os.getcwd()
        self.tmp = tempfile.mkdtemp(prefix="council-test-")
        os.chdir(self.tmp)
        self.deck = D.load_deck()

    def tearDown(self):
        os.chdir(self.old)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def state(self, n=5, judges=2, shortlist=2, rubric="creative", deck=None):
        d = os.path.join(self.tmp, ".council", "run")
        os.makedirs(d)
        with open(os.path.join(d, "brief.md"), "w", encoding="utf-8") as fh:
            fh.write("How might we test a council?\n")
        st = C.new_state(n, 1, deck or self.deck, d, 1, judges, shortlist, 6, rubric=rubric)
        for path in C.all_idea_files(st):   # the member rounds are done; tests start at the curator
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("### idea\n")
        C.save_state(st)
        return st

    def with_pool(self, st, ids=("C01", "C02", "C03")):
        st["pool"] = [{"id": c, "title": "t" + c, "pitch": "p", "parents": ["m01.1"], "members": ["m01"],
                       "orphan": False} for c in ids]
        with open(C.pool_out(st["dir"]), "w", encoding="utf-8") as fh:   # the curator's file, already collected
            json.dump({"concepts": st["pool"]}, fh)
        C.save_state(st)
        return st

    def write_judge(self, st, judge, data):
        os.makedirs(os.path.join(st["dir"], "score"), exist_ok=True)
        with open(C.score_out(st["dir"], judge), "w", encoding="utf-8") as fh:
            fh.write(data if isinstance(data, str) else json.dumps(data))

    def good_scores(self, st, base=5):
        keys = [k for k, _ in st["weights"]]
        return {"scores": {c["id"]: dict({k: base for k in keys}, off_brief=False) for c in st["pool"]}}


# ---------------------------------------------------------------- judges

class StrictJudges(InTempDir):
    def test_garbage_judge_is_rejected_not_counted(self):
        st = self.with_pool(self.state())
        self.write_judge(st, "j1", self.good_scores(st))
        # The audit's t2 judge: wrong id, a non-dict score, a phantom id, no 'emergence' anywhere.
        keys = [k for k, _ in st["weights"] if k != "emergence"]
        self.write_judge(st, "j2", {"scores": {"C1": {k: 5 for k in keys}, "C02": "great",
                                               "C03": {k: 5 for k in keys}, "C99": {k: 5 for k in keys}}})
        code, out, _ = run(["collect", "--dir", st["dir"]])
        self.assertNotEqual(code, 0)
        self.assertIn("rejected", out)
        st = C.load_state(type("A", (), {"dir": st["dir"]})())
        self.assertIsNone(st["shortlist"], "a shortlist was built from one judge")
        self.assertTrue(os.path.exists(C.score_out(st["dir"], "j2") + ".unreadable"))

    def test_missing_criterion_or_non_number_rejects_the_file(self):
        st = self.with_pool(self.state())
        bad = self.good_scores(st)
        bad["scores"]["C02"]["novelty"] = "high"
        problems = C.verdict_problems(st, bad)
        self.assertTrue(any("C02" in p and "novelty" in p for p in problems))
        bad = self.good_scores(st)
        del bad["scores"]["C03"]
        self.assertTrue(any("C03" in p for p in C.verdict_problems(st, bad)))
        bad = self.good_scores(st)
        bad["scores"]["C01"]["value"] = 11
        self.assertTrue(C.verdict_problems(st, bad))
        bad = self.good_scores(st)
        bad["scores"]["C01"]["value"] = True
        self.assertTrue(C.verdict_problems(st, bad))
        self.assertEqual(C.verdict_problems(st, self.good_scores(st)), [])

    def test_judges_counted_per_concept_are_reported(self):
        st = self.with_pool(self.state())
        self.write_judge(st, "j1", self.good_scores(st, 5))
        self.write_judge(st, "j2", self.good_scores(st, 7))
        code, out, _ = run(["collect", "--dir", st["dir"]])
        self.assertEqual(code, 0, out)
        code, out, _ = run(["harvest", "--dir", st["dir"]])
        self.assertEqual(code, 0)
        self.assertIn("2 of 2 judges", out)


# ---------------------------------------------------------------- failure has an end

class EndStates(InTempDir):
    def test_curator_no_output_stops_the_run(self):
        st = self.state()
        with open(C.pool_out(st["dir"]), "w") as fh:
            fh.write("NO OUTPUT\n")
        code, out, err = run(["collect", "--dir", st["dir"]])
        self.assertNotEqual(code, 0)
        code, out, err = run(["next", "--dir", st["dir"]])
        self.assertNotEqual(code, 0)
        self.assertIn("STOPPED", out + err)
        self.assertNotIn("cluster", (out + err).split("STOPPED", 1)[0])

    def test_curator_garbage_twice_stops_the_run(self):
        st = self.state()
        for _ in range(2):
            with open(C.pool_out(st["dir"]), "w") as fh:
                fh.write("not json at all")
            code, _, _ = run(["collect", "--dir", st["dir"]])
            self.assertNotEqual(code, 0)
        code, out, err = run(["next", "--dir", st["dir"]])
        self.assertNotEqual(code, 0)
        self.assertIn("STOPPED", out + err)

    def test_one_garbage_curator_gets_a_rerun(self):
        st = self.state()
        with open(C.pool_out(st["dir"]), "w") as fh:
            fh.write("not json at all")
        run(["collect", "--dir", st["dir"]])
        code, out, _ = run(["next", "--dir", st["dir"]])
        self.assertEqual(code, 0)
        self.assertIn("cluster", out)

    def test_failed_judge_is_dropped_when_enough_remain(self):
        st = self.with_pool(self.state(judges=3))
        self.write_judge(st, "j1", self.good_scores(st, 5))
        self.write_judge(st, "j2", self.good_scores(st, 6))
        self.write_judge(st, "j3", "NO OUTPUT")
        code, out, _ = run(["collect", "--dir", st["dir"]])
        self.assertIn("dropped", out)
        st = C.load_state(type("A", (), {"dir": st["dir"]})())
        self.assertTrue(st["shortlist"])
        code, out, _ = run(["next", "--dir", st["dir"]])
        self.assertEqual(code, 0)
        self.assertIn("develop", out)

    def test_too_few_judges_left_stops_the_run(self):
        st = self.with_pool(self.state(judges=2))
        self.write_judge(st, "j1", self.good_scores(st))
        self.write_judge(st, "j2", "NO OUTPUT")
        code, _, _ = run(["collect", "--dir", st["dir"]])
        self.assertNotEqual(code, 0)
        code, out, err = run(["next", "--dir", st["dir"]])
        self.assertNotEqual(code, 0)
        self.assertIn("STOPPED", out + err)


# ---------------------------------------------------------------- init and errors

class Init(InTempDir):
    def runs(self):
        root = os.path.join(self.tmp, ".council")
        return [x for x in os.listdir(root) if os.path.isdir(os.path.join(root, x))] if os.path.isdir(root) else []

    def test_failed_init_leaves_no_folder(self):
        code, _, err = run(["init", "--brief", "q", "--preset", "code-review", "--relevance", "off"])
        self.assertNotEqual(code, 0)
        self.assertIn("council:", err)
        self.assertEqual(self.runs(), [])

    def test_same_second_retry_works(self):
        with mock.patch.object(C.time, "strftime", return_value="20260101-000000"):
            a = run(["init", "--brief", "q", "--relevance", "off", "--seed", "1"])
            b = run(["init", "--brief", "q", "--relevance", "off", "--seed", "1"])
        self.assertEqual(a[0], 0, a[2])
        self.assertEqual(b[0], 0, b[2])
        self.assertEqual(len(self.runs()), 2)

    def test_missing_brief_file_is_a_message_not_a_traceback(self):
        code, _, err = run(["init", "--brief-file", os.path.join(self.tmp, "nope.md"), "--relevance", "off"])
        self.assertNotEqual(code, 0)
        self.assertIn("council:", err)
        self.assertNotIn("Traceback", err)

    def test_deck_error_is_a_message_not_a_traceback(self):
        code, _, err = run(["init", "--brief", "q", "--preset", "no-such-preset", "--relevance", "off"])
        self.assertNotEqual(code, 0)
        self.assertIn("council:", err)
        self.assertEqual(self.runs(), [])

    def test_members_below_the_minimum_are_refused(self):
        for n in ("0", "-3", "2"):
            code, _, err = run(["plan", "--members", n])
            self.assertNotEqual(code, 0, n)
            self.assertIn("--members", err)
        self.assertEqual(run(["plan", "--members", "3"])[0], 0)

    def test_model_is_recorded_and_named_in_prompts(self):
        code, out, err = run(["init", "--brief", "q", "--relevance", "off", "--seed", "1", "--model", "opus"])
        self.assertEqual(code, 0, err)
        # Judgment phases run on the session's model, research phases on the fast tier.
        self.assertIn("diverge opus", out)
        self.assertIn("develop fast", out)
        self.assertIn("stress fast", out)
        code, out, _ = run(["prompts", "diverge"])
        self.assertIn("model opus", out)
        st = C.load_state(type("A", (), {"dir": None})())
        self.assertEqual(C.phase_model(st, "score"), "opus")
        self.assertEqual(C.phase_model(st, "stress"), "fast")

    def test_default_models_are_tiers_not_one_vendors_names(self):
        # Without --model the run must work in any harness: no Claude model names, no Claude tool names.
        code, out, err = run(["init", "--brief", "q", "--relevance", "off", "--seed", "1"])
        self.assertEqual(code, 0, err)
        self.assertIn("diverge session", out)
        code, out, _ = run(["prompts", "diverge"])
        for vendor in ("sonnet", "opus", "subagent_type", "general-purpose"):
            self.assertNotIn(vendor, out)
        self.assertIn("harness.md", out)

    def test_phase_model_override(self):
        code, out, err = run(["init", "--brief", "q", "--relevance", "off", "--seed", "1", "--model", "opus",
                              "--phase-model", "develop=opus,cluster=sonnet"])
        self.assertEqual(code, 0, err)
        st = C.load_state(type("A", (), {"dir": None})())
        self.assertEqual(C.phase_model(st, "develop"), "opus")
        self.assertEqual(C.phase_model(st, "cluster"), "sonnet")
        self.assertEqual(C.phase_model(st, "stress"), "fast")
        code, _, err = run(["init", "--brief", "q", "--relevance", "off", "--phase-model", "nophase=opus"])
        self.assertNotEqual(code, 0)


# ---------------------------------------------------------------- the pool

class Pool(InTempDir):
    def test_unknown_member_in_lineage_is_rejected(self):
        st = self.state(n=5)
        data = {"concepts": [{"id": "C01", "title": "t", "pitch": "p", "parents": ["m09.1"], "members": ["m09"]}]}
        with self.assertRaises(C.CouncilError):
            C.parse_pool(st, data)
        data = {"concepts": [{"id": "C01", "title": "t", "pitch": "p", "parents": ["m01.1", "zz"]}]}
        with self.assertRaises(C.CouncilError):
            C.parse_pool(st, data)

    def test_good_lineage_is_kept(self):
        st = self.state(n=5)
        pool = C.parse_pool(st, {"concepts": [{"id": "C01", "title": "t", "pitch": "p",
                                               "parents": ["m01.1", "m03.r1.2"], "members": ["m01"]}]})
        self.assertEqual(pool[0]["members"], ["m01", "m03"])


# ---------------------------------------------------------------- tally

class Tally(InTempDir):
    def test_decision_tie_break_uses_novelty(self):
        st = self.state(rubric="decision", shortlist=1)
        st = self.with_pool(st, ("C01", "C02"))
        base = {"feasibility": 5, "running_cost": 5, "specificity": 5, "off_brief": False}
        # Equal weighted means: 35*4 + 10*7 == 35*6 + 10*0. C01 is the more novel one.
        v = {"scores": {"C01": dict(base, value=4, novelty=7), "C02": dict(base, value=6, novelty=0)}}
        table, short = C.tally(st, [v])
        self.assertEqual(table["C01"]["mean"], table["C02"]["mean"])
        self.assertEqual(short, ["C01"])


# ---------------------------------------------------------------- the deck contract

class DeckContract(InTempDir):
    def broken(self, pool, field):
        deck = copy.deepcopy(self.deck)
        del deck[pool][0][field]
        return deck

    def test_check_names_every_missing_card_field(self):
        C.check_deck(self.deck)
        for pool, field in (("lenses", "sees"), ("lenses", "misses"), ("techniques", "how"),
                            ("provocations", "text")):
            with self.assertRaises(C.CouncilError) as cm:
                C.check_deck(self.broken(pool, field))
            self.assertIn(field, str(cm.exception))

    def test_init_fails_before_any_folder_on_a_broken_deck(self):
        deck = self.broken("provocations", "text")
        with mock.patch.object(C, "load_deck", return_value=deck):
            code, _, err = run(["init", "--brief", "q", "--relevance", "off"])
        self.assertNotEqual(code, 0)
        self.assertIn("text", err)
        self.assertFalse(os.path.isdir(os.path.join(self.tmp, ".council")) and
                         any(os.path.isdir(os.path.join(self.tmp, ".council", x))
                             for x in os.listdir(os.path.join(self.tmp, ".council"))))

    def member_prompts(self, st, member):
        templates = C.load_templates()
        brief = C.read_brief(st)
        out = []
        for phase in ("diverge", "cross1"):
            job = next(j for j in C.phase_jobs(st, phase) if j["member"] == member)
            out.append(C.render_job(st, job, templates, brief))
        return "\n".join(out)

    def test_every_lens_field_reaches_the_members(self):
        """Fails when the deck gains a lens field (like instruments) that no member prompt shows."""
        st = self.state()
        for lens in self.deck["lenses"]:
            st["members"]["m01"]["card"]["lens"] = lens
            text = self.member_prompts(st, "m01")
            for field, value in lens.items():
                if field in C.LENS_META_FIELDS:
                    continue
                shown = value if isinstance(value, str) else "; ".join(value)
                self.assertIn(shown, text, "lens %s: field '%s' is never shown to members" % (lens["id"], field))

    def test_instruments_are_rendered_and_required(self):
        deck = copy.deepcopy(self.deck)
        for l in deck["lenses"]:
            l["instruments"] = "a stopwatch and the raw server logs for " + l["id"]
        st = self.state(deck=deck)
        lens = st["members"]["m01"]["card"]["lens"]
        text = self.member_prompts(st, "m01")
        self.assertIn(lens["instruments"], text)
        self.assertIn("which instrument", text)

    def test_no_instruments_line_without_the_field(self):
        st = self.state()
        st["members"]["m01"]["card"]["lens"].pop("instruments", None)
        self.assertNotIn("nstrument", self.member_prompts(st, "m01"))


class Docs(unittest.TestCase):
    def test_no_hardcoded_deck_counts(self):
        # Counts copied from the deck go stale as it grows (SKILL.md once said 36 lenses at 41).
        import re
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pats = [re.compile(r"\b\d{2,}\s+(lenses|techniques|provocations|presets)\b"),
                re.compile(r"\b(lens|lenses|technique|techniques)\b\W[^.]{0,30}\b\d{2,}\b")]
        for f in ("SKILL.md", "prompts.md"):
            with open(os.path.join(root, f), encoding="utf-8") as fh:
                text = fh.read()
            for pat in pats:
                self.assertIsNone(pat.search(text), f)


if __name__ == "__main__":
    unittest.main()
