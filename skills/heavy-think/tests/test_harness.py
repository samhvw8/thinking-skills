"""Guards the skills against lock-in to one harness. Standard library only.

Skill text names capabilities and model tiers; references/harness.md maps them to each harness.
A Claude Code tool, model or variable name may appear elsewhere only as a labelled example:
"Claude Code" on the same line or the line before.

Run: python3 -m unittest discover -s skills/heavy-think/tests
"""
import re
import unittest
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[2]
HARNESS = SKILLS / "heavy-think" / "references" / "harness.md"
# Only this repo's skills: installed, SKILLS is a folder shared with every other skill.
OURS = ("ambition", "council", "creative", "debate", "heavy-think")
VENDOR = re.compile(r"SendMessage|subagent_type|general-purpose|CLAUDE_[A-Z_]+|\b(opus|sonnet|haiku)\b|"
                    r"ToolSearch|mcp__|WebSearch|WebFetch|`Agent`|claude -p", re.I)


def skill_files():
    for p in sorted(q for s in OURS for q in (SKILLS / s).rglob("*")):
        if p.suffix in (".md", ".py", ".json") and p != HARNESS and not {"tests", "evals"} & set(p.parts):
            yield p


class HarnessNeutralTest(unittest.TestCase):
    def test_vendor_names_appear_only_as_labelled_examples(self):
        bad = []
        for p in skill_files():
            lines = p.read_text().splitlines()
            for i, line in enumerate(lines):
                if VENDOR.search(line) and "Claude Code" not in line and (i == 0 or "Claude Code" not in lines[i - 1]):
                    bad.append("%s:%d: %s" % (p.relative_to(SKILLS), i + 1, line.strip()[:100]))
        self.assertEqual(bad, [], "name the capability or tier and map it in harness.md:\n" + "\n".join(bad))

    def test_harness_map_covers_every_tier_the_skills_use(self):
        text = HARNESS.read_text()
        for tier in ("`strong`", "`session`", "`fast`"):
            self.assertIn(tier, text)
        for harness in ("Claude Code", "opencode", "omp"):
            self.assertIn(harness, text)


if __name__ == "__main__":
    unittest.main()
