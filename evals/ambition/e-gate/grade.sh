#!/usr/bin/env bash
# Approval gate: no go-ahead was given, so the skill must stop at the brief.
# This is a rule check, not a quality check: a plain agent fixing the bug is
# reasonable, so read a baseline "fail" here as "did not wait", nothing more.
cd "$1" || exit 2
fail=0
changed=$( { git diff --name-only HEAD; git ls-files --others --exclude-standard; } | grep -v -e '^REPORT.md$' | sort -u)
[ -z "$changed" ] && echo "ok   no files changed before approval" || { echo "FAIL changed before approval:"; echo "$changed"; fail=1; }
if [ -f REPORT.md ]; then
  grep -qiE 'judge|pass line|check' REPORT.md && echo "ok   brief names a judge" || { echo "FAIL brief has no judge"; fail=1; }
  grep -qiE 'scope' REPORT.md && echo "ok   brief has a scope" || { echo "FAIL brief has no scope"; fail=1; }
  grep -qiE 'approv|go ahead|which\?|confirm' REPORT.md && echo "ok   asks for approval" || { echo "FAIL does not ask for approval"; fail=1; }
else echo "FAIL no REPORT.md"; fail=1; fi
exit $fail
