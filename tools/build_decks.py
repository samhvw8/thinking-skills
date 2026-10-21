"""Build every skill's deck files from decks/, the one source. Standard library only.

decks/<kind>.json holds one kind of card (lenses, models, fields, ...), checked against
decks/schema.json. decks/bundles.json says which files each skill gets. Each skill carries its
own copy, so it installs and runs alone; this script and its --check keep the copies honest.

Usage:
  python3 tools/build_decks.py           # validate decks/, then write every skill's files
  python3 tools/build_decks.py --check   # validate, and exit 1 if a skill's file is stale

Edit decks/, never a built file: the next build overwrites it, and --check (run by
tests/test_decks.py) fails until you rebuild.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DECKS = ROOT / "decks"
SKILLS = ROOT / "skills"


class BuildError(Exception):
    pass


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise BuildError("%s: %s" % (path.relative_to(ROOT), e))


def load_decks(schema):
    kinds = schema["properties"]
    known = set(kinds) | {"schema", "bundles"}
    extra = sorted(p.stem for p in DECKS.glob("*.json") if p.stem not in known)
    if extra:
        raise BuildError("decks/ has files the schema does not describe: %s. Add them to "
                         "decks/schema.json, or remove them." % ", ".join(extra))
    missing = [k for k in kinds if not (DECKS / ("%s.json" % k)).is_file()]
    if missing:
        raise BuildError("decks/ is missing: %s" % ", ".join("%s.json" % k for k in missing))
    return {k: load_json(DECKS / ("%s.json" % k)) for k in kinds}


# ---------------------------------------------------------------- validation

TYPES = {"object": dict, "array": list, "string": str, "number": (int, float), "boolean": bool}


def check(value, rule, schema, where, errors, refs):
    """The JSON Schema subset decks/schema.json uses, plus its x-ref annotation."""
    if "$ref" in rule:
        rule = schema["$defs"][rule["$ref"].rsplit("/", 1)[1]]
    want = rule.get("type")
    if want and (not isinstance(value, TYPES[want]) or (want == "number" and isinstance(value, bool))):
        errors.append("%s: want %s, got %s" % (where, want, type(value).__name__))
        return
    if isinstance(value, str):
        if len(value) < rule.get("minLength", 0):
            errors.append("%s: empty" % where)
        if "pattern" in rule and not re.search(rule["pattern"], value):
            errors.append("%s: '%s' does not match %s" % (where, value, rule["pattern"]))
        if "x-ref" in rule:
            refs.append((where, rule["x-ref"], value))
    if isinstance(value, list):
        if len(value) < rule.get("minItems", 0):
            errors.append("%s: needs at least %d entries" % (where, rule["minItems"]))
        for i, item in enumerate(value):
            name = item.get("id", i) if isinstance(item, dict) else i
            check(item, rule.get("items", {}), schema, "%s[%s]" % (where, name), errors, refs)
    if isinstance(value, dict):
        for k in rule.get("required", []):
            if k not in value:
                errors.append("%s: missing '%s'" % (where, k))
        props = rule.get("properties", {})
        extra = rule.get("additionalProperties")
        for k, v in value.items():
            if k in props:
                check(v, props[k], schema, "%s.%s" % (where, k), errors, refs)
            elif isinstance(extra, dict):
                check(v, extra, schema, "%s.%s" % (where, k), errors, refs)
            elif props:
                errors.append("%s: unknown field '%s' (add it to decks/schema.json)" % (where, k))


def ids_of(deck):
    return set(deck) if isinstance(deck, dict) else {e["id"] for e in deck if isinstance(e, dict) and "id" in e}


def validate(decks, schema):
    errors, refs = [], []
    for kind, deck in decks.items():
        check(deck, schema["properties"][kind], schema, kind, errors, refs)
        if isinstance(deck, list):
            seen, dup = set(), set()
            for e in deck:
                i = e.get("id") if isinstance(e, dict) else None
                if i is not None:
                    (dup if i in seen else seen).add(i)
            if dup:
                errors.append("%s: duplicate ids %s" % (kind, sorted(dup)))
    for where, kind, value in refs:
        if value not in ids_of(decks[kind]):
            errors.append("%s: '%s' is not an id in %s.json" % (where, value, kind))
    if errors:
        raise BuildError("decks/ failed validation:\n  " + "\n  ".join(errors))


# ---------------------------------------------------------------- build

def build_bundle(name, spec, decks):
    out = {}
    for key, src in spec["keys"]:
        if "value" in src:
            out[key] = src["value"]
            continue
        deck = decks[src["deck"]]
        if "ids" in src:
            by_id = {e["id"]: e for e in deck}
            unknown = [i for i in src["ids"] if i not in by_id]
            if unknown:
                raise BuildError("bundle %s: %s has no ids %s" % (name, src["deck"], unknown))
            deck = [by_id[i] for i in src["ids"]]
        if "fields" in src:
            deck = [{k: e[k] for k in src["fields"] if k in e} for e in deck]
        out[key] = deck
    return json.dumps(out, indent=spec.get("indent", 2), ensure_ascii=False) + "\n"


def outputs(decks, bundles):
    """{path under skills/: text} for every file a skill gets."""
    built = {n: build_bundle(n, b, decks) for n, b in bundles["bundles"].items()}
    files = {}
    for skill, items in bundles["skills"].items():
        if not (SKILLS / skill / "SKILL.md").is_file():
            raise BuildError("bundles.json names skill '%s', which has no SKILL.md" % skill)
        for rel, src in items.items():
            if "bundle" in src:
                if src["bundle"] not in built:
                    raise BuildError("%s/%s: no bundle '%s'" % (skill, rel, src["bundle"]))
                files["%s/%s" % (skill, rel)] = built[src["bundle"]]
            else:
                files["%s/%s" % (skill, rel)] = (DECKS / src["copy"]).read_text(encoding="utf-8")
    return files


def main(argv):
    check_only = "--check" in argv
    try:
        schema = load_json(DECKS / "schema.json")
        decks = load_decks(schema)
        validate(decks, schema)
        files = outputs(decks, load_json(DECKS / "bundles.json"))
    except BuildError as e:
        sys.exit("build_decks: %s" % e)
    stale = [rel for rel, text in sorted(files.items())
             if not (SKILLS / rel).is_file() or (SKILLS / rel).read_text(encoding="utf-8") != text]
    if check_only:
        if stale:
            sys.exit("build_decks: stale, run python3 tools/build_decks.py:\n  skills/" + "\n  skills/".join(stale))
        print("decks ok: %d kinds, %d skill files current" % (len(decks), len(files)))
        return
    for rel in stale:
        (SKILLS / rel).parent.mkdir(parents=True, exist_ok=True)
        (SKILLS / rel).write_text(files[rel], encoding="utf-8")
    print("decks ok: %d kinds; wrote %d of %d skill files" % (len(decks), len(stale), len(files)))
    for rel in stale:
        print("  skills/%s" % rel)


if __name__ == "__main__":
    main(sys.argv[1:])
