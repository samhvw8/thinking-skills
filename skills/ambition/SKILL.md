---
name: ambition
description: "Do a task, or rewrite a prompt, at a higher level of ambition on seven axes, each with a 0-3 ladder: Altitude (the goal behind the goal), Depth (an expert's raw data, real instruments and an outside judge), Range (methods from other fields), Speed (a clock tight enough to change the method), Reach (the whole class, not the instance), Horizon (lasts and makes the next task cheaper) and Proof (evidence a sceptic accepts). Use when the user says be ambitious, think bigger, aim higher, go deeper, 10x this, what would the best in the field do, or asks to make a prompt more ambitious. Say 'ambition high' for the deep mode (classify, mental models, three approaches, leverage). Not for quick one-liners or mechanical changes."
argument-hint: "[high | rewrite] <task or prompt>"
---

# Ambition

Based on Felix Rieseberg, [*How to be more ambitious: a tutorial for humans with
models*](https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/) (2026-10).
Models can do more than people ask of them. This skill asks for more, and it keeps
the result honest. Hard goals without a fixed judge make agents fake success.
The post names four types of ambition: Speed, Altitude, Depth and Range. This skill
adds three that its examples already use: Reach, Horizon and Proof.

## Modes

Read the mode from the first word of the arguments, or from the user's words:

| Invocation | Mode |
|------------|------|
| `/ambition <task>` | Normal: the process below |
| `/ambition high <task>`, "ambition high", "go all out" | High: normal plus the steps in "Mode: high" |
| `/ambition rewrite <prompt>`, "make this prompt more ambitious" | Rewrite: see "Mode: rewrite a prompt" |

## The seven axes

| Axis | Question | Use when | Weak for |
|------|----------|----------|----------|
| **Altitude** | What should happen *after* this task? | An outcome matters more than the artifact. People will hold meetings about it. The task keeps coming back. | Creative work. Lean on Range there. |
| **Depth** | What would the best expert do, from which raw material, with which instruments? | You want this one thing done really well. | |
| **Range** | Which other fields would do this differently? | The task is creative, or the obvious field is stuck. | |
| **Speed** | If this had to land in a tenth of the time, what would you stop doing? | The loop is slow: a build, a review cycle, a weekly report, a judge that takes hours. The task repeats. | One-off quality work. Never buy speed by weakening the judge. |
| **Reach** | How many other cases share this cause? | The task is one instance of a pattern: a bug class, a question people keep asking, every page with the same flaw. | A truly one-off case. |
| **Horizon** | Will this still work in a year, and will it make the next task cheaper? | The same kind of work comes back, or the result decays (data, docs, config). | Throwaway exploration. |
| **Proof** | What would convince a sceptic who never sees the transcript? | The result drives a decision, or success is easy to fake (a green suite, "it's faster now"). | |

**Speed** is how fast the work reaches its outcome, not how fast the code runs. A
runtime target is a Depth target. Typing the same steps faster is rung 0, normal work.
Speed is ambition when the tighter clock changes the method: Lindbergh and Hall built
the Spirit of St. Louis in 60 days and estimated its range with a globe and a piece of
string (Collison's [Fast](https://patrickcollison.com/fast) list).

Each axis has a ladder. Rung 0 is what a plain run does.

| Axis | 0 | 1 | 2 | 3 |
|------|---|---|---|---|
| Altitude | the artifact asked for | the question behind it | the decision it serves | the outcome, kept true without the user |
| Depth | summaries and the field's vocabulary | the raw data | the field's instruments on the raw data | new knowledge an expert would learn from, shown on unseen data |
| Range | one field | one borrowed method | 3–5 fields from the verbs, each with a receipt | plus a red team that tries to break the result |
| Speed | the same steps, faster | no waiting: batch, run in parallel | a feedback loop of seconds, so you try many more times | a 10x tighter clock that removes steps instead of shortening them |
| Reach | this instance | count the class: how many cases share the cause | fix the cause for the whole class | make the class impossible: a type, a lint rule, a guard, a blocking test |
| Horizon | done once, in a transcript | repeatable: a script or command, not prose | leaves an asset that makes the next task cheaper: a test, a dataset, a tool | improves with each run, with its running cost in the Runs line |
| Proof | your own reading | tests you wrote | an outside judge that already exists: a suite, a source-system total | held-out data, a real device, a production number or an independent second source |

The contract already needs Proof rung 2, or a check labelled `self-built`. Picking
Proof means aiming at rung 3.

## Process

0. **Skip trivia.** If the task needs one tool call or has one right answer, just do it.
1. **Look first, read-only.** Read the code, data or current numbers. Measure the baseline. Make no changes yet.
2. **Pick the axes.** Use the table. Pick the two or three whose signals you see, never all seven. When the signal is unclear, use Altitude, Depth and Range. For each axis, write the rung a plain run would reach and the rung you aim at. On a small change (one file, under about 10 lines), Proof comes before Reach: spend the effort on the strongest check you can run, such as an exhaustive or differential test, and only count the class.
3. **Write the brief** (format below) to `BRIEF.md` and show it to the user, before your first edit to a project file. Step 1's read-only look and baseline come first and are fine; what must come before the work is the Judge and Target, because a pass line chosen after you see the result can always be set to pass. If you fixed them late, say so in Deviations. Never write that the brief was locked earlier than the file shows.
4. **Wait for approval**, unless the user already gave it. Approval locks the contract. Asking for the task is not approving the brief. Only these count as approval:
   - an explicit "go ahead", "no need to wait" or the like;
   - a permission mode the user chose for unattended work, when the harness says it is on: Claude Code's auto mode, `bypassPermissions` ("dangerously skip permissions"), or the equivalent in another harness. A mode you can't confirm counts as not on.

   With approval, show the brief and continue in the same turn. Pre-approval covers only the task as asked: the Scope rows hold the literal request, and anything bigger goes to "Next rung". Without approval, end your turn with the brief and change no project files. A report file the user asked for is fine.
5. **Do the work.** Follow "Rules while working" and "Honest misses".
6. **Report** as a plan-vs-actual table (format below).

## The brief

**Goal question (Altitude).** Don't guess the goal behind the goal. Ask it as a fork:
"I read the goal as X, so I'd do A. If it's Y, I'd do B. Which?" Name the access a
higher rung lacks, such as data, credentials or machines. Building that access is
often the highest rung you can deliver today.

**Plan.**
- **Raw material:** the data an expert starts from, not a summary of it.
- **Instruments:** the methods and tools the best in the field use. Examples: a database, not a markdown table; a statistical model, not eyeballing; a profiler; a real device.
- **Fields:** describe the task with verbs. A QBR is not "a deck". It is "make busy people believe a cause-and-effect story and decide in 30 minutes". Name 3–5 fields that are good at those verbs, each with the method it brings.
- **Axes:** one line per chosen axis: `<axis>: rung <plain> → <aim> — <what reaching it looks like>`. Reach and Horizon above rung 1 usually add files or behavior. They go in Scope only when the request covers them; otherwise they go to "Next rung". Horizon rung 3 adds a Runs line.

**Contract.** Approval locks it.

| Line | Content |
|------|---------|
| Judge | The exact command or check, and its pass line. It must sit outside the model and be hard to game: an existing test suite, held-out data, a real device, an external total. Your own reading of your output is not a judge. Tests you write yourself can only add to the judge, not replace it. When no outside judge exists, label your check `self-built`, and name the outside check that would settle it (a second source, a holdout, a real device); the report carries both. |
| Target | A number and its state: `proven (<source>)`, `unreasonable on purpose`, or `guess (no baseline)`. Aim past the obvious. A proof that someone reached it sets a floor, not a cap. `proven` needs a source outside this task; a target the judge meets by definition is not proven. |
| Stop line | The effort you spend before a miss is allowed, for example "3 real approaches". |
| Scope | The approved deliverables and files, one per row. |
| Runs | `<what> · owner: <who reads it> · kill when: <condition>`, or "nothing new". |

## Goals that work

From Locke and Latham's [35 years of goal-setting research](https://med.stanford.edu/content/dam/sm/s-spire/documents/PD.locke-and-latham-retrospective_Paper.pdf), which the post cites:

- **A number, not "do your best".** Specific hard goals beat "do your best" (effect sizes .42–.80), because "do your best" has no outside referent. That is why the Target is a number.
- **Goal plus feedback.** Goals work better with progress feedback than alone. Run the judge early and often. A judge that runs only at the end is a verdict, not feedback.
- **Give the reason.** Commitment to a hard goal grows when the reason is given. Keep the goal question in the brief.
- **New and complex: learning goal first.** On a novel, complex task, a hard performance target can make results worse. Set a learning goal first ("find and measure three approaches"), plus near sub-targets on the way to the far one. Then set the performance target.

## Honest misses

The post's self-efficacy lessons, turned into rules:

- **Belief while working.** Dantzig solved two "unsolved" problems because he thought they were homework. Treat the target as reachable while you work.
- **An existence proof beats a pep talk.** After Bannister broke the four-minute mile, others followed fast. Look for who already reached the number.
- **Only the report may say "impossible".** It must come after the stop line, and it needs three things: the smallest real attempt (pasted output), the measured gap and the named blocker.
- **A miss with those three things is a full, good result.** Stopping before the stop line without them is a deviation.
- **Never change the judge to pass.** Don't edit the judge, tests, data or target, and don't special-case them. If the judge contradicts the spec, stop and report it. The user decides.

## Rules while working

- **Use the instruments, not just the words.** Calling yourself an expert and then using the same old methods is the main failure. If you name a method, use it.
- **Start from raw data.** Get logs, exports, crash reports or source data. Don't work only from summaries.
- **Challenge what you know.** Try to reproduce the team's belief from the raw data, for example "churn is an onboarding problem". Report when the data does not support it.
- **Produce new knowledge.** First reproduce the known past from the raw data, for example simulate last year from the logs. Then look for a blind spot, and show that the finding predicts data it has not seen.
- **Split before you look.** Set the held-out rows aside before you read the data, and write the prediction to a file before you open them. A holdout you have already printed, plotted or summarised is not a holdout; say so in the report instead of calling it one.
- **Do what the field does, don't role-play it.** Don't write *like* a short seller. Do what a short seller *does* to research a position.

## The report

| Item | Planned | Actual |
|------|---------|--------|
| Judge | `<command>`, pass `<line>` | pasted output or exit code |
| Target | `<n>` (`<state>`) | reached, or missed by `<gap>` |
| Instrument: `<name>` | what it was for | the tool call that ran it, or "struck: `<why>`" |
| Field: `<name>` | its method | done, or "struck: `<why>`" |
| Axis: `<name>` | the aim, in plain words | what you did and what it showed (a file, a count, a number). Name a rung only when it reached 2 or higher |
| Scope: `<row>` | approved | done / not done |

Then three lines:
- **Deviations:** `none`, or every change to the judge, tests, data, target or scope, and why.
- **Unapproved:** `none`, or anything built outside the scope rows.
- **Next rung:** one line (see the Altitude ladder).

## Altitude ladder

Climb one rung at a time, and stop where the user wants to stop. Example, a quarterly business review (QBR):

1. Fill in the template's numbers.
2. "Tell me what changed this quarter, why, and what we should do about it." Use all the data you can get.
3. "Find the three most urgent decisions and draft options for each, with arguments for and against."
4. "The review exists so leadership catches problems early and moves money and people. Design a better way than a quarterly deck. Show from our history that it would have caught things sooner. Run it beside the current one for a quarter."

Code example: "fix this crash", then "keep the app crash-free". The top rung is usually something that runs without the user, so it goes in the Runs line with an owner and a kill condition.

## Range in practice

- To find the fields, ask: "If this had to be extraordinary, who would humanity bring in?" For a QBR, that is an analyst, a journalist, an editor, a motion designer, and a red team (a short seller and a forensic accountant).
- To find more, run `python3 <this skill's folder>/scripts/deal.py fields "<the task's verbs>"`. Each field card names its method, its instruments and its receipt. Use it as a start, not a limit; a field missing from the deck is fine.
- Use what each field *does*: an editor's cut, a forensic accountant's Benford test, a journalist's second source.
- To run the fields as parallel agents, use a multi-agent skill if one is installed, or else plain subagents. Do this when 3 or more fields each need real work, or when the user asks for several views.

## Mode: high

Use when the user says "ambition high", "/ambition high", "go all out" or "max
ambition". It goes harder on the same task, not a bigger task: the contract,
honesty rules and scope stay as above. It costs more tokens, so don't pick it
yourself for routine work.

Run the normal process, with these additions:

1. **Classify first (Cynefin).** Name the domain and the evidence for it. Clear: apply the known fix. Complicated: analyse to the root cause. Complex: run small safe probes, then amplify what works. Chaotic: stabilise first, then analyse.
2. **Deal the cards.** Run `python3 <this skill's folder>/scripts/deal.py patterns`. Pick the one or two patterns that fit the task, then run `python3 <this skill's folder>/scripts/deal.py deal "<task in one line>" --patterns <id>,<id>`. Pass `--patterns`: picking by word overlap is a weak guess, and the output says so. You get three mental models, three Range fields and three lenses; a card marked "no fit" was dealt only to fill a slot. If you can't run Python, read `references/deck.json` and pick the same way.
3. **Use each card as an instrument.** Apply each model's move and leave its receipt, an artifact or a number, as a row in the report. A card earns a row only if it changed the work: point to the tool call, file or number it caused. A card that doesn't fit gets "struck: `<why>`" in one line; striking is a normal result, not a failure. Never write a receipt for work you didn't do. The fields and lenses add to the Field rows; they don't replace them.
4. **Three approaches before choosing.** Write the obvious approach (what a competent engineer does first), the unreasonable-on-purpose approach (aims at about 10x the obvious target, or uses a much stronger instrument), and the one that dissolves the problem (removes the need for the work, for example the step or limit that makes it necessary; invert it, or move up the abstraction ladder until the problem disappears). Score all three against the judge, then pick one and say why.
5. **Climb the leverage ladder.** Name the Meadows level of the chosen change: parameters < buffers < structure < delays < feedback loops < information flows < rules < goals. Try one level higher. If that level is outside Scope, it goes to "Next rung".
6. **Second order.** Trace the chosen change two steps ahead ("and then what?"). Name one unintended effect and the check that would catch it.

The report adds an **Approaches** table (approach, judge result or estimate, why picked or dropped) and one row per dealt card.

## Mode: rewrite a prompt

Deeper, not bigger. Show these four lines first:

1. What a top professional would do here that the prompt does not ask for.
2. The rawest material they would start from.
3. Their specific methods and tools.
4. What, other than the model or the user, would show the result is right.

Then give the rewritten prompt in a code block. It keeps the original deliverables. It adds:
- the raw material and methods from lines 2–3
- a target with its state
- the judge, anchored to something outside the model (a total from the source system, held-out data, an existing test), with "Don't change this check."
- "If you miss, report the miss with the real output. That is a good result."

Under the block, add at most one optional line: `Bigger version: <the higher-altitude ask>`. Never put the bigger version inside the prompt.

## Guardrails

- **Ambition is not scope creep.** The contract's Scope rows are the limit. Anything else goes in "Next rung" or "Unapproved". A behavior change nobody asked for (a new error, new validation, a changed default) is scope too, even inside an approved file. Reach is the axis most likely to creep: counting the class is always in scope, but fixing the rest of the class needs a Scope row.
- **Tools are a requirement.** Depth and the judge need a real computer, data access and runnable checks. Without them, say which parts became words instead of actions.
