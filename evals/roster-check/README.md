# Roster check: builder and brain

Cards for choosing the models behind the agent-ops `builder` and `brain` roles
(`~/.dotfiles/home/.ccp/hub/skills/agent-ops/roster.md`). Run each candidate twice, in print mode, in a
scratch folder outside `/tmp` (agy cannot read `/private/tmp`), for example `~/.cache/agent-ops/<date>-roster-check/`.

## builder

1. Copy `builder/template/` to a new folder per run, then `git init` and commit it.
2. Run the candidate there with `builder/prompt.md` as the prompt:

```sh
claude -p --model haiku --permission-mode acceptEdits --allowedTools 'Bash(python3 -m unittest*)' -- "$(cat prompt.md)"
omp -p --model opencode-go/glm-5.3-flash --cwd "$PWD" "$(cat prompt.md)"
agy --model gemini-3.8-flash-medium --mode accept-edits -p="$(cat prompt.md)"   # agy's -p takes the next word as the prompt
```

3. Pass: `git status --porcelain` lists only `duration.py` (ignore `__pycache__`), and after copying
   `builder/hidden/test_duration.py` over the run's test file, `python3 -m unittest -q` says `OK`.
4. Pick the cheapest candidate that passes both runs at a speed close to the fastest.

## brain

Give each review card in `brain/` as the whole prompt (no tools needed). The planted defects:

| Card | Planted |
|---|---|
| `review-1-pagination.md` | `page` has no default, so `list_users()` breaks its callers (drift); `page * per_page` skips the first page (bug) |
| `review-2-ttl-cache.md` | an expired entry still takes a slot (bug); a write to an existing key keeps the old timestamp (bug); `time.time()` where the card says `time.monotonic()` (drift) |

Pass: every planted defect named, in both runs. Deeper findings (eviction still counts expired entries;
an O(1) purge needs a second order) and checking by running the code separate the strong candidates.

## Results

| Date | Role | Result |
|---|---|---|
| 2026-11-18 | builder | All passed. Claude Sonnet 36/38 s, Haiku 46/49 s, agy Flash medium 61/70 s, omp GLM-5.3-Flash 73/78 s, omp DeepSeek-V4.1-Flash 337/275 s. Picked Haiku. |
| 2026-11-18 | brain | Opus high, Fable, Sonnet, Haiku, agy Hydrogen high, omp GLM-5.3: every planted defect found in both runs. Opus high went deepest both runs and ran the code; Fable matched it, slower. Picked Opus high. |
