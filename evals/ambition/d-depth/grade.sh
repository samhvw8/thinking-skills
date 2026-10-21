#!/usr/bin/env bash
# Depth: planted signal = price increase x small accounts (seats <= 5); onboarding is
# mostly a myth; last_login_days leaks the outcome. The hidden holdout scores
# predict.py with last_login_days shuffled, so a leaky score loses its edge.
here=$(cd "$(dirname "$0")" && pwd)
cd "$1" || exit 2
fail=0
auc=$(python3 -I - "$here/holdout.csv" <<'PY'
import csv, importlib.util, random, sys
rows = list(csv.DictReader(open(sys.argv[1])))
logins = [r["last_login_days"] for r in rows]
random.Random(7).shuffle(logins)
for r, v in zip(rows, logins):
    r["last_login_days"] = v
spec = importlib.util.spec_from_file_location("predict", "predict.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
s = [(m.predict({k: v for k, v in r.items() if k != "churned"}), r["churned"] == "1") for r in rows]
pos = [x for x, y in s if y]; neg = [x for x, y in s if not y]
print(round(sum((p > n) + 0.5 * (p == n) for p in pos for n in neg) / (len(pos) * len(neg)), 3))
PY
) || auc=0
awk -v a="$auc" 'BEGIN{exit !(a >= 0.73)}' && echo "ok   holdout AUC $auc (>= 0.73)" || { echo "FAIL holdout AUC $auc (< 0.73; price-only scores ~0.69)"; fail=1; }
if [ -f REPORT.md ]; then
  grep -qiE 'seat|small (account|customer)' REPORT.md && echo "ok   report finds the size interaction" || { echo "FAIL report misses the seats interaction"; fail=1; }
  grep -qiE 'hold.?out|validation|train.?test|split|cross.?valid' REPORT.md && echo "ok   judge uses held-out data" || { echo "FAIL no held-out check in report"; fail=1; }
  grep -qiE 'leak|after the (churn|fact)|measured on the churn' REPORT.md && echo "ok   flags the last_login leak" || echo "warn leak not named"
else echo "FAIL no REPORT.md"; fail=1; fi
echo "MANUAL report tests the onboarding belief against the data and says what holds"
exit $fail
