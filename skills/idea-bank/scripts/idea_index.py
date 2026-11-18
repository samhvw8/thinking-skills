# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6"]
# ///
"""Index an idea bank: links, convergence, migration-gap candidates, known-bricks coverage,
and perspectives and operations (the skill's seeds plus the bank's files) with where each was used.

Usage: uv run idea_index.py <bank-root> [--json out.json] [--suggest-merges] [--write | --check]

Deterministic and offline. Gap candidates are a list for judgement, not findings.
--write regenerates the views made from frontmatter (including `parts` and `links`): a `# Related` section in every
brick, card, lens, move, perspective and operation, and `bricks/index.md`. It also moves a frontmatter
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


UNIT_TYPES = {"brick": "Brick", "lens": "Lens", "card": "Idea Card",
              "perspective": "Perspective", "operation": "Operation"}  # bare slugs resolve in this order
SEEDED = ("perspective", "operation")  # unit kinds that also have seeds in references/seeds.md
DEFAULT_LENS = "default"  # the lens of a `parts` entry that names none
SEEDS = Path(__file__).resolve().parent.parent / "references" / "seeds.md"
HOW_ALIASES = {"bind": "join"}  # older files say `bind` for `join`
PROVENANCE = {"judge", "owner"}  # `how` values that say who found a part, not which operation made it


def load_seeds(path: Path = SEEDS) -> dict[str, dict[str, dict]]:
    """The seed perspectives and operations that ship with the skill: {"perspective": {id: entry}, "operation": ...}."""
    m = FM_RE.match(path.read_text(encoding="utf-8")) if path.is_file() else None
    if not m:
        raise SystemExit(f"idea_index: cannot read the seed file {path}")
    fm = yaml.safe_load(m.group(1)) or {}
    return {"perspective": {str(e["id"]): e for e in as_list(fm.get("perspectives"))},
            "operation": {str(e["id"]): e for e in as_list(fm.get("operations"))}}


def entry_lens(entry: dict) -> str:
    """The perspective a `parts` entry was made through: `lens`, else the older `cut`, else `default`."""
    return str(entry.get("lens") or entry.get("cut") or DEFAULT_LENS)


def entry_order(entry: dict, where: str) -> float:
    try:
        return float(entry["order"])
    except (TypeError, ValueError):
        raise SystemExit(f"idea_index: {where}: `order` must be a number, got {entry['order']!r}")


def unit_graph(concepts: list[dict], seeds: dict | None = None) -> dict:
    """`parts` (split / join / fuse) and `links` (connect without merging) across every unit kind.

    Each `parts` entry belongs to a lens: the perspective it was made through (`lens`, older files `cut`,
    else `default`). A unit may hold several lenses side by side. Entries with `order` are the steps of a
    recipe: kept in that order, repeats included, and not grouped by lens. A step may name a seed
    operation (`split`) that has no file. Depth is relative and computed: a unit with no parts is 0, a
    whole is 1 + its deepest part. Nothing stores a level name, so a unit split further needs no relabelling.
    """
    seeds = load_seeds() if seeds is None else seeds
    live = {f"{k}:{c['slug']}": c for c in concepts for k, t in UNIT_TYPES.items()
            if c["fm"]["type"] == t and c["fm"].get("status") != "deprecated"}
    known = set(live) | {f"{k}:{s}" for k in SEEDED for s in seeds[k]}

    def resolve(ref, home: str = "") -> str | None:
        ref = str(ref)
        if ":" in ref:
            return ref if ref in known else None
        kinds = list(UNIT_TYPES)
        if home in SEEDED:  # a recipe's steps are operations; a perspective's parts are perspectives
            kinds = [home] + [k for k in kinds if k != home]
        return next((f"{k}:{ref}" for k in kinds if f"{k}:{ref}" in known), None)

    parts: dict[str, list[str]] = {}  # whole -> distinct parts over all lenses (depth uses this)
    part_lenses: dict[str, dict[str, list[str]]] = {}  # whole -> lens -> parts, in frontmatter order
    lens_how: dict[str, dict[tuple[str, str], str]] = {}  # whole -> (lens, part) -> "how: note"
    part_how: dict[str, dict[str, str]] = {}  # whole -> part -> "how: note", for parts that say how they were found
    steps: dict[str, list[dict]] = {}  # recipe -> [{order, step, lens}], sorted by order, repeats kept
    part_of: dict[str, set[str]] = defaultdict(set)
    links, broken = [], []
    for key, c in sorted(live.items()):
        ps, lenses, ordered = [], {}, []
        for i, entry in enumerate(as_list(c["fm"].get("parts"))):
            entry = entry if isinstance(entry, dict) else {"to": entry}
            ref = entry.get("to", "")
            lens = entry_lens(entry)
            r = resolve(ref, key.split(":", 1)[0])
            if not r:
                broken.append({"from": key, "to": f"part:{ref}"})
                continue
            if r not in ps:
                ps.append(r)
            part_of[r].add(key)
            if entry.get("order") is not None:
                ordered.append((entry_order(entry, c["path"]), i,
                                {"order": entry["order"], "step": r, "lens": None if lens == DEFAULT_LENS else lens}))
                continue
            if r not in lenses.setdefault(lens, []):
                lenses[lens].append(r)
            if entry.get("how"):
                how = str(entry["how"]) + (f": {entry['note']}" if entry.get("note") else "")
                lens_how.setdefault(key, {})[(lens, r)] = how
                part_how.setdefault(key, {}).setdefault(r, how)
        if ps:
            parts[key] = ps
        if lenses:
            part_lenses[key] = lenses
        if ordered:
            steps[key] = [s for _, _, s in sorted(ordered, key=lambda t: (t[0], t[1]))]
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
    return {"parts": parts, "part_lenses": part_lenses, "lens_how": lens_how, "part_how": part_how, "steps": steps,
            "part_of": {k: sorted(v) for k, v in sorted(part_of.items())},
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


def cell(value) -> str | None:
    """A table cell or frontmatter value as a label: backticks and blanks removed, `-` is empty."""
    s = str(value or "").strip().strip("`").strip()
    return None if s in ("", "-") else s


def uses_of(concepts: list[dict]) -> list[dict]:
    """Every operation result that names a perspective (`lens`) or an operation (`verb`), and where it is.

    Sources: `parts` entries (verb = `how`, `bind` read as `join`; a recipe step's verb is its operation),
    a Move's `lens` and `move_type`, and the `Lens` and `Operator` columns of a Mutations table in a card
    or reading.
    """
    out = []
    for c in concepts:
        fm, t, slug = c["fm"], c["fm"]["type"], c["slug"]
        kind = next((k for k, v in UNIT_TYPES.items() if v == t), None)
        if kind and fm.get("status") != "deprecated":
            for entry in as_list(fm.get("parts")):
                if not isinstance(entry, dict):
                    continue
                lens = entry_lens(entry)
                how = cell(entry.get("how"))
                verb = str(entry.get("to", "")).split(":")[-1] if entry.get("order") is not None else HOW_ALIASES.get(how, how)
                out.append({"lens": None if lens == DEFAULT_LENS else lens, "verb": verb, "where": f"{kind}:{slug}"})
        if t == "Move":
            out.append({"lens": cell(fm.get("lens")), "verb": cell(fm.get("move_type")), "where": f"move:{slug}"})
        if t in ("Idea Card", "Reading"):
            for row in table_rows(c["body"], "Mutations"):
                out.append({"lens": cell(row.get("lens")), "verb": cell(row.get("operator")),
                            "where": f"{'card' if t == 'Idea Card' else 'reading'}:{slug}"})
    return [u for u in out if u["lens"] or u["verb"]]


def catalog(concepts: list[dict], seeds: dict) -> dict:
    """Perspectives and operations, seeds and bank files together, each with where it was used.

    A perspective's uses are grouped by verb (`part` when the entry names no operation); an operation's by
    the lens it ran through (`no lens`). Labels with no seed and no file are free labels; one used in two or
    more files recurs and is ready for a file of its own.
    """
    uses = uses_of(concepts)
    lens_files = {c["slug"] for c in concepts if c["fm"]["type"] == "Lens"}
    out = {}
    for kind, key, other, blank in (("perspective", "lens", "verb", "part"), ("operation", "verb", "lens", "no lens")):
        items: dict[str, dict] = {}
        for s, e in seeds[kind].items():
            items[s] = {"id": s, "seed": True, "file": False, "origin": e.get("origin", "seed"),
                        "status": e.get("status"), "uses": {}}
        for c in concepts:
            if c["fm"]["type"] == UNIT_TYPES[kind] and c["fm"].get("status") != "deprecated":
                it = items.setdefault(c["slug"], {"id": c["slug"], "seed": False, "status": None, "uses": {}})
                it.update(file=True, origin=c["fm"].get("origin") or it.get("origin") or "invented")
        free: dict[str, dict] = {}
        for u in uses:
            label = u[key]
            if not label or (kind == "operation" and label in PROVENANCE):
                continue
            if label in items:
                group = items[label]["uses"]
            else:
                group = free.setdefault(label, {"label": label, "uses": {}})["uses"]
            where = group.setdefault(u[other] if u[other] and u[other] not in PROVENANCE else blank, [])
            if u["where"] not in where:
                where.append(u["where"])
        for f in free.values():
            f["files"] = len({w for ws in f["uses"].values() for w in ws})
            f["recurs"] = f["files"] >= 2
            if kind == "perspective":
                f["lens_file"] = f["label"] in lens_files
        out[kind] = {"items": list(items.values()), "free": [free[l] for l in sorted(free)]}  # seed order, then files
    return out


def build(concepts: list[dict]) -> dict:
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

    broken, one_way = [], []
    for cs, fm in cards.items():
        for a in as_list(fm.get("bricks")):
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

    links = {a: sorted(set(as_list(fm.get("cards"))) | {cs for cs, cfm in cards.items() if a in as_list(cfm.get("bricks"))})
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

    seeds = load_seeds()
    g = unit_graph(concepts, seeds)
    broken += g["broken"]
    cat = catalog(concepts, seeds)

    return {
        "counts": {t: len(v) for t, v in sorted(by_type.items())},
        "parts": g["parts"],
        "part_lenses": g["part_lenses"],
        "recipes": g["steps"],
        "part_how": {w: {p: h.split(":", 1)[0] for p, h in d.items()} for w, d in g["part_how"].items()},
        "part_of": g["part_of"],
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
        "perspectives": cat["perspective"]["items"],
        "free_lenses": cat["perspective"]["free"],
        "operations": cat["operation"]["items"],
        "free_operations": cat["operation"]["free"],
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
    out += ["## Parts (depth is relative: 0 = no parts yet)"] + (
        [f"- {k}: depth {d}, {len(ix['parts'].get(k, []))} parts in {len(ix['part_lenses'].get(k, {}))} lens(es), "
         f"part of {len(ix['part_of'].get(k, []))}" for k, d in deep[:15]]
        + ([f"- ... {len(deep) - 15} more"] if len(deep) > 15 else []) or ["- none"]) + [""]
    out += ["## Part cycles (fix: a unit cannot contain itself)"] + ([f"- {' -> '.join(c)}" for c in ix["part_cycles"]] or ["- none"]) + [""]
    out += [f"## Unit links: {len(ix['unit_links'])}", ""]
    out += ["## Constraints of the time"] + ([f"- {c}: {', '.join(cs)}" for c, cs in ix["constraints"].items()] or ["- none"]) + [""]
    out += ["## Evidence limits"] + ([f"- {c}: {', '.join(cs)}" for c, cs in ix["evidence_limits"].items()] or ["- none"]) + [""]
    out += ["## Level-3 hints per reading"] + ([f"- {h['reading']} ({h['mode']}): {h['level3_hints']} of {h['notes']} notes" for h in ix["reading_hints"]] or ["- none"]) + [""]
    k = ix["known_bricks"]
    out += ["## Known bricks", f"- owned {len(k['owned'])}, seen {len(k['seen'])}, bank bricks {k['bank_bricks']}, owned share {k['owned_share']}"]
    if k["unknown_slugs"]:
        out.append(f"- slugs not in bank: {', '.join(k['unknown_slugs'])}")
    out.append("")
    out += render_catalog(ix, "perspective", "Perspectives (seeds and bank files; where each was used, by verb)", "for")
    out += render_catalog(ix, "operation", "Operations (seeds and bank files; where each was used, by lens)", "through")
    return "\n".join(out).rstrip("\n") + "\n"


def render_catalog(ix: dict, kind: str, heading: str, joiner: str) -> list[str]:
    items, free = ix[f"{kind}s"], ix["free_lenses" if kind == "perspective" else "free_operations"]

    def where(uses: dict) -> str:
        return "; ".join(f"{joiner} {g}: {', '.join(ws)}" for g, ws in sorted(uses.items()))

    def name(it: dict) -> str:
        tags = ["seed" if it["seed"] else "", "bank file" if it["file"] else "", it.get("status") or "",
                "invented" if it.get("origin") == "invented" else ""]
        steps = ix["recipes"].get(f"{kind}:{it['id']}")
        if steps:
            tags.append("recipe: " + ", ".join(f"{s['step'].split(':', 1)[1]}" + (f" through {s['lens']}" if s["lens"] else "")
                                               for s in steps))
        return f"{it['id']} ({', '.join(t for t in tags if t)})"

    shown = [it for it in items if it["uses"] or it["file"]]  # every bank file gets a row; unused seeds share one
    unused = [it["id"] for it in items if not it["uses"] and not it["file"]]
    rows = [f"- {name(it)}: {where(it['uses']) or 'not used yet'}" for it in shown]
    rows += [f"- Not used yet ({len(unused)}): {', '.join(unused)}"] if unused else []
    out = [f"## {heading}"] + (rows or ["- none"]) + [""]
    label = "Free perspective labels" if kind == "perspective" else "Free operation labels"
    out += [f"## {label} (no seed or file; give one a file when it recurs)"]
    out += [f"- {f['label']}" + (" (a lens file has this name)" if f.get("lens_file") else "")
            + f": {where(f['uses'])}" + (f" -- RECURS in {f['files']} files" if f["recurs"] else "") for f in free] or ["- none"]
    return out + [""]


REL_BEGIN = "<!-- related:begin (generated by idea_index.py --write; edit the frontmatter lists, not this section) -->"
REL_END = "<!-- related:end -->"
REL_RE = re.compile(r"\n*<!-- related:begin.*?<!-- related:end -->\n*", re.S)
SIG_KEYS = ("input", "output", "objective", "constraint", "math")
DIRS = {"Brick": "bricks", "Idea Card": "cards", "Lens": "lenses", "Move": "moves",
        "Perspective": "perspectives", "Operation": "operations"}


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
    for cs, c in by["Idea Card"].items():
        card_bricks[cs] |= set(as_list(c["fm"].get("bricks")))
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
        for cs in sorted(brick_cards[s]):
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
        for a in sorted(card_bricks[cs]):
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

    seeds = load_seeds()
    g = unit_graph(concepts, seeds)
    kt = {k: t for k, t in UNIT_TYPES.items()}

    def at(key: str) -> str:
        k, slug = key.split(":", 1)
        return f"{DIRS[kt[k]]}/{slug}"

    def lk(key: str) -> str:
        k, slug = key.split(":", 1)
        return ln(kt[k], slug) or f"`{slug}`"
    def lens_link(label: str) -> str:  # a perspective file, else an older lens file of that name, else as written
        return ln("Perspective", label) or ln("Lens", label) or f"`{label}`"

    def where_link(w: str) -> str:
        k, slug = w.split(":", 1)
        t = kt.get(k) or {"move": "Move"}.get(k)
        return (ln(t, slug) if t else None) or f"`{w}`"

    for key, lenses in g["part_lenses"].items():
        how = g["lens_how"].get(key, {})
        for lens, ps in lenses.items():  # one line per lens, the perspective named (linked when it has a file)
            out[at(key)].append(f"- Parts by lens {lens_link(lens)}: " + ", ".join(
                lk(p) + (f" ({how[(lens, p)]})" if (lens, p) in how else "") for p in ps) + ".")
    for key, ss in g["steps"].items():
        out[at(key)].append("- Steps in order: " + "; ".join(
            f"{i}. {lk(s['step'])}" + (f" through {lens_link(s['lens'])}" if s["lens"] else "")
            for i, s in enumerate(ss, 1)) + ".")
    cat = catalog(concepts, seeds)
    for kind, phrase in (("perspective", "Used for"), ("operation", "Used through")):
        for it in cat[kind]["items"]:
            if it["file"]:
                for group, ws in sorted(it["uses"].items()):
                    out[f"{DIRS[UNIT_TYPES[kind]]}/{it['id']}"].append(
                        f"- {phrase} `{group}` on " + ", ".join(where_link(w) for w in ws) + ".")
    for key, wholes in g["part_of"].items():
        out[at(key)] += [f"- Part of {lk(w)}." for w in wholes]
    for l in g["unit_links"]:
        tail = (f" via {lk(l['via'])}" if l["via"] else "") + (f": {l['note']}" if l["note"] else "") + "."
        out[at(l["a"])].append(f"- Linked to {lk(l['b'])}{tail}")
        out[at(l["b"])].append(f"- Linked to {lk(l['a'])}{tail}")
    return {k: "\n".join(v) for k, v in out.items()}


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
