#!/usr/bin/env bash
# Systems: hiring alone is the team's plan (Fixes That Fail). The data hides two
# things: follow-ups grow with the backlog (a reinforcing loop, 12% of open tickets
# a week), and 70% of sync tickets come from one bug. Hires arrive late (week 8).
# Scores (customer-weeks): fix sync + docs + 5 hires 17,729; fix sync + 7 hires
# 24,652; best plan without the sync fix 47,416; hire-only 61,593.
here=$(cd "$(dirname "$0")" && pwd)
cd "$1" || exit 2
fail=0
score=$(python3 -I - "$here" <<'PY'
import importlib.util, json, sys
spec = importlib.util.spec_from_file_location("sim", sys.argv[1] + "/sim.py")
sim = importlib.util.module_from_spec(spec); spec.loader.exec_module(sim)
try:
    plan = json.load(open("plan.json"))
    assert isinstance(plan.get("hires", 0), int) and plan.get("hires", 0) >= 0
    assert all(c in sim.BASE for c in plan.get("fixes", [])), "unknown category"
    assert len(set(plan.get("fixes", []))) == len(plan.get("fixes", [])), "duplicate fix"
    assert sim.cost(plan) <= sim.BUDGET["total"], f"over budget: {sim.cost(plan)}"
except Exception as e:
    print(f"invalid {e}"); sys.exit()
print(sum(sim.run(plan)))
PY
)
case "$score" in
  invalid*|"") echo "FAIL plan.json ${score:-missing}"; fail=1;;
  *) if [ "$score" -le 26000 ]; then echo "ok   $score customer-weeks (<= 26,000; hire-only is 61,593)"
     else echo "FAIL $score customer-weeks (> 26,000; hire-only is 61,593)"; fail=1; fi;;
esac
if [ -f REPORT.md ]; then
  grep -qiE 'follow.?up' REPORT.md && grep -qiE 'loop|compound|reinforc|grow(s|ing)? with' REPORT.md \
    && echo "ok   names the follow-up loop" || echo "warn follow-up loop not named"
  grep -qiE 'sync' REPORT.md && grep -qiE 'bug' REPORT.md && echo "ok   names the sync bug" || { echo "FAIL misses the sync bug"; fail=1; }
else echo "FAIL no REPORT.md"; fail=1; fi
exit $fail
