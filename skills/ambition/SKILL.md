---
name: ambition
description: "Do a task, or rewrite a prompt, at a higher level of ambition: Altitude (the goal behind the goal), Depth (an expert's raw data, real instruments and an outside judge) and Range (methods from other fields). Use when the user says be ambitious, think bigger, aim higher, go deeper, 10x this, what would the best in the field do, or asks to make a prompt more ambitious. Not for quick one-liners or mechanical changes."
---

# Ambition

Based on Felix Rieseberg, [*How to be more ambitious: a tutorial for humans with
models*](https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/) (2026-10). Models can do more than people ask of them. This skill asks for more.

## The three axes

| Axis | Question | Use when |
|------|----------|----------|
| **Altitude** | What should happen *after* this task? What is the goal behind the goal? | An outcome matters more than the artifact. People will hold meetings about it. The same task keeps coming back. |
| **Depth** | What would the best expert in the field do, with which raw material and which instruments? | You want this one thing done really well. |
| **Range** | Which other fields would do this differently? | The task is creative, or the obvious field is stuck. |

Two hacks apply to all three axes:

- **Hard goal.** Pick a specific target about 10x past the obvious one, such as 200 ms, not 5 s. Treat it as reachable. When it looks impossible, keep going.
- **Outside judge.** Never grade your own work. Name a test, metric, held-out data set or tool that shows the result is right, and run it.

## Process

0. **Skip trivia.** If the task needs one tool call or has one right answer, just do it.
1. **Look first, read-only.** Read the code, data or current numbers before the brief. A brief without them is a guess. Make no changes yet.
2. **Pick the axes.** Use the table. When the signal is unclear, use all three. The axes decide which lines carry the weight. Keep an unpicked line to a few words.
3. **Write the ambition brief.** Use one line per field, then show it to the user:
   - **Goal behind the goal:** the outcome, one level up from the task.
   - **Raw material:** the data an expert starts from, not a summary of it.
   - **Instruments:** the methods and tools the best in the field use. Examples: a database instead of a markdown table, a statistical model instead of eyeballing, a simulation, a profiler, real devices.
   - **Fields:** describe the task with verbs, not nouns. A QBR is not "a deck". It is "make busy people believe a cause-and-effect story and decide in 30 minutes". Then name 3–5 fields that are good at those verbs.
   - **Hard target and judge:** the number to hit, and what proves it. Base the 10x on the baseline you measured in step 1. With no baseline, mark the target as a guess.
   - **Runs:** what the plan adds that keeps running (CI budgets, monitors, services), or "nothing new".
4. **Wait for the user**, unless they said to go ahead. Altitude can change the task, and that is the user's decision.
5. **Do the work.** Follow the rules below. Run the judge here, not in the brief.
6. **Report.** Give the judge's result with real output, what is still open, and the next rung up (see the Altitude ladder).

## Rules while working

- **Use the instruments, not just the words.** Calling yourself an expert and then using the same old methods is the main failure. If you name a method, use it.
- **Start from raw data.** Ask for logs, exports, crash reports or source data, or fetch them yourself. Do not work only from what someone already summarized.
- **Challenge what you know.** Try to reproduce the team's belief from the raw data, for example "churn is an onboarding problem". Report when the data does not support it.
- **Produce new knowledge.** Once you are deep in the data, look for a blind spot. Show that the finding predicts data it has not seen.
- **Do what the field does, don't role-play it.** Don't write *like* a short seller. Do what a short seller *does* to research a position.
- **Keep going on hard parts, and report honestly.** Persistence never means claiming success. A failed judge is a failed result. Say so.

## Altitude ladder

Climb one rung at a time, and stop where the user wants to stop. Example, a quarterly business review (QBR):

1. Fill in the template's numbers.
2. "Tell me what changed this quarter, why, and what we should do about it." Use all the data you can get.
3. "Find the three most urgent decisions and draft options for each, with arguments for and against."
4. "The review exists so leadership catches problems early and moves money and people. Design a better way than a quarterly deck. Show from our history that it would have caught things sooner. Run it beside the current one for a quarter."

Code example: "fix this crash", then "keep the app crash-free". Higher rungs usually need access: crash reports, a map from app version to git commit, and machines to reproduce on. List the access that blocks the next rung. Don't stop at "I can't".

## Range in practice

- To find the fields, ask: "If this had to be extraordinary, who would humanity bring in?" For a QBR, that is an analyst, a journalist, an editor, a motion designer, and a red team (a short seller and a forensic accountant).
- To run the fields as parallel agents, use a multi-agent skill if one is installed (for example `heavy-think` Perspectives mode or `council`), or else plain subagents. Do this when 3 or more fields each need real work, such as research, data or a build, or when the user asks for several views. Let that skill own the multi-agent mechanism. Don't rebuild it here.
- In one context, use each field's *methods* one after another, then merge.

## Mode: rewrite a prompt

When the user gives a prompt and asks for the ambitious version, work through steps 1–4 silently. They shape the prompt, and are not output. The user approves the higher altitude by choosing to use the prompt. The judge goes *into* the prompt as a check the model must run.

1. Say what a top professional would do here that the prompt does not ask for.
2. Name the rawest material they would start from.
3. Name their specific methods and tools.
4. Name what, other than the model or the user, would show the result is right.
5. Rewrite the prompt to ask for exactly that, with the goal behind the goal and a hard target. Keep it short enough to paste.

Return the rewritten prompt in a code block, then up to three lines on what changed.

## Guardrails

- **Ambition is not scope creep.** Propose higher-altitude goals. Do them only after the user agrees. In a codebase, the diff still covers only what the user approved.
- **Score by running cost.** A bigger design that adds infra, services or things to watch must win on running cost (infra, operations, maintenance), not on impressiveness.
- **Tools are a requirement.** Depth and the outside judge need a real computer, data access and runnable checks. Without them, say which parts became words instead of actions.
