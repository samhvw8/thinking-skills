# Team Brainstorm

Collaborative ideation using **agent teams** — named, persistent teammates that *build on each other's ideas* directly by message (`SendMessage` in Claude Code). The generative counterpart to team-debate: where debate prunes by conflict, a council grows by cross-pollination.

## Contents
- Why teams beat isolated parallel subagents
- Debate vs council
- Prerequisites, When to use
- The lead's playbook
- Brainstormer spawn prompt
- Facilitation rules
- Variants, Fallback, Related

## Why teams beat isolated parallel subagents (for ideation)

The standard Brainstorm mode (Stage 3) spawns **isolated subagents** — each explores alone and never sees the others. Collision happens **once**, later, inside the lead's synthesis. Ideas never fertilize each other.

| | Isolated subagents | Team brainstorm (teammates) |
|---|---|---|
| Idea exposure | Each agent blind to the others | Each sees others' ideas live |
| Collision | Once, in the lead's head | Continuous, between agents |
| Compounding | None — N separate lists | A's idea → B extends → C leaps |
| Output | Union of independent ideas | Emergent ideas in *no* single agent |

Continuous cross-pollination is the whole point — the "1+1=3" that isolated fan-out can't produce.

## Debate vs council (don't confuse the two)

| | Team **debate** | Team **brainstorm** (council) |
|---|---|---|
| Goal | Decide / pressure-test | Expand / discover |
| Core move | "No, but…" — attack | "Yes, and…" — build on |
| Converges by | Elimination (what survives) | Synthesis (what combines) |
| Failure mode | Hostility / stalemate | **Groupthink / premature agreement** |

## Prerequisites

- A harness with live teams (`harness.md`; in Claude Code, `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`). Without one, no teammates — use the isolated-subagent Brainstorm (SKILL.md Mode 1, Stage 3).
- **Main session only.** Agent teams have no nested teams — a teammate cannot spawn teammates. So team-brainstorm runs only when `heavy-think` is followed in the **main conversation**, not inside a subagent.
- Ideation is think-and-message only (no file edits) → no file-conflict risk. Ideal team use case.

## When to use

Use teammates over isolated subagents when **idea compounding matters more than raw breadth**:

- Open-ended product / strategy / design exploration where the best idea is a *combination*
- "How might we…", "what could we build", "expand on this direction"
- Stakes justify ~3–5× the compute of a single pass

Do NOT use for: a quick list (isolated subagents are cheaper), or any decision (use debate).

## The lead's playbook

You (the main session) are the **facilitator + synthesizer**. You do not generate ideas — you frame, spawn, spark, and harvest.

1. **Frame the question — open, not binary.** A "how might we…" or "what could we…", with constraints and what a great idea looks like. No yes/no motions (that's debate).
2. **Deal distinct cards.** 2–4 teammates. Run `python3 "$HT/deck.py" deal --members N [--preset P] --question "<the problem>"` (`HT`: the heavy-think skill folder, the parent of this `references/` folder) and give each teammate its lens *and* technique. Name them. Designate one **wildcard** to keep the space open. Keep the dealt provocations for Phase 2.
3. **Spawn all in one message.** One spawn per teammate, model tier `strong`, each with FULL context (teammates don't inherit your history) and the roster *by name*.
4. **Phase 1 — Diverge.** Each posts its initial ideas *independently* first (seed the space before anyone anchors). Tell them to hold judgment.
5. **Phase 2 — Cross-pollinate.** Now they read each other and BUILD: "yes-and", combine two ideas, push one further, find the adjacent idea. Each message must **add or extend**, never just approve.
6. **Phase 3 — Cluster & elevate.** They group ideas, surface the most novel/promising, and develop the top few deeper together.
7. **Synthesize yourself** (the harvest is the point; delegating it adds one more voice instead of a synthesis). Harvest the *expanded* idea set: the standout concepts, the surprising combinations no single lens produced, ranked by novelty/value, plus what to explore next, and the rest of the idea set one line each. Write it as in `../SKILL.md` (The reply): ideas, not who proposed them. Then shut the teammates down.

## Brainstormer spawn prompt (template)

Spawn each teammate (named, model tier `strong`) with:

```
You are {name}, a collaborator in a live multi-agent brainstorm. Other collaborators
message you and you message them by name through the team's message tool. Nobody sees your
plain text output, so anything you want to contribute goes through a message.

QUESTION: {open question}
CONTEXT & CONSTRAINTS: {context} — {constraints}
YOUR LENS: {lens_name}: {lens_asks} Generate what only this lens reveals; the others cover the rest.
DELIVER: {lens_delivers}
HOW YOUR LENS WORKS: {lens_instruments}
YOUR TECHNIQUE: {technique_name}: {technique_how}
YOUR COLLABORATORS: {name: lens, name: lens, ...}
FACILITATOR: the lead spawned you and will spark and close the session.

Ground your ideas with your tools: do what HOW YOUR LENS WORKS says with real material (web
and social search, files the question points at, arithmetic in the shell). A fact from outside
the question is either checked, with its source, or marked "(unchecked)".

How to collaborate:
1. Diverge first: send 2–4 raw ideas from your lens to the group. Hold judgment; quantity
   and range now, not polish.
2. Build, don't judge: when a collaborator's idea reaches you, extend it ("yes-and"),
   combine it with yours, or push it somewhere new, through your own lens. A message that
   only agrees gives the group nothing, so each one adds. Engage their latest idea, and
   name the ideas you build on.
3. Chase the surprise: prefer the idea that wouldn't exist without two lenses colliding.
4. Stay divergent until the facilitator calls convergence, then help cluster and pick
   the strongest few.

Don't edit files or spawn agents: you build through messages, and the lead owns the output.
```

## Facilitation rules (beat groupthink)

A council's failure mode is the inverse of a debate's — agreeing too fast and collapsing the diversity that made it valuable. Counter each:

- **Diverge before converge.** Enforce Phase 1 (independent ideas) before any building. Early anchoring kills range.
- **Add, don't approve.** Reject "good idea!" with no extension — every message must build.
- **Keep a wildcard.** One teammate must keep injecting "what if the opposite / what's missing."
- **Spark, don't generate.** Inject the deck's provocations (`perspectives.json` → `provocations`, dealt with the cards) one at a time — never add your own ideas; that defeats the independence.
- **Detect false consensus:** if they converge fast, push "you agreed too early — find a wilder option." Converge only at Phase 3.
- **Harvest the emergent, not the obvious** — the value is ideas that exist in no single teammate's output.

## Variants

| Variant | Setup | Use when |
|---|---|---|
| **Open ideation** | Each owns a generative lens, free build | Greenfield "what could we build" |
| **How-might-we** | Frame as HMW; teammates riff and combine | Turning a problem into opportunities |
| **Stakeholder council** | Teammates *are* personas (user, ops, PM, skeptic) | Pressure-testing a direction for blind spots |
| **Combine-and-extend** | Phase 2 forces every idea to merge with another | Forcing cross-pollination, breaking silos |

## Fallback

If your harness has no live teams, or you're inside a sub-agent, use the standard **isolated parallel Brainstorm** (SKILL.md Mode 1, Stage 3) — weaker (no live cross-pollination) but needs no team support.

## Related

- `../SKILL.md` — Mode 1: Brainstorm (Escalation: Team Brainstorm)
- `team-debate.md` — adversarial counterpart (decide / pressure-test)
- `brainstorm-agent-prompt.md` — single-pass perspective + stress-test prompts
- `perspectives.json` — the lens, technique and provocation deck, with presets by scenario (dealt by `../deck.py`)
- `../../council/SKILL.md` — full mode: the same session as file-based rounds, 5–12 members, blind scoring
