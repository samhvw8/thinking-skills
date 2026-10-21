---
name: heavy-think
description: "Multi-agent thinking orchestrator: classifies a hard problem and runs parallel sub-agents (or live teammates) on it, then synthesizes. Modes: brainstorm, perspectives (look at anything through several lenses to understand, evaluate, advise, explain or review it), solve (verifiable answers), decompose, unstick (reframe when stuck), debate (live team debate, or written rounds where the harness has no teams). Use when the user asks for heavy thinking, a deep brainstorm, multiple perspectives or opinions on something, a review or critique, a decomposition, a pressure-test, or says they're stuck — strategic decisions, hard technical problems, high-stakes calls. Not for simple lookups, mechanical tasks, clear next steps, or implementation work."
---

# Heavy Think

One entry point for heavy thinking, with several modes. Most run parallel agents and then your
synthesis: change what the agents explore, and the same engine gives a different kind of thinking.

**Harness.** This skill names capabilities (spawn a sub-agent, a live team, a model tier such as
`strong`), not one harness's tools. `references/harness.md` maps each to Claude Code, opencode and
omp, and gives the fallback when your harness lacks one.

**Teammates vs subagents.** Use a live team when the agents need to talk to each other: debate,
collaborative brainstorm, hand-offs. Use parallel sub-agents when they don't. Teammates compound
through live cross-talk but cost more, and only some harnesses have them (Claude Code agent teams,
main session only); sub-agents are cheaper and collide only once, in your synthesis.

## Dispatch

Classify the problem, then pick the mode. The agent modes are worth their cost only on a problem a
plain answer would get wrong or thin: if you can answer it well in 30 seconds, answer it.

| Signal | Mode | Pattern | Cost vs a plain answer |
|--------|------|---------|------------------------|
| "What should we..." / "what are the options" / subjective question | **Brainstorm** | Parallel lenses generate → collide → synthesize | about 5–9x (3–5 agents); +K calls per cross-pollinate wave |
| "Look at this from multiple perspectives" / "what am I missing" / "opinions on" / "evaluate" / "review" | **Perspectives** | Parallel lenses read the same subject → agree / clash / blind spots → answer the ask | about 5–9x (3–5 agents), plus verifiers for a review |
| Verifiable answer exists (math, logic, algorithm) | **Solve** | Parallel solution paths → deliberate → verify | about K+1 times one solve |
| "How do we break this down" / too big to tackle | **Decompose** | Parallel decomposition strategies → best structure | about 5–9x (3 agents) |
| "I'm stuck" / every option feels wrong / going in circles | **Unstick** | Parallel reframes → the frame that unlocks movement | about 5–9x (3 agents) |
| "Debate this" / "pressure-test" / "argue both sides" / high stakes needing adversarial rigor | **Debate** | Named teammates argue live → you moderate → synthesize | the most: live teammates over several rounds |
| Needs one careful line of reasoning, not several perspectives | **Analyze** | Reason it through yourself, no agents | 1x |

The 5–9x figure is measured: a Perspectives review cost $1.86 against $0.39 for a plain answer, and
a Brainstorm $1.1–1.5 against $0.16, with the skill ahead of the plain answer on a blind judge. The other agent
modes have the same shape (3–5 `strong` agents plus your synthesis), so expect the same order. Agents
that use their tools (web search, reading files) cost more than ones that reason alone.

When the signal is **Debate**, go straight to [Escalation: Agent Debate](#escalation-agent-debate);
don't simulate it inline. A live debate needs a harness with live teams, run from the main session; without one, use the written-round fallback. Debate is
also where synthesis goes when positions are irreconcilable.

When you are unsure which mode fits, ask the user rather than guess. Modes chain: decompose first,
then brainstorm each piece; or unstick, then solve (see [Chaining modes](#chaining-modes)).

## The reply (every mode)

The user compares your reply with what one strong answer, with no agents, would have given. The agents
are worth their cost only if the reply holds everything that answer would, plus what the agents found
that it would miss. Blind judges of real runs marked these reply habits down: process narration, agent
claims passed on unchecked, visible scores, fewer ideas than a plain answer, less runnable material.

- **Write it as one expert's answer about the user's problem, not a report on your method.** Leave out
  agents, lenses, angles, thinkers, rounds, red teams, "verified by one agent", "four angles agreed".
  Turn the synthesis into content instead: what several lenses found independently becomes a plain,
  firm statement; a split becomes a condition ("if you sell to enterprises, X; otherwise Y"); a point
  only one lens saw is simply stated. Describe the method only when the user asks how you got there.
- **Meet the plain answer's floor first.** Before writing, list the ideas and steps a single expert
  would give with no agents (the obvious ones, the local and seasonal ones, the cheap ones), and make
  sure yours contains all of them. Then add what the run found. In practice:
  - technical problem: a runnable command, query or config line for each check or step you recommend,
    not just its name; no implementation code the user did not ask for;
  - brainstorm: every distinct idea worth keeping, one line each and grouped, not only the shortlist;
    the developed picks get a few lines each, the rest one line, nothing more;
  - decision: the call, what would flip it, and the first steps.
- **Agent claims are leads, not facts.** Agents mark what they could not check "(unchecked)". Before a
  specific reaches the reply (a setting, flag or GUC name, a command, an API, a price, a version, a
  date, a statistic, a local custom, or what a product can or cannot do), check it yourself: run it,
  read `--help`, open the docs, the source or the page the agent cited. If you can't check it, cut
  it, or keep it only if the answer needs it and say at that line what to verify. Present something
  as a toggle, flag or setting only if you have seen it exists. An agent saying it verified something
  is not a check. Check what the answer leans on, and cut minor specifics rather than spend a call on
  each.
- **Scores are for your ranking only.** The rubric orders the candidates; the reply gives the order and
  the reason in words. No 0-100 numbers or score tables unless the user asks for them.
- **Length must be earned.** Lead with the answer in the first lines. Aim near the length a plain
  answer would take; go past it only by what the run found that changes the answer. Cut restated
  points, background the user did not ask for, and long examples. A judge reading a longer reply asks
  whether every extra paragraph changed what the user will do.
- **Caveats point at what is in the reply.** State assumptions in a line or two up front, and keep each
  "unverified" note next to the claim it is about.

## The deck

Agents in Brainstorm and Perspectives each get a **card** from the perspective deck: a lens (who is
looking), and for ideation a technique (how it generates). A lens carries its question, what it
must deliver, and its **instruments**: what it actually does, with what material and tools. Pass all
of it into the agent's prompt; the instruments are what make an agent do different work rather than
use different words.

`DECK` stands for `python3 "$SKILL_DIR/deck.py"`, where `SKILL_DIR` is the folder this SKILL.md is
in (Claude Code sets `${CLAUDE_SKILL_DIR}`; never a fixed install path).

```bash
DECK presets                                                                  # which preset fits, and its rubric
DECK deal --members 3 --preset <id> --no-technique --question "<the problem>" # judging or deciding: lenses only
DECK deal --members 5 --preset <id> --question "<the problem>"                # ideation: lens + technique
DECK deal --members 4 --lenses "operator; maintainer; EU regulator: Would this pass a GDPR review?"
```

- **Always pass `--question`.** The deck is fitted to it, and the fit ranks who gets seated. Pass on
  any `deck warn:` line to the user.
- **Techniques are for ideation only.** Deal decisions, reviews and technical problems with
  `--no-technique`.
- **Custom lenses beat the deck** when the problem has a person the deck lacks (a DBA on call, an EU
  regulator, the finance team): write `Name: the question it asks`, and give that agent the material
  that person would work from.
- How the fit and the dealer pick seats, every field of a card, and how to add to the deck:
  **`references/deck.md`**.

## Agents and their tools

Every agent you spawn works from real material with the tools it has: reading files and running
read-only commands, web and social search, code reading (codegraph, grep), and a fresh subagent as a
cold reader when its method calls for one. Don't tell agents to answer from reasoning alone when the
data is reachable: an agent without material invents it, and the invented facts reach the reply.
The prompts in `references/` already say this, and ask each agent to mark any outside claim it
could not check "(unchecked)". Tell agents what they must not touch (the user's live files,
accounts, anything that sends or publishes), and give them paths, URLs or commands rather than
pasting a large subject into every prompt.

---

## Mode 1: Brainstorm

Parallel agents explore the same problem through different lenses. Insight comes from the collision,
not from consensus.

### Stage 1: Frame

```
PROBLEM: [One sentence: what are we trying to figure out?]
CONSTRAINTS: [What's fixed? Budget, timeline, team size, tech stack...]
SUCCESS LOOKS LIKE: [How will we know a good answer when we see it?]
MODE: scan (3 agents, breadth-first) | deep (up to 5 agents, depth-first)
```

### Stage 2: Deal the cards

Choose 3–5 lenses that collide productively: tension, not redundancy. Start from the preset whose
shape fits (`DECK presets`), deal with `--question`, and read the dealt panel: if a lens the problem
plainly needs is missing (the customer, the money, the calendar), add it with `--lenses` rather than
re-dealing.

### Stage 3: Spawn parallel agents

Launch all of them (up to 5) in **one message**, model tier `strong`, with the prompt in
**`references/brainstorm-agent-prompt.md`** (Standard Brainstorm Agent). Each gets the same problem
and its own card: lens, `delivers`, `instruments`, and technique (drop the technique line under
`--no-technique`).

### Stage 3b (optional): Cross-pollinate

Isolated agents collide only once, in your head. One extra wave lets ideas compound without agent
teams: give each agent's output to one other agent (a ring: 1→2, 2→3, …, last→1) with the
cross-pollinate prompt in `references/brainstorm-agent-prompt.md`. Each builds on what it read
through its own lens and names the parent ideas of every build. Costs K more calls. Use it in deep
mode, or when the first wave came back as K separate lists.

### Stage 4: Synthesize (yours)

You do this yourself: the value is in the collision, and a delegated synthesis only adds one more
opinion.

1. **Map**: the territory each lens covered, overlap vs divergence.
2. **Collide**: where lenses directly contradict. The deepest insight usually lives here.
3. **Extract surprises**: what exists in no single output but emerges from combining them (with 3b:
   the builds whose parents come from two lenses).
4. **Second-order cascade**: trace the strongest ideas: then what, and then what?
5. **Score before you rank**: rate the top candidates, baselines included, on `references/rubric.md`
   with the preset's profile (`creative` for ideation, `decision` for anything that ships and has to
   be run). A baseline that wins under `decision` is a fine answer: say so. The scores stay with you.
6. **Converge**: key insights, ranked by surprise → recommendation, with the top picks developed
   (what, why, the first step) → **the rest of the idea set**, one line each, grouped by the cause or
   area it addresses, baselines and the plain answer's ideas included → tensions worth holding, as
   conditions → what to stop doing. A brainstorm reply that offers fewer ideas than a plain answer
   would loses, however sharp its shortlist. A stress test (Stage 5) amends the ideas; it does not
   shrink the set.

### Stage 5 (optional): Stress test

For high stakes, spawn 1–2 agents to attack the synthesis: red team ("find every way this fails") or
pre-mortem ("a year later this failed: what happened?"). Templates in
`references/brainstorm-agent-prompt.md`.

### Escalation: Full Council (creative full mode)

When the question deserves real range (5–12 perspectives, several rounds of building on each other,
a shortlist picked by blind judges rather than by you, and a record on disk), run **`/council full`**.
It is this mode scaled up and made resumable, with no agent-teams flag needed. See
`../council/SKILL.md` (council deals from this skill's deck, so it needs heavy-think linked beside it).

### Escalation: Team Brainstorm (collaborative teammates)

When you want ideas to compound live, escalate to a collaborative council: named teammates that
cross-pollinate by messaging each other, then you harvest the expanded set. Protocol, spawn template,
anti-groupthink rules and variants: **`references/team-brainstorm.md`**.

---

## Mode 2: Perspectives

Look at one subject through several lenses at once and answer the question asked. The subject can be
anything: a question, a situation, a decision, a plan, a draft, a codebase, a diff, a person's
message, a product. Brainstorm *generates options*; Perspectives *reads what is in front of you*: how
it looks to each lens, what each one notices that the others miss, and where they disagree.

### Stage 1: Frame

```
SUBJECT: [What we're looking at, and where: text, paths, a URL, a diff command, or the situation in a few lines]
ASK: understand | evaluate | advise | review | explain   (what the user wants back; pick the closest)
CONTEXT: [Who it's for, what's at stake, what's fixed]
```

| ASK | The user wants | Synthesis ends in |
|-----|----------------|-------------------|
| understand | to see the subject more fully | a map: what each lens sees, where they agree and clash, what nobody can see yet |
| evaluate | to know how good it is, or how it compares | strengths and weaknesses by lens, an overall read with the reasons |
| advise | to know what to do | a recommendation, the trade-off it accepts, the lens that disagrees most and why |
| review | problems found in something that exists | findings ranked by severity and a verdict against a stated bar (see Review below) |
| explain | to explain it to different audiences | one explanation per audience, and what each one needs that the others don't |

Ask the user only if the ASK really cannot be inferred; otherwise state it and go.

### Stage 2: Seat the lenses

3 lenses by default, 4–5 when the subject is broad, always with `--no-technique`. Deal from a preset
whose shape fits, a random deal fitted to the subject, or `--lenses` you pick. The real people around
the subject (the customer, the on-call engineer, the reader, your manager) usually make the best
lenses. Pick lenses that would disagree: three lenses that all care about quality give one opinion
three times. When the ASK is review, start from a review preset (below).

### Stage 3: Spawn

All in **one message**, model tier `strong`, with the perspective prompt in
**`references/perspectives-prompt.md`**. Each agent gets the same subject, ask and context, and one
lens with its `delivers` and `instruments`. For a large subject, point agents at paths or a command.

### Stage 4: Synthesize (yours)

Follow Synthesis in `perspectives-prompt.md`: agreement, disagreement and the value underneath it,
singletons, blind spots, then answer the ASK in the shape from the Stage 1 table. Decide which
concern weighs most for this subject and say it as a reason ("on-call load matters more than lock-in
at three people"), not as a lens name. If a claim would change the answer and you're unsure of it,
check it before you lean on it: read the line, open the source, or for high stakes spawn a fresh
agent told to refute it.

### Review (when the ASK is review)

The same mode with stricter output, for when something has to pass a bar: a merge, a publish, an
approval. For a routine code diff, `/code-review` is cheaper.

- **Frame adds** BAR (what "passes" means) and OUT OF SCOPE. Severity is measured against the bar.
- **Presets** by artifact; `DECK presets` lists their seats, and review presets never seat a wildcard:

  | Artifact | Preset |
  |----------|--------|
  | Code change | `code-review` |
  | Design doc, RFC, architecture | `design-review` |
  | Project plan, roadmap | `plan-review` |
  | Proposal, decision as written | `proposal-review` |
  | Doc, essay, README, post | `writing-review` |
  | UI, flow, onboarding | `ux-review` |
  | Prompt, skill, spec, policy text | `prompt-review` |

- **Reviewers, verifiers and the verdict** follow the review variant in `perspectives-prompt.md`:
  findings need evidence, CRITICAL and HIGH findings are verified before the verdict, and the verdict
  is PASS, PASS WITH FIXES, REVISE or REJECT. Review, don't rewrite, unless asked.

### Escalation

- Lenses split on something that decides the answer → [debate](#escalation-agent-debate) that one question.
- The answer turns out to be "we need options, not opinions" → Brainstorm. Stuck → Unstick.

---

## Mode 3: Solve

K independent agents (3, or 5 for high stakes) solve the same verifiable problem from scratch; you
deliberate over their chains, audit them, cross-check with whatever can be run, and give the final
answer only. Use it for math, algorithms and logic when your confidence is below about 70%, not for
subjective or easy questions. The deliberation is yours: one reader comparing every chain is where
the gain comes from. Protocol, solver prompt and iteration limits: **`references/solve.md`**.

---

## Mode 4: Decompose

Parallel agents each break the problem down with a different strategy; you build the best structure
from their cuts.

### Stage 1: Frame

```
PROBLEM: [What needs to be decomposed?]
WHY DECOMPOSITION IS HARD: [What makes this non-obvious to break down?]
GOAL: [What does a good decomposition enable? Parallel work? Clarity? Prioritization?]
```

### Stage 2: Spawn 3 decomposition agents

Pick the strategies from the deck: `DECK decompositions --question "<the problem>"` lists the ones
that fit, best first; `DECK decompositions` lists every strategy and the sets by situation, and
`--set <id>` prints one set. Launch all in **one message**, model tier `strong`, with the prompt in
**`references/decompose-prompt.md`**: each agent decomposes with its strategy alone into 3–7 pieces,
flags what is parallel, names the hardest piece and its blind spots, and gives each piece a first
concrete action (for technical work, the exact command, query or config line, checked or marked).

### Stage 3: Synthesize (yours)

Overlay, conflict, blind spots, compose: the steps and the reply shape are under Synthesis in
`references/decompose-prompt.md`.

---

## Mode 5: Unstick

Parallel agents each reframe the problem from a different angle, to find the frame that turns
"stuck" into "obvious next step".

### Stage 1: Name the stuckness

```
PROBLEM: [What are you trying to do?]
WHY STUCK: [What's blocking? Every option feels wrong? Going in circles? Can't see the next step?]
WHAT YOU'VE TRIED: [What approaches have been attempted or considered?]
```

### Stage 2: Spawn 3 reframe agents

Pick the reframes from the deck: `DECK reframes --question "<why they are stuck>"` lists the ones that
fit, best first; `DECK reframes` lists every reframe and the sets by kind of stuckness (`--set <id>`
prints one). For deeper stuckness, add two more (at most 6 in flight). Launch all in **one message**,
model tier `strong`, with the prompt in **`references/unstick-prompt.md`**: each agent names the frame that
creates the stuckness, applies its reframe, shows the problem in the new frame, gives 1–2 next steps
that are obvious there, and names what the reframe misses. It does not solve the problem.

### Stage 3: Synthesize

1. **Which reframe unlocks movement?** Not the cleverest: the one that makes the next step most obvious.
2. **Can reframes combine?** Two together sometimes reveal more than either alone.
3. **What's the actual trap?** If several agents found the same underlying assumption, that is the
   real blockage.
4. **Recommend**: the reframe that works, the next concrete step, and what to watch out for.

---

## Mode 6: Analyze

No agents. Use when the problem needs one careful line of reasoning with revision, not parallel
exploration: work it through yourself.

---

## Escalation: Agent Debate

Escalate when parallel → synthesize isn't deep enough: positions that genuinely contradict, low
confidence, high stakes, or the user asks to debate or pressure-test. Say so: "Escalating to debate
because [reason]."

- **Preferred: team debate.** Named teammates argue with each other live; you moderate and
  synthesize what survived. Needs a live team (`references/harness.md`) and the main session. Run it with **`/debate`**, or follow **`references/team-debate.md`** (protocol, spawn
  template, moderation, variants). `DECK debates` lists the formats and the evidence-backed rules.
- **Fallback** (no live team, or you are inside a sub-agent): the round protocol in
  `references/team-debate.md` (Fallback). In short: run the mode for positions, then spawn
  challengers that each attack one position with all of them in view, optionally send the
  challenges back for defenses, and you relay between rounds.
- Either way: at most 2 rounds (gains peak by round 2 and sycophancy grows after), model tier `strong`,
  and the reply is the surviving position and its conditions, written as in [The reply](#the-reply-every-mode).

---

## Chaining modes

| Chain | When |
|-------|------|
| Unstick → Brainstorm | Stuck on direction → once unblocked, explore options |
| Decompose → Brainstorm (per piece) | Big problem → break down → ideate on each component |
| Brainstorm → Solve | Explore options → verify the winning approach rigorously |
| Decompose → Solve (per piece) | Break down → solve each sub-problem with full rigor |
| Unstick → Decompose | Can't see the structure → reframe → then decompose clearly |
| Brainstorm → Perspectives | Pick a direction → see how the people it affects would read it |
| Perspectives → Brainstorm | The lenses agree the current answer is wrong → explore what would work |

State the chain up front: "I'll decompose first, then brainstorm on the hardest piece."

## Anti-patterns

| Pattern | Fix |
|---------|-----|
| Picking a mode without classifying | Match signal → mode first |
| Listing agent outputs instead of synthesizing | The value is in the collision; synthesize it yourself |
| Running every mode "to be thorough" | Pick the mode that fits; chain only when necessary |
| Decomposing when you're actually stuck | Stuck is not complex: it needs a reframe, not more structure |
| Brainstorming when you should be solving | If there's a verifiable answer, solve it |
| Brainstorming when asked for perspectives | Read what exists first; generate alternatives only if asked |
| Perspectives that all agree | The lenses were too alike: seat one that would disagree |
| Agents told to work from reasoning alone | Give them their instruments and tools; invented facts reach the reply |
| Hand-writing a lens the dealer dropped | Start from the preset whose shape fits, or add it with `--lenses` |
| Review findings without evidence | No quote, line or triggering input → it is a suspicion, not a finding |

## References

- `references/harness.md`: capabilities and model tiers mapped to Claude Code, opencode and omp, and the no-sub-agent fallback
- `references/deck.md`: the deck: card fields, the `deck.py` commands, how the fit and the dealer seat lenses, custom lenses, adding entries
- `references/perspectives.json`: the deck itself (dealt and listed by `deck.py`)
- `references/brainstorm-agent-prompt.md`: brainstorm, cross-pollinate and stress-test agent prompts
- `references/perspectives-prompt.md`: the perspective prompt and synthesis, plus the review variant (severity, reviewer and verifier prompts, verdict)
- `references/decompose-prompt.md`: the decomposition agent prompt and the synthesis reply shape
- `references/unstick-prompt.md`: the reframe agent prompt
- `references/solve.md`: Solve mode in full
- `references/team-brainstorm.md`: live-team council, named teammates building on each other's ideas
- `references/team-debate.md`: live-team debate, and the subagent fallback round protocol
- `references/rubric.md`: creative, decision and review profiles with criteria anchors
- `references/compute.md`: cost analysis, K selection, non-monotonic performance
- `references/tensions.md`: design tensions: consensus vs minority, width vs depth
- `references/landscape.md`: how Solve mode compares to Best-of-N, Self-Consistency, Forest-of-Thought
- `references/paper-details.md`: HeavySkill paper methodology details
