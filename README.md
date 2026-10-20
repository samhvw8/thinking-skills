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

`heavy-think` is the core: `council`, `debate` and `creative` read its files (the
perspective deck, the scoring rubric, the team protocols). Install them side by side.

## Install

| Where | How |
|-------|-----|
| Claude Code, as a plugin | `/plugin marketplace add samhvw8/thinking-skills`, then `/plugin install thinking-skills@thinking-skills` |
| Claude Code, Codex, Cursor, OpenCode and others | `npx skills add samhvw8/thinking-skills` |
| [ccp](https://github.com/samhvw8/claude-code-profile) | `ccp install samhvw8/thinking-skills skills/heavy-think --link .` (repeat for each skill) |
| By hand | Copy the folders in `skills/` into `~/.claude/skills/`, keeping them side by side |

## Worth knowing

- **Live modes need agent teams.** `debate`, and the live modes of `council` and
  `heavy-think`, use Claude Code agent teams: set `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
  and run them from the main session (a subagent cannot start teammates). `council full`
  is file-based and runs anywhere.
- **Multi-agent runs cost more.** A `council full` session runs 5–12 agents; `creative`
  is one agent and about the cost of a normal answer.
- **The deck can use an outside ranker, optionally.** `heavy-think/deck.py` fits the
  perspective deck to your question. It uses Cloudflare Workers AI when `CLOUDFLARE_*`
  credentials are set, else TypeSafe when `TYPESAFE_API_KEY` is set, else an offline BM25
  ranking. Nothing is sent anywhere unless you set one of those up.
- **Hand-offs to other skills** (`arena`, `ambition`) are suggestions; they apply only when
  those skills are installed.

## Tests

`python3 -m unittest discover -s skills/heavy-think/tests` checks the deck (standard
library only, no network). `skills/creative/evals/evals.json` holds the creative eval
cases; they are judged by a blind LLM judge in both orders, not by a script.

## License

MIT
