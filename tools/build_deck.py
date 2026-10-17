"""Build skills/ambition/references/deck.json from the mental-models catalog and
heavy-think's lens deck. Rerun after editing RECEIPTS or LENSES.

Usage: python3 tools/build_deck.py <mental-models.html> <perspectives.json>
"""
import json
import re
import sys
from pathlib import Path

# The model, and the receipt that proves it was used (an artifact or a number,
# not a sentence). Only models with an observable move are dealt.
RECEIPTS = {
    "Cynefin Framework": "The domain named (clear, complicated, complex, chaotic) with the evidence for it, and the method that follows from it.",
    "Inversion": "A list of the ways the goal fails, each with the check that rules it out.",
    "Second-Order Thinking": "The chosen change traced two steps ahead ('and then what?'), with one unintended effect and how the judge would catch it.",
    "First Principles Thinking": "The two or three facts nobody can argue with, and the answer rebuilt from them alone.",
    "Abstraction Laddering": "The problem restated one level up (why?) and one level down (how?), and which level the work targets.",
    "Five Whys": "A why-chain from symptom to a cause you can change, each step backed by data.",
    "Root Cause Analysis": "The root cause with the evidence that rules out the other candidates.",
    "Pareto Principle (80/20 Rule)": "A ranked breakdown showing which few causes carry most of the effect, with their share.",
    "Theory of Constraints (TOC)": "The one constraint, measured, and the result after the work moves it.",
    "Leverage Points": "The Meadows level of the chosen change, and the attempt to move one level up.",
    "Causal Loop Diagram (CLD)": "The loops written out (A -> B -> A), each marked reinforcing or balancing, with data for each link.",
    "Stock and Flow": "The stock, its inflows and outflows as numbers, and a projection of where it goes.",
    "Delays": "The delay in each loop, measured or estimated, and how the plan accounts for it.",
    "Fixes That Fail Archetype": "The quick fix, the side effect that brings the problem back, and the data that shows it.",
    "Shifting the Burden Archetype": "The symptomatic fix, the fundamental fix it crowds out, and the plan to do the fundamental one.",
    "Goodhart's Law": "The metric the work improves, and a second measure that shows the real goal moved too.",
    "Cobra Effect": "The incentive the change creates, and the way someone could game it.",
    "Jevons Paradox (Rebound Effect)": "The efficiency gain, and the demand it may unlock, estimated.",
    "Pre-Mortem": "A written 'it failed a year later because...' list, with a guard for the top item.",
    "Steel-Manning": "The strongest case for the option you rejected, in its best form, and why it still loses.",
    "Reference Class Forecasting": "A reference class of similar cases with its base rate, compared to your estimate.",
    "Bayesian Updating": "A prior, the evidence, and the updated estimate, as numbers.",
    "Expected Value": "Options with probabilities and payoffs, and the expected value of each.",
    "Base Rate Fallacy": "The base rate stated before the specific evidence is weighed.",
    "Survivorship Bias": "The cases missing from the data (failures, churned, dropped), and how they change the answer.",
    "Margin of Safety": "The buffer chosen, and the failure it absorbs.",
    "Reversible vs. Irreversible Decisions (Type 1 / Type 2)": "Each decision tagged one-way or two-way door, with the speed that follows.",
    "Morphological Analysis (Zwicky Box)": "A grid of dimensions and options, and the combinations it produced that nobody proposed.",
    "TRIZ (Theory of Inventive Problem Solving)": "The contradiction (improving X worsens Y) and the inventive principle that resolves it.",
    "Jobs to Be Done (JTBD)": "The job the user hires this for, in their words, and what it changes in the solution.",
    "Iceberg Model": "The event, the pattern behind it, the structure behind that, and the mental model behind the structure.",
    "Unit Economics": "The value and cost per unit, and how the change moves each.",
    "Opportunity Cost": "The best option given up, and its value.",
    "Gall's Law": "The smallest working version that the larger design grows from.",
    "Conway's Law": "The team or ownership boundary that the design follows, and whether it should.",
    "Map Is Not the Territory": "The model's main simplification, and a real-world check of it.",
}
# Range lenses copied from heavy-think's deck. Until a shared core exists, edit
# them there and rerun this script.
LENSES = ["outsider", "adversary", "economist", "operator", "historian", "newcomer",
          "competitor", "systems-thinker", "craftsperson", "storyteller", "data-steward",
          "pre-mortem"]


def slug(name):
    name = re.sub(r"\(.*?\)", "", name)
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def main(html_path, deck_path):
    s = Path(html_path).read_text()
    load = lambda k: json.loads(re.search(r'id="jd-%s"[^>]*>(.*?)</script>' % k, s, re.S).group(1))
    catalog = {m["name"]: m for m in load("models")}
    missing = [n for n in RECEIPTS if n not in catalog]
    if missing:
        sys.exit(f"not in catalog: {missing}")
    models = [{
        "id": slug(n), "name": n, "discipline": catalog[n]["category"],
        "use_when": catalog[n]["problem"], "move": catalog[n]["how_it_works"],
        "receipt": RECEIPTS[n],
    } for n in RECEIPTS]
    ids = {m["name"]: m["id"] for m in models}
    patterns = [{
        "id": slug(p["name"]), "name": p["name"], "problem": p["problem"],
        "solution": p["solution"],
        "models": [ids[n] for n in p["models_involved"] if n in ids],
        "other_models": [n for n in p["models_involved"] if n not in ids],
    } for p in load("patterns")]
    hk = {l["id"]: l for l in json.load(open(deck_path))["lenses"]}
    lenses = [{k: hk[i][k] for k in ("id", "family", "name", "asks", "delivers")} for i in LENSES]
    out = Path(__file__).resolve().parent.parent / "skills/ambition/references/deck.json"
    out.write_text(json.dumps({
        "about": "Cards for ambition's high mode. Models: 36 of a 247-model catalog, kept "
                 "because each has a move with a receipt. Patterns route a problem to models. "
                 "Lenses come from heavy-think's perspective deck.",
        "models": models, "patterns": patterns, "lenses": lenses,
    }, indent=1, ensure_ascii=False) + "\n")
    print(f"{len(models)} models, {len(patterns)} patterns, {len(lenses)} lenses -> {out}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
