# Idea bank schema

The single source of truth for bank formats. Every caller skill writes these
shapes and nothing else. All files are OKF concepts: YAML frontmatter with a
non-empty `type`, markdown body, English text.

Common frontmatter on every type: `type`, `title`, `description`, `tags`,
`generated: { by, at }` (actor convention: `claude-code/<model>`, `human:<handle>`,
where `<handle>` is the `Handle` in `me/profile.md`, or `owner` when it is unset).
Add `verified: { by: "human:<handle>", at }` when the owner signed the content off.

Links between bank files use bundle-relative paths, for example
`/ideas/bricks/sparse-overcomplete-code.md`. The index script reads the slugs in
the list fields below, so keep those fields as plain slugs (file name without
`.md`), not links.

**Frontmatter lists are the source of truth; the link views are generated.**
`idea_index.py --write` adds a `# Related` section at the end of every brick,
card, lens, move, perspective and operation (real markdown links, each with its relation in words), and
rewrites `bricks/index.md` (shared roles first, then all bricks). The section sits
between `<!-- related:begin ... -->` and `<!-- related:end -->` markers. Never
edit inside them: change the frontmatter list and run `--write` again.
`--check` exits 1 when a view is out of date. Text outside the markers is kept.

Keep frontmatter short: slugs, enums and one-line values. Long prose goes in
the body, where a stray colon or quote cannot break the parse.

## Rendering for the owner

Bank files use this schema's terms. Chat output to the owner does not: they read it to
learn, and private jargon makes it harder to learn from. Every caller skill
follows these rules for anything shown in chat.

1. **Open with a headline frame.** One plain sentence that holds the whole idea,
   ideally as a sharp picture ("theory as compiler, advice as cache").
2. **Plain words.** A schema term (brick, gem type, layer, zoom, move type,
   cluster, lens) appears only when the owner already owns it (`me/known-bricks.md`), or
   with a one-phrase gloss the first time: "part (the job it does)", "a gap where
   a tool from one field fits another". Never print frontmatter, slugs, cluster
   levels, read-basis tags, guesses about what the owner knows, or notes to yourself.
   Those go in bank files.
3. **Quotation marks mean verbatim.** Use them only for text copied exactly from
   the source. Paraphrase without quote marks. Before output, check every quote
   against the source; when the text is on disk, run
   `../idea-mine/scripts/check_quotes.py <file> <source-text>`, and
   fix or unquote each flagged quote.
4. **Say who says it.** Keep three voices apart: the author (quoted or
   paraphrased with the section), commenters (in a social thread, name the
   poster), and Claude ("(my reading)"; the bank's `(inferred)` renders this way). Never state Claude's diagnosis as the
   author's, and never state as a finding something the source does not show.
5. **Label what is not from the source.** Anything from the bank: "(from your
   bank: <card or brick in plain words>)". Anything from memory: "(from memory,
   unchecked)". Never cite bank content or earlier batches as if the source said it.

## Field vocabulary

- **field**: a lower-case, hyphenated discipline slug: `image-compression`,
  `neuroscience`, `machine-learning`, `learning-science`, `exercise-physiology`,
  `epidemiology`, `medicine`, `ux-design`, `labor-economics`,
  `software-engineering`, `product`, `marketing`. Reuse an existing slug before
  you make a new one (`idea_index.py` lists them).
- **role tag**: a lower-case, hyphenated verb phrase for a job a brick does:
  `sparse-represent-signal`, `filter-bad-samples`, `consolidate-after-signal`.
  Roles describe the job, never the implementation.
- **intent marker**: a quote with its section (`"..." (Methods > 3.2)`), or the
  text `(inferred)` after a claim that is Claude's reading.

### YAML pitfalls

Four bank files once failed their first parse. Quote a frontmatter value when it
contains `: ` (colon and space), starts with `%`, `@`, `*`, `&`, `!`, `|`, `>`
or a quote mark, or is a flow-list item that contains a comma
(`[ "a, b", c ]`). Quote dates and times you want kept as strings
(`at: '2026-11-02T00:00:00Z'`). Run the OKF validator after writing.

## Idea Card (`cards/<slug>.md`)

One card per source (paper, article, post, talk, repo, synthesis note).

**Synthesis notes** (a research note that summarises many studies or views, such
as a topic note elsewhere in the same knowledge bundle) are cards with `source_kind:
synthesis-note`: `read_basis: full-text` means the note was read in full, the
body opens with a `Basis:` line (what the note itself rests on: number and kind
of sources, its own grade), `evidence` follows the note's own grade, and the card
may hold several bets (`# Bets`). A move's parent may be a view reported inside
the note rather than an earlier paper.

```yaml
---
type: Idea Card
title: <source title>
description: <the one idea, one sentence>
tags: [ideas, card, <cluster>]
resource: <canonical URL or DOI>
field: <field slug of the source>
bricks: [<brick slug>, ...]        # bricks used in the recipe
lenses: [<lens slug>, ...]         # view models the author uses
roles: [<role tag>, ...]           # roles the recipe needs filled
tensions: [<role tag>, ...]        # roles the field still lacks a good brick for
parent: <card slug or URL>         # the source this one mutated, if known
moves: [<move slug>, ...]
gem_types: [<gem type>, ...]       # from the taxonomy below
evidence: none | anecdote | weak | moderate | strong   # a tag; never filters
read_basis: abstract | passages | full-text | talk | post
source_kind: primary | synthesis-note | social | talk | repo
intent_sources: [openreview | talk | v1-diff | tweet | repo | rebuttal | interview | blog | paper | note, ...]
constraints: [<constraint slug>, ...]  # limits that forced a METHOD choice, e.g. llm-judge-cost, trial-length
evidence_limits: [<slug>, ...]     # limits on how far the EVIDENCE reaches, e.g. no-control-group
status: draft | stable             # stable once the owner or a review signed it off
generated: { by: ..., at: ... }
---
```

`constraints` slugs name a limit that forced how the work was done, usually a
priced one (`gpu-hour-cost`, `label-cost`, `context-length`, `llm-token-cost`,
`no-vision-model`, `trial-length`, `sample-size-cost`), so a later price tracker
can find every card a price drop unlocks. `evidence_limits` slugs name what the
evidence cannot show (`observational-only`, `no-control-group`,
`self-report-only`, `single-study-evidence`, `animal-model-only`,
`narrow-sample-population`); they feed "Where it is weak", never the price
tracker. Reuse slugs. Older cards with both kinds in `constraints` still parse;
split them when you next touch the card.

Body sections, in this order:

```markdown
# View model (layer 0)
- Picture: <how the author pictures the problem> <intent marker>
- Bottleneck: <what they believe is the real constraint; what they treat as noise>
- Expected solution shape: <scale vs structure, learned vs designed, ...>
- Taste: <what they find elegant or ugly>
- Surprise: <what surprised them; it shows their prior>
- Source domain of the picture: <field the picture is borrowed from>

# Contradiction (layer 1)
<want X and not-X: where the obvious approach trades off>

# Resolution principle (layer 2)
<separation in time / space / scale / condition, or "trades off, not resolved">

# Bet (layer 3)
If <X is the real bottleneck>, then <Y> should work. (inferred)
<Quote marks only when the bet is verbatim in the source, with its section.>

# Bets (synthesis notes only, optional)
1. <the card's main bet, same as above>
2. <bet of another study or view the note reports> (<section>; whose bet)

# Recipe (layer 4)
| Role | Brick (slug) | Signature (input -> output, objective) | Why this brick (author's reason or (inferred)) |
|------|-------------|----------------------------------------|-----------------------------------------------|
Operator: <sequence | loop | gate | nesting | adversarial | distill | ensemble | tree | other: ...>

## Lens: <lens label> — <the angle in plain words>      (one per later angle; "A new angle on the card")
| <the angle's question, step, cost or failure> | What the source says (section) | Pieces (slugs, old or new) |
|------------------------------------------------|--------------------------------|----------------------------|
What this angle shows that the others do not: <one line>

# Diff and constraints (layer 5)
- Parent: <what the source mutated>
- Move: <move type, link to moves/>
- Constraints of the time: <compute, data, tools, cost that forced a brick choice>
- Rejected alternatives: <"we tried X but..." quotes>

# Gems
- <gem type>: <the reason, in one line, with the passage it rests on>

# Story told vs real thinking
<where the paper's framing differs from talks, posts, rebuttals or v1 drafts>

# Raw
Source: <resource URL>. Local copy: <absolute path of the file read, or none>
<the quotes the layers rest on, each with its section>
Re-read for <lens label>: <sections read>      (one line per later angle, then its new quotes)

# Mutations
| Operator | Variant | Role fit | Novelty link | Kill test | Owner verdict | Origin | Lens |
|----------|---------|----------|--------------|-----------|-------------|--------|------|
```

Mutations columns: `Operator` is a `move_type` (or another operation, "Perspective
and Operation" below); `Role fit` says whether the new
brick does the role and what breaks; `Novelty link` is the closest prior work
found, or `none found (<query>)`; `Kill test` is the cheapest test or its result;
`Owner verdict` is `keep`, `kill (<reason>)` or empty; `Origin` is `owner` or `claude`;
`Lens` is the perspective the variant was made through (Parts and links, `lens`).
Older tables have no `Lens` column; they still parse.
Older banks may carry the owner's handle where this schema says `owner` (`Origin`,
`how`, the owner's column headers); read it as `owner`.

### A new angle on the card

When a later session looks at a banked source from a new angle (a re-cut, or
"look at it again by ..."):

- **Never edit lines an earlier session wrote,** on the card or on a brick. Add
  beside them. A correction is a dated line next to the line it corrects. (The
  owner's own corrections are the exception: "Best effort", Parts and links.)
- **Re-read the source,** not the card: the local copy in `# Raw` first, then a
  disk search for its file name, then `resource`. Add the `Re-read for` line and
  the new quotes to `# Raw`.
- **Give the angle its own section** at the end of the Recipe, after the
  `Operator:` line and any earlier angle sections: `## Lens: <lens label> —
  <the angle in plain words>`. Organise its table by the angle: a row per question, step,
  cost or failure the angle names; a column for what the source says (with its
  section); a column for the pieces that answer it. Close with `What this angle
  shows that the others do not:`.
- **Record the pieces** in `parts` with the same `lens` (Parts and links), and
  any new brick as usual. Run `idea_index.py --write`.
- **The reply opens with what the angle shows,** in plain words, then the table.

## Brick (`bricks/<role-slug>.md`)

Name the file by the structure's role, not one field's name for it.

```yaml
---
type: Brick
title: <neutral name, e.g. "Sparse code over an overcomplete basis">
description: <signature in one sentence>
tags: [ideas, brick]
names: { <field slug>: [<names used there>] }
roles: [<role tag>, ...]           # jobs it has done anywhere
fields: [<field slug>, ...]        # fields it has reached
cards: [<card slug>, ...]
migrations:
  - { field: <slug>, year: <yyyy | unknown>, source: <url or card slug>, role: <role tag>, match_confidence: high }
kill_tests:
  - { date: <yyyy-mm-dd>, hypothesis: <...>, result: survived | killed | inconclusive, note: <...> }
cost: <optional: what using it costs: compute, data, money, latency>
fails_when: <optional: the conditions where it breaks>
status: draft | stable | deprecated
generated: { by: ..., at: ... }
---
```

Migration rows may add `match_confidence: high | medium | low`: how sure the
structure match is that put this row here. The index lists `low` rows for review.
`cost` and `fails_when` make the interface form used for delegated clusters
(role, signature, cost, fails_when) without reading the body.

Body: `# Signature`, `# Migrations` (the story of each move, one paragraph
each), `# Where it fails`, then the generated `# Related`. The signature is a
list in the body, not frontmatter, followed by the structure in words:

```markdown
# Signature
- **Input:** <what goes in>
- **Output:** <what comes out>
- **Objective:** <what is optimised or kept>
- **Constraint:** <sparsity, budget, ...>
- **Math:** <one-line form, optional>

<the structure in a few plain sentences>
```

A brick written with a frontmatter `signature:` still parses; `--write` moves
it into this list.

## Parts and links (any unit)

A unit is whatever can be split, joined, fused or linked: a brick, a lens, a
card, a perspective, an operation, or an arrangement pattern written as a brick.
There are no fixed levels. Split as far as
you can judge today and keep that layer; a later pass may split a part again, or
find that a brick is really a whole made of others. Nothing is relabelled or
moved when that happens: only `parts` grows.

```yaml
parts:                               # this unit is made of these
  - <slug>                           # a part you are sure of
  - { to: <slug>, how: split | join | fuse | judge | owner, lens: <label>, note: <optional> }
  - { to: <operation>, order: <n>, lens: <label> }   # a recipe step (Operation files)
links:                               # connect without merging
  - { to: <slug>, via: <slug>, note: <one line> }
```

- **`how` names the operation or who found it.** `split`: cut out of this
  unit. `join`: taped into this bigger unit, each part keeping its own job
  (older files say `bind`; read it as `join`). `fuse`: melted into this new
  unit, which does a job none of its parts did alone; its `note` names that
  job. `judge`: an LLM judge said this unit contains the part. `owner`: the
  owner's call.
- **`lens` names the perspective** the operation ran through: the owner's
  question, a seed (`seeds.md`), a `perspectives/` file, or a free label of a
  few hyphenated words taken from the question asked (`cost-flow`,
  `what-could-break`). Free labels are always valid; nothing is checked against
  a list. Entries with the same `lens` form one way of splitting or combining
  the unit. A unit may hold several at once, and they may overlap or disagree;
  that is the point. An entry with no `lens` belongs to `default`. Older files
  say `cut` for `lens`: read both, write `lens`, and when an entry has both,
  `lens` wins. In a view, a label links to the `perspectives/` file of that
  name, else to an older `lenses/` file of that name, else it is printed as
  written.
- **Every operation records its lens, not only cutting.** A Move has `lens`;
  a Mutations row has a `Lens` column; a recipe step has `lens`. The index
  lists each perspective and operation with where it was used.

- **Refs:** a bare slug resolves as brick, then lens, then card, then
  perspective, then operation (a seed id counts as a file of its kind). Inside
  a Perspective or Operation, its own kind comes first. Write `card:<slug>`,
  `operation:<slug>` and so on when it must be one of those.
- **Depth is computed, never stored.** A unit with no `parts` has depth 0; a
  whole has 1 + its deepest part over all its lenses. The index reports depth,
  `part_of` (the reverse list) and cycles (an error: a unit cannot contain
  itself). The `# Related` view shows one line per lens, and a recipe's steps
  in order.
- **Arrangements are units too.** How parts combine (a gate before a loop, a
  cheap step before a strong check) may be its own brick, listed in `parts` like
  any other, or named as the `via` of a link.
- **`links` are one-sided in the file, two-sided in the view.** Write a link
  once; `--write` shows it on both ends.
- **Provenance lives in the file, never in a side file.** `how: split` came from
  splitting this unit, `how: judge` from an LLM judge saying this unit contains
  the part, `how: owner` from the owner. The view prints it next to the link.
- **Best effort.** A split or link Claude is unsure of still goes in, with its
  `how`. When the owner corrects one, change the entry (or delete it) and set
  `how: owner`, so the next pass starts from their call.

## Lens (`lenses/<slug>.md`)

An author's view model (how they picture the problem) as a reusable node. It
migrates like a brick. It is not a perspective for operating on bricks: those
are in `perspectives/`.

```yaml
---
type: Lens
title: <e.g. "Compression is intelligence">
description: <the picture in one sentence>
tags: [ideas, lens]
people: [<person slug>, ...]
fields: [<field slug>, ...]
cards: [<card slug>, ...]
migrations:
  - { field: <slug>, year: <yyyy | unknown>, source: <url or card slug> }
generated: { by: ..., at: ... }
---
```

Create a Lens file the second time a view model appears across sources. A view
seen once goes in the `## Candidates (seen once)` section of `lenses/index.md` (one line: the
picture in plain words, the card that holds it), so the second sighting finds it.

Body: `# Picture`, `# What it predicts`, `# What it ignores`, `# Inverse lens`
(the opposite assumption, for lens inversion).

## Perspective and Operation (`perspectives/<slug>.md`, `operations/<slug>.md`)

Perspectives and operations are bricks of another kind: a perspective is a way
of looking (a question), an operation is something done to bricks (split, join,
fuse, swap, invert, transfer, any other). They can be split, joined and fused
like any unit, and several operations can be combined into one bigger operation:
a recipe of steps. The skill ships seeds in `seeds.md`, including but not
limited to; the bank holds only the ones that recur or were invented. A bank
file with a seed's id overrides the seed.

```yaml
---
type: Perspective                    # or Operation
title: <e.g. "What goes unchecked">
description: <one sentence>
tags: [ideas, perspective]           # or operation
question: <the question to ask>      # Perspective
verbs: [<operation>, ...]            # Perspective, optional: the operations it suits
origin: seed | invented
source: <card slug, session, or URL where it came from>
parts:                               # Operation that is a recipe: its steps
  - { to: <operation>, order: 1, lens: <label> }
links: [...]
generated: { by: ..., at: ... }
---
```

- **A free label gets a file only when it recurs**, the second time it is used
  (`idea_index.py` lists free labels and flags those used in two or more files).
  This is the second-sighting rule for lenses, applied to perspectives and
  operations.
- **A recipe** lists its steps in `parts` with `order` (a number) and an
  optional `lens` per step. Steps may repeat and may name seed operations. The
  index keeps them in order.
- Body: `# Question` (Perspective) or `# Steps` (Operation), then what it turned
  up where it was used, then the generated `# Related`.

## Move (`moves/<slug>.md`)

The diff between a child source and its parent: the reusable unit of an idea.

```yaml
---
type: Move
title: <e.g. "Human-written steps -> self-generated steps + filter">
description: <one sentence>
tags: [ideas, move]
move_type: substitute-brick | substitute-operator | remove | lift-constraint | invert | migrate-brick | transfer | cross-card | resolve-contradiction | lens-transfer | lens-inversion | correct-parameter | relabel | retarget
lens: <label>                      # the perspective the move was made through (Parts and links)
parent: <card slug or URL>
child: <card slug or URL>
card: <card slug of the child, when it exists>
role: <role tag the move acted on>
from_brick: <brick slug>           # for substitute-brick
to_brick: <brick slug>
brick: <brick slug>                # for migrate-brick: the brick that moved
from_field: <field slug>           # for migrate-brick and transfer
to_field: <field slug>
generated: { by: ..., at: ... }
---
```

Examples: few-shot CoT → zero-shot CoT (`remove`: exemplars), CoT → Tree of
Thoughts (`substitute-operator`: sequence → tree), CoT → STaR (`substitute-brick`:
human-written steps → self-generated + filter), sparse coding → sparse
autoencoder features (`migrate-brick`: same brick, field neuroscience →
interpretability, role explain-receptive-fields → decompose-activations).

## Person (`people/<slug>.md`, optional)

```yaml
---
type: Person
title: <name>
description: <their recurring bet in one sentence>
tags: [ideas, person]
lenses: [<lens slug>, ...]
generated: { by: ..., at: ... }
---
```

Body: `# Recurring bets`, `# Taste`, `# Public hunches` (table: date, hunch,
source, later outcome or "open"). Hunches are tracked to learn whose intuition
runs ahead, not to grade truth.

## Reading (`readings/YYMMDD-<slug>.md`)

```yaml
---
type: Reading
title: <source title>
description: <what the session found, one sentence>
tags: [ideas, reading]
card: <card slug>                  # omitted in a deal session
mode: brief | deep | skim | deal
deal: { kind: role | lens | gap | pair | move, seed: <int>, x: <int>, items: [<slug>, ...] }  # deal only
stage: 1 | 2 | 3 | 4               # the owner's handover stage during the session
generated: { by: ..., at: ... }
---
```

Body sections: `# Recall` (step-0 result: questions, the owner's answers, right or
wrong; or `skipped: overloaded` / `skipped: <reason>`), `# Owner's guess` (written
before reading), `# Notes` (table: `| Owner | Claude | gem | hint |`; `gem` is a gem
type, `hint` is the level 1-3 a Claude note was opened at, or `-` for the owner's own
notes; the index counts `hint` = 3), `# Disagreements` (table: point, Owner's view, Claude's view, how to
settle, status), `# Mutations` (the owner's first, then Claude's, each with the owner's
keep/kill and reason), `# Kill test` (prediction written before the run, result),
`# Teach-back` (the owner's five sentences and the gaps probed), `# What we learned`
(new bricks, lenses, moves, open questions).

## Scout Batch (`batches/YYMMDD-batch-<n>.md`)

```yaml
---
type: Scout Batch
title: Scout batch <n> (<yyyy-mm-dd>)
description: <scopes covered and card count>
tags: [ideas, scout]
status: draft                      # stable once the owner has voted
sources: [{ id, resource, title }, ...]
generated: { by: ..., at: ... }
---
```

Body: `# Basis` (how each card was read), `# Votes` (table: `| # | Card |
Cluster | Level | Guess | Vote | One word | Zoom |`; `Level` is the cluster level
or `unset`; `Guess` is the owner's gem-type guess before seeing the card's reason, from
stage 2 on, else empty; `Vote` is `up | down | later`; `Zoom` is `yes` when the owner
asked for the brief of that card, else empty), then one section per card
when the cards are stored in the file.

## State files (`me/`, type `State`)

Each is one file, edited at runtime. No skill hardcodes their values.

| File | Body |
|------|------|
| `profile.md` | Facts about the owner, as a table `\| Key \| Value \|`. `Name`: what to call the owner. `Handle`: the actor id in `human:<handle>` (default `owner`). `Chat language`: the language for chat when the owner's own messages do not show one (default: the language the owner writes in). `Presence default`: `absent` or `present`, the mode a new conversation starts in (default `absent`). `Compute`: where heavy runs and kill-tests may go, and what to check before adding load (default: this machine only). `# Scopes`: starting scopes, copied into `scopes.md` only when that file is missing. Every key is optional |
| `scopes.md` | Table: scope, since, note |
| `interest-state.md` | `# Clusters` table: `| Cluster | Level | Zooms | Signals | Since |`; `Level` is `core`, `adjacent`, `delegated` or empty; `Zooms` counts briefs the owner asked for in that cluster. A cluster with no level gets the short role-level card; the one-line interface card is for `delegated` only. `# Settings`: cards per batch, explore slots per batch, weekly card budget. `# Change log` table: date, cluster, from → to, why. The owner's commands win, in any language |
| `known-bricks.md` | Table: brick slug, level (`seen`, `owned`), since, evidence (how the owner showed it: explained it, spotted it in a new source). Only core and adjacent clusters |
| `taste.md` | Table: date, source, gem the owner saw that Claude missed, gem type. Table: date, card, vote, one-word reason |
| `progress.md` | Table, one row per session: `| Date | Reading | Mode | Unaided gems | Roles named right | Owner-unique mutations | Level-3 hints | Gems Claude missed | Skips |`. `Mode` is `brief`, `deep`, `skim` or `deal`. The three skill columns are finding gems (`Unaided gems`), naming roles (`Roles named right`, of total) and proposing mutations (`Owner-unique mutations`). `# Stage` with the criteria below |

Handover stages (defaults; change them in `progress.md` from real data):

| Stage | Owner does | Move up when |
|-------|----------|--------------|
| 1 | Votes with one-word reasons; asks in briefs | About 30 bricks `owned` |
| 2 | Guesses the gem type before reading the card's reason | Over 60 % of guesses right |
| 3 | Writes the recipe for chosen sources; Claude reviews | The owner's cards need few corrections |
| 4 | Full co-reads on hard sources; brings new scopes and seeds | — |

## Bulk staging

`idea-mine` in bulk writes into a staging folder outside the bank (for example
`$TMPDIR/idea-mine-<date>/`, with the same layout), then merges in:

1. Dedupe bricks against the bank by structure, rewrite slugs, append migrations
   and cards to existing bricks.
2. **Normalize role tags and tensions.** Run
   `idea_index.py <staging> --suggest-merges` (and on the bank plus staging
   together). For each suggested pair, decide by meaning whether the two tags
   name the same job; rewrite the losing tag everywhere (cards' `roles` and
   `tensions`, bricks' `roles` and migration rows, moves' `role`). Keep the tag
   the bank already uses. The index matches tags exactly, so an unmerged
   synonym hides a migration gap.
3. Copy only after `idea_index.py` on the staged folder reports no broken links.

A half-finished bulk run never touches the bank.

## Gem taxonomy

Use these values in `gem_types` and in `[gem: ...]` margin tags.

| Gem type | What it is |
|----------|-----------|
| `migration-gap` | A brick mature in field X fits an open tension in field Y, and Y has not used it |
| `lifted-constraint` | A brick was forced by a limit of its time; the limit has gone |
| `unpopular` | Few agree, and the reason is diagnosed as one of the gem reasons below |
| `view-model` | The author's picture, hunch or surprise is reusable beyond the source |
| `convergence` | Unrelated groups reached the same role with different bricks: the role is real |
| `rejected-alternative` | A "we tried X but" passage; X may win once its constraint is gone |
| `contradiction-resolved` | The source resolves a want-X-and-not-X instead of trading off |

### Why is it unpopular?

| Reason | Gem? |
|--------|------|
| The bet is wrong | No: drop it |
| A constraint of its time, now lifted | Yes: pair with `lifted-constraint` |
| Wrong vocabulary or field: the people who need it don't read it | Yes: pair with `migration-gap` |
| Unfashionable: the field is chasing another direction | Yes |
| Poor execution, good bet | Yes: redo it well |
| Lives in another language community | Yes |

## Mutation operators

These, with `split`, `join` and `fuse`, are the seed operations (`seeds.md`),
including but not limited to.

| Operator (`move_type`) | Move |
|------------------------|------|
| `substitute-brick` | Keep the role, change the brick (C → D) |
| `substitute-operator` | Change how bricks combine: sequence → loop, tree, gate, adversarial |
| `remove` | Drop a brick; does the bet still hold? |
| `lift-constraint` | Rebuild a brick as if its limit were gone |
| `invert` | Reverse order, direction, or who does what |
| `migrate-brick` | Keep the brick, move it to another field or role |
| `transfer` | Keep the bet, apply it to another field's tension (the bricks may change) |
| `correct-parameter` | Keep the recipe, fix a number the parent got wrong (a dose, a threshold, a ratio) |
| `relabel` | Keep the structure, rename what it is for; the new name changes who uses it |
| `retarget` | Keep the method, change the outcome it optimises or is judged by |
| `cross-card` | Take a brick or operator from another card |
| `resolve-contradiction` | Separate the want-X-and-not-X in time, space, scale or condition |
| `lens-transfer` | See problem P through another person's or field's lens |
| `lens-inversion` | Assume the opposite of the dominant lens and see which solution appears |
