"""Pull the final verdict JSON out of a claude -p --output-format json result.

Usage: python3 judge/extract_verdict.py <raw.json> <verdict.json>
Some setups print the whole event list, and a Stop hook can add a later turn, so this
searches every assistant text block, newest first, for the last {"packet" ...} object.
"""
import json
import sys

data = json.load(open(sys.argv[1]))
events = data if isinstance(data, list) else [data]
texts = [e.get("result") or "" for e in events if e.get("type") == "result"]
for e in events:
    if e.get("type") == "assistant":
        texts += [c.get("text", "") for c in e["message"]["content"] if c.get("type") == "text"]
for text in reversed(texts):
    i = text.rfind('{"packet"')
    if i >= 0:
        verdict, _ = json.JSONDecoder().raw_decode(text[i:])
        json.dump(verdict, open(sys.argv[2], "w"), indent=1)
        sys.exit(0)
sys.exit(f"no verdict in {sys.argv[1]}")
