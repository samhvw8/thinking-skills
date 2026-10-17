"""Deal cards for ambition's high mode: the patterns that fit the task, three
mental models (from the patterns, plus one from another discipline), and three
Range lenses from different families. Standard library only.

Usage:
  python3 deal.py patterns                                   # list the 23 patterns, one line each
  python3 deal.py deal "<task>" --patterns id1,id2 [--seed N]  # deal for the patterns you picked
  python3 deal.py deal "<task>"                              # let keyword overlap pick (weaker)
"""
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


def words(text):
    out = set()
    for w in re.findall(r"[a-z]+", text.lower()):
        if len(w) > 3 and w not in STOP:
            out.add(w[:6])  # a crude stem, so "failing" and "failed" match
    return out


def deal(task, seed=None, pattern_ids=None):
    deck = json.loads(DECK.read_text())
    rng = random.Random(seed if seed is not None else task)
    models = {m["id"]: m for m in deck["models"]}
    tw = words(task)

    def score(text):
        return len(tw & words(text))

    if pattern_ids:
        by_id = {p["id"]: p for p in deck["patterns"]}
        unknown = [i for i in pattern_ids if i not in by_id]
        if unknown:
            sys.exit(f"unknown pattern id: {', '.join(unknown)}. Run: deal.py patterns")
        top = [by_id[i] for i in pattern_ids]
    else:
        pats = sorted(deck["patterns"], key=lambda p: -score(p["name"] + " " + p["problem"] + " " + p["solution"]))
        top = [p for p in pats[:2] if score(p["name"] + " " + p["problem"] + " " + p["solution"]) > 0] or pats[:1]

    chosen = []
    for p in top:
        ranked = sorted((i for i in p["models"] if i != "cynefin-framework"),
                        key=lambda i: -score(models[i]["use_when"] + " " + models[i]["move"]))
        for i in ranked[:2 if len(top) == 1 else 1]:
            if i not in chosen:
                chosen.append(i)
    if "cynefin-framework" in chosen:
        chosen.remove("cynefin-framework")  # always applied in step 1 anyway
    used = {models[i]["discipline"] for i in chosen}
    others = [m["id"] for m in deck["models"] if m["discipline"] not in used and m["id"] not in chosen
              and m["id"] != "cynefin-framework"]
    while len(chosen) < 3 and others:
        pick = rng.choice(others)
        chosen.append(pick)
        others = [i for i in others if models[i]["discipline"] != models[pick]["discipline"]] or \
                 [i for i in others if i != pick]

    lenses, families = [], set()
    for lens in rng.sample(deck["lenses"], len(deck["lenses"])):
        if lens["family"] not in families:
            lenses.append(lens)
            families.add(lens["family"])
        if len(lenses) == 3:
            break
    return top, [models[i] for i in chosen[:3]], lenses


def flag(args, name):
    if name in args:
        k = args.index(name)
        value = args[k + 1]
        del args[k:k + 2]
        return value
    return None


def main():
    args = sys.argv[1:]
    if args[:1] == ["patterns"]:
        for p in json.loads(DECK.read_text())["patterns"]:
            print(f"{p['id']}: {p['problem'][:150]}")
        return
    if args[:1] == ["deal"]:
        args = args[1:]
    seed = flag(args, "--seed")
    pats = flag(args, "--patterns")
    if not args:
        sys.exit(__doc__)
    top, models, lenses = deal(" ".join(args), int(seed) if seed else None,
                               [p.strip() for p in pats.split(",")] if pats else None)
    print("## Patterns that fit")
    for p in top:
        print(f"- **{p['name']}**: {p['solution']}")
    print("\n## Models to use as instruments (leave the receipt, or strike with a reason)")
    for m in models:
        print(f"- **{m['name']}** ({m['discipline']})\n  - Move: {m['move']}\n  - Receipt: {m['receipt']}")
    print("\n## Range lenses (do what the field does)")
    for l in lenses:
        print(f"- **{l['name']}**: {l['asks']} Deliver: {l['delivers']}")


if __name__ == "__main__":
    main()
