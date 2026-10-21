# Team Debate

The one playbook for a live debate: named teammates argue with each other through the team's
message tool (`SendMessage` in Claude Code), you moderate, and you write the verdict. `/debate` and heavy-think's Debate escalation
both run this file.

Contents: Before you start · Why the playbook looks like this · The playbook · Formats · Debater spawn
template · Fallback

## Before you start

- **Main session, in a harness with live teams** (`harness.md`; in Claude Code,
  `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`). Teammates cannot spawn teammates, so
  inside a subagent (the `heavy-thinker` agent, for one) a team debate cannot run. If either is
  missing, say so and use the Fallback, labelled as simulated: a role-played debate passed off as a
  live one would mislead the user about how the answer was tested.
- **Worth it?** A debate costs 3-5x a single pass. Use it for a decision with genuinely conflicting
  options, low first-pass confidence, high stakes, or when the user asks ("debate this",
  "pressure-test", "steelman", "red-team"). Say in one line why you are running one.
- **Model.** Teammates run on this session's model unless the user named another; pass it explicitly.

Done means: `verdict.md` is written, the reply is given, and every teammate is shut down.

## Why the playbook looks like this

`python3 "$HT/deck.py" debates` (`HT`: the heavy-think skill folder, the parent of this `references/`
folder) prints the formats and the evidence-backed rules. Run it at the start. Each rule shapes a step:

| Deck rule | Where it shows up |
|---|---|
| Compare against a plain vote | Step 3: every debater answers alone first; the verdict is compared with that baseline |
| Diversify the reasoning method, not the persona | Step 1: each debater gets a different method |
| Stop after one or two rounds | Step 4: the cap, stated once |
| Keep dissent moderate | The spawn template: disagree where the method supports it, concede with a reason |
| 3 or 4 distinct roles when judging | Step 1: roster size |
| Never let the author review its own work | You moderate and never argue a side |

## The playbook

1. **Frame the motion, pick the format, cast the roster.** The motion is one debatable sentence (A vs
   B, or yes/no) plus the hidden axes that would change the verdict. Pick the format from the deck
   list by its `when` line (Formats, below) and say which and why in one line. Cast 2-4 debaters (3-4
   when the debate judges a draft or plan). Give each the role its format assigns and a different
   reasoning method: first principles, base rates (the reference class and its usual outcome),
   working backwards from failure, analogy from another field, or an evidence audit (what we would
   have to observe for each side to be true). Personas change the words; methods change what gets
   found.
2. **Open the transcript.** Create `debate/<YYYYMMDD-HHMM>-<short-motion>/` in the working directory
   and write `motion.md`: the motion, the format, the roster (name, role, method) and the round cap.
   Each debater appends what it sends to `<name>.md` there; you write `baseline.md` and `verdict.md`.
   The folder is what lets anyone audit or re-judge the debate later.
3. **Alone first: the baseline vote.** Spawn every debater in one message with the template below.
   Each first writes its own answer (answer, confidence 0-100, the fact that would change it) without
   reading anyone, and sends it to you only. When all are in, write them to `baseline.md` with the
   tally. That is the plain vote the debate has to beat.
4. **Open the debate.** Message each debater "open". The cap is **two rounds**: a round is each
   debater sending one message to each opponent and answering what it received. Most of a debate's
   gain arrives in the first round, and later rounds add agreement, not accuracy. Close earlier when
   the exchanges only restate.
5. **Moderate, don't argue.** When debaters talk past each other, ask one sharpening question. When a
   debater concedes without a reason, ask for the reason. When one attacks everything, ask which
   objection it would keep if it could keep one. Never argue a side: that removes the independence the
   debate is for.
6. **Close.** Ask each debater for what it concedes and why, what survives, and its final answer
   with confidence.
7. **Verdict (you, never delegated).** Write `verdict.md`, then the reply:
   - the decision and the conditions under which it holds;
   - what survived challenge and what broke, and which argument did the breaking;
   - against the baseline: did the final answer differ from the alone-first vote? If not, say the
     debate added conditions or confidence, not a new answer. If it did, name the argument that moved
     it. Report the spread of final confidences, not only the consensus;
   - claims the verdict leans on that no debater sourced are leads: check them, cut them, or mark
     them at that line.

   Write it as heavy-think's reply (`../SKILL.md`, The reply): the position and its conditions, not a
   transcript of who said what. Give the transcript folder path in one line at the end.
8. **Shut down** every teammate.

## Formats

Fill the template's `{format_role}` from this table. `blind-first` is step 3 for every format; picked on
its own, it is step 3 plus one reveal-and-revise round (cap one round).

| Format (deck id) | Each debater's `{format_role}` | Round shape |
|---|---|---|
| `position` | "You hold {position}. Argue for it against the others' positions." | Open with your case, then answer theirs |
| `disprove` | "You hold hypothesis {position}. Try to disprove the others' hypotheses with evidence; yours stands only if theirs fall." | Each round: one disproof per rival hypothesis |
| `steelman` | "Before any rebuttal, restate each opponent's case better than they did, and get them to accept the restatement." | Restate, then rebut |
| `method-cards` | "No assigned position: answer the motion with your method only." | Compare where the methods disagree |
| `calibrated-critic` | Critic: "Find the real flaws in {draft}; you may concede. Strict, not absolute." Author: "Defend {draft} or change it." A third debater judges | Critic, defence, judge rules |
| `authentic-dissent` | Dissenter: "You want {conflicting goal}. Defeat the plan." Others: "Defend the plan." | Attack, defence; you rule after both have fought |
| `opposite-rigor` | One: "Make the case for." The other: "Make the case against, with the same rigour and the same length." | One case each, then one answer each |
| `pr-faq` | Author: "Write the launch press release and the hardest customer and internal FAQ." Reviewers: "Attack only the FAQ answers." | FAQ, attacks, revised answers |
| `cross-model` | Needs a reviewer from another model family. Teammates all run this model, so this format cannot run here: say so and suggest running the reviewer through that model's own CLI | |

## Debater spawn template

```text
You are {name}, one of {n} debaters on the motion below. You reach the others only through the team's message tool, by name. Nobody sees your plain text output, so anything you want counted goes in a message.

Motion: {motion}
Context and constraints: {context}
Format: {format_name}. Your role: {format_role}
Your reasoning method: {method}. Reason with it and say when an argument comes from it. The other debaters use different methods on purpose, so what you add is what this method finds.
The others: {roster: name, role, method}
Moderator: {moderator}, who opens, steers and closes the debate.
Transcript: append every message you send, word for word, under a heading naming the recipient, to {transcript_dir}/{name}.md. Write nothing else on disk.

1. Alone first. Before you read any message from another debater, write your own answer to the motion: the answer, your confidence from 0 to 100, and the one fact that would change it. Append it to your transcript under "## Baseline" and send it to the moderator only. Then wait for the moderator's "open".
2. After "open", play your role. Answer the latest version of each argument, not an opponent's opening once they have moved on. At most {rounds} rounds; a round is one message to each other debater plus your answers to theirs.
3. Disagree where your method and the evidence support it, and concede where an argument is right, with the reason. Attacking everything and agreeing to be agreeable both hide what actually holds, which is what the moderator needs.
4. Mark each claim as checked (with its source) or as your reasoning.
5. When the moderator asks you to close: what you concede and why, what survives, and your final answer with confidence from 0 to 100.

Do not edit anything except your transcript file, and do not spawn agents.
```

## Fallback

Without live teams, or inside a sub-agent, use heavy-think's Round Protocol (`../SKILL.md`, Escalation:
Agent Debate, Fallback): subagents cannot talk to each other, so you relay frozen positions between
rounds. Keep steps 1-3 and 7 of this playbook (a method per debater, the transcript, the baseline
vote, the verdict against the baseline), and tell the user it was simulated.
