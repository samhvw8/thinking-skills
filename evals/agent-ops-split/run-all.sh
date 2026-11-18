#!/usr/bin/env bash
# Run every scenario once per arm (current, split), plus a second current run on the noise-floor
# scenarios (chosen before any result: s03 s05 s06 s07 s08). Run folders get shuffled neutral ids
# (r01..), so no path in a plan names its arm; runs-key.tsv maps them back.
# Decision rule (fixed before judging): ship the split only if counted split losses vs current do not
# exceed counted losses in the current-vs-current noise pairs, and it loads fewer skill tokens.
# Usage: [ARMS="current split"] [NOISE="..."] ./run-all.sh [out-dir]
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
out=${1:-$here/out/$(date +%y%m%d-%H%M)}; mkdir -p "$out/run"; : > "$out/runs-key.tsv"
noise=${NOISE-"s03_receive s05_dialog s06_pair s07_live_team s08_swarm"}; arms=${ARMS:-"current split"}   # ARMS="split2" NOISE="" runs one new arm
jobs=()
for s in $(ls "$here/scenarios" | sed 's/\.md$//'); do
  for a in $arms; do jobs+=("$s $a"); done
  case " $noise " in *" $s "*) jobs+=("$s current2");; esac
done
printf '%s\n' "${jobs[@]}" | python3 -I -c "import sys,random; l=sys.stdin.read().split(chr(10)); l=[x for x in l if x]; random.Random(7).shuffle(l); [print(x, 'r%02d'%(i+1)) for i,x in enumerate(l)]" \
  | while read -r s arm rid; do a=$arm; [ "$arm" = current2 ] && a=current; echo "$s $a $rid $arm"; done > "$out/plan.txt"
# current2 runs the current arm; the key records it as current2
export here out
cat "$out/plan.txt" | xargs -P 6 -L 1 bash -c 'sc=$0 a=$1 rid=$2 label=$3; "$here/run-subject.sh" "$sc" "$a" "$rid" "$out" >/dev/null; sed -i "" "s/^$rid\t$sc\t$a$/$rid\t$sc\t$label/" "$out/runs-key.tsv"; echo "done $rid $sc $label"'
echo "$out"
