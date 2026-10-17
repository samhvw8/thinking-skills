"""Generate f-systems history: 12 weeks of tickets from the same model as sim.py,
ending at sim.START_BACKLOG. Deterministic."""
import csv
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sim  # noqa: E402

here = Path(__file__).resolve().parent
rng = random.Random(20261018)
rows, weekly, n = [], [], 0
backlog = 420.0
for week in range(-11, 1):
    opened = 0
    for cat, base in sim.BASE.items():
        for _ in range(round(base * rng.uniform(0.93, 1.07))):
            n += 1; opened += 1
            rows.append({"ticket_id": f"t{n:06d}", "week": week, "category": cat, "kind": "new",
                         "caused_by_bug": int(rng.random() < sim.BUG_SHARE[cat])})
    follow = round(sim.FOLLOWUP * backlog * rng.uniform(0.9, 1.1))
    cats = list(sim.BASE)
    for _ in range(follow):
        n += 1; opened += 1
        rows.append({"ticket_id": f"t{n:06d}", "week": week,
                     "category": rng.choices(cats, weights=[sim.BASE[c] for c in cats])[0],
                     "kind": "followup", "caused_by_bug": ""})
    closed = sim.CAPACITY
    backlog = max(0.0, backlog + opened - closed)
    weekly.append({"week": week, "opened": opened, "closed": closed, "open_at_end": round(backlog)})
scale = sim.START_BACKLOG / backlog  # land exactly on the simulator's start
for w in weekly:
    w["open_at_end"] = round(w["open_at_end"] * scale)
for name, data in (("tickets.csv", rows), ("weekly.csv", weekly)):
    with open(here / "fixture" / "data" / name, "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(data[0]))
        wr.writeheader(); wr.writerows(data)
print(len(rows), "tickets;", weekly[-1])
