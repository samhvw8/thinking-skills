"""Map judge scores back to arms and average them.

Usage: python3 unblind.py <run-dir> [<run-dir> ...]
Reads every <run-dir>/judge*/key.json and the scores*.json beside it (one per packet:
{"packet": "<case>-<i>", "scores": {"A": {"ambition": n, ...}, ...}, "rank": ["B","A","C"]}).
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

CRIT = ["ambition", "grounding", "honesty", "scope", "usefulness"]
tot = defaultdict(lambda: defaultdict(list))
firsts = defaultdict(int)
per_case = defaultdict(dict)
for run in sys.argv[1:]:
  model = Path(run).name.split("-", 2)[-1]
  for j in sorted(Path(run).glob("judge*/")):
    key = json.loads((j / "key.json").read_text())
    items = []
    for f in sorted(j.glob("scores*.json")):  # one object per file, or an array of them
        d = json.loads(f.read_text())
        items += d if isinstance(d, list) else [d]
    for s in items:
        letters = key[s["packet"]]
        firsts[letters[s["rank"][0]]] += 1
        for letter, sc in s["scores"].items():
            arm = letters[letter]
            for c in CRIT:
                tot[arm][c].append(sc[c])
            per_case[(model, s["packet"])].setdefault(arm, []).append(sum(sc[c] for c in CRIT))
arms = [a for a in ("high", "skill", "base") if a in tot]
print(f"{'criterion':12}" + "".join(f"{a:>8}" for a in arms))
for c in CRIT + ["total"]:
    vals = [(sum(sum(tot[a][k]) / len(tot[a][k]) for k in CRIT) if c == "total"
             else sum(tot[a][c]) / len(tot[a][c])) for a in arms]
    print(f"{c:12}" + "".join(f"{v:8.1f}" for v in vals))
print("ranked first: " + ", ".join(f"{a} {firsts[a]}" for a in arms))
print("\nper packet (sum of 5 criteria, max 50):")
for (model, p), v in sorted(per_case.items()):
    print(f"  {model:18} {p:14}" + "".join(f"{a}={(sum(v[a]) / len(v[a])) if a in v else 0:<6.1f}" for a in arms))
