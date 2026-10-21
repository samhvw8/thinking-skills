#!/usr/bin/env bash
# Run every case with and without the skill, headless, then grade each run and
# check its receipts against the transcript.
#
# Usage: evals/ambition/run-all.sh [-m model] [-n runs] [-j parallel] [-b usd-per-run] [-a "base skill high"] [case ...]
#        evals/ambition/run-all.sh -g evals/ambition/out/<run-dir>    # re-grade saved runs, no agents
# Output: evals/ambition/out/<date>-<model>/<case>-<arm>-<i>/ and a summary table.
#
# Agents run with acceptEdits and a short tool allow-list (file tools, python3,
# read-only git). Your user settings and hooks are left out (--setting-sources
# project,local); both arms see the same setup. Each run is capped by -b dollars.
# Set ANTHROPIC_API_KEY to run with --bare, which also leaves out CLAUDE.md.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
skill="$(cd "$here/../.." && pwd)/skills/ambition/SKILL.md"
model=claude-opus-5-5; runs=1; jobs=3; budget=5; regrade=; arms="skill base"
while getopts "m:n:j:b:g:a:" o; do
  case $o in m) model=$OPTARG;; n) runs=$OPTARG;; j) jobs=$OPTARG;; b) budget=$OPTARG;; g) regrade=$OPTARG;; a) arms=$OPTARG;; *) exit 2;; esac
done
shift $((OPTIND - 1))
cases=("$@"); [ ${#cases[@]} -eq 0 ] && cases=(a-honest a2-speed b-scope c-rewrite d-depth e-gate e2-auto f-systems)

hide_artifacts() {  # keep run files out of the git status the graders read
  printf '%s\n' transcript.jsonl stderr.txt grade.txt receipts.txt .grade.tmp >> "$1/.git/info/exclude"
}

grade() {  # case arm i dir
  local c=$1 arm=$2 i=$3 d=$4 g=pass r=pass cost
  "$here/$c/grade.sh" "$d" > "$d/.grade.tmp" 2>&1 || g=fail
  mv "$d/.grade.tmp" "$d/grade.txt"
  if [ -f "$d/REPORT.md" ]; then
    python3 -I "$here/receipts.py" "$d/transcript.jsonl" "$d/REPORT.md" > "$d/receipts.txt" 2>&1 || r=fail
  else r=none; fi
  cost=$(python3 -I -c "import json,sys
c=0
for l in open(sys.argv[1]):
    try: e=json.loads(l)
    except Exception: continue
    if e.get('type')=='result': c=e.get('total_cost_usd') or 0
print(round(c,2))" "$d/transcript.jsonl" 2>/dev/null || echo 0)
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$c" "$arm" "$i" "$g" "$r" "$cost" >> "$out/results.tsv"
  echo "done $c $arm $i: grade=$g receipts=$r \$$cost"
}

one() {  # case arm i
  local c=$1 arm=$2 i=$3 d="$out/$1-$2-$3" task prompt mode=acceptEdits
  local sys_args=() iso=(--setting-sources project,local)
  # With an API key, --bare also skips CLAUDE.md, so your own rules don't leak into
  # either arm. Without one (OAuth login), runs include your global CLAUDE.md.
  [ -n "${ANTHROPIC_API_KEY:-}" ] && iso=(--bare)
  [ -f "$here/$c/mode" ] && mode=$(cat "$here/$c/mode")   # a case can ask for another permission mode
  # Headless runs don't tell the model its mode; interactive Claude Code does. A case
  # can pass that notice on, so the eval matches what the model sees interactively.
  [ -f "$here/$c/system" ] && sys_args=(--append-system-prompt "$(cat "$here/$c/system")")
  task=$("$here/run.sh" "$c" "$d")
  hide_artifacts "$d"
  case $arm in
    skill) prompt="First read $skill and follow it for this task."$'\n\n'"$task";;
    high)  prompt="First read $skill and follow it in high mode (ambition high) for this task."$'\n\n'"$task";;
    *)     prompt="$task";;
  esac
  ( cd "$d" && claude -p "$prompt" --model "$model" --output-format stream-json --verbose \
      --permission-mode "$mode" --disable-slash-commands --no-session-persistence \
      "${iso[@]}" --max-budget-usd "$budget" "${sys_args[@]}" \
      --allowedTools Read Edit Write Glob Grep "Bash(python3:*)" "Bash(git diff:*)" "Bash(git status:*)" "Bash(git log:*)" \
      > transcript.jsonl 2> stderr.txt ) || true
  grade "$c" "$arm" "$i" "$d"
}

if [ -n "$regrade" ]; then
  out=$(cd "$regrade" && pwd); : > "$out/results.tsv"
  for d in "$out"/*/; do
    d=${d%/}; n=$(basename "$d"); i=${n##*-}; rest=${n%-*}; arm=${rest##*-}; c=${rest%-*}
    hide_artifacts "$d"; grade "$c" "$arm" "$i" "$d"
  done
else
  out="$here/out/$(date +%y%m%d-%H%M)-$model"; mkdir -p "$out"
  export -f one grade hide_artifacts; export here skill model budget out
  for c in "${cases[@]}"; do for arm in $arms; do for i in $(seq 1 "$runs"); do echo "$c $arm $i"; done; done; done \
    | xargs -P "$jobs" -L 1 bash -c 'one "$0" "$1" "$2"'
fi

python3 -I - "$out/results.tsv" <<'PY'
import collections, sys
rows = [l.rstrip("\n").split("\t") for l in open(sys.argv[1])]
t = collections.defaultdict(lambda: [0, 0, 0, 0.0])
for c, arm, i, g, r, cost in rows:
    k = t[(c, arm)]; k[0] += g == "pass"; k[1] += 1; k[2] += r == "fail"; k[3] += float(cost)
arms = [a for a in ("high", "skill", "base") if any(k[1] == a for k in t)]
print("\n" + f"{'case':12}" + "".join(f"{a:>9}" for a in arms) + "   fake receipts   cost $")
for c in sorted({c for c, _ in t}):
    cells = [t[(c, a)] for a in arms]
    print(f"{c:12}" + "".join(f"{x[0]:>5}/{x[1]:<3}" for x in cells)
          + "   " + "/".join(str(x[2]) for x in cells).ljust(15) + f" {sum(x[3] for x in cells):.2f}")
print(f"\ntotal ${sum(v[3] for v in t.values()):.2f}  ->  {sys.argv[1].rsplit('/',1)[0]}")
PY
