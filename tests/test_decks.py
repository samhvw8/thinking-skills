"""The shared decks: one source in decks/, a current copy in every skill, and every skill
working with no other skill installed. Standard library only.

Run: python3 -m unittest discover -s tests
"""
import copy
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("build_decks", ROOT / "tools" / "build_decks.py")
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)

# What each skill must still do when it is the only skill installed.
ALONE = {
    "ambition": [["scripts/deal.py", "patterns"]],
    "council": [["council.py", "presets"], ["council.py", "deal", "--members", "4", "--seed", "1", "--relevance", "off"]],
    "heavy-think": [["deck.py", "presets"], ["deck.py", "deal", "--members", "4", "--seed", "1", "--relevance", "off"]],
    "debate": [["deck/deck.py", "debates"]],
    "creative": [],
}


def py(*args, cwd):
    return subprocess.run([sys.executable, *args], cwd=cwd, capture_output=True, text=True)


class DecksTest(unittest.TestCase):
    def test_every_skill_copy_is_current(self):
        r = py(str(ROOT / "tools" / "build_decks.py"), "--check", cwd=ROOT)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_a_dangling_reference_fails_the_build(self):
        schema = B.load_json(B.DECKS / "schema.json")
        decks = B.load_decks(schema)
        B.validate(decks, schema)
        broken = copy.deepcopy(decks)
        broken["presets"][0]["lenses"][0] = "no-such-lens"
        with self.assertRaises(B.BuildError) as e:
            B.validate(broken, schema)
        self.assertIn("no-such-lens", str(e.exception))
        broken = copy.deepcopy(decks)
        broken["patterns"][0]["models"].append("no-such-model")
        with self.assertRaises(B.BuildError):
            B.validate(broken, schema)

    def test_a_missing_field_or_duplicate_id_fails_the_build(self):
        schema = B.load_json(B.DECKS / "schema.json")
        decks = B.load_decks(schema)
        broken = copy.deepcopy(decks)
        del broken["lenses"][0]["instruments"]
        broken["models"].append(dict(broken["models"][0]))
        with self.assertRaises(B.BuildError) as e:
            B.validate(broken, schema)
        self.assertIn("instruments", str(e.exception))
        self.assertIn("duplicate", str(e.exception))

    def test_every_deck_file_is_reusable_json_with_ids(self):
        for path in sorted(B.DECKS.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, list) and data and isinstance(data[0], dict) and path.stem != "debate_rules":
                self.assertTrue(all("id" in e for e in data), path.name)


class NoSiblingDeckTest(unittest.TestCase):
    def test_no_skill_reads_another_skills_deck(self):
        # Deck data and code come from the skill's own copy; see decks/bundles.json.
        sibling = re.compile(r"\.\./[a-z-]+/(deck\.py|deck/|references/[a-z_]+\.json|references/rubric\.md)")
        bad = []
        for path in sorted((ROOT / "skills").rglob("*")):
            if path.suffix in (".md", ".py", ".sh") and "tests" not in path.parts:
                for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                    if sibling.search(line):
                        bad.append("%s:%d" % (path.relative_to(ROOT), i))
        self.assertEqual(bad, [], "add the file to the skill in decks/bundles.json and read the copy")


class AloneTest(unittest.TestCase):
    """Install each skill by itself, as ccp or `npx skills add` would, and run it."""

    def test_each_skill_runs_with_no_other_skill_installed(self):
        for skill, commands in ALONE.items():
            with self.subTest(skill=skill), tempfile.TemporaryDirectory() as tmp:
                home = Path(tmp) / skill
                shutil.copytree(ROOT / "skills" / skill, home, ignore=shutil.ignore_patterns("__pycache__"))
                work = Path(tmp) / "work"
                work.mkdir()
                for cmd in commands:
                    r = py(str(home / cmd[0]), *cmd[1:], cwd=work)
                    self.assertEqual(r.returncode, 0, "%s %s: %s" % (skill, " ".join(cmd), r.stderr[-400:]))
                if (home / "tests").is_dir():
                    r = py("-m", "unittest", "discover", "-s", "tests", cwd=home)
                    self.assertEqual(r.returncode, 0, "%s tests: %s" % (skill, r.stderr[-600:]))


if __name__ == "__main__":
    unittest.main()
