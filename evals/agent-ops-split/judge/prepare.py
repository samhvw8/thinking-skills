"""Build blind pairwise packets from one run folder (adapted from search-evals/judge/prepare.py).

Usage: python3 judge/prepare.py <out/run-dir> [--seed N]
Pairs per scenario: current vs every other arm in the run (split, split2, current2 = the noise floor).
Writes <run-dir>/judge/packets/<scenario>-p<k>-o<1|2>.md (both orders) and <run-dir>/key.json (outside the
judges' folder), and copies the reference skill (arms/current) to <run-dir>/judge/reference/agent-ops/.
"""
import json, random, re, shutil, sys
from pathlib import Path

LIMIT = 40000
here = Path(__file__).resolve().parent.parent
SPLIT_FILES = r"(?:layout|tasks|dialogs|worktree|pair|live-team|swarm|roles)\.md"
LEAKS = re.compile(SPLIT_FILES + r"|SKILL\.md|reference files?|skill files?", re.I)


def clip(text, run_dir):
    outs = re.escape(str(run_dir.parent)) + r"/[\w.-]+/run/r\d\d"   # any run folder, so plans reused from another run do not stand out
    text = re.sub(outs + r"/agent-ops", "<skill dir>", text)
    text = re.sub(outs, "<cwd>", text)
    text = LEAKS.sub("[redacted]", text)
    return text if len(text) <= LIMIT else text[:LIMIT] + f"\n[... cut, {len(text) - LIMIT} more characters]"


def main():
    out = Path(sys.argv[1]).resolve()
    rng = random.Random(int(sys.argv[sys.argv.index("--seed") + 1]) if "--seed" in sys.argv else 1)
    runs = {}
    for line in (out / "runs-key.tsv").read_text().splitlines():
        rid, sc, arm = line.split("\t")
        runs.setdefault(sc, {})[arm] = out / "run" / rid
    jdir = out / "judge"; pdir = jdir / "packets"; pdir.mkdir(parents=True, exist_ok=True)
    ref = jdir / "reference" / "agent-ops"
    if ref.exists(): shutil.rmtree(ref)
    shutil.copytree(here / "arms" / "current" / "agent-ops", ref)
    key = {}
    for sc, arms in sorted(runs.items()):
        pairs = [("current", a) for a in sorted(arms) if a != "current"]
        rng.shuffle(pairs)
        for k, pair in enumerate(pairs, 1):
            pair = list(pair); rng.shuffle(pair)
            for o, order in ((1, pair), (2, pair[::-1])):
                name = f"{sc}-p{k}-o{o}"
                body = [f"# Packet {name}\n\n## Scenario given to both\n" + (here / "scenarios" / f"{sc}.md").read_text().strip() + "\n"]
                for n, arm in enumerate(order, 1):
                    plan = arms[arm] / "PLAN.md"
                    body.append(f"## Answer {n}\n\n" + clip(plan.read_text() if plan.exists() else "(no plan)", out))
                (pdir / f"{name}.md").write_text("\n\n".join(body))
                key[name] = {"1": order[0], "2": order[1]}
    (out / "key.json").write_text(json.dumps(key, indent=1))
    print(f"{len(key)} packets -> {pdir}")


if __name__ == "__main__":
    main()
