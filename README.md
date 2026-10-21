# thinking-skills

Agent skills for thinking harder and wider than one pass of a model: get past the first,
most typical answer, look at a problem through several minds at once, build ideas on each
other, and pressure-test a decision.

| Skill | What it does | Agents |
|-------|--------------|--------|
| `creative` | Gets past the model's first, most typical answer on names, ideas, campaign angles, hooks and story premises: fences off the obvious answers, generates from several methods, checks names and prior art outside the model | One |
| `heavy-think` | Classifies a hard problem (brainstorm, perspectives, solve, decompose, unstick, debate) and runs parallel agents on it, then synthesizes | Several, in parallel |
| `council` | Collaborative brainstorm where perspectives build on each other ("yes, and…"); live teammates or a file-based session of 5–12 agents dealt lens and technique cards | 2–12 |
| `debate` | Live debate between named teammates who argue through messages; you moderate and keep what survived | 2–4 teammates |
| `ambition` | Does a task, or rewrites a prompt, at a higher level: the goal behind the goal (Altitude), an expert's raw data, real instruments and an outside judge (Depth), and methods from other fields (Range). Writes a brief with a contract and waits for your OK; `/ambition high` adds mental-model cards and three approaches | One (Range can fan out) |

`heavy-think` is the core: `council`, `debate` and `creative` read its files (the
perspective deck, the scoring rubric, the team protocols). Install them side by side.
`ambition` stands alone; it hands multi-field work to `heavy-think` or `council` when
they are installed.

## Install

| Where | How |
|-------|-----|
| Claude Code, as a plugin | `/plugin marketplace add samhvw8/thinking-skills`, then `/plugin install thinking-skills@thinking-skills` |
| Claude Code, Codex, Cursor, OpenCode and others | `npx skills add samhvw8/thinking-skills` |
| [ccp](https://github.com/samhvw8/claude-code-profile) | `ccp install samhvw8/thinking-skills skills/heavy-think --link .` (list more `skills/<name>` to install several) |
| By hand | Copy the folders in `skills/` into your harness's skills folder (for example `~/.claude/skills/`), keeping them side by side |

## Worth knowing

- **Not tied to one harness.** The skills name capabilities (spawn a sub-agent, a live
  team) and model tiers (`strong`, `session`, `fast`), never one harness's tools or models.
  [`heavy-think/references/harness.md`](skills/heavy-think/references/harness.md) maps them
  to Claude Code, opencode and omp, with a fallback for a harness that has no sub-agents.
  `heavy-think/tests/test_harness.py` fails when a vendor name appears unlabelled.
- **Live modes need live teams.** `debate`, and the live modes of `council` and
  `heavy-think`, need agents that message each other. Today only Claude Code has them: set
  `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` and run from the main session. Elsewhere these
  modes run written rounds of sub-agents and say so. `council full` is file-based and runs
  in any harness with sub-agents.
- **Multi-agent runs cost more.** A `council full` session runs 5–12 agents; `creative`
  is one agent and about the cost of a normal answer.
- **The deck can use an outside ranker, optionally.** `heavy-think/deck.py` fits the
  perspective deck to your question. It uses Cloudflare Workers AI when `CLOUDFLARE_*`
  credentials are set, else TypeSafe when `TYPESAFE_API_KEY` is set, else an offline BM25
  ranking. Nothing is sent anywhere unless you set one of those up.
- **Hand-offs to other skills** (for example `arena`) are suggestions; they apply only when
  those skills are installed.
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
skills/ambition/tests` checks ambition's dealer and deck. `tools/build_deck.py` rebuilds
that deck (models with a move and a receipt, Range field cards, and lenses copied from
heavy-think); it refuses to build a pattern that would deal no fitted model.

## License

MIT
