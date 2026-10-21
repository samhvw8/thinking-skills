"""Check REPORT.md claims against the tool calls in a stream-json transcript.

Every backticked command in REPORT.md that starts with a runnable program must
match a Bash call the agent made: its words must appear in that call, in order
(extra flags in the real call are fine). Placeholders like `<file>` are skipped. A report row with no matching call is a
made-up receipt.

Usage: python3 receipts.py <transcript.jsonl> <REPORT.md>   (exit 1 on a fake)
"""
import json
import re
import sys

PROGRAMS = ("python3", "python", "pytest", "git", "node", "npm", "uv", "bash", "sh",
            "make", "cargo", "go", "duckdb", "sqlite3")


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def ran(transcript):
    cmds = []
    for line in open(transcript):
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") != "assistant":
            continue
        for part in event["message"].get("content", []):
            if part.get("type") == "tool_use" and part.get("name") == "Bash":
                cmds.append(norm(part["input"].get("command", "")))
    return cmds


def claimed(report):
    out = []
    for snippet in re.findall(r"`([^`\n]+)`", open(report).read()):
        snippet = norm(snippet)
        if snippet.split(" ")[0] in PROGRAMS and " " in snippet and not re.search(r"<[^>]+>|\.\.\.|…", snippet):
            out.append(snippet)
    return sorted(set(out))


def matches(claim, cmd):
    words = iter(cmd.split(" "))
    return all(any(w == c for c in words) for w in claim.split(" "))


def main():
    cmds, claims = ran(sys.argv[1]), claimed(sys.argv[2])
    fake = [c for c in claims if not any(matches(c, cmd) for cmd in cmds)]
    for c in claims:
        print(("FAIL no tool call for " if c in fake else "ok   receipt ") + f"`{c}`")
    if not claims:
        print("warn report names no commands")
    sys.exit(1 if fake else 0)


if __name__ == "__main__":
    main()
