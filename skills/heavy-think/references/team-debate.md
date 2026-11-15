# Team Debate

The one playbook for a live debate: named debaters argue on a shared board and in direct duels, you
moderate, and you write the verdict from the board. It runs the live protocol (`live-protocol.md`) on
any live-team transport (`harness.md`, Live-team transports). `/debate` and heavy-think's Debate
escalation both run this file.

Contents: Before you start · Why the playbook looks like this · The playbook · Formats · Debater spawn
template · Fallback

## Before you start

- **A live-team transport** (`harness.md`). Each has its own limits: Claude Code agent teams run only
  from the main session, because a teammate cannot spawn teammates, so inside a subagent use
  harness-ops sessions or the Fallback. With no transport, say so and use the Fallback, labelled as
  simulated: a role-played debate passed off as a live one would mislead the user about how the
  answer was tested.
- **Worth it?** A debate costs 3-5x a single pass. Use it for a decision with genuinely conflicting
  options, low first-pass confidence, high stakes, or when the user asks ("debate this",
  "pressure-test", "steelman", "red-team"). Say in one line why you are running one.
- **Model.** Debaters run on `session` unless the user named another or the diversity setting says
  otherwise (`harness.md`, Diversity). The `cross-model` format and a debate that judges a review are
  `mixed`. Pass each debater's model role explicitly.

Done means: `verdict.md` is written, the reply is given, and every debater is shut down.

## Why the playbook looks like this

`python3 "$HT/deck.py" debates` (`HT`: the heavy-think skill folder, the parent of this `references/`
folder) prints the formats and the evidence-backed rules. Run it at the start. Each rule shapes a step:

| Deck rule | Where it shows up |
|---|---|
| Compare against a plain vote | Step 3: every debater opens alone first; the verdict is compared with that baseline |
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
2. **Open the session.** Create `debate/<YYYYMMDD-HHMM>-<short-motion>/` in the working directory and
   write `motion.md`: the motion, the format, the roster (name, role, method, model role), the
   transport, the diversity setting and the round cap. Create an empty `board.md` beside it: the
   debaters write only there; you write `baseline.md` and `verdict.md`. The folder is what lets anyone
   audit or re-judge the debate later.
3. **Openings, alone: the baseline vote.** Start every debater with the template below (transport
   table). Send all of them `Your turn: round 1`. Each appends its opening (answer, confidence 0-100,
   the fact that would change it, and its case) without reading the board. When all are done, write
   them to `baseline.md` with the tally. That is the plain vote the debate has to beat.
4. **Cross-examine.** Shape it by roster size (`live-protocol.md`, Shape by size):
   - 2 debaters: one duel (round 2). They question each other directly, 3 messages each.
   - 3: lead turns in a fixed order (round 2), each answering the latest version of every opponent's
     case on the board; then, if two still clash on the point that decides the motion, one duel
     between them (round 3).
   - 4: lead turns only.

   The cap is **two exchange rounds** after the openings (a lead-turn round or a duel each count as
   one). Most of a debate's gain arrives in the first, and later rounds add agreement, not accuracy.
   Close earlier when the board only restates.
5. **Moderate, don't argue.** Your one line of focus in `Your turn` is the tool. When debaters talk
   past each other, ask one sharpening question. When a debater concedes without a reason, ask for
   the reason. When one attacks everything, ask which objection it would keep if it could keep one.
   Never argue a side: that removes the independence the debate is for.
6. **Close.** Send every debater `Your turn: round N (close)`: each appends what it concedes and why,
   what survives, and its final answer with confidence.
7. **Verdict (you, never delegated), from the board alone.** Judge only what is on the board, not your
   own view of the motion. Write `verdict.md`, then the reply:
   - the decision and the conditions under which it holds;
   - what survived challenge and what broke, and which argument (on the board) did the breaking;
   - against the baseline: did the final answer differ from the alone-first vote? If not, say the
     debate added conditions or confidence, not a new answer. If it did, name the argument that moved
     it. Report the spread of final confidences, not only the consensus;
   - claims the verdict leans on that no debater sourced are leads: check them, cut them, or mark
     them at that line.

   Write it as heavy-think's reply (`../SKILL.md`, The reply): the position and its conditions, not a
   transcript of who said what. Give the session folder path in one line at the end.
8. **Shut down** every debater (transport table), and check nothing you started is still open.

## Formats

Fill the template's `{format_role}` from this table. `blind-first` is step 3 for every format; picked on
its own, it is step 3 plus one reveal-and-revise round (cap one round).

| Format (deck id) | Each debater's `{format_role}` | Round shape |
|---|---|---|
| `position` | "You hold {position}. Argue for it against the others' positions." | Open with your case, then answer theirs |
| `disprove` | "You hold hypothesis {position}. Try to disprove the others' hypotheses with evidence; yours stands only if theirs fall." | Each round: one disproof per rival hypothesis |
| `steelman` | "Before any rebuttal, restate each opponent's case better than they did, and get them to accept the restatement." | Restate, then rebut |
| `method-cards` | "No assigned position: answer the motion with your method only." | Compare where the methods disagree |
| `calibrated-critic` | Critic: "Find the real flaws in {draft}; you may concede. Strict, not absolute." Author: "Defend {draft} or change it." A third debater judges | Critic and author duel; the judge rules from the board |
| `authentic-dissent` | Dissenter: "You want {conflicting goal}. Defeat the plan." Others: "Defend the plan." | Attack, defence; you rule after both have fought |
| `opposite-rigor` | One: "Make the case for." The other: "Make the case against, with the same rigour and the same length." | One case each, then one duel |
| `pr-faq` | Author: "Write the launch press release and the hardest customer and internal FAQ." Reviewers: "Attack only the FAQ answers." | FAQ, attacks, revised answers |
| `cross-model` | Reviewer (`other-family`): "Review {work} from outside the others' model family. Every claim needs evidence; concede nothing without a reason." The others defend or fix | Review, defence, then a duel on what stays disputed. Diversity `mixed`. Needs a transport that starts other harnesses (harness-ops sessions). On a transport with one model family, it cannot run: say so, and suggest harness-ops or running the reviewer through that model's own CLI |

## Debater spawn template

Append the member protocol block from `live-protocol.md` to this template.

```text
You are {name}, one of {n} debaters on the motion below. The debate happens on a shared board and, when the moderator opens one, in a direct duel. The protocol below says how.

Motion: {motion}
Context and constraints: {context}
Format: {format_name}. Your role: {format_role}
Your reasoning method: {method}. Reason with it and say when an argument comes from it. The other debaters use different methods on purpose, so what you add is what this method finds.
The others: {roster: name, role, method}
Moderator: {moderator}, who opens, steers and closes every round.

1. Round 1, alone: append your opening: the answer, your confidence from 0 to 100, the one fact that would change it, and your case.
2. Later rounds: play your role. Answer the latest version of each argument on the board, not an opponent's opening once they have moved on. At most {rounds} exchange rounds.
3. Disagree where your method and the evidence support it, and concede where an argument is right, with the reason. Attacking everything and agreeing to be agreeable both hide what actually holds, which is what the moderator needs.
4. Mark each claim as checked (with its source) or as your reasoning.
5. When the moderator asks you to close: what you concede and why, what survives, and your final answer with confidence from 0 to 100.

{member protocol block}
```

## Fallback

Without a live-team transport, use heavy-think's Round Protocol (`../SKILL.md`, Escalation: Agent
Debate, Fallback): subagents cannot talk to each other, so you relay frozen positions between rounds.
Keep steps 1-3 and 7 of this playbook (a method per debater, the session folder, the baseline vote,
the verdict against the baseline), and tell the user it was simulated.
