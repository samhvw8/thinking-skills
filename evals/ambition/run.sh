#!/usr/bin/env bash
# Usage: evals/run.sh <case> <dest-dir>
# Copies the case's fixture into a fresh git repo at <dest-dir> and prints the task.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
case_dir="$here/$1"; dest="$2"
mkdir -p "$dest"
[ -d "$case_dir/fixture" ] && cp -R "$case_dir/fixture/." "$dest/"
cd "$dest"
git init -q && git add -A && git -c user.email=eval@local -c user.name=eval commit -q --allow-empty -m fixture
cat "$case_dir/task.md"
