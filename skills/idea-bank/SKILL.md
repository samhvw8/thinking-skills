---
name: idea-bank
description: "Shared store and formats for the owner's idea work: where the bank lives ($IDEA_HOME), the schema for idea cards, bricks, lenses, moves, readings, scout batches and state files, how bricks are cut, bound and linked (`parts`, `links`), the index script that finds links, convergence and migration gaps, the search script (embeddings + BM25) that finds existing bricks, and how to commit the bank. Use when another idea skill (idea-scout, co-read, idea-forge, idea-mine) writes or reads the bank, when the owner asks to search the bank for something, find or dedupe bricks, see what a brick is part of or linked to, run the idea index, or see convergence and migration gaps. Not for deciding what to read or how to collaborate; the caller skills own that."
---

# Idea bank

This skill owns the mechanism: location, formats, links, index, commits.
The caller skills own policy: what to read, how the owner and Claude split the work,
what goes in a batch. Keep that split, so one schema change reaches every caller.

## What a brick is

Every idea skill works with bricks. Read this before you split, bind, name or
match one.

A **brick** is any piece of an idea that does one job you can name: it takes
something in, gives something out, and keeps to a constraint. "Filters bad
samples" is a brick; so is "a cheap check before a strong one", and so is a
whole method seen as one block.

- **No fixed size.** Bricks cut into smaller bricks and bind into bigger ones.
  No brick is the smallest piece: never call one atomic or final.
- **Scissors and tape.** A split cuts a brick into parts; a bind tapes existing
  bricks into a bigger one. Both write the brick's `parts`, from opposite
  directions (`how: split`, `how: bind`), and name a kind of cut in `cut`: a
  registry id such as `cost` or `data-flow` when one fits. A cut kind is a way
  to cut, not a lens file; `lenses/` holds authors' view models.
- **Keep every cut.** A new cut goes beside the old ones and never replaces
  one. Never rename, move or relabel a brick for it. It must draw a new
  boundary: `references/recut.md`.
- **The method is a brick.** A card records the source and points to its method
  brick (`method`). Every split of the method, the first included, is a cut on
  that brick; the card's Recipe table renders one named cut.
- **Name by job, match by structure** (Rules; "Link and dedupe bricks").

Rules for cuts and binds: `references/schema.md`, Parts and links.

## The owner

The **owner** is the person whose bank this is: the one the idea skills read,
scout and forge for. Every idea skill uses this word for that person. In a bulk
brief the reader is a lead agent, not the owner.

Facts about the owner (name, handle, chat language, presence default, compute,
starting scopes) live in the bank's `me/profile.md` (`references/schema.md`,
State files), never in a skill. Read it once per session, with the bank root.
When it is missing, use the defaults: chat in the language the owner writes in,
absent mode, heavy runs only on this machine. Tell the owner once that they can
create the file.

## Find the bank

Resolve the root once per session, in this order:

1. `$IDEA_HOME`, when it is set.
2. `~/ideas`.

Create the root and the layout below on first use. When the root came from a
default, tell the owner once which path you use. Never write bank files anywhere else,
because a second copy splits the links.

## Layout

| Path | Holds | Type (`schema.md`) |
|------|-------|--------------------|
| `bricks/` | One brick per file, named by its role-level slug | `Brick` |
| `lenses/` | One view model per file | `Lens` |
| `moves/` | One move (diff between a source and its parent) per file | `Move` |
| `cards/` | One six-layer card per source | `Idea Card` |
| `people/` | Optional profiles | `Person` |
| `readings/` | `YYMMDD-<slug>.md`, one per reading session | `Reading` |
| `batches/` | `YYMMDD-batch-<n>.md`, one per scout batch | `Scout Batch` |
| `me/` | The owner's state: `profile`, `scopes`, `interest-state`, `known-bricks`, `taste`, `progress` | `State` |

Bulk runs (`idea-mine`) stage outside the bank and merge in only after the
index on the staged folder shows no broken links (`schema.md`, Bulk staging).

Every directory has an `index.md` (no frontmatter). Add a line there and a dated
line in the bundle's `log.md` when you create a concept. `bricks/index.md` is the
exception: `idea_index.py --write` regenerates it. The bank is an area of an
OKF bundle: load the `okf` skill before restructuring it.

## Rules

- **Files in English, chat in the owner's language.** Bank files are read by every
  model and tool; the chat follows the language the owner writes in.
- **Formats come from `references/schema.md` only.** Read it before writing any
  bank file. Do not invent fields in a caller skill; add them to the schema.
- **Intent is quoted or marked.** Every field that states what an author meant,
  felt or believed carries a quote with its section, or `(inferred)`. Without this
  rule a model writes tidy intentions the author never had.
- **Keep the raw beside the bricks.** A card stores the quotes and a source
  pointer next to its bricks. Summaries drop nuance that later retrieval needs.
- **Name bricks by role, not by identity.** "filters bad samples", not "reward
  model". Substitution and migration only work at the role level.
- **Best effort, then the owner corrects.** Splitting, linking, merging and naming
  units is Claude's work, done as far as Claude can judge, not held back for a
  perfect rule. Mark a doubtful call `(inferred)` and make it anyway. Record
  each correction the owner makes (in the unit's file, and as a row in
  `me/progress.md`), so the next pass starts from it.
- **Presence mode: the owner is absent unless they turn it on.** This is the only
  definition; the other idea skills point here.
  - **Absent (default, unless `me/profile.md` sets `Presence default:
    present`).** Claude does every step itself, best effort: splits,
    recombines, writes variants, cards and kill-test predictions, files drafts.
    It never stops to ask the owner to write first, and logs no skip: absence is not a
    skip.
  - **Present.** On after the owner types `/idea-present` (or `/idea-present on`) in
    this conversation, until `/idea-present off`. The "owner writes first" steps of
    co-read, idea-forge and idea-scout then run as written, and skips are counted.
  - Steps that only make sense with the owner (co-read deep mode, idea-forge deal mode,
    the owner's own kill-test prediction, scout's gem-type guess) run only in present
    mode. In absent mode, offer them in one line: "Type /idea-present to do this
    together." and stop there. Asking for one of these steps ("deal me some
    bricks", "go deep") does not turn present mode on; only the switch does.
  - The switch lives in the conversation. A new session, or a compaction summary
    that does not show it, starts in the profile's presence default (absent
    when unset).
- **State is data, not config.** Levels, budgets and ratios live in `me/`.
  No skill hardcodes a topic level or a number the owner can change at runtime.

## Link and dedupe bricks

Two bricks are the same when their structural signatures match (input, output,
objective, constraint, math form), whatever each field calls them. Judge this by
structure mapping: compare the relations, not the names. Name or embedding
similarity misleads here, because each field renames the same structure
("sparse coding", "dictionary learning", "SAE features").

To merge: keep the older file, move the other names into `names`, append the
other file's `migrations` and `cards`, and leave the removed file as
`status: deprecated` with a link to the kept one. Log the merge.

## Search the bank

```bash
uv run <this skill's folder>/scripts/idea_search.py <bank-root> index                    # embed changed chunks
uv run <this skill's folder>/scripts/idea_search.py <bank-root> search "<text>" --type brick [--rerank]
uv run <this skill's folder>/scripts/idea_search.py <bank-root> like <brick> --other-fields
```

`search` fuses EmbeddingGemma 2 vectors (several chunks per file: signature,
gloss, names per field, migrations; card layers and rows) with BM25 and returns
30 candidates. `like` ranks bricks by signature and shows topic similarity and
shared fields beside it. It starts llama.cpp's `llama-server` for one command
and stops it after (first index of the author's bank: about a minute on a laptop).
Vectors are cached in `<bank-root>/.index/`, which is git-ignored derived data.

The list is a shortlist, not an answer. Judge each candidate by structure
before you link or merge it: measured on the author's bank, the correct brick
was in the top 10 for 72% of real links and in the top 30 for 81%. `--rerank`
reorders the brick shortlist by structure with one `fast`-tier model call
(Claude Code CLI with Haiku, about $0.002; it needs that CLI): on held-out rows the
right brick came first 53% of the time instead of 39%. Use it when a reader will
look at only the first few rows (bulk mode); a model that reads all 30 does the
same job itself. `--graph` adds Personalized PageRank over the links; no graph
variant beat plain fusion on held-out rows at this bank size.

## Run the index

```bash
uv run <this skill's folder>/scripts/idea_index.py <bank-root> [--json out.json]
uv run <this skill's folder>/scripts/idea_index.py <bank-root> --write   # regenerate link views
uv run <this skill's folder>/scripts/idea_index.py <bank-root> --check   # exit 1 if views are stale
```

It is deterministic and offline. It reports:

- brick ↔ card links and broken links;
- bricks by number of fields;
- **cuts**: labels against the registry, near-duplicates, binds, cards with
  no method brick, Recipes out of step (`--cuts` prints the registry);
- **re-cuts** (`--recuts`): what each cut shares with the others, and a cut
  that only re-tags another;
- **convergence**: one role filled by bricks from two or more fields, and hot
  slots (a card role whose brick was substituted two or more times in `moves/`);
- **migration-gap candidates**: a brick whose role tags match a card's
  `tensions` in a field the brick has not reached yet;
- `migrate-brick` moves (they widen a brick's fields; hot slots count only
  `substitute-brick`);
- low-confidence migration matches, for review;
- cards by constraint of the time (input for a later price tracker);
- level-3 hints per reading;
- known-bricks coverage (`me/known-bricks.md`).

Gap candidates are a list for judgement, not findings. Open each candidate and
judge by structure whether the brick could fill the role in that field before you
show it to the owner.

## Monthly view

Once a month, or when the owner asks: run the index, then show the owner the convergence
list, the top gap candidates you judged real, and bricks that moved from "seen" to
"owned" in `me/known-bricks.md`. Callers (`idea-scout` retro) use this view.

## Commit after each session

The bank sits inside a git repo (often the repo of a knowledge bundle). After a
session that changed bank files:

1. Regenerate the link views: `idea_index.py <bank-root> --write`, then
   refresh the search cache: `idea_search.py <bank-root> index`.
2. Validate with the OKF validator (the `validate` skill, when installed):
   `uv run <validate skill folder>/scripts/okf_validate.py <bundle-root> --strict`.
3. Stage only bank paths and the bundle `log.md`: `git -C <repo> add <bank-root> <bundle>/log.md`.
4. Commit with a conventional message, for example `feat(ideas): add card for <slug>`.
   Add no AI attribution lines.

If the root is not in a git repo, say so once and suggest `git init`; do not
create a repo yourself.

## References

- `references/schema.md`: every type's frontmatter and body template, the gem
  taxonomy, the unpopularity diagnosis and the mutation operators.
- `scripts/idea_search.py`: hybrid search; `scripts/test_idea_search.py`
  tests it without a model. The numbers above were measured on the author's bank.
- `scripts/idea_deal.py`: deals a hand (bricks, lenses, moves) for idea-forge's
  deal mode; `scripts/test_idea_deal.py` tests it.
- `references/cuts.json`: the cut registry, built from the repo's decks.
- `references/recut.md`: how to cut a brick through a new angle.
- `scripts/idea_index.py`: the index; `scripts/test_idea_index.py` and
  `scripts/fixtures/` test it.
