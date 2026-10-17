---
name: ambition
description: "Do a task, or rewrite a prompt, at a higher level of ambition: Altitude (the goal behind the goal), Depth (an expert's raw data, real instruments and an outside judge) and Range (methods from other fields). Use when the user says be ambitious, think bigger, aim higher, go deeper, 10x this, what would the best in the field do, or asks to make a prompt more ambitious. Not for quick one-liners or mechanical changes."
---

# Ambition

Based on Felix Rieseberg, [*How to be more ambitious: a tutorial for humans with
models*](https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/) (2026-10).
Models can do more than people ask of them. This skill asks for more, and it keeps
the result honest. Hard goals without a fixed judge make agents fake success.

## The three axes

| Axis | Question | Use when | Weak for |
|------|----------|----------|----------|
| **Altitude** | What should happen *after* this task? | An outcome matters more than the artifact. People will hold meetings about it. The task keeps coming back. | Creative work. Lean on Range there. |
| **Depth** | What would the best expert do, from which raw material, with which instruments? | You want this one thing done really well. | |
| **Range** | Which other fields would do this differently? | The task is creative, or the obvious field is stuck. | |

Doing the same work faster is not ambition here. That is normal work.

## Process

0. **Skip trivia.** If the task needs one tool call or has one right answer, just do it.
1. **Look first, read-only.** Read the code, data or current numbers. Measure the baseline. Make no changes yet.
2. **Pick the axes.** Use the table. When the signal is unclear, use all three.
3. **Write the brief** (format below) and show it to the user.
4. **Wait for approval**, unless the user said to go ahead. Approval locks the contract.
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

**Contract.** Approval locks it.

| Line | Content |
|------|---------|
| Judge | The exact command or check, and its pass line. It must sit outside the model and be hard to game: an existing test suite, held-out data, a real device, an external total. Your own reading of your output is not a judge. Tests you write yourself can only add to the judge, not replace it. |
| Target | A number and its state: `proven (<source>)`, `unreasonable on purpose`, or `guess (no baseline)`. Aim past the obvious. A proof that someone reached it sets a floor, not a cap. |
| Stop line | The effort you spend before a miss is allowed, for example "3 real approaches". |
| Scope | The approved deliverables and files, one per row. |
| Runs | `<what> · owner: <who reads it> · kill when: <condition>`, or "nothing new". |

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
- **Do what the field does, don't role-play it.** Don't write *like* a short seller. Do what a short seller *does* to research a position.

## The report

| Item | Planned | Actual |
|------|---------|--------|
| Judge | `<command>`, pass `<line>` | pasted output or exit code |
| Target | `<n>` (`<state>`) | reached, or missed by `<gap>` |
| Instrument: `<name>` | what it was for | the tool call that ran it, or "struck: `<why>`" |
| Field: `<name>` | its method | done, or "struck: `<why>`" |
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
- Use what each field *does*: an editor's cut, a forensic accountant's Benford test, a journalist's second source.
- To run the fields as parallel agents, use a multi-agent skill if one is installed, or else plain subagents. Do this when 3 or more fields each need real work, or when the user asks for several views.

## Mode: rewrite a prompt

Deeper, not bigger. Show these four lines first:

1. What a top professional would do here that the prompt does not ask for.
2. The rawest material they would start from.
3. Their specific methods and tools.
4. What, other than the model or the user, would show the result is right.

Then give the rewritten prompt in a code block. It keeps the original deliverables. It adds:
- the raw material and methods from lines 2–3
- a target with its state
- the judge, with "Don't change this check."
- "If you miss, report the miss with the real output. That is a good result."

Under the block, add at most one optional line: `Bigger version: <the higher-altitude ask>`. Never put the bigger version inside the prompt.

## Guardrails

- **Ambition is not scope creep.** The contract's Scope rows are the limit. Anything else goes in "Next rung" or "Unapproved".
- **Tools are a requirement.** Depth and the judge need a real computer, data access and runnable checks. Without them, say which parts became words instead of actions.
