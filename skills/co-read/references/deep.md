# Deep mode

The owner does the generative steps. Claude guides, reviews, recalls and runs
experiments. Each step waits for the owner's input before Claude reveals its own.

## Steps

| Step | Owner must | Claude does | Claude must not |
|------|----------|-------------|-----------------|
| 0 Recall | Answer 2–3 questions on bricks from past cards, without looking | Pick bricks the owner will meet again in this source; give feedback after each answer | Give the answer before the owner tries; run this step when the owner is overloaded |
| 1 Guess | Write 3 lines: what problem they solve, and their bet | Then give the reading map: where gems likely are and why; 3–5 questions to carry; "you own these bricks, skim §X"; "this part is new" | Summarise the source or name its conclusion |
| 2 Read | Mark what is interesting or odd; write hunches | Prepare margin notes, each tagged `[gem: <type>]` with its passage, kept hidden | Show notes before the owner says they are done |
| 3 Compare | Mark each Claude note: agree / disagree / couldn't see | Reveal by the hint ladder; log gems the owner saw that Claude missed; ledger the disagreements | Win a disagreement by authority |
| 4 Card | Write the card (schema `Idea Card`) in their words | Review: roles named by job, quotes present, bet vs result kept apart; link bricks to the bank and flag same-structure bricks under other names | Rewrite the card for them |
| 5 Hands-on | Re-derive one key equation, or type the ~20 core lines of the main brick on toy data | Write loaders, plots, harness; explain errors when asked | Write the core lines |
| 6 Mutation duel | Propose mutations first (aim for 3+) | Propose after, typed by operator; the owner keeps or kills each with a reason; hand the survivors to `idea-forge` | Present a list for the owner to nod at |
| 7 Kill test | Pick one mutation; write a prediction and the pass line | Build and run the cheapest test that could kill it (`paper-replicate`; the owner's GPU machine from `me/profile.md`, per the rules there, when idle); report real numbers | Change the pass line after the run |
| 8 Teach-back | Explain the idea in 5 sentences, as to a colleague | Ask about each gap; note what to revisit | Correct it for them |

**Skim** runs steps 1, 3 and 8 only. The owner still guesses first and teaches back.

## Hint ladder

The owner opens a hint by saying what they tried.

| Level | Example |
|-------|---------|
| 1 | "Something in Methods §3 is worth a second look." |
| 2 | "It is about why they chose X over Y." |
| 3 | The full note: the quote, the brick link, the gem type and why it matters |

Start level comes from `progress.md`: where the owner's unaided gem count is rising,
start at level 1 and wait longer; where they are stuck, start at level 2.

## Disagreement ledger

| Point | Owner's view | Claude's view | How to settle | Status |
|-------|-----------|---------------|---------------|--------|

Prefer "settle by experiment" or "settle by a second source". "Open" is a valid
status. Claude argues the strongest opposite case once per conclusion.

## Kill test rules

- The prediction and the pass line are written in the Reading file before the
  run starts.
- The cheapest test that could kill the idea comes first: a toy dataset, a small
  simulation, a five-minute script.
- Report the miss with the real output. A killed idea is a good result; record it
  in the brick's `kill_tests`.
- Heavy compute: check the machine in `me/profile.md` (`Compute`) first;
  long jobs follow the rules written there.
