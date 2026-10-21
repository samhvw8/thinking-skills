# Harness map

The thinking skills name capabilities, not one harness's tools. This file maps each capability to
the tool that provides it. When your harness is not listed, find the closest tool; when none exists,
use the fallback and tell the user what it costs.

## Capabilities

| Capability | Claude Code | opencode | omp (oh-my-pi) | No such tool |
|---|---|---|---|---|
| **Spawn a sub-agent**: a fresh context that gets one prompt and returns one answer | `Agent` tool, `subagent_type: general-purpose` | `task` tool, `subagent_type: general` | `task` tool, agent `task` | Do each job yourself, one at a time (see Fallback) |
| **Parallel sub-agents** | several `Agent` calls in one message | several `task` calls in one message | several `task` calls in one message | sequential |
| **Live team**: named agents that message each other | agent teams: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, main session only, `SendMessage` | none | none | use the skill's no-team fallback |
| **Skill folder** (`SKILL_DIR`) | `${CLAUDE_SKILL_DIR}`, or the "Base directory for this skill" line | the folder the SKILL.md is in | the folder the SKILL.md is in | the folder the SKILL.md is in |
| **Web search** | any search tool you have: an MCP search server, `WebSearch`, `gh search` | same | same | say the claim is unchecked |
| **Headless run** | `claude -p "<prompt>" --add-dir <skills folder> --allowedTools ...` | `opencode run "<prompt>"` | `omp -p "<prompt>"` | — |

## Model tiers

Skills name a tier, never a model. Pick the model for the tier from what your harness offers.

| Tier | Use | Claude Code | omp | opencode |
|---|---|---|---|---|
| `strong` | the hard thinking: diverge, judge, solve | `opus` (or the session's model when it is stronger) | `@slow` role | the session's model |
| `session` | whatever this session runs on | omit `model` | omit the model | omit the model |
| `fast` | web research, checking claims, bulk reading | `sonnet` | `@smol` role | the session's model, or an agent defined with a cheaper model |

opencode sets a sub-agent's model in the agent's definition, not per call. To get a cheaper `fast`
tier there, define an agent with that model and pass its name as `subagent_type`.

When the harness has only one model, every tier is that model. Say so in the report, because it
changes the cost and the result.

## Fallback: no sub-agents

The parallel modes rely on independence: each agent answers without seeing the others. Without
sub-agents you cannot get it fully, so get as close as you can:

1. Write every job's prompt to a file before you answer any of them.
2. Answer one job at a time. Write each answer to its own file before you start the next.
3. Do not reread an earlier answer until all of them are written.
4. In the report, say the agents were simulated in one context and are less independent.

Live teams have no fallback that keeps the live exchange. Each skill names its own: heavy-think's
Round Protocol, council's full mode, or a debate run as written rounds.
