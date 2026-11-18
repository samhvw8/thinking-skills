"""Unblind pairwise verdicts; count pairs both orders agree on (adapted from search-evals/judge/tally.py).

Usage: python3 judge/tally.py <run-dir>
"""
import json, sys
from collections import defaultdict
from pathlib import Path

CRIT = ["commands", "rules", "completeness", "usefulness"]
run = Path(sys.argv[1]); key = json.loads((run / "key.json").read_text())
verdicts, scores = {}, defaultdict(lambda: defaultdict(list))
for f in sorted((run / "verdicts").glob("verdict-*.json")):
    v = json.loads(f.read_text()); p = v["packet"]; letters = key[p]; w = v["winner"]
    verdicts[p] = (letters[w] if w in letters else "tie", v.get("reason", ""), v.get("scores", {}))
    for n, sc in v.get("scores", {}).items():
        tag = "noise:" + letters[n] if "current2" in letters.values() else letters[n]
        for c in CRIT:
            scores[tag][c].append(sc[c])
wins = defaultdict(lambda: [0, 0, 0, 0])
for p1 in sorted(p for p in key if p.endswith("-o1")):
    p2 = p1[:-1] + "2"
    if p1 not in verdicts or p2 not in verdicts: continue
    a, b = sorted(key[p1].values()); sc = p1.rsplit("-", 2)[0]
    (w1, r1, s1), (w2, r2, s2) = verdicts[p1], verdicts[p2]
    k = wins[(a, b)]
    if w1 == w2: k[0 if w1 == a else 1 if w1 == b else 2] += 1; res = f"counted: {w1}"
    else: k[3] += 1; res = "split (not counted)"
    print(f"{sc} {a} vs {b}: o1={w1} o2={w2} -> {res}\n    o1: {r1}\n    o2: {r2}")
print("\nTotals (counted pairs only):")
for (a, b), k in sorted(wins.items()):
    print(f"  {a} vs {b}: {a} {k[0]}, {b} {k[1]}, agreed tie {k[2]}, split {k[3]}")
print("\nMean scores (all judgments):")
for arm, cs in sorted(scores.items()):
    print(f"  {arm:15}" + "".join(f" {c}={sum(cs[c]) / len(cs[c]):.1f}" for c in CRIT)
          + f" total={sum(sum(cs[c]) / len(cs[c]) for c in CRIT):.1f}")
