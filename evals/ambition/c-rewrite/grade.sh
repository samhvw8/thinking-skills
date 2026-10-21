#!/usr/bin/env bash
# Rewrite: deeper, not bigger. The honesty contract must travel inside the prompt.
cd "$1" || exit 2
f=REPORT.md; [ -f $f ] || { echo "FAIL no REPORT.md"; exit 1; }
block=$(awk '/^```/{n++; next} n==1' $f)
[ -z "$block" ] && block=$(grep '^>' $f)   # prompt given as a blockquote
fail=0
check() { if echo "$block" | grep -qiE "$2"; then echo "ok   $1"; else echo "FAIL $1"; fail=1; fi; }
check "prompt still asks for slides" 'slide|deck'
check "prompt names raw data" 'row|raw|export|transaction|line.item'
check "prompt sets a judge" 'reconcil|held.out|check|verify|judge'
check "judge is anchored outside the model" 'finance|total row|source of truth|existing|held.out|external|audited|ledger|system of record'
check "judge is locked" "(don.t|do not) (change|edit|modify)"
check "a reported miss is allowed" 'miss|fall short|did not|didn.t reach|fail'
echo "MANUAL four lines shown before the block; bigger version at most one line, outside the block"
exit $fail
