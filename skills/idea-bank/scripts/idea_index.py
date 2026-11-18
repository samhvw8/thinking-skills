# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6"]
# ///
"""Index an idea bank: links, convergence, migration-gap candidates, cuts, known-bricks coverage.

Usage: uv run idea_index.py <bank-root> [--json out.json] [--suggest-merges] [--write | --check | --cuts | --recuts]

Deterministic and offline. Gap candidates are a list for judgement, not findings.
The Cuts report checks every `cut` label against the cut registry (references/cuts.json, built from the
repo's decks) and the labels already in the bank, and lists near-duplicate labels. The Re-cuts report shows,
per unit with two or more cuts, the parts each cut shares with the others and flags a later cut that only
re-tags an earlier one.
--write also puts a `# Cuts compared` table on every card whose method brick has two or more cuts.
--write regenerates the views made from frontmatter (including `parts` and `links`): a `# Related` section in every
brick, card, lens and move, and `bricks/index.md`. It also moves a frontmatter
`signature` into the body. --check exits 1 when any of these is out of date.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

RESERVED = {"index.md", "log.md"}
FM_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", re.S)


def as_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return [v for v in value if v is not None]
    return [value]


def load(root: Path) -> list[dict]:
    """Parse every concept under root. A file with broken frontmatter is an error, not skipped."""
    concepts, errors = [], []
    for path in sorted(root.rglob("*.md")):
        if path.name in RESERVED:
            continue
        text = path.read_text(encoding="utf-8")
        m = FM_RE.match(text)
        if not m:
            errors.append(f"{path.relative_to(root)}: no frontmatter")
            continue
        try:
            fm = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError as e:
            errors.append(f"{path.relative_to(root)}: bad YAML ({e.__class__.__name__})")
            continue
        if not isinstance(fm, dict) or not fm.get("type"):
            errors.append(f"{path.relative_to(root)}: missing type")
            continue
        concepts.append({"slug": path.stem, "path": str(path.relative_to(root)), "fm": fm, "body": m.group(2)})
    if errors:
        raise SystemExit("idea_index: cannot parse bank:\n  " + "\n  ".join(errors))
    return concepts


UNIT_TYPES = {"brick": "Brick", "lens": "Lens", "card": "Idea Card"}  # bare slugs resolve in this order
UNLABELLED = "unlabelled"  # the cut of a `parts` entry that names none (older banks); not a preferred view
CUTS_FILE = Path(__file__).resolve().parent.parent / "references" / "cuts.json"


def load_registry(path: Path = CUTS_FILE) -> dict[str, str]:
    """Cut kinds: {id: how to cut} from the built registry (decompositions + idea cuts). Missing or clashing ids crash."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise SystemExit(f"idea_index: cannot read the cut registry {path}: {e}")
    reg: dict[str, str] = {}
    for key in ("decompositions", "cuts"):
        for e in data.get(key) or []:
            if e["id"] in reg:
                raise SystemExit(f"idea_index: cut registry id '{e['id']}' appears twice")
            reg[e["id"]] = e.get("how") or e.get("name") or e["id"]
    if not reg:
        raise SystemExit(f"idea_index: the cut registry {path} is empty")
    return reg


def unit_graph(concepts: list[dict]) -> dict:
    """`parts` (split / bind) and `links` (connect without merging) across bricks, lenses and cards.

    Each `parts` entry belongs to a cut: the kind of cut it was split by or bound under (`cut`, else
    `unlabelled`). A unit may hold several cuts side by side. `how: bind` marks a whole made by
    binding existing bricks (tape); `split` marks parts found by cutting (scissors): one record, two
    directions. Depth is relative and computed: a unit with no parts is 0, a whole is 1 + its deepest
    part over all cuts. Nothing stores a level name, so a unit split further later needs no relabelling.
    """
    live = {f"{k}:{c['slug']}": c for c in concepts for k, t in UNIT_TYPES.items()
            if c["fm"]["type"] == t and c["fm"].get("status") != "deprecated"}

    def resolve(ref) -> str | None:
        ref = str(ref)
        if ":" in ref:
            return ref if ref in live else None
        return next((f"{k}:{ref}" for k in UNIT_TYPES if f"{k}:{ref}" in live), None)

    parts: dict[str, list[str]] = {}  # whole -> distinct parts over all cuts (depth uses this)
    part_cuts: dict[str, dict[str, list[str]]] = {}  # whole -> cut -> parts, in frontmatter order
    cut_how: dict[str, dict[str, dict[str, str]]] = {}  # whole -> cut -> part -> "how: note"
    cut_group: dict[str, dict[str, dict[str, str]]] = {}  # whole -> cut -> part -> its place in that cut
    part_of: dict[str, set[str]] = defaultdict(set)
    part_of_cuts: dict[str, dict[str, list[str]]] = defaultdict(dict)  # part -> whole -> cuts it is in
    binds: dict[str, list[str]] = {}  # whole -> cuts that hold a `how: bind` entry
    cut_entries: list[tuple[str, str]] = []  # (whole, cut) for every resolved entry, for the Cuts report
    links, broken = [], []
    for key, c in sorted(live.items()):
        ps, cuts = [], {}
        for entry in as_list(c["fm"].get("parts")):
            entry = entry if isinstance(entry, dict) else {"to": entry}
            ref = entry.get("to", "")
            cut = str(entry.get("cut") or UNLABELLED)
            r = resolve(ref)
            if r:
                if r not in ps:
                    ps.append(r)
                if r in cuts.setdefault(cut, []):
                    continue  # the same part twice in one cut counts once; the first entry wins
                cuts[cut].append(r)
                cut_entries.append((key, cut))
                part_of[r].add(key)
                part_of_cuts[r].setdefault(key, []).append(cut)
                if entry.get("group"):
                    cut_group.setdefault(key, {}).setdefault(cut, {})[r] = str(entry["group"])
                if entry.get("how"):
                    how = str(entry["how"]) + (f": {entry['note']}" if entry.get("note") else "")
                    cut_how.setdefault(key, {}).setdefault(cut, {})[r] = how
                    if str(entry["how"]) == "bind" and cut not in binds.setdefault(key, []):
                        binds[key].append(cut)
            else:
                broken.append({"from": key, "to": f"part:{ref}"})
        if ps:
            parts[key] = ps
            part_cuts[key] = cuts
        for l in as_list(c["fm"].get("links")):
            l = l if isinstance(l, dict) else {"to": l}
            to = resolve(l.get("to", ""))
            if not to:
                broken.append({"from": key, "to": f"link:{l.get('to')}"})
                continue
            via = resolve(l["via"]) if l.get("via") else None
            if l.get("via") and not via:
                broken.append({"from": key, "to": f"via:{l['via']}"})
            links.append({"a": key, "b": to, "via": via, "note": l.get("note", "")})

    depth: dict[str, int] = {}
    cycles: list[list[str]] = []
    open_: set[str] = set()

    def visit(k: str, stack: list[str]) -> int:
        if k in depth:
            return depth[k]
        if k in open_:
            cyc = stack[stack.index(k):]
            if sorted(cyc) not in [sorted(c) for c in cycles]:
                cycles.append(cyc)
            return 0
        open_.add(k)
        stack.append(k)
        d = 1 + max((visit(p, stack) for p in parts.get(k, [])), default=-1)
        stack.pop()
        open_.discard(k)
        depth[k] = d
        return d

    for k in sorted(set(parts) | set(part_of)):
        visit(k, [])
    return {"parts": parts, "part_cuts": part_cuts, "cut_how": cut_how, "cut_group": cut_group, "binds": binds,
            "part_of": {k: sorted(v) for k, v in sorted(part_of.items())},
            "part_of_cuts": {k: dict(sorted(v.items())) for k, v in sorted(part_of_cuts.items())},
            "cut_entries": cut_entries,
            "depth": dict(sorted(depth.items())), "part_cycles": cycles, "unit_links": links, "broken": broken}


def brick_fields(fm: dict, moved: dict[str, set[str]] | None = None, slug: str | None = None) -> set[str]:
    """Fields a brick has reached: declared, migration rows, names, and migrate-brick moves."""
    fields = set(as_list(fm.get("fields")))
    if moved and slug:
        fields |= moved.get(slug, set())
    fields |= {m.get("field") for m in as_list(fm.get("migrations")) if isinstance(m, dict) and m.get("field")}
    fields |= set((fm.get("names") or {}).keys()) if isinstance(fm.get("names"), dict) else set()
    return fields


def brick_roles(fm: dict) -> set[str]:
    roles = set(as_list(fm.get("roles")))
    roles |= {m.get("role") for m in as_list(fm.get("migrations")) if isinstance(m, dict) and m.get("role")}
    return roles


def parse_known_bricks(body: str) -> dict[str, str]:
    """Read the table rows `| slug | seen/owned | ... |` from me/known-bricks.md."""
    known = {}
    for line in body.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and cells[1].lower() in {"seen", "owned"}:
            known[cells[0].strip("`")] = cells[1].lower()
    return known


def table_rows(body: str, section: str) -> list[dict[str, str]]:
    """Rows of the first markdown table under `# <section>`, keyed by lower-case header."""
    lines, inside = body.splitlines(), False
    rows, header = [], None
    for line in lines:
        if line.startswith("# "):
            if inside and header:
                break
            inside = line[2:].strip().lower() == section.lower()
            continue
        if not inside or not line.strip().startswith("|"):
            if inside and header and not line.strip():
                break
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cells]
        elif not set("".join(cells)) <= set("-: "):
            rows.append(dict(zip(header, cells)))
    return rows


STOP = {"to", "the", "a", "an", "of", "by", "and", "for", "in", "on", "with", "from", "into", "as", "at"}


def tokens(tag: str) -> set[str]:
    return {t for t in tag.lower().split("-") if t and t not in STOP}


def suggest_merges(concepts: list[dict], min_jaccard: float = 0.5, min_ratio: float = 0.85) -> list[dict]:
    """Near-duplicate role tags and tensions, for an LLM to confirm. Deterministic."""
    uses: dict[str, set[str]] = defaultdict(set)      # tag -> where it is used (kind:slug)
    filled_by: dict[str, set[str]] = defaultdict(set)  # tag -> bricks that fill it
    for c in concepts:
        fm, slug, t = c["fm"], c["slug"], c["fm"]["type"]
        if t == "Idea Card":
            for tag in as_list(fm.get("roles")):
                uses[tag].add(f"card-role:{slug}")
            for tag in as_list(fm.get("tensions")):
                uses[tag].add(f"tension:{slug}")
        elif t == "Brick" and fm.get("status") != "deprecated":
            for tag in brick_roles(fm):
                uses[tag].add(f"brick:{slug}")
                filled_by[tag].add(slug)
        elif t == "Move" and fm.get("role"):
            uses[fm["role"]].add(f"move:{slug}")
    tags = sorted(uses)
    out = []
    for i, a in enumerate(tags):
        ta = tokens(a)
        for b in tags[i + 1:]:
            tb = tokens(b)
            jac = len(ta & tb) / len(ta | tb) if ta | tb else 0.0
            ratio = difflib.SequenceMatcher(None, a, b).ratio()
            shared = sorted(filled_by[a] & filled_by[b])
            if jac >= min_jaccard or ratio >= min_ratio or (shared and jac > 0):
                out.append({"a": a, "b": b, "jaccard": round(jac, 2), "ratio": round(ratio, 2),
                            "shared_bricks": shared, "uses_a": len(uses[a]), "uses_b": len(uses[b])})
    out.sort(key=lambda r: (-(len(r["shared_bricks"]) > 0), -r["jaccard"], -r["ratio"], r["a"], r["b"]))
    return out


SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CUT_LINE_RE = re.compile(r"^Cut:\s*`?([^`\s]+)`?", re.M)


def recipe(body: str) -> tuple[str | None, list[str]]:
    """The `Cut:` label and the brick slugs of a card's `# Recipe ...` section (cells that are not slugs are skipped)."""
    cut, rows = recipe_roles(body)
    return cut, list(rows)


def recipe_roles(body: str) -> tuple[str | None, dict[str, str]]:
    """The `Cut:` label and {brick slug: Role cell} of a card's `# Recipe ...` section, in table order."""
    text, inside = [], False
    for line in body.splitlines():
        if line.startswith("# "):
            if inside:
                break
            inside = line[2:].strip().lower().startswith("recipe")
            continue
        if inside:
            text.append(line)
    section = "\n".join(text)
    m = CUT_LINE_RE.search(section)
    slugs, header = {}, None
    for line in section.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if set("".join(cells)) <= set("-: "):
            continue
        col = next((i for i, h in enumerate(header) if h.startswith("brick")), None)
        rcol = next((i for i, h in enumerate(header) if h.startswith("role")), None)
        cell = cells[col].strip("` ") if col is not None and col < len(cells) else ""
        if SLUG_RE.match(cell) and cell not in slugs:
            slugs[cell] = cells[rcol] if rcol is not None and rcol < len(cells) else ""
    return (m.group(1) if m else None), slugs


def cut_tokens(label: str) -> set[str]:
    return {t for t in label.lower().split("-") if t and t not in STOP | {"vs", "by"}}


def cut_report(g: dict, registry: dict[str, str]) -> dict:
    """Cut labels in use, which are registry kinds, and near-duplicate labels (a list for judgement)."""
    wholes: dict[str, set[str]] = defaultdict(set)
    entries: dict[str, int] = defaultdict(int)
    for whole, cut in g["cut_entries"]:
        wholes[cut].add(whole)
        entries[cut] += 1
    unlabelled = sorted(wholes.pop(UNLABELLED, set()))
    entries.pop(UNLABELLED, None)
    labels = {c: {"wholes": len(ws), "parts": entries[c], "registry": c in registry}
              for c, ws in sorted(wholes.items())}
    near = []
    pool = sorted(set(labels) | set(registry))
    for i, a in enumerate(pool):
        for b in pool[i + 1:]:
            if a in registry and b in registry:
                continue  # registry kinds are distinct on purpose
            if a not in labels and b not in labels:
                continue
            shared = sorted(cut_tokens(a) & cut_tokens(b))
            ratio = difflib.SequenceMatcher(None, a, b).ratio()
            if shared or ratio >= 0.8:
                near.append({"a": a, "b": b, "shared": shared, "ratio": round(ratio, 2)})
    return {"registry": sorted(registry), "labels": labels,
            "unregistered": sorted(c for c in labels if c not in registry),
            "unlabelled_wholes": unlabelled, "near_duplicates": near,
            "binds": {w: cs for w, cs in sorted(g["binds"].items())}}


def recut_report(g: dict) -> list[dict]:
    """Per whole with two or more cuts: the parts each cut shares with every other cut, and re-tags.

    Cuts are taken in the order they first appear in `parts`. A later cut draws a new boundary when it
    has a part no earlier cut has (a split piece, a bound whole, an added piece) or cuts one of its parts
    again under the same label. A later cut whose parts are all parts of one earlier cut, with neither of
    those, only re-tags that cut: flag it (record the angle as a note on the brick, not as a cut).
    """
    out = []
    for whole, cuts in g["part_cuts"].items():
        if len(cuts) < 2:
            continue
        names, rows = list(cuts), []
        for i, c in enumerate(names):
            mine = cuts[c]
            overlap = {}
            for o in names:
                if o != c:
                    shared = [p for p in mine if p in cuts[o]]
                    overlap[o] = {"shared": len(shared), "of": len(mine), "pct": round(100 * len(shared) / len(mine))}
            earlier = {p for o in names[:i] for p in cuts[o]}
            new = [p for p in mine if p not in earlier] if i else []
            recut = [p for p in mine if c in g["part_cuts"].get(p, {})] if i else []
            retag = [o for o in names[:i] if set(mine) <= set(cuts[o])] if not (new or recut) else []
            rows.append({"cut": c, "parts": len(mine), "new_parts": new, "parts_cut_again": recut,
                         "overlap": overlap, "retag_of": retag, "no_new_boundary": bool(i) and not (new or recut)})
        out.append({"whole": whole, "cuts": rows})
    return out


def build(concepts: list[dict], registry: dict[str, str] | None = None) -> dict:
    registry = load_registry() if registry is None else registry
    by_type: dict[str, dict[str, dict]] = defaultdict(dict)
    for c in concepts:
        by_type[c["fm"]["type"]][c["slug"]] = c
    bricks = {s: c["fm"] for s, c in by_type["Brick"].items() if c["fm"].get("status") != "deprecated"}
    cards = {s: c["fm"] for s, c in by_type["Idea Card"].items()}
    moves = {s: c["fm"] for s, c in by_type["Move"].items()}
    readings = by_type["Reading"]

    moved: dict[str, set[str]] = defaultdict(set)
    migrate_moves = []
    for ms, fm in sorted(moves.items()):
        if fm.get("move_type") == "migrate-brick" and fm.get("brick"):
            if fm.get("to_field"):
                moved[fm["brick"]].add(fm["to_field"])
            migrate_moves.append({"move": ms, "brick": fm["brick"], "from_field": fm.get("from_field"), "to_field": fm.get("to_field")})

    def fields_of(slug: str) -> set[str]:
        return brick_fields(bricks[slug], moved, slug)

    def card_bricks(fm: dict) -> list[str]:
        """The card's `bricks` plus its `method` brick (the whole the cuts hang on), each once."""
        out = list(dict.fromkeys(as_list(fm.get("bricks"))))
        if fm.get("method") and fm["method"] not in out:
            out.append(fm["method"])
        return out

    broken, one_way = [], []
    for cs, fm in cards.items():
        for a in card_bricks(fm):
            if a not in bricks:
                broken.append({"from": f"card:{cs}", "to": f"brick:{a}"})
            elif cs not in as_list(bricks[a].get("cards")):
                one_way.append({"from": f"card:{cs}", "to": f"brick:{a}"})
        for mv in as_list(fm.get("moves")):
            if mv not in moves:
                broken.append({"from": f"card:{cs}", "to": f"move:{mv}"})
    for a, fm in bricks.items():
        for cs in as_list(fm.get("cards")):
            if cs not in cards:
                broken.append({"from": f"brick:{a}", "to": f"card:{cs}"})
    for ms, fm in moves.items():
        for key in ("from_brick", "to_brick", "brick"):
            if fm.get(key) and fm[key] not in bricks:
                broken.append({"from": f"move:{ms}", "to": f"brick:{fm[key]}"})

    links = {a: sorted(set(as_list(fm.get("cards"))) | {cs for cs, cfm in cards.items() if a in card_bricks(cfm)})
             for a, fm in bricks.items()}
    by_field_count = sorted(({"brick": a, "fields": sorted(fields_of(a))} for a in bricks),
                            key=lambda r: (-len(r["fields"]), r["brick"]))

    role_bricks: dict[str, list[str]] = defaultdict(list)
    for a, fm in bricks.items():
        for r in brick_roles(fm):
            role_bricks[r].append(a)
    convergence = []
    for role, members in sorted(role_bricks.items()):
        members = sorted(members)
        unrelated = [(x, y) for i, x in enumerate(members) for y in members[i + 1:]
                     if not (fields_of(x) & fields_of(y))]
        if unrelated:
            convergence.append({"role": role, "bricks": members,
                                "fields": {m: sorted(fields_of(m)) for m in members},
                                "unrelated_pairs": [list(p) for p in unrelated]})

    slot_moves: dict[str, list[str]] = defaultdict(list)
    for ms, fm in moves.items():
        if fm.get("move_type") == "substitute-brick" and fm.get("role"):
            slot_moves[fm["role"]].append(ms)
    hot_slots = [{"role": r, "moves": sorted(ms)} for r, ms in sorted(slot_moves.items()) if len(ms) >= 2]

    gaps = []
    for cs, fm in sorted(cards.items()):
        field = fm.get("field")
        tensions = set(as_list(fm.get("tensions")))
        if not field or not tensions:
            continue
        for a, afm in sorted(bricks.items()):
            matched = sorted(brick_roles(afm) & tensions)
            if matched and field not in fields_of(a):
                gaps.append({"brick": a, "card": cs, "field": field, "roles": matched,
                             "brick_fields": sorted(fields_of(a))})

    low_confidence = [{"brick": a, "field": m.get("field"), "source": m.get("source"), "role": m.get("role")}
                      for a, fm in sorted(bricks.items()) for m in as_list(fm.get("migrations"))
                      if isinstance(m, dict) and str(m.get("match_confidence", "")).lower() == "low"]

    constraints: dict[str, list[str]] = defaultdict(list)
    evidence_limits: dict[str, list[str]] = defaultdict(list)
    for cs, fm in sorted(cards.items()):
        for c in as_list(fm.get("constraints")):
            constraints[c].append(cs)
        for c in as_list(fm.get("evidence_limits")):
            evidence_limits[c].append(cs)

    hints = []
    for rs, c in sorted(readings.items()):
        rows = table_rows(c["body"], "Notes")
        hints.append({"reading": rs, "mode": c["fm"].get("mode"),
                      "level3_hints": sum(1 for r in rows if r.get("hint", "").strip() == "3"),
                      "notes": len(rows)})

    known_state = by_type["State"].get("known-bricks")
    known = parse_known_bricks(known_state["body"]) if known_state else {}
    coverage = {
        "owned": sorted(k for k, v in known.items() if v == "owned"),
        "seen": sorted(k for k, v in known.items() if v == "seen"),
        "unknown_slugs": sorted(k for k in known if k not in bricks),
        "bank_bricks": len(bricks),
        "owned_share": round(sum(1 for k, v in known.items() if v == "owned" and k in bricks) / len(bricks), 3) if bricks else 0.0,
    }

    g = unit_graph(concepts)
    broken += g["broken"]

    # The card points to its method brick; the Recipe table renders one named cut of it.
    old_shape, recipe_drift = [], []
    for cs, c in sorted(by_type["Idea Card"].items()):
        method = c["fm"].get("method")
        if not method:
            old_shape.append(cs)
            continue
        if method not in bricks:
            continue  # reported as a broken link above
        cut, rows = recipe(c["body"])
        have = [p.split(":", 1)[1] for p in g["part_cuts"].get(f"brick:{method}", {}).get(cut or "", [])]
        if cut is None or set(rows) != set(have):
            recipe_drift.append({"card": cs, "method": method, "cut": cut,
                                 "only_in_recipe": sorted(set(rows) - set(have)),
                                 "only_in_parts": sorted(set(have) - set(rows))})

    return {
        "counts": {t: len(v) for t, v in sorted(by_type.items())},
        "parts": g["parts"],
        "part_cuts": g["part_cuts"],
        "cut_how": {w: {c: {p: h.split(":", 1)[0] for p, h in d.items()} for c, d in cs.items()}
                    for w, cs in g["cut_how"].items()},
        "part_of": g["part_of"],
        "part_of_cuts": g["part_of_cuts"],
        "cuts": cut_report(g, registry),
        "recuts": recut_report(g),
        "cards_without_method": old_shape,
        "recipe_drift": recipe_drift,
        "depth": g["depth"],
        "part_cycles": g["part_cycles"],
        "unit_links": g["unit_links"],
        "fields": sorted({f for a in bricks for f in fields_of(a)} | {fm.get("field") for fm in cards.values() if fm.get("field")}),
        "links": links,
        "broken_links": broken,
        "one_way_links": one_way,
        "bricks_by_field_count": by_field_count,
        "convergence": convergence,
        "hot_slots": hot_slots,
        "migration_gap_candidates": gaps,
        "migrate_brick_moves": migrate_moves,
        "low_confidence_matches": low_confidence,
        "constraints": dict(sorted(constraints.items())),
        "evidence_limits": dict(sorted(evidence_limits.items())),
        "reading_hints": hints,
        "known_bricks": coverage,
    }


def render(ix: dict) -> str:
    out = ["# Idea index", "", "Counts: " + (", ".join(f"{k} {v}" for k, v in ix["counts"].items()) or "empty bank"), ""]
    out += ["Fields: " + (", ".join(ix["fields"]) or "none"), ""]
    out += ["## Broken links"] + ([f"- {b['from']} -> {b['to']}" for b in ix["broken_links"]] or ["- none"]) + [""]
    out += ["## One-way links (brick does not list the card)"] + ([f"- {b['from']} -> {b['to']}" for b in ix["one_way_links"]] or ["- none"]) + [""]
    out += ["## Bricks by field count"] + ([f"- {r['brick']}: {len(r['fields'])} ({', '.join(r['fields'])})" for r in ix["bricks_by_field_count"]] or ["- none"]) + [""]
    out += ["## Convergence"] + ([f"- {c['role']}: {', '.join(c['bricks'])}" for c in ix["convergence"]] or ["- none"]) + [""]
    out += ["## Hot slots"] + ([f"- {h['role']}: {len(h['moves'])} substitutions ({', '.join(h['moves'])})" for h in ix["hot_slots"]] or ["- none"]) + [""]
    out += ["## Migration-gap candidates (judge each by structure)"] + (
        [f"- {g['brick']} -> {g['field']} (card {g['card']}, roles {', '.join(g['roles'])})" for g in ix["migration_gap_candidates"]] or ["- none"]) + [""]
    out += ["## Migrate-brick moves"] + ([f"- {m['move']}: {m['brick']} {m['from_field']} -> {m['to_field']}" for m in ix["migrate_brick_moves"]] or ["- none"]) + [""]
    out += ["## Low-confidence matches (review)"] + ([f"- {m['brick']} in {m['field']} ({m['source']})" for m in ix["low_confidence_matches"]] or ["- none"]) + [""]
    deep = sorted(ix["depth"].items(), key=lambda kv: (-kv[1], kv[0]))
    out += ["## Parts (depth is relative and taken over all cuts: 0 = no parts yet)"] + (
        [f"- {k}: depth {d}, {len(ix['parts'].get(k, []))} parts in {len(ix['part_cuts'].get(k, {}))} cut(s), "
         f"part of {len(ix['part_of'].get(k, []))}" for k, d in deep[:15]]
        + ([f"- ... {len(deep) - 15} more"] if len(deep) > 15 else []) or ["- none"]) + [""]
    out += ["## Part cycles (fix: a unit cannot contain itself)"] + ([f"- {' -> '.join(c)}" for c in ix["part_cycles"]] or ["- none"]) + [""]
    cu = ix["cuts"]
    out += ["## Cuts (check a new label against the registry and the labels in use)",
            "- registry: " + ", ".join(cu["registry"])]
    out += [f"- in use: {c} ({'registry' if r['registry'] else 'NOT in registry'}): {r['wholes']} whole(s), {r['parts']} part(s)"
            for c, r in cu["labels"].items()] or ["- in use: none"]
    if cu["unlabelled_wholes"]:
        out.append(f"- unlabelled: {len(cu['unlabelled_wholes'])} whole(s) have parts that name no cut (older shape)")
    out += [f"- near-duplicate: {n['a']} ~ {n['b']} (" + (f"shares {', '.join(n['shared'])}" if n["shared"] else f"ratio {n['ratio']}") + ")"
            for n in cu["near_duplicates"]]
    out += [f"- bound (how: bind): {w} under {', '.join(cs)}" for w, cs in cu["binds"].items()]
    out += [""]
    out += render_recuts(ix["recuts"])
    out += [f"## Cards without a method brick (older shape): {len(ix['cards_without_method'])}"] + (
        [f"- {', '.join(ix['cards_without_method'][:15])}" + (f", ... {len(ix['cards_without_method']) - 15} more" if len(ix['cards_without_method']) > 15 else "")]
        if ix["cards_without_method"] else ["- none"]) + [""]
    out += ["## Recipe out of step with its cut (fix the table or the method brick's parts)"] + (
        [f"- {d['card']}: method {d['method']}, cut {d['cut'] or '(no Cut: line)'}"
         + (f"; only in recipe: {', '.join(d['only_in_recipe'])}" if d["only_in_recipe"] else "")
         + (f"; only in parts: {', '.join(d['only_in_parts'])}" if d["only_in_parts"] else "")
         for d in ix["recipe_drift"]] or ["- none"]) + [""]
    out += [f"## Unit links: {len(ix['unit_links'])}", ""]
    out += ["## Constraints of the time"] + ([f"- {c}: {', '.join(cs)}" for c, cs in ix["constraints"].items()] or ["- none"]) + [""]
    out += ["## Evidence limits"] + ([f"- {c}: {', '.join(cs)}" for c, cs in ix["evidence_limits"].items()] or ["- none"]) + [""]
    out += ["## Level-3 hints per reading"] + ([f"- {h['reading']} ({h['mode']}): {h['level3_hints']} of {h['notes']} notes" for h in ix["reading_hints"]] or ["- none"]) + [""]
    k = ix["known_bricks"]
    out += ["## Known bricks", f"- owned {len(k['owned'])}, seen {len(k['seen'])}, bank bricks {k['bank_bricks']}, owned share {k['owned_share']}"]
    if k["unknown_slugs"]:
        out.append(f"- slugs not in bank: {', '.join(k['unknown_slugs'])}")
    return "\n".join(out) + "\n"


def render_recuts(recuts: list[dict]) -> list[str]:
    out = ["## Re-cuts (a later cut must draw a new boundary: split, bind or add a piece)"]
    for w in recuts:
        for r in w["cuts"]:
            share = "; ".join(f"shares {o['shared']}/{o['of']} ({o['pct']}%) with `{c}`" for c, o in r["overlap"].items())
            line = f"- {w['whole']}: `{r['cut']}` ({r['parts']} parts"
            if r["new_parts"]:
                line += f", new: {', '.join(p.split(':', 1)[1] for p in r['new_parts'])}"
            if r["parts_cut_again"]:
                line += f", cut again: {', '.join(p.split(':', 1)[1] for p in r['parts_cut_again'])}"
            line += f"): {share}"
            if r["retag_of"]:
                line += f". RE-TAG of {', '.join(f'`{c}`' for c in r['retag_of'])}: all its parts are parts of that cut"
            elif r["no_new_boundary"]:
                line += ". NO NEW BOUNDARY: every part is in an earlier cut"
            out.append(line)
    return (out if len(out) > 1 else out + ["- none (no unit has two cuts)"]) + [""]


REL_BEGIN = "<!-- related:begin (generated by idea_index.py --write; edit the frontmatter lists, not this section) -->"
REL_END = "<!-- related:end -->"
REL_RE = re.compile(r"\n*<!-- related:begin.*?<!-- related:end -->\n*", re.S)
SIG_KEYS = ("input", "output", "objective", "constraint", "math")
DIRS = {"Brick": "bricks", "Idea Card": "cards", "Lens": "lenses", "Move": "moves"}


def link_prefix(root: Path) -> str:
    """Bundle-relative prefix of the bank (`/ideas`) when the bank sits in an OKF bundle, else ''."""
    root = root.resolve()
    for anc in [root, *root.parents]:
        idx = anc / "index.md"
        if idx.is_file() and "okf_version" in idx.read_text(encoding="utf-8")[:200]:
            rel = root.relative_to(anc).as_posix()
            return "" if rel == "." else "/" + rel
    return ""


def views(concepts: list[dict], prefix: str) -> dict[str, str]:
    """Generated `# Related` block per concept path (bank-relative), from frontmatter lists only."""
    by = {t: {c["slug"]: c for c in concepts if c["fm"]["type"] == t} for t in DIRS}

    def ln(t: str, slug: str) -> str | None:
        c = by[t].get(slug)
        if not c:
            return None
        return f"[{c['fm'].get('title') or slug}]({prefix}/{DIRS[t]}/{slug}.md)"

    out: dict[str, list[str]] = defaultdict(list)
    bricks = {s: c["fm"] for s, c in by["Brick"].items()}
    role_bricks: dict[str, list[str]] = defaultdict(list)
    for s, fm in bricks.items():
        if fm.get("status") != "deprecated":
            for r in brick_roles(fm):
                role_bricks[r].append(s)

    card_bricks: dict[str, set[str]] = defaultdict(set)   # union of both directions
    method_of: dict[str, list[str]] = defaultdict(list)   # brick -> cards whose method it is
    for cs, c in by["Idea Card"].items():
        card_bricks[cs] |= set(as_list(c["fm"].get("bricks")))
        if c["fm"].get("method"):
            card_bricks[cs].add(c["fm"]["method"])
            method_of[c["fm"]["method"]].append(cs)
    for s, fm in bricks.items():
        for cs in as_list(fm.get("cards")):
            card_bricks[cs].add(s)
    brick_cards: dict[str, set[str]] = defaultdict(set)
    for cs, ss in card_bricks.items():
        for s in ss:
            brick_cards[s].add(cs)
    move_refs: dict[tuple[str, str], list[tuple[str, str]]] = defaultdict(list)  # (type, slug) -> [(move, how)]
    for ms, c in by["Move"].items():
        fm = c["fm"]
        for key, t, how in (("from_brick", "Brick", "from this brick"), ("to_brick", "Brick", "to this brick"),
                            ("brick", "Brick", "moves this brick"), ("parent", "Idea Card", "parent"),
                            ("child", "Idea Card", "child"), ("card", "Idea Card", "child")):
            if fm.get(key):
                move_refs[(t, fm[key])].append((ms, how))
    lens_cards: dict[str, set[str]] = defaultdict(set)
    for cs, c in by["Idea Card"].items():
        for l in as_list(c["fm"].get("lenses")):
            lens_cards[l].add(cs)
    for l, c in by["Lens"].items():
        lens_cards[l] |= set(as_list(c["fm"].get("cards")))

    for s, fm in sorted(bricks.items()):
        lines = out[f"bricks/{s}"]
        role_in = {m.get("source"): m.get("role") for m in as_list(fm.get("migrations")) if isinstance(m, dict)}
        for cs in sorted(method_of.get(s, [])):
            l = ln("Idea Card", cs)
            if l:
                lines.append(f"- Method of {l}.")
        for cs in sorted(brick_cards[s] - set(method_of.get(s, []))):
            l = ln("Idea Card", cs)
            if l:
                field = by["Idea Card"][cs]["fm"].get("field")
                lines.append(f"- Used in {l}" + (f" ({field})" if field else "") + (f", as `{role_in[cs]}`" if role_in.get(cs) else "") + ".")
        for r in sorted(brick_roles(fm)):
            for o in sorted(set(role_bricks[r]) - {s}):
                ofields = sorted(brick_fields(bricks[o]))
                lines.append(f"- Shares role `{r}` with {ln('Brick', o)}" + (f" ({', '.join(ofields)})" if ofields else "") + ".")
        for ms, how in sorted(set(move_refs[("Brick", s)])):
            mfm = by["Move"][ms]["fm"]
            lines.append(f"- Move {ln('Move', ms)} ({mfm.get('move_type', 'move')}, {how}).")
    for cs, c in sorted(by["Idea Card"].items()):
        fm, lines = c["fm"], out[f"cards/{cs}"]
        if fm.get("method"):
            l = ln("Brick", fm["method"])
            lines.append(f"- Method brick {l}." if l else f"- Method brick `{fm['method']}` (no file yet).")
        for a in sorted(card_bricks[cs] - {fm.get("method")}):
            l = ln("Brick", a)
            lines.append(f"- Brick {l}." if l else f"- Brick `{a}` (no file yet).")
        for l in sorted(set(as_list(fm.get("lenses"))) | {x for x, cc in lens_cards.items() if cs in cc}):
            lk = ln("Lens", l)
            if lk:
                lines.append(f"- Lens {lk}.")
        if fm.get("parent") and ln("Idea Card", fm["parent"]):
            lines.append(f"- Parent card {ln('Idea Card', fm['parent'])}.")
        mv = set(as_list(fm.get("moves"))) | {m for m, _ in move_refs[("Idea Card", cs)]}
        for ms in sorted(mv):
            l = ln("Move", ms)
            if l:
                mfm = by["Move"][ms]["fm"]
                role = f" on `{mfm['role']}`" if mfm.get("role") else ""
                lines.append(f"- Move {l} ({mfm.get('move_type', 'move')}{role}).")
    for l, c in sorted(by["Lens"].items()):
        lines = out[f"lenses/{l}"]
        for cs in sorted(lens_cards[l]):
            lk = ln("Idea Card", cs)
            if lk:
                lines.append(f"- Seen in {lk}.")
    for ms, c in sorted(by["Move"].items()):
        fm, lines = c["fm"], out[f"moves/{ms}"]
        for key, t, label in (("parent", "Idea Card", "Parent card"), ("child", "Idea Card", "Child card"),
                              ("card", "Idea Card", "Child card"), ("from_brick", "Brick", "From brick"),
                              ("to_brick", "Brick", "To brick"), ("brick", "Brick", "Brick moved")):
            l = ln(t, fm.get(key) or "")
            row = f"- {label} {l}." if l else None
            if row and row not in lines:
                lines.append(row)

    g = unit_graph(concepts)
    kt = {k: t for k, t in UNIT_TYPES.items()}

    def at(key: str) -> str:
        k, slug = key.split(":", 1)
        return f"{DIRS[kt[k]]}/{slug}"

    def lk(key: str) -> str:
        k, slug = key.split(":", 1)
        return ln(kt[k], slug) or f"`{slug}`"
    for key, cuts in g["part_cuts"].items():
        how = g["cut_how"].get(key, {})
        for cut, ps in cuts.items():  # one line per cut, the cut named
            head = "- Parts (no cut recorded): " if cut == UNLABELLED else f"- Parts by cut `{cut}`: "
            out[at(key)].append(head + ", ".join(
                lk(p) + (f" ({how[cut][p]})" if p in how.get(cut, {}) else "") for p in ps) + ".")
    for key, wholes in g["part_of_cuts"].items():
        for w, cuts in wholes.items():
            named = [c for c in cuts if c != UNLABELLED]
            tail = f" (cut{'s' if len(named) > 1 else ''} {', '.join(f'`{c}`' for c in named)})" if named else ""
            out[at(key)].append(f"- Part of {lk(w)}{tail}.")
    for l in g["unit_links"]:
        tail = (f" via {lk(l['via'])}" if l["via"] else "") + (f": {l['note']}" if l["note"] else "") + "."
        out[at(l["a"])].append(f"- Linked to {lk(l['b'])}{tail}")
        out[at(l["b"])].append(f"- Linked to {lk(l['a'])}{tail}")
    return {k: "\n".join(v) for k, v in out.items()}


CUTS_BEGIN = ("<!-- cuts:begin (generated by idea_index.py --write from the method brick's parts and cuts; "
              "edit those, not this table) -->")
CUTS_END = "<!-- cuts:end -->"
CUTS_RE = re.compile(r"\n*<!-- cuts:begin.*?<!-- cuts:end -->\n*", re.S)


def cut_tables(concepts: list[dict], prefix: str) -> dict[str, str]:
    """`# Cuts compared` per card whose method brick holds two or more cuts: a row per piece, a column per cut.

    A cell names the piece's place in that cut: its `group` (for the Recipe's cut, the Recipe's Role cell),
    `inside X` (the cut keeps the piece within its part X), `spans X, Y` (the piece joins parts the cut
    keeps apart), or a dash (the cut does not have it). The closing lines come from the brick's `cuts`.
    """
    g = unit_graph(concepts)
    units = {f"{k}:{c['slug']}": c for c in concepts for k, t in UNIT_TYPES.items() if c["fm"]["type"] == t}
    memo: dict[str, set[str]] = {}

    def below(k: str) -> set[str]:
        if k not in memo:
            memo[k], todo = set(), list(g["parts"].get(k, []))
            while todo:
                q = todo.pop()
                if q not in memo[k]:
                    memo[k].add(q)
                    todo += g["parts"].get(q, [])
        return memo[k]

    def title(k: str) -> str:
        c = units.get(k)
        return str(c["fm"].get("title") or c["slug"]) if c else k.split(":", 1)[1]

    def esc(text: str) -> str:
        return str(text).replace("|", "\\|").replace("\n", " ")

    out = {}
    for c in concepts:
        method = c["fm"].get("method") if c["fm"]["type"] == "Idea Card" else None
        whole = f"brick:{method}"
        cuts = g["part_cuts"].get(whole, {})
        if len(cuts) < 2:
            continue
        rcut, roles = recipe_roles(c["body"])
        groups = g["cut_group"].get(whole, {})
        meta = {str(m["cut"]): m for m in as_list(units[whole]["fm"].get("cuts")) if isinstance(m, dict) and m.get("cut")}
        names = sorted(cuts, key=lambda n: n != rcut)  # the Recipe's cut first, the others in order

        def cell(p: str, n: str) -> str:
            if p in cuts[n]:
                return groups.get(n, {}).get(p) or (roles.get(p.split(":", 1)[1]) if n == rcut else "") or "part"
            inside = [q for q in cuts[n] if p in below(q)]
            if inside:
                return "inside " + ", ".join(title(q) for q in inside)
            spans = [q for q in cuts[n] if q in below(p)]
            return "spans " + ", ".join(title(q) for q in spans) if spans else "-"

        def head(n: str) -> str:
            return ("no cut recorded" if n == UNLABELLED else f"`{n}`") + (" (Recipe)" if n == rcut else "")

        rows = ["| Piece | " + " | ".join(head(n) for n in names) + " |",
                "|" + "---|" * (len(names) + 1)]
        for p in dict.fromkeys(q for n in names for q in cuts[n]):
            k, slug = p.split(":", 1)
            piece = f"[{esc(title(p))}]({prefix}/{DIRS[UNIT_TYPES[k]]}/{slug}.md)"
            rows.append(f"| {piece} | " + " | ".join(esc(cell(p, n)) for n in names) + " |")
        shows = []
        for i, n in enumerate(names):
            m = meta.get(n, {})
            asked = f" (asked: {m['angle']})" if m.get("angle") else ""
            if m.get("shows"):
                shows.append(f"- {head(n)}{asked}: {m['shows']}")
            elif i:
                shows.append(f"- {head(n)}{asked}: not written yet (add `shows` to this cut in the method brick's `cuts`)")
        out[f"cards/{c['slug']}"] = "\n".join(
            [CUTS_BEGIN, "# Cuts compared", "",
             "Each row is a piece of the method; each column is one cut and names the piece's place in it. "
             "`inside X`: the cut keeps the piece within X. `spans X`: the piece joins parts the cut keeps apart. "
             "`-`: the cut does not have the piece.", ""] + rows
            + ([""] + ["What each cut shows that the others do not:"] + shows if shows else []) + [CUTS_END])
    return out


def with_cuts(body: str, block: str) -> str:
    """Put the generated `# Cuts compared` block right after the card's Recipe section (or drop it)."""
    lines = CUTS_RE.sub("\n\n", body).split("\n")
    if not block:
        return "\n".join(lines)
    start = next((i for i, l in enumerate(lines) if l.startswith("# ") and l[2:].strip().lower().startswith("recipe")), -1)
    at = next((i for i in range(start + 1, len(lines))
               if (start >= 0 and lines[i].startswith("# ")) or lines[i].startswith("<!-- related:begin")), len(lines))
    before, after = "\n".join(lines[:at]).rstrip("\n"), "\n".join(lines[at:]).lstrip("\n")
    return (before + "\n\n" if before.strip() else "") + block + ("\n\n" + after if after.strip() else "\n")


def related_block(lines: str) -> str:
    return f"{REL_BEGIN}\n# Related\n\n{lines or '- none yet'}\n{REL_END}\n"


def with_related(body: str, lines: str) -> str:
    stripped = REL_RE.sub("\n", body).rstrip("\n")
    return (stripped + "\n\n" if stripped.strip() else "") + related_block(lines)


def sig_lines(sig) -> str:
    if isinstance(sig, dict):
        rows = [f"- **{k.capitalize()}:** {sig[k]}" for k in SIG_KEYS if sig.get(k) not in (None, "")]
        rows += [f"- **{k.capitalize()}:** {v}" for k, v in sig.items() if k not in SIG_KEYS and v not in (None, "")]
        return "\n".join(rows)
    return f"- {sig}"


def lift_signature(fm_text: str, body: str, sig) -> tuple[str, str]:
    """Remove `signature:` (and its indented lines) from the frontmatter text; put it as a list under # Signature."""
    out, skip = [], False
    for line in fm_text.splitlines():
        if line.startswith("signature:"):
            skip = True
            continue
        if skip and (line.startswith((" ", "\t")) or not line.strip()):
            continue
        skip = False
        out.append(line)
    block = sig_lines(sig)
    if re.search(r"^# Signature[ \t]*$", body, re.M):
        body = re.sub(r"^# Signature[ \t]*\n+", lambda m: f"# Signature\n{block}\n\n", body, count=1, flags=re.M)
    else:
        body = f"# Signature\n{block}\n\n" + body.lstrip("\n")
    return "\n".join(out), body


def bricks_index(concepts: list[dict]) -> str:
    bricks = {c["slug"]: c["fm"] for c in concepts if c["fm"]["type"] == "Brick"}
    live = {s: fm for s, fm in bricks.items() if fm.get("status") != "deprecated"}
    role_bricks: dict[str, list[str]] = defaultdict(list)
    for s, fm in live.items():
        for r in brick_roles(fm):
            role_bricks[r].append(s)
    shared = {r: sorted(ss) for r, ss in sorted(role_bricks.items()) if len(ss) >= 2}
    out = ["# bricks", "",
           "Generated by `idea_index.py --write` from brick frontmatter; do not edit by hand.", "",
           "## Shared roles", "",
           "Roles that two or more bricks fill: the places to compare or substitute. Every other role has one brick; grep `roles:` for it.", ""]
    out += [f"* `{r}` - " + ", ".join(f"[{live[s].get('title') or s}]({s}.md) ({', '.join(sorted(brick_fields(live[s]))) or 'no field'})" for s in ss)
            for r, ss in shared.items()] or ["* none yet"]
    out += ["", "## All bricks", ""]
    for s, fm in sorted(bricks.items(), key=lambda kv: (kv[1].get("title") or kv[0]).lower()):
        dep = " (deprecated)" if fm.get("status") == "deprecated" else ""
        out.append(f"* [{fm.get('title') or s}]({s}.md){dep} - {fm.get('description', '')}".rstrip(" -"))
    return "\n".join(out) + "\n"


def sync_views(root: Path, write: bool) -> list[str]:
    """Bring generated views up to date. Returns bank-relative paths that changed (or would change)."""
    concepts = load(root)
    rel = views(concepts, link_prefix(root))
    tables = cut_tables(concepts, link_prefix(root))
    changed = []
    for c in concepts:
        t = c["fm"]["type"]
        if t not in DIRS:
            continue
        path = root / c["path"]
        text = path.read_text(encoding="utf-8")
        m = FM_RE.match(text)
        fm_text, body = m.group(1), m.group(2)
        if t == "Brick" and c["fm"].get("signature") is not None:
            fm_text, body = lift_signature(fm_text, body, c["fm"]["signature"])
        if t == "Idea Card":
            body = with_cuts(body, tables.get(f"cards/{c['slug']}", ""))
        new = f"---\n{fm_text}\n---\n\n" + with_related(body.lstrip("\n"), rel.get(f"{DIRS[t]}/{c['slug']}", ""))
        if new != text:
            changed.append(c["path"])
            if write:
                path.write_text(new, encoding="utf-8")
    bricks_dir = root / "bricks"
    if bricks_dir.is_dir():
        idx = bricks_dir / "index.md"
        new = bricks_index(load(root) if write else concepts)
        if not idx.is_file() or idx.read_text(encoding="utf-8") != new:
            changed.append("bricks/index.md")
            if write:
                idx.write_text(new, encoding="utf-8")
    return changed


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("root", type=Path)
    ap.add_argument("--json", type=Path, help="also write the index as JSON to this path")
    ap.add_argument("--suggest-merges", action="store_true",
                    help="also list near-duplicate role tags and tensions for an LLM to confirm")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true",
                      help="regenerate # Related sections and bricks/index.md; move frontmatter signatures to the body")
    mode.add_argument("--check", action="store_true", help="exit 1 when generated views are out of date")
    mode.add_argument("--cuts", action="store_true",
                      help="print the cut registry (id: how to cut) and the cut labels in use; run it before you write a cut")
    mode.add_argument("--recuts", action="store_true",
                      help="print only the Re-cuts report (overlap between cuts, re-tags); run it after you write a cut")
    args = ap.parse_args(argv)
    if not args.root.is_dir():
        print(f"idea_index: {args.root} is not a directory", file=sys.stderr)
        return 2
    if args.write or args.check:
        changed = sync_views(args.root, write=args.write)
        verb = "updated" if args.write else "out of date"
        print(f"idea_index: {len(changed)} file(s) {verb}" + "".join(f"\n  {p}" for p in changed))
        return 1 if (args.check and changed) else 0
    concepts = load(args.root)
    if args.cuts:
        reg = load_registry()
        cu = build(concepts, reg)["cuts"]
        sys.stdout.write("# Cut registry\n" + "".join(f"- {i}: {h}\n" for i, h in sorted(reg.items())))
        sys.stdout.write("\n# Labels in use\n" + ("".join(
            f"- {c}{'' if r['registry'] else ' (NOT in registry)'}: {r['wholes']} whole(s)\n"
            for c, r in cu["labels"].items()) or "- none\n"))
        return 0
    if args.recuts:
        sys.stdout.write("\n".join(render_recuts(build(concepts)["recuts"])))
        return 0
    ix = build(concepts)
    if args.suggest_merges:
        ix["merge_suggestions"] = suggest_merges(concepts)
    if args.json:
        args.json.write_text(json.dumps(ix, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    sys.stdout.write(render(ix))
    if args.suggest_merges:
        rows = ix["merge_suggestions"]
        sys.stdout.write("\n## Merge suggestions (confirm by meaning before merging)\n")
        sys.stdout.write("".join(f"- {r['a']} ~ {r['b']} (jaccard {r['jaccard']}, ratio {r['ratio']}"
                                 + (f", shared bricks {', '.join(r['shared_bricks'])}" if r["shared_bricks"] else "")
                                 + f"; uses {r['uses_a']}/{r['uses_b']})\n" for r in rows) or "- none\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
