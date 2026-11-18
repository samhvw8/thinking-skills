"""Files the subject read, bytes and approx tokens of skill text loaded, cost, from transcript.jsonl.

Usage: python3 metrics.py <run-dir>      -> JSON on stdout; writes PLAN.md (the final answer)
Skill text loaded = SKILL.md (injected into the prompt, as the Skill tool does) + every distinct
skill file the subject Read in full. Tokens are approximated as bytes / 4.
"""
import json, sys
from pathlib import Path
d = Path(sys.argv[1]); base = d / "agent-ops"
reads, cost, usage, result, tools = [], 0.0, {}, "", None
for line in open(d / "transcript.jsonl"):
    try: e = json.loads(line)
    except Exception: continue
    if e.get("type") == "system" and e.get("subtype") == "init":
        tools = e.get("tools")
    if e.get("type") == "assistant":
        for c in e["message"]["content"]:
            if c.get("type") == "tool_use" and c["name"] == "Read":
                reads.append(c["input"].get("file_path", ""))
    if e.get("type") == "result":
        cost = e.get("total_cost_usd") or 0; usage = e.get("usage") or {}; result = e.get("result") or ""
(d / "PLAN.md").write_text(result)
files = sorted({Path(p).name for p in reads if p.startswith(str(base))})
outside = [p for p in reads if not p.startswith(str(base))]
loaded = ["SKILL.md"] + [f for f in files if f != "SKILL.md"]
b = sum((base / f).stat().st_size for f in loaded if (base / f).exists())
print(json.dumps({"files_read": files, "reads_outside": outside, "skill_bytes": b, "skill_tokens_approx": b // 4,
                  "cost_usd": round(cost, 4), "input_tokens": usage.get("input_tokens", 0) + usage.get("cache_read_input_tokens", 0) + usage.get("cache_creation_input_tokens", 0),
                  "output_tokens": usage.get("output_tokens", 0), "tools": tools}))
