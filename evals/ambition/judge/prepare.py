"""Build blind judging packets from one run-all output folder.

Usage: python3 prepare.py <evals/out/run-dir> [--seed N]
Writes <run-dir>/judge/<case>-<i>.md (judge-s<N>/ for --seed N other than 1) (A/B/C in random order) and
<run-dir>/judge/key.json (which letter is which arm). Judges get packets only.
"""
import json
import random
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

LIMIT = 9000  # characters per report or diff; longer text is cut, and the cut is marked


LEAKS = re.compile(r"ambition[\w-]*|high mode|mode: high|the skill|this skill|skill\.md|deal\.py|\bskill\b", re.I)


def clip(text):
    text = LEAKS.sub("[redacted]", text)
    return text if len(text) <= LIMIT else text[:LIMIT] + f"\n[... cut, {len(text) - LIMIT} more characters]"


def arm_block(d):
    report = (d / "REPORT.md").read_text() if (d / "REPORT.md").exists() else "(no REPORT.md)"
    diff = subprocess.run(["git", "-C", str(d), "diff", "HEAD", "--", ".", ":(exclude)REPORT.md"],
                          capture_output=True, text=True).stdout
    new = subprocess.run(["git", "-C", str(d), "ls-files", "--others", "--exclude-standard"],
                         capture_output=True, text=True).stdout.split()
    for f in new:
        if f != "REPORT.md" and (d / f).stat().st_size < 20000:
            diff += f"\n--- new file {f}\n" + (d / f).read_text(errors="replace")
    grade = (d / "grade.txt").read_text() if (d / "grade.txt").exists() else ""
    return f"### Grader facts\n```\n{grade.strip()}\n```\n\n### Report\n{clip(report)}\n\n### Changes\n```\n{clip(diff.strip()) or '(none)'}\n```\n"


def main():
    out = Path(sys.argv[1]).resolve()
    seed = int(sys.argv[sys.argv.index("--seed") + 1]) if "--seed" in sys.argv else 1
    rng = random.Random(seed)
    evals = Path(__file__).resolve().parent.parent
    groups = defaultdict(dict)
    for d in sorted(p for p in out.iterdir() if p.is_dir() and not p.name.startswith("judge")):
        rest, i = d.name.rsplit("-", 1)
        case, arm = rest.rsplit("-", 1)
        groups[(case, i)][arm] = d
    jdir = out / ("judge" if seed == 1 else f"judge-s{seed}"); jdir.mkdir(exist_ok=True)
    key = {}
    for (case, i), arms in sorted(groups.items()):
        if len(arms) < 2:
            continue
        names = list(arms); rng.shuffle(names)
        letters = dict(zip("ABC", names))
        task = (evals / case / "task.md").read_text()
        body = [f"# Case {case}, run {i}\n\n## Task given to all three\n{task}\n"]
        for letter, arm in letters.items():
            body.append(f"## Answer {letter}\n\n" + arm_block(arms[arm]))
        (jdir / f"{case}-{i}.md").write_text("\n".join(body))
        key[f"{case}-{i}"] = letters
    (jdir / "key.json").write_text(json.dumps(key, indent=1))
    print(f"{len(key)} packets -> {jdir}")


if __name__ == "__main__":
    main()
