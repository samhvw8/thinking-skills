#!/usr/bin/env python3
"""council.py: the state machine behind /council full mode.

A full council runs a creative session as rounds of file-based sub-agents, so it
scales past the 2 to 4 live teammates of a live council, needs no agent-teams flag,
and survives a context compaction: everything lives in council.json.

    python3 council.py plan [--members 8 --cross 2 --judges 3 --shortlist 4]   # calls per phase. Writes nothing.
    python3 council.py deal --members 4 [--preset P] [--seed S]                # cards only, for a live council
    python3 council.py presets                                                 # the preset lens sets
    python3 council.py init --brief-file brief.md [--members 8] [--preset P | --lenses a,b,c] [--seed S] [--model M] [--phase-model develop=strong]
    python3 council.py next                       # what to do now, and the exact command for it
    python3 council.py prompts <phase>            # write the briefs, list the jobs still to run
    python3 council.py check <phase>              # which outputs are still missing
    python3 council.py collect                    # read the pool or the judges' scores into the state
    python3 council.py status                     # where the run is
    python3 council.py harvest                    # shortlist, scores, lineage and the files to read
    python3 council.py card <member>              # one member's card

Phases, in order: diverge, cross1 .. crossC, cluster, score, develop, stress.
Every command takes --dir; without it, the run named in .council/LATEST is used.
The prompt templates live in prompts.md beside this file.

Exit codes: 0 when the step worked, 1 when it did not (an error, an output rejected,
or a run that stopped because a job failed twice; `next` then prints STOPPED).

Python 3.8+, standard library only.
"""
import argparse
import json
import os
import random
import re
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SELF = os.path.abspath(__file__)
PROMPTS_PATH = os.path.join(HERE, "prompts.md")

ROOT = ".council"
LATEST = "LATEST"
STATE_FILE = "council.json"
TEMPLATES = ("diverge", "cross", "curator", "judge", "developer", "stress")

DEFAULTS = {"members": 8, "cross": 2, "judges": 3, "shortlist": 4, "parallel": 6}
QUICK = {"members": 5, "cross": 1, "judges": 2, "shortlist": 3}
MIN_JUDGES = 2          # below this the "independent panel" is one opinion; fewer usable judges stop the run
NO_OUTPUT = "NO OUTPUT"
# Judgment (generating, curating, judging) runs on the session's model. Web research and the stress
# test run on the fast tier: under a fixed budget, the strongest model everywhere bought fewer
# concepts and lost to this mix. Tiers, not model names, so the run works in any harness;
# heavy-think's references/harness.md maps each tier to a model.
SESSION_MODEL = "session"
RESEARCH_MODEL = "fast"
RESEARCH_PHASES = ("develop", "stress")  # what the orchestrator writes into a job's output after the job failed twice


# ---------------------------------------------------------------- the deck

def _find_deck():
    """council carries its own copy of the shared deck in deck/ (built from the repo's decks/ by
    tools/build_decks.py), so it runs without any other skill installed."""
    cand = os.path.join(HERE, "deck")
    if os.path.isfile(os.path.join(cand, "deck.py")):
        return cand
    raise SystemExit("council: deck/deck.py is missing from %s. Reinstall the council skill." % HERE)


sys.path.insert(0, _find_deck())
import deck as D  # noqa: E402

load_deck = D.load_deck
deal_cards = D.deal_cards
RUBRIC_PATH = D.RUBRIC_PATH
MIN_MEMBERS = len(D.REQUIRED_FAMILIES)   # the deal seats one lens from each required family

# The card fields the member templates show, by placeholder. check_deck validates exactly these
# (plus the family, which seats the ring, and the provocation) before a run starts.
CARD_FIELDS = {
    "lens_name": ("lens", "name"), "lens_asks": ("lens", "asks"), "lens_sees": ("lens", "sees"),
    "lens_misses": ("lens", "misses"), "lens_delivers": ("lens", "delivers"),
    "technique_name": ("technique", "name"), "technique_how": ("technique", "how"),
}
OPTIONAL_CARD_FIELDS = {"lens_instruments": ("lens", "instruments")}   # shown only when the lens has it
# Dealing data and provenance, never shown to members. A field added to the deck's lenses is either
# rendered in prompts.md or listed here on purpose; tests/test_council.py fails otherwise.
LENS_META_FIELDS = ("id", "family", "clashes", "source")
DECK_POOLS = {"lens": "lenses", "technique": "techniques", "provocation": "provocations"}


class CouncilError(Exception):
    pass


def check_deck(deck, extra_lenses=()):
    """Every card field a council prompt uses, present and non-empty, on every entry. Runs at
    init so a deck change fails before any agent is paid for, not at the last cross round."""
    load_templates()
    need = {}
    for part, field in list(CARD_FIELDS.values()) + [("lens", "family"), ("provocation", "text")]:
        need.setdefault(part, []).append(field)
    problems = []
    for part, fields in sorted(need.items()):
        items = list(deck.get(DECK_POOLS[part]) or [])
        if part == "lens":
            items += list(extra_lenses)
        for it in items:
            for f in fields:
                v = it.get(f)
                if not isinstance(v, str) or not v.strip():
                    problems.append("%s '%s' has no '%s'" % (part, it.get("id", "?"), f))
    if problems:
        more = " (and %d more)" % (len(problems) - 8) if len(problems) > 8 else ""
        raise CouncilError("the deck is missing card fields the council prompts use: %s%s"
                           % ("; ".join(problems[:8]), more))


def member_ids(n):
    return ["m%02d" % i for i in range(1, n + 1)]


def make_ring(members, agents, seed):
    """Seat the members in a ring where neighbours come from different families
    wherever possible. Cross-pollination partners are read off this ring."""
    rng = random.Random("council-ring:%s" % seed)
    left = list(members)
    rng.shuffle(left)
    ring = [left.pop(0)]
    while left:
        fam = agents[ring[-1]]["card"]["lens"]["family"]
        j = next((k for k, m in enumerate(left) if agents[m]["card"]["lens"]["family"] != fam), 0)
        ring.append(left.pop(j))
    return ring


def partners(state, member, rnd):
    """Cross round k reads the members k seats away on both sides of the ring. The last
    round also reads the member straight across the ring, so ideas from opposite sides
    meet before the curator, not only inside it."""
    ring = state["ring"]
    n = len(ring)
    i = ring.index(member)
    offsets = [rnd, -rnd]
    if rnd == state["cross"] and n >= 5:
        offsets.append(n // 2)
    out = []
    for off in offsets:
        p = ring[(i + off) % n]
        if p != member and p not in out:
            out.append(p)
    return out


# ---------------------------------------------------------------- phases and paths

def phases(state):
    return ["diverge"] + ["cross%d" % k for k in range(1, state["cross"] + 1)] + \
        ["cluster", "score", "develop", "stress"]


def stage_file(d, member, stage):
    """stage 0 is the member's diverge file, stage k its cross round k file."""
    if stage == 0:
        return os.path.join(d, "diverge", member + ".md")
    return os.path.join(d, "cross%d" % stage, member + ".md")


def pool_out(d):
    return os.path.join(d, "pool.json")


def score_out(d, judge):
    return os.path.join(d, "score", judge + ".json")


def develop_out(d, cid):
    return os.path.join(d, "develop", cid + ".md")


def stress_out(d, cid):
    return os.path.join(d, "stress", cid + ".md")


def prompt_path(d, phase, job_id):
    return os.path.join(d, "prompts", phase, job_id + ".md")


def _has_output(path):
    return os.path.isfile(path) and os.path.getsize(path) > 0


def judge_ids(state):
    return ["j%d" % i for i in range(1, state["judges"] + 1)]


def active_judges(state):
    return [j for j in judge_ids(state) if j not in state.get("dropped", [])]


def all_idea_files(state):
    d = state["dir"]
    files = []
    for m in sorted(state["members"]):
        for stage in range(0, state["cross"] + 1):
            files.append(stage_file(d, m, stage))
    return files


# ---------------------------------------------------------------- state

def new_state(n, seed, deck, run_dir, cross, judges, shortlist, parallel, preset=None, explicit=None,
              rubric=None, techniques=True):
    run_dir = os.path.abspath(run_dir)
    ids = member_ids(n)
    rubric = rubric or D.preset_rubric(deck, preset) or "creative"
    if rubric not in ("creative", "decision"):
        # The review rubric ranks findings on an existing artifact, not concepts.
        raise CouncilError("preset '%s' scores with the '%s' rubric, which council judges cannot use: pass "
                           "--rubric creative|decision, or use heavy-think Perspectives mode with ASK review" % (preset, rubric))
    weights = D.rubric_weights(deck, rubric)
    agents = {}
    for mid, card in zip(ids, deal_cards(n, seed, deck, preset, explicit, techniques=techniques)):
        agents[mid] = {"card": card}
    state = {
        "version": 2,
        "created": time.strftime("%Y-%m-%d %H:%M:%S"),
        "seed": seed,
        "dir": run_dir,
        "members_n": n,
        "cross": cross,
        "judges": judges,
        "shortlist_n": shortlist,
        "pool_max": max(shortlist * 3, 8),
        "parallel": parallel,
        "preset": preset,
        "rubric": rubric,
        "weights": weights,
        "members": agents,
        "pool": None,
        "scores": None,
        "shortlist": None,
        "failures": {},   # job id -> failed attempts; 2 ends the job
        "dropped": [],    # judges that failed twice
        "ended": None,    # why the run stopped, when a job it cannot do without failed twice
        "model": None,    # the session's model: diverge, cross, cluster and score run on it
        "phase_models": {},  # per-phase overrides; develop and stress default to RESEARCH_MODEL
    }
    state["ring"] = make_ring(ids, agents, seed)
    return state


def plan_rows(n, cross, judges, shortlist):
    return [("diverge", n)] + [("cross%d" % k, n) for k in range(1, cross + 1)] + \
        [("cluster", 1), ("score", judges), ("develop", shortlist), ("stress", shortlist)]


# ---------------------------------------------------------------- jobs

def phase_jobs(state, phase):
    if phase not in phases(state):
        raise CouncilError("unknown phase '%s' (one of: %s)" % (phase, ", ".join(phases(state))))
    d = state["dir"]
    jobs = []
    if phase == "diverge" or phase.startswith("cross"):
        stage = 0 if phase == "diverge" else int(phase[5:])
        for m in sorted(state["members"]):
            jobs.append({"id": "%s.%s" % (m, phase), "kind": "diverge" if stage == 0 else "cross",
                         "phase": phase, "member": m, "stage": stage,
                         "outputs": [stage_file(d, m, stage)]})
    elif phase == "cluster":
        jobs.append({"id": "curator", "kind": "curator", "phase": phase, "outputs": [pool_out(d)]})
    elif phase == "score":
        if state["pool"] is not None:
            for j in active_judges(state):
                jobs.append({"id": j, "kind": "judge", "phase": phase, "judge": j,
                             "outputs": [score_out(d, j)]})
    elif phase in ("develop", "stress"):
        for cid in state["shortlist"] or []:
            out = develop_out(d, cid) if phase == "develop" else stress_out(d, cid)
            jobs.append({"id": "%s.%s" % (cid, phase), "kind": "developer" if phase == "develop" else "stress",
                         "phase": phase, "concept": cid, "outputs": [out]})
    for j in jobs:
        j["prompt"] = prompt_path(d, phase, j["id"])
    return jobs


def missing_jobs(jobs):
    return [j for j in jobs if not all(_has_output(p) for p in j["outputs"])]


def next_action(state):
    """(phase, jobs_left, jobs_total). phase is a phase name, 'collect', 'ended' or 'done'."""
    if state.get("ended"):
        return "ended", [], []
    for phase in phases(state):
        if phase == "score" and state["pool"] is None:
            return "collect", [], []
        if phase == "develop" and state["shortlist"] is None:
            return "collect", [], []
        jobs = phase_jobs(state, phase)
        left = missing_jobs(jobs)
        if left:
            return phase, left, jobs
    return "done", [], []


# ---------------------------------------------------------------- templates

_TEMPLATE_RE = re.compile(r"<!-- template:([a-z]+) -->\s*```text\n(.*?)\n```\s*<!-- /template:\1 -->", re.S)
_PLACEHOLDER_RE = re.compile(r"\{\{(\w+)\}\}")


def load_templates(path=PROMPTS_PATH):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    found = {m.group(1): m.group(2) for m in _TEMPLATE_RE.finditer(text)}
    missing = [t for t in TEMPLATES if t not in found]
    if missing:
        raise CouncilError("prompts.md is missing prompt templates: %s" % ", ".join(missing))
    known = set(CARD_FIELDS) | set(OPTIONAL_CARD_FIELDS)
    unknown = sorted(set(p for t in found.values() for p in _PLACEHOLDER_RE.findall(t)
                         if p.startswith(("lens_", "technique_")) and p not in known))
    if unknown:
        raise CouncilError("prompts.md uses card placeholders council.py does not fill: %s" % ", ".join(unknown))
    return found


def fill(template, values):
    """One pass, so a brief that itself contains {{braces}} is left exactly as written."""
    wanted = set(_PLACEHOLDER_RE.findall(template))
    missing = sorted(wanted - set(values))
    if missing:
        raise CouncilError("no value for placeholder(s): %s" % ", ".join(missing))
    return _PLACEHOLDER_RE.sub(lambda m: str(values[m.group(1)]), template)


def read_brief(state):
    with open(os.path.join(state["dir"], "brief.md"), encoding="utf-8") as fh:
        return fh.read().rstrip("\n")


def _bullets(paths):
    return "\n".join("- " + p for p in paths)


def concept(state, cid):
    for c in state["pool"] or []:
        if c["id"] == cid:
            return c
    raise CouncilError("no concept '%s' in the pool" % cid)


def _instruments(lens):
    """The lens's instruments as a card line, or nothing when the lens has none. When it has
    them, the member must work with them: a lens without method changes the words, not the work."""
    v = lens.get("instruments")
    if isinstance(v, (list, tuple)):
        v = "; ".join(str(x) for x in v)
    v = str(v or "").strip()
    if not v:
        return ""
    return ("\nYour instruments: %s\nWork with them, not only with the lens's vocabulary: get each idea by "
            "putting the brief through at least one of them, and say which instrument it came from." % v)


def render_job(state, job, templates, brief):
    d = state["dir"]
    v = {"brief": brief, "council_dir": d, "rubric": os.path.join(d, "rubric.md"),
         "n": state["members_n"], "out": job["outputs"][0]}
    kind = job["kind"]
    if kind in ("diverge", "cross"):
        m = job["member"]
        card = state["members"][m]["card"]
        v["member"] = m
        for ph, (part, field) in CARD_FIELDS.items():
            v[ph] = card[part][field]
        v["lens_instruments"] = _instruments(card["lens"])
        if kind == "cross":
            k = job["stage"]
            ps = partners(state, m, k)
            reads = []
            for p in ps:
                reads.append(stage_file(d, p, k - 1))
                if k - 1 > 0:
                    reads.append(stage_file(d, p, 0))
            v.update(round=k, own_file=stage_file(d, m, k - 1), partner_files=_bullets(reads),
                     partners=", ".join(ps))
            if k == state["cross"]:
                v["provocation"] = ("The facilitator's provocation for this round. Answer it with at least one "
                                    "build: \"%s\"" % card["provocation"]["text"])
            else:
                v["provocation"] = "No provocation this round."
    elif kind == "curator":
        v.update(idea_files=_bullets(all_idea_files(state)), pool_max=state["pool_max"], orphan_slots=ORPHAN_SLOTS,
                 member_list=", ".join(sorted(state["members"])))
    elif kind == "judge":
        crit = [k for k, _ in state["weights"]]
        v.update(judge=job["judge"], pool=pool_out(d), profile=state["rubric"],
                 criteria=", ".join("%s (%d)" % tuple(kv) for kv in state["weights"]),
                 score_fields=", ".join('"%s": 0' % k for k in crit),
                 concept_ids=", ".join(c["id"] for c in state["pool"]))
    elif kind in ("developer", "stress"):
        c = concept(state, job["concept"])
        srcs = sorted(set(stage_file(d, m, s) for m in c.get("members", []) if m in state["members"]
                          for s in range(0, state["cross"] + 1)))
        v.update(concept_id=c["id"], concept_title=c["title"], concept_pitch=c["pitch"],
                 parents=", ".join(c.get("parents", [])) or "none listed", source_files=_bullets(srcs) or "- none",
                 develop_file=develop_out(d, c["id"]))
    return fill(templates[kind], v)


def write_prompts(state, phase):
    if state.get("ended"):
        raise CouncilError("the run stopped: %s" % state["ended"])
    jobs = phase_jobs(state, phase)
    left = missing_jobs(jobs)
    if not left:
        return left
    templates = load_templates()
    brief = read_brief(state)
    for j in left:
        for p in j["outputs"] + [j["prompt"]]:
            os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(j["prompt"], "w", encoding="utf-8") as fh:
            fh.write(render_job(state, j, templates, brief) + "\n")
    return left


# ---------------------------------------------------------------- collect

def extract_json(text):
    text = text.strip()
    try:
        return json.loads(text)
    except ValueError:
        pass
    i, j = text.find("{"), text.rfind("}")
    if i != -1 and j > i:
        try:
            return json.loads(text[i:j + 1])
        except ValueError:
            return None
    return None


def _set_aside(path):
    os.replace(path, path + ".unreadable")


def _is_no_output(text):
    return text.strip().upper().startswith(NO_OUTPUT)


def _failed(state, job, path, no_output):
    """Count a failed attempt and set the file aside. NO OUTPUT means the orchestrator already
    ran the job twice. Returns True when the job is out of attempts."""
    f = state.setdefault("failures", {})
    f[job] = 2 if no_output else f.get(job, 0) + 1
    _set_aside(path)
    return f[job] >= 2


PARENT_RE = re.compile(r"^(m\d+)\.\S+$")


ORPHAN_SLOTS = 3


def parse_pool(state, data):
    """Concepts, plus up to ORPHAN_SLOTS orphans: single odd ideas the curator copies
    as written instead of folding them into a tamer concept."""
    if not isinstance(data, dict) or not isinstance(data.get("concepts"), list) or not data["concepts"]:
        raise CouncilError("pool.json needs a non-empty 'concepts' list")
    orphans = data.get("orphans") if isinstance(data.get("orphans"), list) else []
    items = [(c, False) for c in data["concepts"][:state["pool_max"]]] + \
        [(c, True) for c in orphans[:ORPHAN_SLOTS]]
    out, seen = [], set()
    for c, orphan in items:
        if not isinstance(c, dict):
            raise CouncilError("a concept is not a JSON object")
        cid = str(c.get("id") or "").strip().upper()
        if not re.match(r"^C\d+$", cid) or cid in seen:
            raise CouncilError("concept id '%s' is missing, malformed (want C01) or repeated" % cid)
        if not str(c.get("title") or "").strip() or not str(c.get("pitch") or "").strip():
            raise CouncilError("concept %s needs a title and a pitch" % cid)
        parents = [str(p).strip().lower() for p in c.get("parents") or []]
        for p in parents:
            if not PARENT_RE.match(p):
                raise CouncilError("concept %s: parent '%s' is not an idea id like m03.2 or m03.r1.4" % (cid, p))
        members = sorted(set(str(m).strip().lower() for m in (c.get("members") or [])) |
                         set(PARENT_RE.match(p).group(1) for p in parents))
        unknown = [m for m in members if m not in state["members"]]
        if unknown:
            raise CouncilError("concept %s cites member(s) %s, but the council is %s"
                               % (cid, ", ".join(unknown), ", ".join(sorted(state["members"]))))
        if not members:
            raise CouncilError("concept %s names no member and no parent idea: its lineage is lost" % cid)
        seen.add(cid)
        out.append({"id": cid, "title": str(c["title"]).strip(), "pitch": str(c["pitch"]).strip(),
                    "parents": parents, "members": members, "orphan": orphan})
    return out


def verdict_problems(state, v):
    """Why a judge's file cannot be counted: every pool concept, every criterion, a number
    from 0 to 10, and no ids outside the pool. Empty when it can."""
    if not isinstance(v, dict) or not isinstance(v.get("scores"), dict):
        return ["no 'scores' object"]
    scores = {str(k).strip().upper(): s for k, s in v["scores"].items()}
    ids = [c["id"] for c in state["pool"]]
    problems = []
    for cid in ids:
        s = scores.get(cid)
        if not isinstance(s, dict):
            problems.append("%s %s" % (cid, "not scored" if s is None else "is not an object of scores"))
            continue
        for key, _ in state["weights"]:
            val = s.get(key)
            if isinstance(val, bool) or not isinstance(val, (int, float)) or not 0 <= val <= 10:
                problems.append("%s '%s' is %s, not a number from 0 to 10" % (cid, key, json.dumps(val)))
    extra = sorted(set(scores) - set(ids))
    if extra:
        problems.append("ids not in the pool: %s" % ", ".join(extra))
    return problems


def weighted_total(scores, weights):
    if not isinstance(scores, dict):
        return None
    total = 0.0
    for key, weight in weights:
        v = scores.get(key)
        if isinstance(v, bool):
            return None
        try:
            v = float(v)
        except (TypeError, ValueError):
            return None
        total += max(0.0, min(10.0, v)) * weight
    return round(total / 10.0, 2)


def _truthy(v):
    if isinstance(v, str):
        return v.strip().lower() in ("true", "yes", "1")
    return bool(v)


def tally(state, verdicts):
    """Average the judges per concept, drop the majority off-brief ones, and take the
    top of the table. The last slot is the dissent slot: the concept one judge loved
    most that the average left out, when that judge's total beats the slot's average.
    Divisive ideas are where the novelty usually is."""
    table = {}
    keys = [k for k, _ in state["weights"]]
    nov_key = "novelty" if "novelty" in keys else keys[0]   # the tie-break, under every rubric
    for c in state["pool"]:
        totals, off, nov = [], 0, []
        for v in verdicts:
            s = (v.get("scores") or {}).get(c["id"])
            t = weighted_total(s, state["weights"])
            if t is None:
                continue
            totals.append(t)
            nov.append(float(s.get(nov_key, 0)))
            off += 1 if _truthy(s.get("off_brief")) else 0
        if not totals:
            continue
        table[c["id"]] = {"mean": round(sum(totals) / len(totals), 2), "max": max(totals),
                          "spread": round(max(totals) - min(totals), 2), "judges": len(totals),
                          "novelty": round(sum(nov) / len(nov), 2), "off_brief": off * 2 > len(totals)}
    eligible = sorted((cid for cid, r in table.items() if not r["off_brief"]),
                      key=lambda cid: (-table[cid]["mean"], -table[cid]["novelty"], cid))
    k = min(state["shortlist_n"], len(eligible))
    short = eligible[:k]
    if k >= 2:
        rest = [cid for cid in eligible if cid not in short]
        if rest:
            dissent = max(rest, key=lambda cid: (table[cid]["max"], table[cid]["spread"]))
            if table[dissent]["max"] > table[short[-1]]["mean"]:
                table[dissent]["dissent"] = True
                short[-1] = dissent
    return table, short


def _read(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def collect(state):
    """Read the pool or the judges' scores. Each result is (what, status, note); a status other
    than recorded, read or dropped means the step did not go through."""
    d = state["dir"]
    if state.get("ended"):
        return [("run", "stopped", state["ended"])]
    if state["pool"] is None:
        path = pool_out(d)
        if not _has_output(path):
            return [("pool", "missing", "")]
        text = _read(path)
        no_output = _is_no_output(text)
        if not no_output:
            data = extract_json(text)
            try:
                state["pool"] = parse_pool(state, data)
            except (CouncilError, D.DeckError) as e:
                note = str(e)
            else:
                cut = max(0, len(data["concepts"]) - state["pool_max"])
                note = "%d concepts" % len(state["pool"])
                if cut:
                    note += " (%d more were cut: the pool holds %d)" % (cut, state["pool_max"])
                return [("pool", "recorded", note)]
        else:
            note = "the curator wrote NO OUTPUT"
        if _failed(state, "curator", path, no_output):
            state["ended"] = ("the curator failed twice (%s). Without a pool there is nothing to score: "
                              "report the run as stopped and give the user the member files" % note)
            return [("pool", "failed", note)]
        return [("pool", "unreadable", note + ". Rerun the cluster phase once")]
    if state["shortlist"] is None:
        results, verdicts = [], []
        for j in judge_ids(state):
            if j in state.get("dropped", []):
                results.append((j, "dropped", "failed twice earlier"))
                continue
            path = score_out(d, j)
            if not _has_output(path):
                results.append((j, "missing", ""))
                continue
            text = _read(path)
            no_output = _is_no_output(text)
            v = None if no_output else extract_json(text)
            problems = ["the judge wrote NO OUTPUT"] if no_output else verdict_problems(state, v)
            if problems:
                note = "; ".join(problems[:6]) + (" (and %d more)" % (len(problems) - 6) if len(problems) > 6 else "")
                if _failed(state, j, path, no_output):
                    state.setdefault("dropped", []).append(j)
                    results.append((j, "dropped", note))
                else:
                    results.append((j, "rejected", note + ". Rerun this judge once"))
                continue
            v["scores"] = {str(k).strip().upper(): s for k, s in v["scores"].items()}
            verdicts.append(v)
            results.append((j, "read", "all %d concepts scored" % len(state["pool"])))
        if any(r[1] in ("missing", "rejected") for r in results):
            return results
        need = min(MIN_JUDGES, state["judges"])
        if len(verdicts) < need:
            state["ended"] = ("only %d of %d judges gave usable scores and the panel needs %d: report the run as "
                              "stopped, with the pool unscored" % (len(verdicts), state["judges"], need))
            results.append(("score", "failed", state["ended"]))
            return results
        table, short = tally(state, verdicts)
        if not short:
            raise CouncilError("no concept survived scoring (all off-brief?). Rerun cluster or narrow the brief")
        state["scores"], state["shortlist"] = table, short
        results.append(("shortlist", "recorded", "%s (every concept scored by %d of %d judges)"
                        % (", ".join(short), len(verdicts), state["judges"])))
        return results
    return []


# ---------------------------------------------------------------- io

def run_dir_from(args):
    if getattr(args, "dir", None):
        return os.path.abspath(args.dir)
    latest = os.path.join(ROOT, LATEST)
    if not os.path.isfile(latest):
        raise CouncilError("no council here: run init first, or pass --dir")
    with open(latest, encoding="utf-8") as fh:
        return os.path.abspath(os.path.join(ROOT, fh.read().strip()))


def load_state(args):
    d = run_dir_from(args)
    path = os.path.join(d, STATE_FILE)
    if not os.path.isfile(path):
        raise CouncilError("no %s in %s" % (STATE_FILE, d))
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def save_state(state):
    path = os.path.join(state["dir"], STATE_FILE)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2)
    os.replace(tmp, path)


def _cmd(*parts):
    return " ".join(["python3", '"%s"' % SELF] + list(parts))


def _card_line(card):
    return "%s (%s) + %s" % (card["lens"]["name"], card["lens"]["family"], card["technique"]["name"])


def _sizes(args):
    base = dict(DEFAULTS)
    if getattr(args, "quick", False):
        base.update(QUICK)
    for key in ("members", "cross", "judges", "shortlist", "parallel"):
        val = getattr(args, key, None)
        if val is not None:
            base[key] = val
    if base["members"] < MIN_MEMBERS:
        raise CouncilError("--members must be at least %d: the deal seats one lens from each of %s"
                           % (MIN_MEMBERS, ", ".join(D.REQUIRED_FAMILIES)))
    if base["parallel"] < 1:
        raise CouncilError("--parallel must be at least 1")
    if base["cross"] < 1:
        raise CouncilError("--cross must be at least 1: cross-pollination is the point of a council")
    if base["judges"] < 1 or base["shortlist"] < 1:
        raise CouncilError("--judges and --shortlist must be at least 1")
    return base


# ---------------------------------------------------------------- commands

def cmd_plan(args):
    s = _sizes(args)
    rows = plan_rows(s["members"], s["cross"], s["judges"], s["shortlist"])
    total = sum(n for _, n in rows)
    for name, n in rows:
        print("%-9s %3d call%s" % (name, n, "" if n == 1 else "s"))
    print("total     %3d sub-agent calls, at most %d in flight" % (total, s["parallel"]))
    print("summary: %d members, %d cross round%s, %d judges, %d on the shortlist, %d calls"
          % (s["members"], s["cross"], "" if s["cross"] == 1 else "s", s["judges"], s["shortlist"], total))


def cmd_deal(args):
    D.cmd_deal(args)


def cmd_presets(args):
    D.cmd_presets(args)


def _make_run_dir():
    """A new, empty run folder. Names are second-resolution timestamps, so a retry within the
    same second gets a suffix instead of failing."""
    os.makedirs(ROOT, exist_ok=True)
    base = time.strftime("%Y%m%d-%H%M%S")
    name, k = base, 2
    while True:
        try:
            os.makedirs(os.path.join(ROOT, name))
            return name
        except FileExistsError:
            name, k = "%s-%d" % (base, k), k + 1


def cmd_init(args):
    deck = load_deck()
    s = _sizes(args)
    if args.brief_file:
        with open(args.brief_file, encoding="utf-8") as fh:
            brief = fh.read()
    elif args.brief:
        brief = args.brief
    else:
        raise CouncilError("pass --brief-file or --brief")
    if not brief.strip():
        raise CouncilError("the brief is empty")
    seed = args.seed if args.seed is not None else random.randrange(1, 10 ** 6)
    explicit = D.parse_lens_spec(args.lenses, deck) if args.lenses else None
    check_deck(deck, explicit or ())
    # Fit the deck to the brief before dealing: Clef, else Jev, else BM25, else the whole pool (deck.py).
    full = deck
    deck, relevance = D.fit_deck(deck, brief, s["members"], mode=args.relevance, minimum=args.relevance_min,
                                 techniques=not args.no_technique, preset=args.preset, key=D._key(),
                                 cf_auth=D._cf(args.relevance))
    # Everything that can fail on bad input runs before the folder exists.
    state = new_state(s["members"], seed, deck, ".", s["cross"], s["judges"], s["shortlist"],
                      s["parallel"], args.preset, explicit, rubric=args.rubric, techniques=not args.no_technique)
    state["model"] = args.model
    state["phase_models"] = _parse_phase_models(args.phase_model, state)
    state["relevance"] = ({k: relevance.get(k) for k in ("method", "model", "minimum", "fallback", "notes")}
                          if relevance else None)
    name = _make_run_dir()
    run_dir = os.path.join(ROOT, name)
    state["dir"] = os.path.abspath(run_dir)
    try:
        if relevance:
            with open(os.path.join(run_dir, "relevance.json"), "w", encoding="utf-8") as fh:
                json.dump(relevance, fh, indent=1)
                fh.write("\n")
        with open(os.path.join(run_dir, "brief.md"), "w", encoding="utf-8") as fh:
            fh.write(brief.rstrip("\n") + "\n")
        with open(RUBRIC_PATH, encoding="utf-8") as src, \
                open(os.path.join(run_dir, "rubric.md"), "w", encoding="utf-8") as dst:
            dst.write(src.read())
        save_state(state)
    except BaseException:
        shutil.rmtree(run_dir, ignore_errors=True)
        raise
    with open(os.path.join(ROOT, LATEST), "w", encoding="utf-8") as fh:
        fh.write(name + "\n")
    total = sum(n for _, n in plan_rows(s["members"], s["cross"], s["judges"], s["shortlist"]))
    print("council %s: %d members, seed %s, %s rubric, %d calls"
          % (state["dir"], s["members"], seed, state["rubric"], total))
    print("models: %s" % _models_line(state))
    for line in D.report_lines(relevance, full):
        print(line)
    for m in sorted(state["members"]):
        print("  %s  %s" % (m, _card_line(state["members"][m]["card"])))
    print("next: %s" % _cmd("next"))


def _parse_phase_models(spec, state):
    out = {}
    for part in [x.strip() for x in (spec or "").split(",") if x.strip()]:
        phase, _, model = part.partition("=")
        phase, model = phase.strip(), model.strip()
        known = ["diverge", "cross", "cluster", "score", "develop", "stress"]
        if phase not in known or not model:
            raise CouncilError("--phase-model wants phase=model with a phase from %s, not '%s'"
                               % (", ".join(known), part))
        out[phase] = model
    return out


def phase_model(state, phase):
    """The model for a phase's sub-agents: an override, else the fast tier for research, else the session's."""
    key = "cross" if phase.startswith("cross") else phase
    over = (state.get("phase_models") or {}).get(key)
    if over:
        return over
    if key in RESEARCH_PHASES:
        return RESEARCH_MODEL
    return state.get("model") or SESSION_MODEL


def _models_line(state):
    order = ["diverge", "cross", "cluster", "score", "develop", "stress"]
    return ", ".join("%s %s" % (p, phase_model(state, p)) for p in order)


def cmd_next(args):
    state = load_state(args)
    phase, left, jobs = next_action(state)
    if phase == "ended":
        print("STOPPED: %s" % state["ended"])
        return 1
    if phase == "done":
        print("DONE. Run %s, then read the develop and stress files it lists." % _cmd("harvest"))
    elif phase == "collect":
        print("collect: %s" % _cmd("collect"))
    else:
        print("phase %s: %d of %d jobs left" % (phase, len(left), len(jobs)))
        print("run: %s" % _cmd("prompts", phase))
    return 0


def cmd_prompts(args):
    state = load_state(args)
    left = write_prompts(state, args.phase)
    if not left:
        print("nothing left in %s. %s" % (args.phase, _cmd("next")))
        return
    print("%d job%s in %s. Keep at most %d in flight; launch the next as each finishes."
          % (len(left), "" if len(left) == 1 else "s", args.phase, state["parallel"]))
    print("Each: one general sub-agent, model %s, description 'council <job>', "
          "prompt 'Read <prompt file>: it is your whole brief.' (Tool and tier names per harness: %s)"
          % (phase_model(state, args.phase), os.path.join(os.path.dirname(HERE), "heavy-think", "references", "harness.md")))
    for j in left:
        print("  %-18s %s" % (j["id"], j["prompt"]))


def cmd_check(args):
    state = load_state(args)
    jobs = phase_jobs(state, args.phase)
    left = missing_jobs(jobs)
    print("%s: %d of %d done" % (args.phase, len(jobs) - len(left), len(jobs)))
    for j in left:
        for p in j["outputs"]:
            if not _has_output(p):
                print("  missing %s (%s)" % (p, j["id"]))


def cmd_collect(args):
    state = load_state(args)
    results = collect(state)
    save_state(state)
    if not results:
        print("nothing to collect")
    for what, status, note in results:
        print("%-10s %-10s %s" % (what, status, note))
    print("next: %s" % _cmd("next"))
    return 0 if all(st in ("recorded", "read", "dropped") for _, st, _ in results) else 1


def cmd_status(args):
    state = load_state(args)
    print("council %s, seed %s, %d members" % (state["dir"], state["seed"], state["members_n"]))
    print("models: %s" % _models_line(state))
    if state.get("ended"):
        print("STOPPED: %s" % state["ended"])
    for phase in phases(state):
        try:
            jobs = phase_jobs(state, phase)
        except CouncilError:
            jobs = []
        if not jobs:
            print("  %-9s waiting" % phase)
            continue
        done = len(jobs) - len(missing_jobs(jobs))
        print("  %-9s %d/%d" % (phase, done, len(jobs)))
    if state["pool"] is not None:
        print("pool: %d concepts" % len(state["pool"]))
    if state["shortlist"]:
        print("shortlist: %s" % ", ".join(state["shortlist"]))


def cmd_harvest(args):
    state = load_state(args)
    if not state["shortlist"]:
        raise CouncilError("no shortlist yet: %s" % _cmd("next"))
    members = state["members"]
    table = state["scores"] or {}
    print("SHORTLIST")
    for cid in state["shortlist"]:
        c = concept(state, cid)
        r = table.get(cid, {})
        lenses = ", ".join("%s %s" % (m, members[m]["card"]["lens"]["name"]) for m in c["members"]) or "?"
        tag = "  [dissent slot: one judge scored it %s]" % r.get("max") if r.get("dissent") else ""
        tag += "  [orphan: one member's idea, kept as written]" if c.get("orphan") else ""
        print("\n%s  %s  mean %s, spread %s, %s of %d judges%s"
              % (cid, c["title"], r.get("mean"), r.get("spread"), r.get("judges"), state["judges"], tag))
        print("  pitch: %s" % c["pitch"])
        print("  lineage: %s" % (", ".join(c["parents"]) or "none"))
        print("  lenses: %s" % lenses)
        print("  read: %s" % develop_out(state["dir"], cid))
        print("        %s" % stress_out(state["dir"], cid))
    rest = sorted((cid for cid in table if cid not in state["shortlist"]),
                  key=lambda cid: -table[cid]["mean"])
    if rest:
        print("\nREST OF THE POOL")
        for cid in rest:
            r = table[cid]
            flag = " OFF-BRIEF" if r["off_brief"] else ""
            print("  %s  %-6s spread %-6s %s of %d judges  %s%s"
                  % (cid, r["mean"], r["spread"], r["judges"], state["judges"], concept(state, cid)["title"], flag))
    print("\nrun folder: %s" % state["dir"])


def cmd_card(args):
    state = load_state(args)
    m = args.member.strip().lower()
    if m not in state["members"]:
        raise CouncilError("no member '%s'" % m)
    c = state["members"][m]["card"]
    print("%s: %s" % (m, _card_line(c)))
    print("  asks: %s" % c["lens"]["asks"])
    print("  technique: %s" % c["technique"]["how"])
    print("  provocation: %s" % c["provocation"]["text"])


def build_parser():
    p = argparse.ArgumentParser(prog="council.py", description="state machine for /council full mode")
    sub = p.add_subparsers(dest="cmd", required=True)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--dir", help="run folder (default: .council/LATEST)")
    sizes = argparse.ArgumentParser(add_help=False)
    sizes.add_argument("--members", type=int)
    sizes.add_argument("--cross", type=int, help="cross-pollination rounds")
    sizes.add_argument("--judges", type=int)
    sizes.add_argument("--shortlist", type=int)
    sizes.add_argument("--parallel", type=int, help="sub-agents in flight at once")
    sizes.add_argument("--quick", action="store_true", help="5 members, 1 cross round, 2 judges, 3 shortlisted")

    sub.add_parser("plan", parents=[sizes], help="calls per phase")
    s = sub.add_parser("deal", help="deal cards without starting a run (live council)")
    s.add_argument("--members", type=int, default=4)
    s.add_argument("--preset")
    s.add_argument("--lenses", help="deck ids and/or custom 'Name: question'")
    s.add_argument("--no-technique", action="store_true")
    s.add_argument("--seed")
    D.add_relevance_args(s)
    sub.add_parser("presets", help="list preset lens sets")
    s = sub.add_parser("init", parents=[sizes], help="deal the cards and write council.json")
    s.add_argument("--brief-file")
    s.add_argument("--brief")
    s.add_argument("--preset")
    s.add_argument("--lenses", help="deck ids and/or custom 'Name: question'")
    s.add_argument("--rubric", choices=("creative", "decision"), help="default: the preset's, else creative")
    s.add_argument("--no-technique", action="store_true", help="lenses only")
    s.add_argument("--seed")
    s.add_argument("--model", help="the session's model, for the judgment phases (diverge, cross, cluster, "
                                   "score); printed with every phase")
    s.add_argument("--phase-model", help="overrides as phase=model,... (default: develop and stress on %s)"
                   % RESEARCH_MODEL)
    s.add_argument("--relevance", choices=("auto", "clef", "jev", "bm25", "off"), default="auto",
                   help="fit the deck to the brief first: auto (default) uses Clef if Cloudflare is logged "
                        "in, else Jev if TYPESAFE_API_KEY is set, else BM25. clef / jev: that one or fail. "
                        "bm25: BM25 only. off: the whole deck")
    s.add_argument("--relevance-min", type=float, default=None,
                   help="the bar an entry must clear (default %g for Clef, %g otherwise)"
                        % (D.CLEF_MIN, D.RELEVANCE_MIN))
    sub.add_parser("next", parents=[common], help="what to do now")
    for name in ("prompts", "check"):
        s = sub.add_parser(name, parents=[common])
        s.add_argument("phase")
    sub.add_parser("collect", parents=[common], help="read the pool or the scores")
    sub.add_parser("status", parents=[common])
    sub.add_parser("harvest", parents=[common], help="shortlist, scores, lineage")
    s = sub.add_parser("card", parents=[common])
    s.add_argument("member")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    handler = globals()["cmd_" + args.cmd]
    try:
        return handler(args) or 0
    except (CouncilError, D.DeckError) as e:
        print("council: %s" % e, file=sys.stderr)
    except OSError as e:
        print("council: %s: %s" % (e.strerror or e, e.filename or ""), file=sys.stderr)
    except json.JSONDecodeError as e:   # a council.json or deck that is not JSON
        print("council: not valid JSON: %s" % e, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
