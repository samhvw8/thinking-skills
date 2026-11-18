#!/usr/bin/env bash
# Usage: run-subject.sh <scenario-id> <arm> <run-id> <out-dir>
# One headless subject: sonnet, safe mode (no CLAUDE.md, skills, hooks), restricted to its run folder,
# Read and Glob only. Its run folder holds only the arm's skill copy.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
sc=$1; arm=$2; rid=$3; out=$4
d="$out/run/$rid"; mkdir -p "$d"
cp -R "$here/arms/$arm/agent-ops" "$d/agent-ops"
printf '%s\t%s\t%s\n' "$rid" "$sc" "$arm" >> "$out/runs-key.tsv"
python3 -I - "$here/subject-prompt.md" "$d/agent-ops" "$here/scenarios/$sc.md" > "$d/prompt.txt" <<'PY'
import sys
t=open(sys.argv[1]).read(); base=sys.argv[2]
t=t.replace("{{BASE}}", base).replace("{{SKILL}}", open(base+"/SKILL.md").read()).replace("{{SCENARIO}}", open(sys.argv[3]).read().strip())
print(t)
PY
( cd "$d" && claude -p "$(cat prompt.txt)" --model claude-sonnet-5-5 --safe-mode --restricted --tools Read,Glob \
    --output-format stream-json --verbose --no-session-persistence --max-budget-usd 1 \
    > transcript.jsonl 2> stderr.txt ) || true
python3 -I "$here/metrics.py" "$d" > "$d/metrics.json" || true
echo "done $rid $sc $arm"
