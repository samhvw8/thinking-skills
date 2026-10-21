# Decks

The cards every thinking skill deals from, one kind per file, each entry with a stable `id`.
This folder is the only place to edit them. It is not installed: `tools/build_decks.py` copies
what each skill needs into that skill's folder.

| File | What it holds | Used by |
|---|---|---|
| `lenses.json`, `families.json` | who is looking: 52 lenses in 6 families, each with what it asks, sees, misses, delivers and its instruments | heavy-think, council, debate, ambition (13) |
| `techniques.json` | how to generate | heavy-think, council, debate, creative |
| `provocations.json` | sparks for a quiet room | heavy-think, council, debate |
| `presets.json`, `composition_rules.json` | lens sets by scenario, and the rules a set must meet | heavy-think, council |
| `reframes.json`, `reframe_sets.json` | ways out when stuck | heavy-think |
| `decompositions.json`, `decomposition_sets.json` | ways to break a problem down | heavy-think |
| `debates.json`, `debate_rules.json` | debate formats and the evidence-backed rules | heavy-think, debate |
| `rubrics.json`, `rubric.md` | scoring weights, and their anchors | heavy-think, council, creative |
| `models.json`, `patterns.json` | 88 mental models with a move and a receipt; patterns that route a problem to them | ambition |
| `fields.json` | Range cards: a field, its verbs, method, instruments and receipt | ambition |
| `deck.py` | the dealer (fit, deal, list) | heavy-think, council, debate |

## Reuse

- **From a skill:** add the file to the skill in `bundles.json`, run `python3 tools/build_decks.py`,
  and read the copy inside the skill. Never read another skill's folder: it may not be installed.
- **From anything else:** read the JSON directly. Validate one file against
  `schema.json#/properties/<kind>`. A property with `x-ref: <kind>` holds an id from that file.
- **Adding a card:** add it to the kind's file with a new `id`, then rebuild. The build refuses a
  missing field, a duplicate id or a reference to an id that does not exist.
