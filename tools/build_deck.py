"""Build skills/ambition/references/deck.json from the mental-models catalog and
heavy-think's lens deck. Rerun after editing MODELS, FIELDS, HIDDEN or LENSES.

Usage: python3 tools/build_deck.py <mental-models.html> <perspectives.json>
"""
import json
import re
import sys
from pathlib import Path

# name -> (move, receipt). The move is one imperative line: what to do, not the
# model's history (the catalog's how_it_works is often a story). The receipt is
# the artifact or number that proves the move ran. Only models with an
# observable move are dealt.
MODELS = {
    # Decision-making and forecasting
    "Cynefin Framework": (
        "Name the domain from evidence: clear (apply best practice), complicated (analyse), complex (probe, sense, respond), chaotic (act to stabilise first).",
        "The domain named (clear, complicated, complex, chaotic) with the evidence for it, and the method that follows from it."),
    "Reversible vs. Irreversible Decisions (Type 1 / Type 2)": (
        "Tag each decision one-way or two-way door; move fast on two-way doors and slow down only for one-way doors.",
        "Each decision tagged one-way or two-way door, with the speed that follows."),
    "Expected Value": (
        "List the options, give each outcome a probability and a payoff, and compute the sum per option.",
        "Options with probabilities and payoffs, and the expected value of each."),
    "Reference Class Forecasting": (
        "Find past cases like this one, take their actual outcome distribution, and start your estimate from it.",
        "A reference class of similar cases with its base rate, compared to your estimate."),
    "Bayesian Updating": (
        "Write a prior as a number, weigh each piece of evidence by how much likelier it is under each hypothesis, and update.",
        "A prior, the evidence, and the updated estimate, as numbers."),
    "Decision Matrix": (
        "Fix the criteria and their weights before scoring any option, score every option, then test whether the winner holds when the top weight moves.",
        "Options × criteria with weights fixed before scoring, the totals, and whether the winner survives the top weight moving ±50%."),
    "Opportunity Cost": (
        "Name the best alternative use of the same time or money, and price it.",
        "The best option given up, and its value."),
    "Margin of Safety": (
        "Size a buffer against the worst plausible case, not the expected one.",
        "The buffer chosen, and the failure it absorbs."),
    "Pre-Mortem": (
        "Assume it failed a year from now; write why, then guard the most likely cause.",
        "A written 'it failed a year later because...' list, with a guard for the top item."),
    "Steel-Manning": (
        "Write the strongest version of the option you are about to reject, then show why it still loses.",
        "The strongest case for the option you rejected, in its best form, and why it still loses."),
    "Scenario Planning": (
        "Cross the two most important uncertainties into four futures, run the plan through each, and name the early signal for each.",
        "Two key uncertainties crossed into four scenarios, the plan's result in each, and the early signal that shows which one is unfolding."),
    # Cognitive bias: only biases with a countermove that leaves an artifact
    "Base Rate Fallacy": (
        "State the base rate before you look at the specific evidence.",
        "The base rate stated before the specific evidence is weighed."),
    "Survivorship Bias": (
        "List who is missing from the data (churned, failed, filtered out) and fetch them before concluding.",
        "The cases missing from the data (failures, churned, dropped), and how they change the answer."),
    "Confirmation Bias": (
        "Write the result that would prove your favoured explanation wrong, then go look for it.",
        "The result that would prove the favoured explanation wrong, the search for it, and what the search found."),
    "Anchoring Effect": (
        "Write your own estimate before you read the number you were given.",
        "An independent estimate written down before you saw the given number, and the gap between the two."),
    "Planning Fallacy": (
        "Set the inside-view estimate beside how long similar past tasks actually took, and correct it.",
        "The inside-view estimate beside the actual durations of past similar tasks, and the corrected estimate."),
    "Overconfidence Bias": (
        "Give 90% intervals instead of points, and check how often past intervals held the truth.",
        "Estimates as 90% intervals, and the hit rate of past intervals."),
    "Curse of Knowledge": (
        "Give the artifact alone to a reader with none of your context (a fresh subagent) and record where it stalls.",
        "The cold reader's stall points, quoted, and the fix for each."),
    # Problem-solving and root cause
    "Inversion": (
        "Ask how to guarantee failure, list the ways, then rule each one out.",
        "A list of the ways the goal fails, each with the check that rules it out."),
    "First Principles Thinking": (
        "Strip the problem to the facts nobody can dispute, then rebuild the answer from those alone.",
        "The two or three facts nobody can argue with, and the answer rebuilt from them alone."),
    "Abstraction Laddering": (
        "Ask why to move up a level and how to move down; pick the level where the work pays most.",
        "The problem restated one level up (why?) and one level down (how?), and which level the work targets."),
    "Five Whys": (
        "Ask why from the symptom until you reach a cause you can change, backing each step with data.",
        "A why-chain from symptom to a cause you can change, each step backed by data."),
    "Root Cause Analysis": (
        "List the candidate causes and rule each out with evidence until one remains.",
        "The root cause with the evidence that rules out the other candidates."),
    "Fishbone Diagram (Ishikawa / Cause-and-Effect Diagram)": (
        "Sort candidate causes into categories (people, process, tools, data, environment) and confirm or rule out each with data.",
        "Cause categories with their candidate causes, each marked confirmed or ruled out by a named piece of data."),
    "Issue Trees (Logic Trees)": (
        "Split the question into sub-questions that don't overlap and together cover it, down to ones data can answer.",
        "The tree, with each leaf answered by a named piece of data."),
    "MECE Principle": (
        "Break the whole into parts that don't overlap and leave nothing out, and check that the parts sum to the whole.",
        "The breakdown's parts, with a check that none overlap and that their numbers sum to the whole."),
    "Retrograde Analysis (Working Backwards)": (
        "Write the finished end state first, then derive each step that must precede it.",
        "The end state written first, and the chain of steps derived back to today."),
    "Constraint Relaxation": (
        "Tag every constraint as real (with its source) or assumed, and solve once with an assumed one dropped.",
        "Every constraint tagged real (with its source) or assumed, and the solution with one assumed constraint dropped."),
    "Ishikawa Conflict Resolution Diagram (Evaporating Cloud)": (
        "Write the goal, the two needs and the two conflicting wants, then surface the assumption under each arrow and break one.",
        "The cloud (goal, two needs, two conflicting wants), the assumption under each arrow, and the one shown false."),
    "PDSA Cycle (Plan-Do-Study-Act)": (
        "Write the predicted result before the change, run the change small, compare result with prediction, then adopt, adapt or drop.",
        "The prediction file written before the change, the measured result, and the decision."),
    # Creativity and option expansion
    "Divergent / Convergent Thinking": (
        "Generate options with judging switched off, then write the criteria, then converge.",
        "A count of options generated before any was judged, then the criteria written down and the shortlist they produced."),
    "SCAMPER": (
        "Run the subject through Substitute, Combine, Adapt, Modify, Put to another use, Eliminate, Reverse.",
        "At least one idea per SCAMPER verb (seven or more), and the two kept, each with its reason."),
    "Reverse Brainstorming": (
        "List ways to make the problem worse, mark the ones already happening, and invert each into a fix.",
        "A list of ways to make the problem worse, the ones already happening marked, and each inverted into a candidate fix."),
    "Concept Fan": (
        "Step up from the idea to the concept it serves, then fan out to other ideas that serve the same concept.",
        "The concept one level up, and at least three alternatives that serve it."),
    "Morphological Analysis (Zwicky Box)": (
        "List the problem's independent dimensions, the options for each, and scan the combinations.",
        "A grid of dimensions and options, and the combinations it produced that nobody proposed."),
    "TRIZ (Theory of Inventive Problem Solving)": (
        "State the contradiction (improving X worsens Y) and apply the inventive principle that resolves it.",
        "The contradiction (improving X worsens Y) and the inventive principle that resolves it."),
    "Analogical Thinking": (
        "Find a field that solved the same shape of problem, map its mechanism part by part, and test one prediction it makes here.",
        "The source field, the part-by-part mapping, and the prediction tested."),
    "Jobs to Be Done (JTBD)": (
        "Find the job the user hires this for, in their words, from real interviews or support tickets.",
        "The job the user hires this for, in their words, and what it changes in the solution."),
    "Impact-Effort Matrix": (
        "Estimate impact and effort for each option as numbers, and take the high-impact, low-effort ones first.",
        "Each option with an impact and an effort estimate (numbers, not adjectives), and the quick wins taken first."),
    # Systems thinking
    "Leverage Points": (
        "Name the Meadows level of the change (parameters up to goals) and try one level higher.",
        "The Meadows level of the chosen change, and the attempt to move one level up."),
    "Causal Loop Diagram (CLD)": (
        "Write the variables and the causal links with their signs, and close the loops.",
        "The loops written out (A -> B -> A), each marked reinforcing or balancing, with data for each link."),
    "Reinforcing Feedback Loop": (
        "Find the loop that feeds itself and measure its gain per cycle.",
        "The loop written out, with its gain measured from data (growth or decay per cycle, or doubling time)."),
    "Balancing Feedback Loop": (
        "Find the loop that pulls the system back to a target, and measure the target and the gap.",
        "The balancing loop, its goal, and the measured gap and correction rate."),
    "Stock and Flow": (
        "Name the stock, measure its inflows and outflows, and project it forward.",
        "The stock, its inflows and outflows as numbers, and a projection of where it goes."),
    "Delays": (
        "Measure or estimate the delay in each loop, and plan for the overshoot it causes.",
        "The delay in each loop, measured or estimated, and how the plan accounts for it."),
    "Iceberg Model": (
        "Go below the event to the pattern, below the pattern to the structure, and below that to the belief that holds it.",
        "The event, the pattern behind it, the structure behind that, and the mental model behind the structure."),
    "Fixes That Fail Archetype": (
        "Find the quick fix whose side effect brings the problem back, and show it in the data.",
        "The quick fix, the side effect that brings the problem back, and the data that shows it."),
    "Shifting the Burden Archetype": (
        "Separate the symptomatic fix from the fundamental one it crowds out, and plan the fundamental one.",
        "The symptomatic fix, the fundamental fix it crowds out, and the plan to do the fundamental one."),
    "Limits to Growth Archetype": (
        "Find the growth loop and the resource that will stop it, and measure how close that limit is.",
        "The growth loop, the limiting resource, and the level at which it binds, with how far away that is now."),
    "Escalation Archetype": (
        "Plot both sides' moves over time to show each one responding to the other, then find a one-sided step that breaks the loop.",
        "Both sides' moves plotted over time, showing each response to the other, and the one-sided step that breaks the loop."),
    "Tragedy of the Commons": (
        "Name the shared resource, and set each user's private gain against the shared cost.",
        "The shared resource, each user's gain against the shared cost as numbers, and the depletion rate."),
    "Ostrom's Design Principles": (
        "Check the shared resource's governance against Ostrom's eight principles and add the missing one.",
        "The eight principles checked against the shared resource, and the missing one the plan adds."),
    "Tipping Point": (
        "Find the threshold where behaviour changes, and measure where the system sits now.",
        "The threshold value, where the system is now, and the distance to it."),
    "Power Laws / Fat Tails": (
        "Measure what share the top 1% and 10% carry before trusting any average.",
        "The top-1% and top-10% shares, and whether the mean is safe to use."),
    "Normal Accidents Theory": (
        "Rate the system's coupling (tight or loose) and interactions (linear or complex); where both are high, add slack or decouple.",
        "Each component rated on coupling and complexity, and the decoupling or slack added at the worst one."),
    "Goodhart's Law": (
        "For each metric the work improves, pick a second measure that would show if the real goal did not move.",
        "The metric the work improves, and a second measure that shows the real goal moved too."),
    "Cobra Effect": (
        "Describe the incentive the change creates, then play the person who games it.",
        "The incentive the change creates, and the way someone could game it."),
    "Jevons Paradox (Rebound Effect)": (
        "Estimate the demand an efficiency gain unlocks before you count the saving.",
        "The efficiency gain, and the demand it may unlock, estimated."),
    "Unintended Consequences": (
        "Ask who else the change touches and what they will do differently, then look for the earliest sign of it.",
        "Each affected party, its likely response, and the metric that would show it first."),
    # Strategy and operations
    "Pareto Principle (80/20 Rule)": (
        "Rank causes by their share of the effect and work only on the top few.",
        "A ranked breakdown showing which few causes carry most of the effect, with their share."),
    "Theory of Constraints (TOC)": (
        "Find the one step that limits throughput, measure it, and improve only that step until it moves.",
        "The one constraint, measured, and the result after the work moves it."),
    "Bottleneck Analysis": (
        "Measure the queue and utilisation at every step; the one with the longest queue is the bottleneck.",
        "Utilisation and queue length per step, and the bottleneck named."),
    "Critical Path Method (CPM)": (
        "Lay out the tasks with durations and dependencies, find the longest path, and protect it.",
        "The task graph with durations, the critical path and its length, and the slack on the other tasks."),
    "Unit Economics": (
        "Compute value and cost per unit (user, order, request), and show how the change moves each.",
        "The value and cost per unit, and how the change moves each."),
    "Gall's Law": (
        "Build the smallest version that works end to end, and grow it from there.",
        "The smallest working version that the larger design grows from."),
    "Conway's Law": (
        "Draw the team and ownership boundaries beside the design's module boundaries, and decide whether they should match.",
        "The team or ownership boundary that the design follows, and whether it should."),
    "Map Is Not the Territory": (
        "Name the model's main simplification and test it against the real system.",
        "The model's main simplification, and a real-world check of it."),
    "Minimum Viable Product (MVP)": (
        "Write the learning goal and its pass line, then build the least that tests it.",
        "The hypothesis, the pass line set before the test, and the result."),
    "North Star Metric": (
        "Pick the one metric that tracks the value users get, plus a guardrail metric it must not hurt.",
        "The north star with its current value, and the guardrail metric beside it."),
    "Network Effects": (
        "Plot value per user against network size, and name which kind of network effect it is.",
        "Value per user plotted against the number of users (or another measure of network size), and which kind of network effect it is."),
    "Flywheel Effect": (
        "Write the loop's steps and measure the conversion rate at each one.",
        "The loop's steps written out, with the conversion rate measured at each step, and the weakest step named."),
    "Competitive Moat": (
        "Name the moat type (switching cost, network, scale, brand, intangible) and the evidence that it holds.",
        "The moat type, and a number that shows it holding (retention, price premium, cost gap)."),
    "Porter's Five Forces": (
        "Rate rivalry, new entrants, substitutes, buyer power and supplier power, each with evidence.",
        "The five forces rated with evidence, and the strongest one named."),
    "Wardley Mapping": (
        "Place each component by how visible it is to the user and how evolved it is, then decide build, buy or outsource.",
        "Components placed by user visibility and evolution stage, and a build, buy or outsource call for each."),
    "Path Dependence / Lock-In": (
        "Estimate what it would cost to reverse the choice later, and what would keep it reversible.",
        "The switching cost of the choice, estimated in time or money, and what would keep it reversible."),
    "Technology Adoption Lifecycle (Crossing the Chasm)": (
        "Name the segment you are selling to now and the one beachhead niche that gets you to the early majority.",
        "The current adopter segment, the beachhead niche, and the whole product it needs."),
    "Diffusion of Innovation (S-Curve)": (
        "Place the product on its adoption S-curve from real numbers, and name the next segment's main objection.",
        "The adoption share now, the curve's phase, and the next segment's objection."),
    "Antifragility": (
        "Find where the system gains from stress, and add small, cheap, frequent stressors there.",
        "The stressor added, and a measure that shows the system got stronger from it."),
    "Black Swan": (
        "List the rare events with outsized impact, and make the plan survive them, not predict them.",
        "The rare events listed, the plan's exposure to each, and the cap on the worst one."),
    # Communication and people
    "Minto Pyramid Principle (BLUF)": (
        "Put the answer first in one sentence, then three supporting points, then the evidence for each.",
        "The answer in one sentence at the top, three supporting points under it, the evidence under each, and nothing left over."),
    "SCQA Framework": (
        "Open with Situation, Complication, Question and Answer, one sentence each.",
        "The opening written as Situation, Complication, Question and Answer, each in one sentence, with the Answer matching the recommendation."),
    "Situation-Behavior-Impact (SBI)": (
        "Rewrite each piece of feedback as situation, observable behaviour and impact, without judgment words.",
        "Each piece of feedback rewritten as situation, observable behaviour and impact, with every judgment word removed."),
    "Psychological Safety": (
        "Measure whether people can speak up (Edmondson's seven survey items, or who speaks in meetings) before asking for candour.",
        "The survey scores or the speaking counts, and the lowest item addressed."),
    "BATNA & ZOPA": (
        "Write both sides' best alternative to a deal, and the zone where a deal beats both.",
        "Each side's BATNA with its value, and the ZOPA's bounds, or proof that none exists."),
    "Principled Negotiation (Interest-Based Negotiation)": (
        "List the interests behind each side's position, and generate options that serve both, judged by an objective standard.",
        "Each side's interests, the options generated, and the objective standard used to choose."),
    # Learning
    "Deliberate Practice": (
        "Pick the one sub-skill just beyond current ability, drill it with immediate feedback, and score each repetition.",
        "The one sub-skill just beyond current ability, a drill with immediate feedback, and the score per repetition."),
    "Feynman Technique": (
        "Explain it in plain words to a newcomer, mark where the explanation breaks, and go back to the source for each gap.",
        "A plain-language explanation for a newcomer, the places where it broke down, and the source used to fill each gap."),
    "Double-Loop Learning": (
        "When a fix keeps recurring, state the assumption behind it and test that instead of the fix.",
        "The assumption behind the recurring fix, stated and tested against data, and the rule changed if it fails."),
}

# Patterns left out of `deal.py patterns`: high mode step 1 already classifies,
# and the lattice pattern is about choosing models, which the dealer does.
HIDDEN = {"classify-before-solving", "model-lattice-navigation"}

# Range cards: a field, the verbs it is good at, and what it does. SKILL.md
# describes the task with verbs, then names fields good at those verbs; these
# give each field a method and an instrument, not only a name.
FIELDS = [
    ("forensic-accounting", "Forensic accounting", ["trace", "reconcile", "detect manipulation", "find missing volume", "audit"],
     "Reconcile every unit of a total to an independent total; test digit distributions for fabrication.",
     "A reconciliation join between two sources; a Benford first-digit test.",
     "A reconciliation table with the unexplained residual, and the Benford test statistic."),
    ("epidemiology", "Epidemiology", ["link a cause to an outcome", "rule out confounders", "date an exposure", "attribute"],
     "Compare exposed and unexposed groups over the same period (difference-in-differences, case-control); look for dose-response.",
     "A 2×2 table or difference-in-differences estimate with an unexposed control group.",
     "The effect with its confidence interval, and the control group that rules out a common shock."),
    ("investigative-journalism", "Investigative journalism", ["verify a claim", "find who knows", "build a timeline"],
     "Two independent sources per key fact; a dated document trail.",
     "A source log: claim, source 1, source 2, date.",
     "Each key claim with two independent sources, or marked single-source."),
    ("sre", "Site reliability engineering", ["keep a service up", "find why it broke", "decide what to alert on", "debug"],
     "A blameless timeline from raw logs; service level objectives with error budgets.",
     "A log query that builds a minute-by-minute timeline; a service level indicator query.",
     "The timeline with the trigger and the contributing factors, and the error budget burned."),
    ("experimental-design", "Clinical trials and biostatistics", ["prove a change causes an effect", "size a test", "predict", "evaluate"],
     "Pre-register the prediction, randomize, size the sample by power analysis, and analyse as planned.",
     "A prediction file written before the data is read; a power calculation; a randomized holdout.",
     "The prediction file (written before the data was read), n from the power calculation, and the effect with its interval."),
    ("short-seller", "Short-seller research", ["find what is overstated", "test a claim against reality", "check a number"],
     "Channel checks: compare each reported number with an observable proxy from outside the company.",
     "An independent data source set against the reported metric.",
     "The claim, the independent measure, and the gap."),
    ("editing", "Editing (books, film)", ["make a busy reader follow", "cut", "order an argument", "persuade"],
     "Reverse-outline the draft, then cut every section that doesn't advance the one point.",
     "A reverse outline: one line per section stating its point.",
     "Word count before and after, and the reverse outline with the cut sections marked."),
    ("aviation-safety", "Aviation safety and human factors", ["prevent rare catastrophic error", "make routine steps reliable", "harden"],
     "Failure modes and effects analysis; checklists for critical steps; read-back.",
     "An FMEA table scored severity × occurrence × detection.",
     "FMEA rows with risk priority numbers, and the mitigation for the top row."),
    ("operations-research", "Operations research and queueing", ["allocate scarce capacity", "cut waiting", "schedule", "optimize throughput"],
     "Model the system (Little's law, M/M/c queues, linear programming) and simulate before changing it.",
     "A queueing model or LP solver checked against observed throughput.",
     "Modelled vs observed wait and throughput, and the objective value of the chosen allocation."),
    ("red-team", "Security red team", ["find how it breaks under an adversary", "abuse a limit", "attack"],
     "Threat model (STRIDE), an attack tree, then real exploit attempts.",
     "An attack tree and a proof-of-concept script run against the real system.",
     "Each leaf of the attack tree tried, with the working proof of concept or the blocked result."),
    ("performance-engineering", "Performance engineering", ["make it faster", "find where time goes", "cut cost per request"],
     "Measure first: profile under a realistic load, fix the top frame, and measure again.",
     "A profiler (flame graph) and a benchmark with a fixed workload and repeat runs.",
     "The before and after benchmark with variance, and the flame-graph frame that moved."),
    ("ux-research", "UX research", ["learn what users need", "find where people get stuck", "test a design"],
     "Watch five real users try the task without help, and count where they fail.",
     "A task-based usability test script and a session recording or transcript.",
     "Task success rate per step, and the quoted stall points."),
    ("actuarial-science", "Actuarial science", ["price a risk", "estimate a tail", "plan reserves"],
     "Fit a loss distribution to historical claims and price from its tail, not its mean.",
     "A fitted frequency-severity model on historical loss data.",
     "The fitted distribution, the 99th-percentile loss, and the reserve it implies."),
    ("supply-chain", "Supply chain and logistics", ["keep things flowing", "buffer against variability", "cut lead time"],
     "Map the flow end to end with lead times and inventory at each node; size buffers from demand variability.",
     "A value-stream map with lead time and inventory per step; a safety-stock calculation.",
     "Lead time per step, the share that is waiting, and the buffer sized from variance."),
    ("game-design", "Game design", ["make people want to come back", "teach without instructions", "balance"],
     "Design the core loop and its reward schedule, then playtest and tune numbers from telemetry.",
     "A core-loop diagram and playtest telemetry (drop-off per step).",
     "The loop, the drop-off per step from a playtest, and the number tuned."),
    ("intelligence-analysis", "Intelligence analysis", ["decide under deception", "weigh conflicting evidence", "forecast"],
     "Analysis of competing hypotheses: score every piece of evidence against every hypothesis and keep the least-contradicted one.",
     "An ACH matrix of evidence × hypotheses.",
     "The matrix, the surviving hypothesis, and the single piece of evidence that would flip it."),
    ("law", "Litigation and contract law", ["argue a case", "find the loophole", "write rules that hold"],
     "Read the text literally, find the strongest opposing reading, and test every clause against an adversarial counterparty.",
     "A clause-by-clause adversarial read with precedent or source cited.",
     "Each clause with its hostile reading, and the rewrite that closes it."),
    ("ethnography", "Ethnography", ["understand a culture", "find the unwritten rule", "see the workaround"],
     "Observe people doing the real work in place, and record what they do, not what they say.",
     "Field notes or a screen recording of the real workflow.",
     "The workarounds observed, each quoted or timestamped, and the rule each reveals."),
]

# Range lenses copied from heavy-think's deck. Edit them there and rerun this script.
LENSES = ["outsider", "adversary", "economist", "operator", "historian", "newcomer",
          "competitor", "systems-thinker", "craftsperson", "storyteller", "data-steward",
          "skeptic", "fact-checker"]


def slug(name):
    name = re.sub(r"\(.*?\)", "", name)
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def main(html_path, deck_path):
    s = Path(html_path).read_text()
    load = lambda k: json.loads(re.search(r'id="jd-%s"[^>]*>(.*?)</script>' % k, s, re.S).group(1))
    catalog = {m["name"]: m for m in load("models")}
    missing = [n for n in MODELS if n not in catalog]
    if missing:
        sys.exit(f"not in catalog: {missing}")
    models = [{
        "id": slug(n), "name": n, "discipline": catalog[n]["category"],
        "use_when": catalog[n]["problem"], "move": move, "receipt": receipt,
    } for n, (move, receipt) in MODELS.items()]
    ids = {m["name"]: m["id"] for m in models}
    patterns = [{
        "id": slug(p["name"]), "name": p["name"], "problem": p["problem"],
        "solution": p["solution"],
        "models": [ids[n] for n in p["models_involved"] if n in ids],
        "other_models": [n for n in p["models_involved"] if n not in ids],
        **({"hidden": True} if slug(p["name"]) in HIDDEN else {}),
    } for p in load("patterns")]
    unknown = HIDDEN - {p["id"] for p in patterns}
    if unknown:
        sys.exit(f"HIDDEN names unknown patterns: {sorted(unknown)}")
    # A pattern that deals no fitted model falls back to random cards; refuse to build one.
    empty = [p["id"] for p in patterns if not p["models"] and p["id"] not in HIDDEN]
    if empty:
        sys.exit(f"patterns with no dealt model (add one to MODELS or HIDDEN): {empty}")
    fields = [{"id": i, "name": n, "verbs": v, "method": m, "instruments": ins, "receipt": r}
              for i, n, v, m, ins, r in FIELDS]
    hk = {l["id"]: l for l in json.load(open(deck_path))["lenses"]}
    unknown = [i for i in LENSES if i not in hk]
    if unknown:
        sys.exit(f"LENSES not in {deck_path}: {unknown}")
    keys = ("id", "family", "name", "asks", "instruments", "delivers")
    lenses = [{k: hk[i][k] for k in keys if k in hk[i]} for i in LENSES]
    out = Path(__file__).resolve().parent.parent / "skills/ambition/references/deck.json"
    out.write_text(json.dumps({
        "about": f"Cards for ambition's high mode. Models: {len(models)} of a {len(catalog)}-model "
                 "catalog, kept because each has a move with a receipt. Patterns route a problem "
                 "to models. Fields are Range cards: a field, its verbs, method, instruments and "
                 "receipt. Lenses come from heavy-think's perspective deck.",
        "models": models, "patterns": patterns, "fields": fields, "lenses": lenses,
    }, indent=1, ensure_ascii=False) + "\n")
    print(f"{len(models)} models, {len(patterns)} patterns ({len(HIDDEN)} hidden), "
          f"{len(fields)} fields, {len(lenses)} lenses -> {out}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
