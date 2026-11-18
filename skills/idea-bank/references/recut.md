# Re-cut a brick

Use this when someone asks to look at a brick again through a new angle: "by
what question each part answers", "by where it can fail", "by who pays". The
brick is most often a card's method brick, and the ask often comes in a later
session. Formats are in `schema.md` (Parts and links); this file is the
procedure.

## 1. Find the whole and its cuts

Find the card (`idea_search.py`, or the card titles) and open its method brick.
Its `# Related` lists every cut it has; `idea_index.py <bank> --recuts` shows how
they overlap. Never rewrite or relabel an old cut.

## 2. The angle sets the cut; the registry only names it

Write the angle in the asker's words. Cut where the angle says. Only then look
for a label: a registry id from `idea_index.py <bank> --cuts` when one names this
angle, else a new label checked against the labels in use. Never move a boundary
to fit a registry kind: a generic cut (`functional`, `temporal`) is not the
angle that was asked.

## 3. Re-read the source for the angle

The bank holds what the first cut needed, not what a new angle needs. Open the
source from the card's `resource` and the pointer in `# Raw`. Read its outline,
then only the sections this angle needs: for an angle about assumptions, the
assumptions and limitations; about questions or estimates, the steps that
produce each number; about cost, the methods and resources. Do not re-read the
whole text by default.

Add one line to the card's `# Raw`: `Re-read for cut <label>: <sections>`, then
the new quotes with their sections. When the source cannot be reached, write
`Re-read for cut <label>: none (bank only)` and say so in the reply.

## 4. Cut from the source, then compare

Walk the angle over the source, not over the old parts: for each group the
angle names (each question, failure or cost), find what in the source does that
job. Only then lay the old parts beside it. The new cut must draw at least one
new boundary:

| Boundary | What it looks like | How to write it |
|----------|--------------------|-----------------|
| Split | One old part does two jobs under this angle | Two new bricks. List them in the new cut, and add them to the old part's `parts` with the same `cut` |
| Merge | Several old parts do one job under this angle | One new brick bound from them (`how: bind`, same `cut`) |
| Add | A piece no old cut has: a hidden term the result depends on, an assumption nobody estimated, an arrangement at a hand-off (where one part's output becomes another's input), a rival placement (where else a part could sit) | A new brick, matched against the bank first. A rival placement also gets a row in the card's `# Mutations` (the move that puts the part there) |

Old parts that keep their boundary go in the new cut too, each with its new
`group`.

**No new boundary, no cut.** When every piece of the angle is an old part and
only the names change, write no `parts`. Add a `notes` entry on the brick
(`{ at, note: "angle <...>: no new boundary; it re-tags cut <label>" }`) and
tell the asker in one line.

## 5. Write it

- Each part entry: `{ to, how, cut, group }`. `group` names the piece's place
  under this angle in a few words: the question it answers, the stage, the risk.
- On the method brick, add a `cuts` entry: `{ cut, angle, shows }`. `shows` is
  one line: what this cut shows that the other cuts do not.
- Run `idea_index.py <bank> --write`. It puts a `# Cuts compared` table on the
  card, after the Recipe: a row per piece, a column per cut. Then run
  `--recuts`. A `RE-TAG` or `NO NEW BOUNDARY` flag means step 4 failed: fix the
  cut, or turn it into a note.

## 6. Reply

Show the `# Cuts compared` table with titles in plain words, and the `shows`
line. Name each new boundary in one line: which part split, which parts merged,
what was added. Follow "Rendering for the owner" in `schema.md`.
