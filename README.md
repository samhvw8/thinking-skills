# thinking-skills

Agent skills for thinking harder and wider than one pass of a model: get past the first,
most typical answer, look at a problem through several minds at once, build ideas on each
other, and pressure-test a decision.

| Skill | What it does | Agents |
|-------|--------------|--------|
| `creative` | Gets past the model's first, most typical answer on names, ideas, campaign angles, hooks and story premises: fences off the obvious answers, generates from several methods, checks names and prior art outside the model | One |
| `heavy-think` | Classifies a hard problem (brainstorm, perspectives, solve, decompose, unstick, debate) and runs parallel agents on it, then synthesizes | Several, in parallel |
| `council` | Collaborative brainstorm where perspectives build on each other ("yes, and…"); a live team or a file-based session of 5–12 agents dealt lens and technique cards | 2–12 |
| `debate` | Live debate between named debaters who argue on a shared board and in direct duels; you moderate and keep what survived | 2–4 debaters |
| `ambition` | Does a task, or rewrites a prompt, at a higher level on seven axes, each with a 0-3 ladder: the goal behind the goal (Altitude), an expert's raw data, real instruments and an outside judge (Depth), methods from other fields (Range), a clock tight enough to change the method (Speed), the whole class instead of one case (Reach), a result that lasts and makes the next task cheaper (Horizon), and evidence a sceptic accepts (Proof). Writes a brief with a contract and waits for your OK; `/ambition high` adds mental-model cards and three approaches | One (Range can fan out) |
| `idea-bank` | The shared store for the idea skills: where the bank lives (`$IDEA_HOME`, else `~/ideas`), the formats of idea cards, bricks (pieces of an idea named by the job they do), lenses, moves and the owner's state files, plus an offline index (links, convergence, migration gaps), a hybrid search and a hand dealer | None (scripts) |
| `idea-mine` | Breaks a paper, article, talk, repo or social thread into its bricks and files an idea card: what the author believed and bet on, the recipe by role, what changed from the parent source, and the gems. One source or many in bulk | One, or up to 6 in bulk |
| `idea-forge` | Makes new ideas by recombining bricks (swap, move to another field, change how pieces combine, remove, invert) and designs the cheapest test that could kill each one | One |
| `idea-scout` | Sweeps the owner's scopes for sources that carry an idea gem and writes a short batch of triage cards pitched one step above what the owner knows; records votes and runs a monthly retro | One |
| `co-read` | Reads one source together with the owner, idea-first: a brief by default, or a deep session where the owner does the generative steps and the agent guides and runs experiments | One |
| `idea-present` | The `/idea-present [on\|off]` switch: in present mode the owner writes first in co-read, idea-forge and idea-scout; by default the agent does every step | None |

`heavy-think` is the core: `council`, `debate` and `creative` read its files (the
perspective deck, the scoring rubric, the live protocol). Install them side by side.
`ambition` stands alone; it hands multi-field work to `heavy-think` or `council` when
they are installed.

The idea skills share one bank. `idea-mine`, `idea-forge`, `idea-scout`, `co-read` and
`idea-present` read `idea-bank` beside them (`../idea-bank/...`), so install `idea-bank`
with any of them. The bank's owner is the person it belongs to; facts about them (name,
chat language, presence default, compute, starting scopes) live in the bank's
`me/profile.md`, never in a skill. Set `IDEA_HOME` to the bank's folder, or the skills use
`~/ideas`.

## Install

| Where | How |
|-------|-----|
| Claude Code, as a plugin | `/plugin marketplace add samhvw8/thinking-skills`, then `/plugin install thinking-skills@thinking-skills` |
| Claude Code, Codex, Cursor, OpenCode and others | `npx skills add samhvw8/thinking-skills` |
| [ccp](https://github.com/samhvw8/claude-code-profile) | `ccp install samhvw8/thinking-skills skills/heavy-think --link .` (list more `skills/<name>` to install several; for the idea skills: `skills/idea-bank skills/idea-mine skills/idea-forge skills/idea-scout skills/co-read skills/idea-present`) |
| By hand | Copy the folders in `skills/` into your harness's skills folder (for example `~/.claude/skills/`), keeping them side by side |

## Worth knowing

- **Not tied to one harness.** The skills name capabilities (spawn a sub-agent, a live
  team) and model tiers (`strong`, `session`, `fast`), never one harness's tools or models.
  [`heavy-think/references/harness.md`](skills/heavy-think/references/harness.md) maps them
  to Claude Code, opencode and omp, with a fallback for a harness that has no sub-agents.
  `heavy-think/tests/test_harness.py` fails when a vendor name appears unlabelled.
- **Live modes need a live-team transport.** `debate`, and the live modes of `council` and
  `heavy-think`, need agents that take turns and talk to each other. They all run one protocol
  (a shared board, lead-run turns, short duels:
  [`live-protocol.md`](skills/heavy-think/references/live-protocol.md)) on any of three
  transports: harness-ops sessions through the [`agent-ops` skill](https://github.com/samhvw8/dotfiles/tree/main/home/.ccp/hub/skills/agent-ops)
  ([termctl](https://github.com/samhvw8/termctl); any harness and model, one visible terminal
  session per member, and the only one that mixes model families), Claude Code agent teams
  (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, main session only, not together with Code Mode),
  or omp named tasks. Without one, these modes run written rounds of sub-agents and say so.
  `council full` is file-based and runs in any harness with sub-agents.
- **Multi-agent runs cost more.** A `council full` session runs 5–12 agents; `creative`
  is one agent and about the cost of a normal answer.
- **The deck can use an outside ranker, optionally.** `heavy-think/deck.py` fits the
  perspective deck to your question. It uses Cloudflare Workers AI when `CLOUDFLARE_*`
  credentials are set, else TypeSafe when `TYPESAFE_API_KEY` is set, else an offline BM25
  ranking. Nothing is sent anywhere unless you set one of those up.
- **Hand-offs to other skills** (for example `arena`, or `paper-appraisal`, `paper-download`,
  `paper-replicate` and `lead-researcher` in the idea skills) are suggestions; they apply only
  when those skills are installed.
- **The idea bank's search runs a local embedding model.** `idea_search.py` starts llama.cpp's
  `llama-server` with EmbeddingGemma (downloaded on first use; set `IDEA_LLAMA_SERVER` to the
  binary). Its optional `--rerank` makes one call through the Claude Code CLI; without that CLI,
  skip it. The index (`idea_index.py`) and the dealer are offline and need no model.
- **`ambition` needs real tools for Depth and its judge**: a shell, access to your data
  and checks it can run. In a plain chat it still writes the brief, and it says which
  checks stayed on paper. It suggests a bigger scope but never takes one.

## Tests

`python3 -m unittest discover -s skills/heavy-think/tests` checks the deck (standard
library only, no network). `skills/creative/evals/evals.json` holds the creative eval
cases; they are judged by a blind LLM judge in both orders, not by a script.
`evals/ambition/` has eight cases (honesty twice, scope, rewrite, depth, systems, the
approval gate, auto mode) with graders, a receipts check against the transcript, a
blind judge pass and `run-all.sh` to run them headless; see
[evals/ambition/README.md](evals/ambition/README.md). `python3 -m unittest discover -s
skills/ambition/tests` checks ambition's dealer and deck. `uv run --with pytest --with pyyaml
--with numpy pytest skills/idea-bank/scripts skills/idea-mine/scripts` checks the idea bank's
index, search, dealer and quote checker on a synthetic fixture bank (no model, no network).
`evals/agent-ops-split/` is the blind
eval that split the agent-ops skill into a core and reference files (2026-11-18); its result is in
[evals/agent-ops-split/RESULT.md](evals/agent-ops-split/RESULT.md).

## Shared decks

Every card lives once, in [`decks/`](decks/README.md): one JSON file per kind (lenses,
techniques, mental models, patterns, Range fields, reframes and more), checked against
`decks/schema.json`. `python3 tools/build_decks.py` writes each skill its own copy, as
`decks/bundles.json` lists, so every skill installs and runs alone (ccp and `npx skills`
install only the skill folder). Edit `decks/`, never a built copy, then rebuild.
`python3 -m unittest discover -s tests` fails on a stale copy, a dangling id, a skill that
reads another skill's deck, or a skill that breaks when installed alone.

## License

MIT
