# The perspective deck

How the deck (`perspectives.json`) is built and how `deck.py` deals from it. Shared by every
heavy-think mode, `/council` and `/debate`. The deck is the only copy of its content: list it with
the commands below rather than copying entries or counts into a doc, since copies go stale as the
deck grows.

## Contents
- What a card holds
- Commands
- Fitting the deck to the question
- What the dealer seats
- Writing a custom lens
- Adding to the deck

## What a card holds

A card is one **lens** (who is looking) and, for ideation only, one **technique** (how it generates).
Each lens has:

| Field | What the agent does with it |
|-------|-----------------------------|
| `asks` | The question it holds the subject to |
| `sees`, `misses` | What it notices first, and its blind spot |
| `delivers` | The output it must hand back |
| `instruments` | What it actually does: the raw material it works from, the tools it uses (shell, web and social search, code reading, a fresh subagent as a cold reader) and the check it runs, plus what to do when that material is out of reach |
| `clashes` | Lenses it tends to disagree with, so a panel argues instead of agreeing three times |

Pass `delivers` and `instruments` into every agent prompt verbatim. A lens name alone changes the
words an agent uses, not the work it does; the instruments change the work.

Lenses fall into six families: challenger, stakeholder, temporal, systems, craft and wildcard. The
deck also holds techniques, provocations (the facilitator's sparks), presets by question shape (each
naming its scoring rubric), reframes for Unstick, decompositions for Decompose, debate formats, and
the rubric weights.

## Commands

`DECK` stands for `python3 "$SKILL_DIR/deck.py"`. `SKILL_DIR` is the heavy-think
skill folder: the folder its SKILL.md is in (Claude Code sets `${CLAUDE_SKILL_DIR}`). Never a fixed install path:
the skill is installed in different places.

```bash
DECK presets                                         # every preset: its shape, lenses, deep adds, rubric
DECK deal --members 3 --preset incident --no-technique --question "<the problem>"   # judging: lenses only
DECK deal --members 5 --preset greenfield --question "<the problem>"                # ideation: lens + technique
DECK deal --members 4 --lenses "operator; maintainer; EU regulator: Would this pass a GDPR review?"
DECK reframes --question "<why they are stuck>"      # or --set <id>; no flag lists every reframe and set
DECK decompositions --question "<the problem>"       # or --set <id>
DECK debates                                         # debate formats and the evidence-backed rules
DECK rubric [creative|decision|review]               # scoring weights
```

`deal` prints, for each seat: the lens with its family, `asks`, `sees`, `misses`, `delivers` and
`instruments`, then (without `--no-technique`) its technique and a provocation for later.

## Fitting the deck to the question

Always pass `--question` (the problem in one or two sentences, or `--question-file`). Each lens,
technique and provocation is asked one yes/no question, "does this fit this problem?", and only
the ones that fit are dealt. The scorer is Clef when Cloudflare is logged in, else Jev when
`TYPESAFE_API_KEY` is set, else BM25 word overlap (`deck.py deal --help`). The deal prints which one
it used and what it kept, and a `deck warn:` line when a scorer failed: pass that on to the user.

- The fit scores also rank the seats: within a family, the best-fitting lens is seated first, with a
  small bonus for clashing with a lens already seated.
- A required family (challenger, stakeholder, temporal) with no fitting lens is still seated, from
  its best-scoring lens.
- When Clef or Jev finds no wildcard lens that fits, no wildcard seat is dealt.
- A pool with too few fitting entries is dealt from in full, best fit first.
- The fit never drops a preset's or `--lenses`' lenses.

## What the dealer seats

- **A random deal** seats at least one challenger, one stakeholder and one temporal lens, a wildcard
  from 4 members up (unless none fits), then fills the least-represented families.
- **A preset** fills the seats in its order: its lenses, then its deep adds, up to `--members`. If a
  required family is then missing, the dealer swaps out the last lens whose family is doubled, and
  takes the replacement from the preset's own deep adds before the rest of the deck. When every seat
  already holds a different family, nothing is swapped.
- **Review presets** (`*-review`) never seat a wildcard: a moonshot finds no defects.
- **`--lenses`** are always seated as given and never swapped. With `--preset`, they take the first
  seats and the preset fills the rest. Missing families go only into spare seats, so with no spare
  seat a family can be missing: read the printed `[family]` tags, and add the lens you need to
  `--lenses` yourself rather than re-dealing.
- To seat a preset exactly as listed, pass its lenses with `--lenses` (from `DECK presets`).

**Techniques are for ideation only.** For architecture, strategy, reviews and other decisions, deal
with `--no-technique`: a forced technique (random entry, lateral provocation) helps generate ideas
and hurts reasoning about trade-offs (`tensions.md`, independence vs diversity). That flag also
drops the provocations.

## Writing a custom lens

The real people around the problem (the customer, the DBA on call, the finance team, the reader)
often make better lenses than the deck. Write one as `Name: the question it asks` in `--lenses`;
separate entries with `;` when a question contains commas. A custom lens gets a generic
`instruments` line from `deck.py`; when you know the material that person would really work from
(the on-call runbook, last quarter's invoices), write it into that agent's prompt instead.

## Adding to the deck

Add an entry to `perspectives.json` and `deck.py` picks it up. Every lens needs every field in the
table above; `load_deck` refuses a lens without `delivers` or `instruments`. Ids are unique within a
list, every id a preset or set names must exist, and entries from research carry a `source`. Run
the tests after a change: `python3 -m unittest discover -s tests` in the skill folder.
