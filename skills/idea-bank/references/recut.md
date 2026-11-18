# Re-cut a brick

Use this when someone asks to look at a brick again through a new angle: "by
what question each part answers", "by where it can fail", "by who pays". The
brick is most often a card's method brick, and the ask often comes in a later
session. Formats are in `schema.md` (Parts and links); this file is the
procedure. Its short form, five steps, is the Re-cut section of idea-mine's
`SKILL.md`; this file adds the detail and works without idea-mine.

## 1. Find the whole and its cuts

Find the card (`idea_search.py`, or the card titles) and open its method brick.
Its `# Related` lists every cut it has; `idea_index.py <bank> --recuts` shows how
they overlap.

## 2. The angle sets the cut; the registry only names it

Write the angle in the asker's words. Cut where the angle says. Only then look
for a label: a registry id from `idea_index.py <bank> --cuts` when one names this
angle, else a new label checked against the labels in use, with its question in
each part entry's `note`. Never move a boundary to fit a registry kind: a
generic cut (`functional`, `temporal`) is not the angle that was asked.

## 3. Re-read the source for the angle

The bank holds what the first cut needed, not what a new angle needs. Get the
source in this order, and stop at the first that works:

1. The local copy named in the card's `# Raw` (`Local copy: <path>`).
2. A search of the disk for that file name (or the source's title), under the
   folders the path names and the bank's parent folders.
3. The card's `resource` URL.

Read its outline, then the sections this angle needs: for an angle about
assumptions, the assumptions and limitations; about questions or estimates, the
steps that produce each number; about cost, the methods and resources.

Add one line to the card's `# Raw`: `Re-read for cut <label>: <sections>`, then
the new quotes with their sections. Only when all three routes fail, write
`Re-read for cut <label>: none (bank only; tried <each route>)` and say so in
the reply.

## 4. Cut from the source, then compare

Walk the angle over the source, not over the old parts: for each group the
angle names (each question, step, cost or failure), find what in the source
does that job. Only then lay the old parts beside it. The new cut must draw at
least one new boundary:

| Boundary | What it looks like | How to write it |
|----------|--------------------|-----------------|
| Regroup | The angle's groups cut across the old cut's: one group holds parts an old cut keeps apart, or two groups split parts an old cut keeps together | The old bricks in the new cut, each with its `group`. No new brick |
| Split | The source shows one old part doing two jobs under this angle | Two new bricks, each titled by the job that differs from its parent. List them in the new cut, and add them to the old part's `parts` with the same `cut`. A child whose description would restate the parent is not filed: keep the parent in the cut and name the second job in its entry's `note` |
| Merge | Several old parts do one job under this angle | One new brick bound from them (`how: bind`, same `cut`) |
| Add | A piece no old cut has: a hidden term the result depends on, an assumption nobody estimated, an arrangement at a hand-off (where one part's output becomes another's input), a rival placement (where else a part could sit) | A new brick, matched against the bank first. A rival placement also gets a row in the card's `# Mutations` (the move that puts the part there) |

Reuse before you make. A regroup is a full boundary: most angles need no new
brick. Split an old brick only when the source shows it doing two jobs;
otherwise place it in a group.

**No new boundary, no cut.** When the angle's groups only rename an old cut's
groups, write no `parts`. Never split a brick to make the cut count. Add a
`notes` entry on the brick
(`{ at, note: "angle <...>: no new boundary; it re-tags cut <label>" }`) and
tell the asker in one line.

## 5. Write it

Never edit lines an earlier session wrote, on the card or on a brick. Add beside
them; a correction is a dated line next to the one it corrects.

- **The card.** Add a section at the end of the Recipe, after the `Operator:`
  line and any earlier cut sections: `## Cut: <label> — <the angle in plain
  words>`. Its table has a row per group of the angle (each question, step, cost
  or failure), a column for what the source says (with its section) and a
  column for the pieces that answer it (slugs, old or new). Close with one line:
  `What this cut shows that the others do not: ...`.
- **The method brick.** Each part entry: `{ to, how, cut, group }`, plus `note`
  for a new label. `group` is the row of the card's table the piece sits in.
  Add a `cuts` entry: `{ cut, angle, shows }`, with the same `shows` line.
- Run `idea_index.py <bank> --write`. It puts the generated `# Cuts compared`
  table (a row per piece, a column per cut) on the method brick. Then run
  `--recuts`. A `RE-TAG` or `NO NEW BOUNDARY` flag means section 4 failed: fix
  the cut, or turn it into a note.

## 6. Reply

Open with what the angle shows (the `shows` line, in plain words), then the
card's `## Cut:` table with plain-word titles. Name each new boundary in one
line: which parts regrouped, which part split, which parts merged, what was
added. Put caveats and bookkeeping last. Follow "Rendering for the owner" in
`schema.md`.
