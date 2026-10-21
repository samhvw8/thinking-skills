"""Deal cards for ambition's high mode: the patterns that fit the task, three
mental models, three Range fields and three lenses. Standard library only.

Usage:
  python3 deal.py patterns                                     # list the patterns, with their model counts
  python3 deal.py deal "<task>" --patterns id1,id2 [--seed N]  # deal for the patterns you picked
  python3 deal.py deal "<task>"                                # let word overlap pick the patterns (weaker)
  python3 deal.py fields "<the task's verbs>"                  # rank the Range fields by verb overlap

Cards picked by word overlap with the task are marked "fit". Cards that fill a
slot with no overlap are marked "no fit": strike them unless they apply.
"""
import argparse
import json
import random
import re
import sys
from pathlib import Path

DECK = Path(__file__).resolve().parent.parent / "references" / "deck.json"
STOP = set("""a an the and or but of to in on for with from by is are was were be been
this that these those it its as at into than then so if not no you your we our they
their them what which who when where why how all any can could should would will
make makes made get gets very more most much many some such only also just""".split())
SUFFIXES = ("ations", "ation", "ings", "ing", "ers", "er", "ies", "ied", "ed", "es", "ly", "s")


def stem(w):
    for s in SUFFIXES:
        if w.endswith(s) and len(w) - len(s) >= 4:
            return w[:-len(s)]
    return w


def words(text):
    """Content-word stems, so "failing", "failed" and "fails" all match "fail"."""
    return {stem(w) for w in re.findall(r"[a-z]+", text.lower()) if len(w) > 3 and w not in STOP}


def load():
    return json.loads(DECK.read_text())


def deal(task, seed=None, pattern_ids=None, n=3):
    deck = load()
    rng = random.Random(seed if seed is not None else task)
    models = {m["id"]: m for m in deck["models"]}
    tw = words(task)

    def score(text):
        return len(tw & words(text))

    def model_score(i):
        return score(models[i]["use_when"] + " " + models[i]["move"] + " " + models[i]["name"])

    def pattern_score(p):
        return score(p["name"] + " " + p["problem"] + " " + p["solution"])

    visible = [p for p in deck["patterns"] if not p.get("hidden")]
    if pattern_ids:
        by_id = {p["id"]: p for p in deck["patterns"]}
        unknown = [i for i in pattern_ids if i not in by_id]
        if unknown:
            sys.exit(f"unknown pattern id: {', '.join(unknown)}. Run: deal.py patterns")
        top, auto_note = [by_id[i] for i in pattern_ids], None
    else:
        ranked = sorted(visible, key=lambda p: (-pattern_score(p), rng.random()))
        best = pattern_score(ranked[0])
        top = ranked[:2]
        auto_note = ("no pattern shares a word with the task; these are guesses. Run `deal.py patterns` "
                     "and pass --patterns") if best == 0 else \
                    f"picked by word overlap (best shares {best} words); --patterns is more reliable"

    # Each pattern contributes its best-fitting models that aren't already chosen.
    chosen, why = [], {}
    per = n if len(top) == 1 else max(1, n // len(top))
    for p in top:
        ranked = sorted((i for i in p["models"] if i != "cynefin-framework" and i not in chosen),
                        key=lambda i: (-model_score(i), rng.random()))
        for i in ranked[:per]:
            chosen.append(i)
            why[i] = f"pattern: {p['id']}"
    # Fill the rest from other disciplines, best task overlap first; random only breaks ties.
    used = {models[i]["discipline"] for i in chosen}
    rest = sorted((i for i in models if i not in chosen and i != "cynefin-framework"),
                  key=lambda i: (models[i]["discipline"] in used, -model_score(i), rng.random()))
    for i in rest:
        if len(chosen) >= n:
            break
        chosen.append(i)
        why[i] = "fill: fit" if model_score(i) else "fill: no fit, strike it unless it applies"
    chosen = chosen[:n]

    fields = rank_fields(deck, task, rng)[:n]

    # Lenses: best task overlap per family, with a challenger always seated.
    lenses = sorted(deck["lenses"], key=lambda l: (-score(" ".join(
        l.get(k, "") for k in ("name", "asks", "instruments", "delivers"))), rng.random()))
    picked, families = [], set()
    challenger = next((l for l in lenses if l["family"] == "challenger"), None)
    if challenger:
        picked.append(challenger)
        families.add("challenger")
    for l in lenses:
        if len(picked) >= n:
            break
        if l["family"] not in families:
            picked.append(l)
            families.add(l["family"])
    return top, auto_note, [(models[i], why[i]) for i in chosen], fields, picked


def rank_fields(deck, text, rng=None):
    rng = rng or random.Random(text)
    tw = words(text)
    scored = [(len(tw & words(" ".join(f["verbs"]) + " " + f["method"])), f) for f in deck["fields"]]
    return sorted(scored, key=lambda x: (-x[0], rng.random()))


def print_field(s, f):
    tag = "fit" if s else "no fit, strike it unless it applies"
    print(f"- **{f['name']}** ({tag}; good at: {', '.join(f['verbs'])})\n"
          f"  - Method: {f['method']}\n  - Instruments: {f['instruments']}\n  - Receipt: {f['receipt']}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("patterns", help="list the patterns with their model counts")
    d = sub.add_parser("deal", help="deal models, fields and lenses for a task")
    d.add_argument("task", nargs="+")
    d.add_argument("--patterns", help="comma-separated pattern ids from `deal.py patterns`")
    d.add_argument("--seed", type=int)
    f = sub.add_parser("fields", help="rank the Range fields by overlap with the task's verbs")
    f.add_argument("verbs", nargs="+")
    a = ap.parse_args()

    if a.cmd == "patterns":
        for p in load()["patterns"]:
            if not p.get("hidden"):
                print(f"{p['id']} ({len(p['models'])} models): {p['problem'][:150]}")
        return
    if a.cmd == "fields":
        for s, fl in rank_fields(load(), " ".join(a.verbs))[:5]:
            print_field(s, fl)
        return

    pats = [p.strip() for p in a.patterns.split(",") if p.strip()] if a.patterns else None
    top, note, models, fields, lenses = deal(" ".join(a.task), a.seed, pats)
    print("## Patterns that fit")
    if note:
        print(f"_({note})_")
    for p in top:
        print(f"- **{p['name']}**: {p['solution']}")
    print("\n## Models to use as instruments (a card earns a report row only if it changed the work)")
    for m, why in models:
        print(f"- **{m['name']}** ({m['discipline']}; {why})\n  - Move: {m['move']}\n  - Receipt: {m['receipt']}")
    print("\n## Range fields (do what the field does; rerun `deal.py fields \"<verbs>\"` with the task's verbs)")
    for s, fl in fields:
        print_field(s, fl)
    print("\n## Lenses (look from here, with these instruments)")
    for l in lenses:
        ins = f" Instruments: {l['instruments']}" if l.get("instruments") else ""
        print(f"- **{l['name']}** [{l['family']}]: {l['asks']}{ins} Deliver: {l['delivers']}")


if __name__ == "__main__":
    main()
