# Harness map

The thinking skills name capabilities, not one harness's tools. This file maps each capability to
the tool that provides it. When your harness is not listed, find the closest tool; when none exists,
use the fallback and tell the user what it costs.

## Capabilities

| Capability | Claude Code | opencode | omp (oh-my-pi) | No such tool |
|---|---|---|---|---|
| **Spawn a sub-agent**: a fresh context that gets one prompt and returns one answer | `Agent` tool, `subagent_type: general-purpose` | `task` tool, `subagent_type: general` | `task` tool (or `agent()` / `workpool()` in `eval`) | Do each job yourself, one at a time (see Fallback) |
| **Parallel sub-agents** | several `Agent` calls in one message | several `task` calls in one message | `tasks[]` batch in one `task` call, or `workpool()` in `eval` | sequential |
| **Live team**: named members that take turns and talk to each other (`live-protocol.md`) | harness-ops sessions, or agent teams (see Live-team transports) | harness-ops sessions | harness-ops sessions, or named tasks + `agent://` | use the skill's no-team fallback |
| **Append to a shared file**: one atomic append (O_APPEND), never read-modify-write | `Bash`: `cat >> <file> <<'EOF' ... EOF` | shell tool: `cat >> <file> <<'EOF' ... EOF` | `sh 'cat >> <file> <<EOF ... EOF'` inside `eval` (the top-level `bash` tool refuses `>>` redirection) | none: use one file per member, joined by the lead |
| **Batch / chain MCP & tool calls** | parallel tool calls | parallel tool calls | `eval` tool (`await tool.mcp__<server>_<tool>(args)`, `await tool.<name>(args)`, `judge`, `browser`) | sequential tool calls |
| **Skill folder** (`SKILL_DIR`) | `${CLAUDE_SKILL_DIR}`, or the "Base directory for this skill" line | the folder the SKILL.md is in | `skill://<name>` or the `[Skill directory: ...]` footer path | the folder the SKILL.md is in |
| **Web search & fetch** | Parallax MCP (`mcp__parallax_*`), `WebSearch` / `WebFetch`, `gh search` | same | Parallax MCP (`await tool.mcp__parallax_*` in `eval` or `xd://`), `omp` built-in `web_search` and `read` (URLs), `gh search` | say the claim is unchecked |
| **Headless run** | `claude -p "<prompt>" --add-dir <skills folder> --allowedTools ...` | `opencode run "<prompt>"` | `omp -p "<prompt>"` | — |

## Model tiers

Skills name a tier, never a model. Pick the model for the tier from what your harness offers.

| Tier | Use | Claude Code | omp | opencode |
|---|---|---|---|---|
| `strong` | the hard thinking: diverge, judge, solve | `opus` (or the session's model when it is stronger) | `@slow` role | the session's model |
| `session` | whatever this session runs on | omit `model` | omit the model | omit the model |
| `fast` | web research, checking claims, bulk reading | `sonnet` | `@smol` role | the session's model, or an agent defined with a cheaper model |
| `other-family` | live roles that need another family's blind spots: opponent, manager, blind reviewer | a harness-ops member with that role | a harness-ops member with that role | a harness-ops member with that role |
| `open-panel` | extra diversity: members on a mix of open-weight models | harness-ops members with that role | harness-ops members with that role | harness-ops members with that role |

Live members run on `session` unless the playbook, the diversity setting or the user says otherwise.
The lead of a live run is this session; a swarm calls it the `director`. On harness-ops, the agent-ops
skill's Roles section maps each role to a launch command; skill text names only the role. A transport
that runs one model family (agent teams, named tasks on one model) has no `other-family` or
`open-panel`: say so, and run the mode on `session`.

opencode sets a sub-agent's model in the agent's definition, not per call. To get a cheaper `fast`
tier there, define an agent with that model and pass its name as `subagent_type`.

When the harness has only one model, every tier is that model. Say so in the report, because it
changes the cost and the result.

## Diversity

Each live run has a diversity setting. Say which one you use, in one line.

| Setting | Members | When |
|---|---|---|
| `same` | all on `session` | the default |
| `mixed` | `session` plus at least one `other-family` (or `open-panel`) member | automatic for a review, the `cross-model` debate format, or a "diverse" / "tunnel vision" ask |
| `max` | each member a different family | when the user asks for the widest spread |

Members of one family share blind spots, so a review or a pressure-test that must catch what this
model misses needs another family. `mixed` and `max` need a transport that starts other harnesses
(harness-ops sessions).

## Live-team transports

A live mode follows `live-protocol.md`; the transport only delivers it. Use any one your session
has, except that `mixed` and `max` need harness-ops sessions:

1. **harness-ops sessions** (the `agent-ops` skill, https://github.com/samhvw8/dotfiles/tree/main/home/.ccp/hub/skills/agent-ops, and its `harness-ops` CLI, https://github.com/samhvw8/termctl).
   Any harness and any model per member; each member is a visible terminal session (tmux, iTerm2 or
   Herdr). Works from any harness that has a shell, and the only transport for `mixed` and `max`.
   The agent-ops skill's Live team, Swarm and Roles sections have the details.
2. **Claude Code agent teams** (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`). Main session only, because
   a teammate cannot spawn teammates; one model family; and Claude Code Code Mode will not start
   while agent teams are on, so a session cannot use both.
3. **omp named tasks** (`task` tool with `name` on each item, messages through `write agent://<id>`,
   `agent://all` to broadcast). omp only.

| Step | harness-ops sessions | Claude Code agent teams | omp named tasks |
|---|---|---|---|
| Start a member | `harness-ops spawn <harness> --cwd <dir> --label <name> --prompt-file <brief>`; `harness-ops task new` when the member's work is a tracked task (swarm workers) | spawn every named teammate in one message, each with the full brief | one `task` call, `name` on each item |
| Send a turn | `harness-ops send <target> "Your turn: round N"` (`task send <id>` for a task) | `SendMessage` to the teammate by name | `write agent://<id>` |
| Member reaches the lead or a duel partner | `harness-ops send <target> "<text>"`; give every member the lead's and the roster's targets | `SendMessage` by name | `write agent://<id>` |
| Wait | end your turn: the `DONE` message wakes you; as a watchdog, `harness-ops wait-idle <target>` or `task wait --any` in the background | messages arrive on their own | messages arrive on their own |
| Shut down | `harness-ops close <target>`, or `task accept <id> --close`; then check nothing you started is still open | a shutdown request to every teammate | end each member's task |

## Fallback: no sub-agents

The parallel modes rely on independence: each agent answers without seeing the others. Without
sub-agents you cannot get it fully, so get as close as you can:

1. Write every job's prompt to a file before you answer any of them.
2. Answer one job at a time. Write each answer to its own file before you start the next.
3. Do not reread an earlier answer until all of them are written.
4. In the report, say the agents were simulated in one context and are less independent.

Without a live-team transport, nothing keeps the live exchange. Each skill names its own fallback:
heavy-think's Round Protocol, council's full mode, or a debate run as written rounds.
