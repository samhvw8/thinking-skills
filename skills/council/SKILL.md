---
name: council
description: "Collaborative brainstorm where perspectives build on each other ('yes, and…'), then you synthesize. Two modes: live (2-4 named teammates cross-pollinating by message, where the harness has live teams) and full (a file-based session of 5-12 sub-agents dealt lens + technique cards from heavy-think's perspective deck: diverge, cross-pollinate rounds, cluster, blind scoring on a creative or decision rubric, develop and stress-test the shortlist). Use when the user types /council, wants an open question ('how might we…', 'what could we build') explored by compounding perspectives, or asks for a full / creative / big brainstorm. Not for a quick idea list (heavy-think Brainstorm), choosing between options (/debate), finding the single best answer to a task (/arena), or mechanical tasks."
argument-hint: "[full] [--quick | --members N] [--preset P] [--rubric creative|decision] [--seed S] <question>"
---

# Council

The generative "yes, and…" counterpart to `/debate`'s "no, but…" and `/arena`'s "only one survives".
Perspectives meet, build on each other, and you harvest what no single perspective would have
produced. You facilitate. You never add ideas of your own: provocations come from the deck, so your
taste never enters the pool.

What the user typed after `/council`: `$ARGUMENTS`

## Pick the mode

| | Live | Full |
|---|---|---|
| Trigger | `/council <question>` | `/council full <question>`, or "full / creative / big brainstorm" |
| Who | 2-4 named teammates | 5-12 sub-agents (default 8) |
| How they meet | messages, live | each other's files, across rounds |
| Needs | main session + a harness with live teams (Claude Code agent teams) | read access to this skill folder and heavy-think beside it, permission to run `python3`, write access to `.council/` in the working directory |
| Picks the shortlist | you, in synthesis | judges on a written rubric, blind |
| Survives compaction | no | yes, the state is on disk |
| Cost | ~3-5x one pass | `council.py plan` prints the calls |

Live wins when ideas need fast back-and-forth between a few minds. Full wins when you want range,
an honest shortlist and a record. If live mode's prerequisites fail, say so and offer full mode
rather than quietly simulating a council.

Full mode works in any harness that can spawn sub-agents. `../heavy-think/references/harness.md`
maps the sub-agent tool and the model tiers (`session`, `fast`, `strong`) for Claude Code, opencode
and omp; without sub-agents, follow its Fallback and say the run was simulated. Headless, full mode
needs the skills folder readable, `python3` allowed, and the web tools the developer and stress jobs
use (Claude Code: `--add-dir <skills folder> --allowedTools "Bash(python3:*)" Read Write Edit Agent`). Without them the run cannot start: say so instead of
answering without the council.

## The deck

The deck lives in the heavy-think skill: `../heavy-think/references/perspectives.json`, dealt by
`../heavy-think/deck.py`. A member's card is one **lens** (who is looking, from six families:
challenger, stakeholder, temporal, systems, craft, wildcard; with the instruments that lens works
with) plus one **technique** (how they generate: SCAMPER, reverse brainstorm, forced mashup, TRIZ
principles and more). **Provocations** are the facilitator's sparks. **Presets** are lens sets for
common question shapes, and each names its rubric. `COUNCIL presets` lists them; the deck grows, so
read it there rather than from memory.

A random deal always seats a challenger, a stakeholder and a temporal lens (plus a wildcard from 4
members up), spreads the families, and prefers lenses that clash with ones already seated. A preset
or `--lenses` is a deliberate choice and is kept: the dealer fills missing families only into empty
seats, and swaps a preset lens only when the preset doubled up a family.

**A lens written for this problem beats any lens in the deck.** Mix them in as `Name: the question it
asks`, for example `--lenses "operator; EU regulator: Would this pass a GDPR review, as built?"` (use
`;` between entries when a question contains a comma).

**Pick the rubric.** `creative` for ideation; `decision` for anything that ships and has to be run
(it weighs running cost). Presets set it; `--rubric` overrides. Weights and anchors:
`../heavy-think/references/rubric.md`. For decision-shaped questions, consider `--no-technique` too:
forced techniques can make technical answers gimmicky.

```bash
COUNCIL = python3 "$SKILL_DIR/council.py"
COUNCIL presets                         # preset lens sets and their rubric
COUNCIL deal --members 4 --preset greenfield --question "<the question>"   # cards only, for a live council
```

`SKILL_DIR` is the folder this SKILL.md is in (Claude Code sets `${CLAUDE_SKILL_DIR}`).

## Live mode

The protocol, spawn template and anti-groupthink rules are in
`../heavy-think/references/team-brainstorm.md`. Read it before spawning. What the deck adds:

1. Run `COUNCIL deal --members N --question "<the question>"` (with `--preset` if one fits) and give
   each teammate its lens (name, asks, sees, instruments) and its technique in the spawn prompt. Name
   the wildcard.
2. Use the dealt provocations as your Phase 2 sparks, one at a time, when the room goes quiet or
   agrees too fast. That keeps you a facilitator: the spark is the deck's, not yours.
3. In Phase 2, every build names its parent ideas ("builds on Ada's 2 and Lin's 1"). In synthesis,
   keep that lineage. It shows which ideas only exist because two lenses met.

## Full mode

Done means: every phase drained and `COUNCIL next` prints DONE, then your reply (Step 5). Or `next`
prints STOPPED, and you tell the user what failed and hand over what exists.

### Step 1: size it, name the models, and say so before you start

- **Models, per phase.** The judgment work (diverge, cross, cluster, score, and your own synthesis) runs
  on this session's model, because it decides what ideas exist and which survive. The developer and
  stress jobs run on the `fast` tier (Sonnet in Claude Code): they research the web and test claims,
  which a cheaper model does well, and under a fixed budget the strongest model everywhere bought fewer
  concepts and lost to this mix in blind judging. Record it with `init --model <session model>`;
  override with `--phase-model develop=strong,...` only when the user asks. `prompts` prints each
  phase's model or tier: pass it on every sub-agent call, translated by `harness.md`.
- **Size.** Run `COUNCIL plan` (add `--quick` or `--members N`, `--shortlist N`). Without a ceiling, use
  the default. With one (dollars, calls or time, from the user or the harness), pick a size where every
  phase fits, stress included: a run that stops before the stress test hands the user untested ideas,
  and blind judges rank that below a smaller, finished run. Developer and stress calls research the
  web and cost the most per call, so cut the shortlist first, then members, then judges (never below
  two). A $6 ceiling fits `--quick` with this model mix.
- **Announce** in your first message, before `init`: size, calls, the model per phase and why, for
  example "8 members, 2 cross rounds, 3 judges, 4 shortlisted: 36 sub-agent calls; ideas, curation and
  judging on this session's model, research and stress tests on the fast tier (the default size)". Name
  the real models. Then
  start. If the user did not ask for a council and you are proposing it, ask first.

Sub-agents write into `.council/` in the current directory. In the default permission mode that is
one approval per file. Suggest accept-edits mode (Shift+Tab) for the run. Do not change settings
yourself.

### Step 2: write the brief

Sub-agents cannot see this conversation. Write `.council/brief.md` so it stands on its own:

- The question, open-ended ("how might we…", "what could we…"), in the user's words where you can.
- Who it is for, the constraints the user stated (budget, team, timeline, stack, what must not change),
  and what already exists. Absolute paths to anything they should read.
- What a great outcome looks like, if the user said.
- Ideas the user already has or has rejected, labelled as such, so members can build on them or avoid
  them.

Do not add constraints the user never gave, and do not write your own favourite idea into it: that
pulls every member toward it.

### Step 3: init

```bash
COUNCIL init --brief-file .council/brief.md --model <model> [--members N | --quick] [--preset P | --lenses "a; Name: question"] [--rubric creative|decision] [--no-technique] [--seed S]
```

It checks the deck has every card field the prompts use, fits the deck to the brief, deals the
cards, seats members in a ring where neighbours come from different families, and writes
`council.json`. The fit is heavy-think's `deck.py`, which picks the scorer and falls back on its own.
It prints what it used and kept (and a `deck warn:` line when a scorer failed: pass that on to the
user), and the scores stay in `relevance.json`. `--relevance off` skips it.

### Step 4: the loop

Drive it with `COUNCIL next`. Every sub-agent phase works the same way:

1. `COUNCIL prompts <phase>` writes one brief per job and lists the jobs still to run, with the phase's
   model.
2. Launch them as a rolling pool: at most the run's `parallel` value in flight, starting the next
   queued job as soon as one finishes. Each call is a general sub-agent (`harness.md`), the
   phase's model, `description: council <job id>`, `prompt: Read <prompt path>: it is your whole brief.`
3. When the phase is drained, run `COUNCIL next` (and `COUNCIL collect` when it says so). A missing or
   rejected output sends you back to the same phase, and `prompts` lists only those jobs: rerun each
   once. If a job fails a second time, write `NO OUTPUT` into its output file and move on. `collect`
   then drops a failed judge (the panel needs two) or stops the run when it cannot go on without the
   job. When `next` prints STOPPED, stop: tell the user what failed and point to the member files.
   Never score or curate anything yourself, since that would put your taste into the pool.

The order: **diverge** (each member alone, through its card) → **cross1 .. crossC** (each member
reads the members k seats away on the ring and builds on them; the last round adds the member straight
across the ring and each member's provocation) → **cluster** (one curator merges everything into a pool
of concepts with lineage, plus up to 3 orphans: odd single ideas kept as written, then
`COUNCIL collect`) → **score** (independent judges score the pool blind on `rubric.md`, then `COUNCIL
collect`, which refuses any judge file that misses a concept or a criterion, averages the rest, and
fills the shortlist, keeping the last slot for the concept one judge loved most when the average left
it out) → **develop** (one developer per shortlisted concept) → **stress** (one red-team and
pre-mortem per developed concept) → DONE.

After each phase, give the user one line ("Cross round 1 done: 8 members built on each other").
Never paste ideas, builds or scores into the chat during the run.

### Step 5: harvest and synthesize (you, never delegated)

Run `COUNCIL harvest`. Read only the develop and stress files it lists. Then give the user:

Treat the judges' totals as a sort, not a verdict: LLM judgments of idea quality agree with human
reviewers barely above chance (Si et al., arXiv 2409.04109). Read the developed concepts yourself.

Write the reply as one expert's answer about the user's problem, not a report on the session, and
start it with the answer, not a status line. Blind judges of real runs preferred the council's ideas
to a plain answer, but marked replies down for three faults:

- **Process talk.** Members, rounds, judges, scores, concept codes (C01), "dissent slot", "orphans",
  lens credits, the budget or run size, which files you read, the run folder: none of it goes in the
  reply. It stays in the run folder, which you name only if the user asks.
- **No tie to the goal.** Say what each idea contributes to the user's stated goal, in the user's own
  unit when they gave one (users, revenue, hours), with an honest range, and how the ideas add up
  to the target or fall short of it.
- **Nothing to do this week.** Every idea ends in a play the user can start this week within their
  stated constraints: what, where, how long, and the signal that says continue or stop.

1. **The shortlist**, each as: the concept in two lines, what it contributes to the goal, the play for
   this week, the strongest stress-test finding (as a risk to the idea) and whether the concept
   survives it.
2. **What makes each one non-obvious**: say what the obvious answer misses that this idea catches. If a
   concept only exists because two very different angles met, say what those angles were in plain
   words ("a waste-collection logistics view crossed with a habit-forming one"), never by lens name.
3. **Tensions worth holding**: where concepts pull against each other, as conditions for the user.
4. **The long shot**: if `harvest` flags a concept the judges split on, or one only one member
   proposed, present it as a riskier bet and say why it might matter most. No judging vocabulary.
5. **The rest of the pool**, one line each, then what to try next.

Agent claims are leads: check any specific the reply leans on (a statistic, a law, a program that
"exists"), or cut it, or mark it at that line. Members work offline, so a number that came from a
member and was not sourced by a developer or stress test is unchecked.

If a concept would change files in the user's project, do not apply it. Ask.

## Rules for the facilitator

- Facilitate, don't generate. Your sparks come from the deck's provocations.
- Diverge before converge. Nobody judges before the score phase.
- Web access is for the developer and the stress test only. Members, the curator and the judges work
  without it: outside material pulls ideas toward the same sources, and diverging works best in isolation.
- Every sub-agent gets the brief byte for byte through `prompts`. Never add a hint for one member.
- Do not read idea, build or score files during the run. `next`, `status` and `harvest` are enough.
- After a compaction: `COUNCIL status`, then `COUNCIL next`.
- Run every command from the directory you ran `init` in.

The sub-agent prompts live in `prompts.md` beside `council.py`, which fills and writes them. You never
need to read it. Change a template there, never a written brief for one member.

## Related

- [team-brainstorm protocol](../heavy-think/references/team-brainstorm.md): live mode in full
- [heavy-think](../heavy-think/SKILL.md): Brainstorm mode is the cheaper, isolated version
- [debate](../debate/SKILL.md): decide or pressure-test instead of expand
- arena: when the goal is one best answer to a task, not a range of ideas
