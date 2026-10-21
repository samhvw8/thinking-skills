"""The hidden support-queue simulator for f-systems. The fixture never sees it.

Weekly: backlog += new tickets + follow-ups - capacity, where follow-ups are
customers chasing open tickets (FOLLOWUP x backlog). A fix removes the bug-caused
share of one category's new tickets from week FIX_WEEK. Docs cut how-to tickets
from week DOCS_WEEK. A hire adds HIRE_CAP closed tickets a week from HIRE_WEEK.
"""
BASE = {"sync": 130, "billing": 60, "how-to": 110, "login": 50, "export": 40}
BUG_SHARE = {"sync": 0.7, "billing": 0.05, "how-to": 0.0, "login": 0.1, "export": 0.05}
FOLLOWUP = 0.12
CAPACITY = 400
START_BACKLOG = 900
HIRE_CAP, HIRE_WEEK = 18, 8
FIX_WEEK, DOCS_WEEK, DOCS_CUT = 5, 3, 0.30
BUDGET = {"hire": 1, "fix": 3, "docs": 2, "total": 10}
WEEKS = 26


def cost(plan):
    return plan.get("hires", 0) * BUDGET["hire"] + len(plan.get("fixes", [])) * BUDGET["fix"] \
        + (BUDGET["docs"] if plan.get("docs") else 0)


def run(plan, weeks=WEEKS, start=START_BACKLOG):
    backlog, trace = float(start), []
    for w in range(1, weeks + 1):
        new = 0.0
        for cat, n in BASE.items():
            if cat in plan.get("fixes", []) and w >= FIX_WEEK:
                n *= 1 - BUG_SHARE[cat]
            if cat == "how-to" and plan.get("docs") and w >= DOCS_WEEK:
                n *= 1 - DOCS_CUT
            new += n
        cap = CAPACITY + (plan.get("hires", 0) * HIRE_CAP if w >= HIRE_WEEK else 0)
        backlog = max(0.0, backlog + new + FOLLOWUP * backlog - cap)
        trace.append(round(backlog))
    return trace


if __name__ == "__main__":
    import itertools
    rows = []
    cats = list(BASE)
    for docs in (False, True):
        for k in range(0, 3):
            for fixes in itertools.combinations(cats, k):
                plan = {"fixes": list(fixes), "docs": docs}
                plan["hires"] = BUDGET["total"] - cost(plan)
                if plan["hires"] < 0:
                    continue
                rows.append((run(plan)[-1], plan))
    for final, plan in sorted(rows, key=lambda r: r[0])[:6] + sorted(rows, key=lambda r: r[0])[-3:]:
        print(final, plan)
    print("hire-only", run({"hires": 10})[-1], " do nothing", run({})[-1])
