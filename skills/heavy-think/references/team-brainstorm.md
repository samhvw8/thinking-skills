# Team Brainstorm

Collaborative ideation by a **live team**: named, persistent members that *build on each other's ideas* on a shared board, in turns, and in short duels. It runs the live protocol (`live-protocol.md`) on any live-team transport (`harness.md`, Live-team transports). The generative counterpart to team-debate: where debate prunes by conflict, a council grows by cross-pollination.

## Contents
- Why a live team beats isolated parallel subagents
- Debate vs council
- Prerequisites, When to use
- The lead's playbook
- Brainstormer spawn prompt
- Facilitation rules
- Variants, Fallback, Related

## Why a live team beats isolated parallel subagents (for ideation)

The standard Brainstorm mode (Stage 3) spawns **isolated subagents** — each explores alone and never sees the others. Collision happens **once**, later, inside the lead's synthesis. Ideas never fertilize each other.

| | Isolated subagents | Team brainstorm (live members) |
|---|---|---|
| Idea exposure | Each agent blind to the others | Each reads the others' ideas on the board, round by round |
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

- A live-team transport (`harness.md`, Live-team transports). Without one, no live members — use the isolated-subagent Brainstorm (SKILL.md Mode 1, Stage 3).
- The transport's own limits apply. Claude Code agent teams run only from the main session (a teammate cannot spawn teammates); inside a subagent, use harness-ops sessions or the Fallback.
- Ideation writes only the board, append-only → no file-conflict risk. Ideal live-team use case.

## When to use

Use a live team over isolated subagents when **idea compounding matters more than raw breadth**:

- Open-ended product / strategy / design exploration where the best idea is a *combination*
- "How might we…", "what could we build", "expand on this direction"
- Stakes justify ~3–5× the compute of a single pass

Do NOT use for: a quick list (isolated subagents are cheaper), or any decision (use debate).

## The lead's playbook

You (the lead) are the **facilitator + synthesizer**. You do not generate ideas — you frame, spawn, spark, and harvest.

1. **Frame the question — open, not binary.** A "how might we…" or "what could we…", with constraints and what a great idea looks like. No yes/no motions (that's debate).
2. **Deal distinct cards.** 2–4 members. Run `python3 "$HT/deck.py" deal --members N [--preset P] --question "<the problem>"` (`HT`: the heavy-think skill folder, the parent of this `references/` folder) and give each member its lens *and* technique. Name them. Designate one **wildcard** to keep the space open. Keep the dealt provocations for Phase 2.
3. **Open the session and start everyone.** Create `council/<YYYYMMDD-HHMM>-<slug>/` with the shared brief and an empty `board.md` (`live-protocol.md`, The session folder). Start one member per card (transport table), model tier `strong` unless the diversity setting (`harness.md`, Diversity) adds other families, each with FULL context (members don't inherit your history) and the roster *by name*.
4. **Phase 1 — Diverge (round 1, alone).** Send all members `Your turn: round 1`. Each appends its initial ideas *without reading the board* (seed the space before anyone anchors). Tell them to hold judgment.
5. **Phase 2 — Cross-pollinate (build-on turns).** Give turns in a fixed order, one member at a time: each reads the board and BUILDS — "yes-and", combine two ideas, push one further, find the adjacent idea. Each block must **add or extend**, never just approve. Put a dealt provocation in the turn's focus line when the board goes quiet or agrees too fast. With 3 members, when two ideas from different members look like they belong together, you may open one **short duel** between their owners to merge them (3 messages each; the merged idea goes on the board). With 2 members, that duel *is* Phase 2; with 4, merges happen in turns (`live-protocol.md`, Shape by size).
6. **Phase 3 — Cluster & elevate.** One more round of turns: each groups ideas, names the most novel/promising, and develops one of the top few deeper.
7. **Synthesize yourself** (the harvest is the point; delegating it adds one more voice instead of a synthesis). Harvest the *expanded* idea set: the standout concepts, the surprising combinations no single lens produced, ranked by novelty/value, plus what to explore next, and the rest of the idea set one line each. Write it as in `../SKILL.md` (The reply): ideas, not who proposed them. Then shut every member down (transport table).

## Brainstormer spawn prompt (template)

Start each member (named, model tier `strong`) with this, followed by the member protocol block from `live-protocol.md`:

```
You are {name}, a collaborator in a live multi-agent brainstorm. You build on the other
collaborators' ideas on a shared board, in the turns the facilitator gives you, and in a
short duel when the facilitator opens one. The protocol below says how.

QUESTION: {open question}
CONTEXT & CONSTRAINTS: {context} — {constraints}
YOUR LENS: {lens_name}: {lens_asks} Generate what only this lens reveals; the others cover the rest.
DELIVER: {lens_delivers}
HOW YOUR LENS WORKS: {lens_instruments}
YOUR TECHNIQUE: {technique_name}: {technique_how}
YOUR COLLABORATORS: {name: lens, name: lens, ...}
FACILITATOR: the lead started you and will give turns, spark and close the session.

Ground your ideas with your tools: do what HOW YOUR LENS WORKS says with real material (web
and social search, files the question points at, arithmetic in the shell). A fact from outside
the question is either checked, with its source, or marked "(unchecked)".

How to collaborate:
1. Diverge first (round 1): append 2–4 raw ideas from your lens. Hold judgment; quantity
   and range now, not polish.
2. Build, don't judge (later rounds): take a collaborator's idea from the board and extend
   it ("yes-and"), combine it with yours, or push it somewhere new, through your own lens.
   A block that only agrees gives the group nothing, so each one adds. Engage their latest
   idea, and name the ideas you build on ("builds on Ada's 2 and Lin's 1").
3. Chase the surprise: prefer the idea that wouldn't exist without two lenses colliding.
4. Stay divergent until the facilitator calls convergence, then help cluster and pick
   the strongest few.

{member protocol block}
```

## Facilitation rules (beat groupthink)

A council's failure mode is the inverse of a debate's — agreeing too fast and collapsing the diversity that made it valuable. Counter each:

- **Diverge before converge.** Enforce Phase 1 (round 1 alone) before any building. Early anchoring kills range.
- **Add, don't approve.** Reject "good idea!" with no extension — every block must build.
- **Keep a wildcard.** One member must keep injecting "what if the opposite / what's missing."
- **Spark, don't generate.** Inject the deck's provocations (`perspectives.json` → `provocations`, dealt with the cards) one at a time — never add your own ideas; that defeats the independence.
- **Detect false consensus:** if they converge fast, push (in the next turn's focus line) "you agreed too early — find a wilder option." Converge only at Phase 3.
- **Harvest the emergent, not the obvious** — the value is ideas that exist in no single member's output.

## Variants

| Variant | Setup | Use when |
|---|---|---|
| **Open ideation** | Each owns a generative lens, free build | Greenfield "what could we build" |
| **How-might-we** | Frame as HMW; members riff and combine | Turning a problem into opportunities |
| **Stakeholder council** | Members *are* personas (user, ops, PM, skeptic) | Pressure-testing a direction for blind spots |
| **Combine-and-extend** | Phase 2 forces every idea to merge with another | Forcing cross-pollination, breaking silos |

## Fallback

Without a live-team transport, use the standard **isolated parallel Brainstorm** (SKILL.md Mode 1, Stage 3) — weaker (no live cross-pollination) but needs no team support.

## Related

- `../SKILL.md` — Mode 1: Brainstorm (Escalation: Team Brainstorm)
- `team-debate.md` — adversarial counterpart (decide / pressure-test)
- `brainstorm-agent-prompt.md` — single-pass perspective + stress-test prompts
- `perspectives.json` — the lens, technique and provocation deck, with presets by scenario (dealt by `../deck.py`)
- `../../council/SKILL.md` — full mode: the same session as file-based rounds, 5–12 members, blind scoring
