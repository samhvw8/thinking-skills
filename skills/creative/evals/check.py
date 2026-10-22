#!/usr/bin/env python3
"""Script assertions for the creative skill's evals.

Format checks live here, not in the blind judge's rubric: a baseline can't pass them
without the skill, so a judge that sees them scores compliance instead of the ideas.

Usage: python3 check.py <eval-id> <output.md> [<output.md> ...]
Each file is one sample's final answer. With two or more files, it also prints each
sample's top pick and flags exact repeats; send the picks to a judge for "same core idea".
Exit code 1 when any check fails.
"""
import os
import re
import sys
import unicodedata

def creative_weights():
    """The creative profile's weights, read from the rubric copy so there is no second list."""
    ref = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references", "rubric.md"), encoding="utf-8").read()
    row = re.search(r"^\| `creative` \|[^\n]*\| ([^|\n]+) \|$", ref, re.M).group(1)
    out = {}
    for part in row.split(","):
        m = re.fullmatch(r"\s*([a-z][a-z ]*?)\s+(\d+)\s*", part, re.I)
        if not m:
            sys.exit(f"rubric.md: can't parse creative weight {part!r}")
        out[m.group(1).lower().replace(" ", "_")] = int(m.group(2)) / 10
    if abs(sum(out.values()) - 10) > 1e-9:
        sys.exit(f"rubric.md: creative weights sum to {sum(out.values()) * 10:g}, not 100")
    return out


WEIGHTS = creative_weights()
FORBIDDEN = {6: [r"30[- ]day", r"influencer"]}
WRITING = {5: (150, 250)}  # eval id -> word range for the one finished piece
FENCE = r"(?:skipped|left out|ruled out)[^:\n]{0,30}"


def norm(s):
    s = unicodedata.normalize("NFKD", s.lower())
    return re.sub(r"[^a-z0-9 ]", "", "".join(c for c in s if not unicodedata.combining(c))).strip()


def headings(text):
    """Shortlist item titles: markdown headings or bold numbered items."""
    out = []
    for line in text.splitlines():
        m = re.match(r"^\s*(?:#{2,4}\s*)?(?:\*\*)?\s*(\d+)[.)]\s*(.+?)(?:\*\*|$)", line)
        if m and (line.lstrip().startswith("#") or line.lstrip().startswith("**")):
            out.append(m.group(2).strip(" *"))
    return out


def score_tables(text):
    """Yield (row_name, {criterion: score}, printed_total) for rubric tables."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        cells = [c.strip(" *").lower() for c in line.strip().strip("|").split("|")]
        cells = ["emergence" if c.startswith("combines") else c for c in cells]
        if "novelty" not in cells or "|" not in line:
            continue
        cols = {c: j for j, c in enumerate(cells)}
        tcol = next((j for c, j in cols.items() if c.startswith("total")), None)
        for row in lines[i + 2:]:
            if not row.strip().startswith("|"):
                break
            r = [c.strip().strip("*~ ") for c in row.strip().strip("|").split("|")]
            try:
                scores = {k: float(r[cols[k]]) for k in WEIGHTS if k in cols}
                total = float(r[tcol]) if tcol is not None and r[tcol] else None
            except (ValueError, IndexError):
                continue
            yield r[0], scores, total


def tells():
    """The writing-tells list from references/generators.md, as plain words and phrases."""
    ref = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references", "generators.md"), encoding="utf-8").read()
    block = re.search(r"## Writing tells.*?`([^`]+)`", ref, re.S).group(1)
    out = []
    for t in block.replace("\n", " ").split(","):
        t = t.strip()
        if "(as " in t:  # a judgment call ("journey (as metaphor)"), not a grep
            continue
        t = re.sub(r"\(.*?\)", "", t).strip()  # "whisper(ed|s)" -> "whisper", matched as a prefix below
        if t and " X " not in f" {t} ":
            out.append(t)
    return out


def check_writing(eid, text):
    """One finished piece between '---' lines: word range, no tells, exactly one piece."""
    fails = []
    parts = re.split(r"^\s*---+\s*$", text, flags=re.M)
    if len(parts) != 3:
        fails.append(f"expected one piece between two '---' lines, found {max(len(parts) - 1, 0)} separators")
    piece = parts[1] if len(parts) >= 3 else text
    lo, hi = WRITING[eid]
    n = len(re.findall(r"[\w'’-]+", piece))
    if not lo <= n <= hi:
        fails.append(f"piece is {n} words, want {lo}-{hi}")
    hits = [t for t in tells() if re.search(r"\b" + re.escape(t) + r"\w*\b", piece, re.I)]
    if hits:
        fails.append(f"writing tells in the piece: {hits}")
    if not re.search(r"(?:" + FENCE + r"|what i left out)", text, re.I):
        fails.append("no line naming what was left out")
    return [f"piece ({n} words)"], fails


def check(eid, text):
    if eid in WRITING:
        return check_writing(eid, text)
    fails = []
    fence = FENCE
    if not re.search(r"(?:" + fence + r"|what i left out)[^\n]*obvious|what i left out", text, re.I):
        fails.append("no fence line for the obvious tier")
    if not re.search(fence + "clever", text, re.I):
        fails.append("no fence line for the clever tier")
    items = headings(text)
    receipts = len(re.findall(r"receipt\s*:", text, re.I))
    if receipts < max(1, min(len(items), 3)):
        fails.append(f"receipts {receipts} < shortlist items {len(items)}")
    for name, scores, total in score_tables(text):
        if total is None:
            continue
        if set(scores) != set(WEIGHTS):
            fails.append(f"'{name}': total printed without all {len(WEIGHTS)} criteria")
            continue
        want = sum(scores[k] * w for k, w in WEIGHTS.items())
        if abs(want - total) > 0.5:
            fails.append(f"'{name}': total {total:g}, weights give {want:g}")
    for pat in FORBIDDEN.get(eid, []):
        hit = [h for h in items if re.search(pat, h, re.I)]
        if hit:
            fails.append(f"fenced idea in shortlist: {hit}")
    return items, fails


def main():
    if len(sys.argv) < 3 or not sys.argv[1].isdigit():
        sys.exit(__doc__)
    eid, files = int(sys.argv[1]), sys.argv[2:]
    tops, bad = [], False
    for f in files:
        items, fails = check(eid, open(f, encoding="utf-8").read())
        tops.append(items[0] if items else "")
        print(f"{f}: {'PASS' if not fails else 'FAIL'} ({len(items)} items)")
        for x in fails:
            print("  -", x)
        bad |= bool(fails)
    if len(files) > 1:
        print("top picks:", tops)
        seen = [norm(t) for t in tops if t]
        if len(seen) != len(set(seen)):
            print("  - FAIL: the same top pick in several samples")
            bad = True
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
