# Close a session

Formats come from `../idea-bank/references/schema.md`. Then commit
with the idea-bank steps.

| File | Write |
|------|-------|
| `readings/YYMMDD-<slug>.md` | `Reading`: mode (`brief`, `deep` or `skim`), stage, `# Recall` (step-0 result or `skipped: overloaded`), the owner's guess, the notes table `\| Owner \| Claude \| gem \| hint \|` (hint 1–3 for each Claude note, `-` for the owner's), disagreements, mutations as the schema's Mutations table (the owner's rows first, origin `owner`), kill test, teach-back, what we learned |
| `cards/<slug>.md` | `Idea Card`. Deep mode: The owner's text, plus Claude's links and the Raw section. Brief mode: Claude may write it |
| `bricks/`, `lenses/`, `moves/` | New bricks, lenses and moves met in the session; update `cards` and `migrations` on existing ones |
| `me/known-bricks.md` | `seen` for each new brick in a core or adjacent cluster; `owned` only with evidence (the owner explained it, or spotted it in another source); write the evidence |
| `me/taste.md` | Gems the owner saw that Claude missed, with gem type |
| `me/progress.md` | One row: date, reading, mode, unaided gems (finding gems), roles named right of total (naming roles), Owner-unique mutations (proposing mutations), level-3 hints, gems Claude missed, skips. Check the stage criteria; propose a stage change to the owner, never apply it silently |
| `me/interest-state.md` | When the owner zoomed, add 1 to the cluster's `Zooms`; when they said "go deep on X", log the signal. Propose a level change, the owner decides |

Last, tell the owner in one or two lines what changed in their state (new owned bricks,
stage, a rising skip share) in their chat language.
