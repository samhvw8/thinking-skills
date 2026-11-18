# agent-ops split eval: result (2026-11-18)

This file covers two arms: **split**, which lost (first part), and **split2**, which passed and shipped (the follow-up at the end).

**Decision: the split loses. The live skill was not touched.** In counted pairs, current beat split 8 to 0,
with 2 split pairs and no agreed ties.

**Noise floor.** Current against a second current run, on the 5 pre-registered scenarios, gave current 1, current2 3
and 1 split pair. So 4 of 5 same-arm pairs still produced a counted winner: a single counted pair is weak evidence.
The evidence is the direction: the noise pairs go both ways, while all 8 counted split pairs go to current. Under the
pre-registered rule, the split's 8 counted losses in 10 pairs exceed the noise floor's 3 in 5 (80% against 60%).
A sign test, added after unblinding, gives p ≈ 0.008 for 8-0.

## Setup

- **Arms.** `arms/current/agent-ops/` is the live skill, copied unchanged. `arms/split/agent-ops/` has a 14,070-byte
  SKILL.md core plus `layout.md`, `tasks.md`, `dialogs.md`, `worktree.md`, `pair.md`, `live-team.md`, `swarm.md` and `roles.md`. The
  briefs and the roster are unchanged, except for one pointer in `roster.md`.
- **Content identity.** `arms/split-identity.txt` was checked by a script, line by line, as a multiset. The only original
  lines missing from the split are 8 cross-references, each retargeted from "## X" to the file name. The only added
  lines are the reference map, the file titles and a one-line stub in `tasks.md` that points to `dialogs.md`.
- **Subjects.** `run-subject.sh` runs `claude -p` with claude-sonnet-5-5, `--safe-mode` (no CLAUDE.md, skills or hooks),
  `--restricted` and `--tools Read,Glob`. Each run folder holds only that arm's files. SKILL.md is injected with its
  base directory, the way the Skill tool loads it, and the subject Reads the other files on its own. A smoke test confirmed
  that the tools were only Read and Glob, that no CLAUDE.md loaded, and that a Read of the live hub path was refused.
- **Judges.** `judge/` is adapted from search-evals and runs claude-sonnet-5-5 the same way. A judge sees the rubric
  (commands, rules, completeness, usefulness), the packet and the current skill as the reference. Pairs are shown
  in both orders, and a pair counts only when both orders pick the same winner. Run folders have shuffled neutral ids,
  and paths in the plans are normalized. A scan found no split file names in any packet.
- **Pre-registration.** The noise-floor scenarios were fixed before any run: s03, s05, s06, s07 and s08. So was the
  decision rule: ship only if counted split losses do not exceed the noise floor and the split loads fewer tokens.
- **Cap.** The run used 58 model calls: 1 smoke test, 25 subjects, 30 judges and 2 re-judged packets.

## Per-scenario verdicts (judges' reasons, unblinded)

```
s01_short_send current vs split: o1=current o2=current -> counted: current
    o1: Answer 2 ends with `ls --mine` and `task ls`, which the reference's 'Close what you start' rule requires before reporting work done. It also handles the exit-5 wait timeout more fully. Answer 1 has no cleanup step.
    o2: Answer 1 includes the reference's pre-report cleanup check (`ls --mine` and `task ls`), which Answer 2 omits. Otherwise the plans follow the same rules.
s02_long_send current vs split: o1=current o2=current -> counted: current
    o1: Both follow the send, note, queue and no-force rules; Answer 2 adds the required pre-report `ls --mine` and `task ls` check and a guard against destructive requests in the peer's reply.
    o2: Answer 1 stops at a dialog on the target pane (Sam's call) and ends with the ls --mine / task ls check. Answer 2 sends into a pane that may be showing a dialog and has no closing check.
s03_receive current vs split: o1=current o2=current -> counted: current
    o1: Both refuse to push or delete without Sam and skip /tmp. Answer 2 uses a runnable read command, includes the required ls --mine and task ls cleanup, and handles the remote delete and the push separately.
    o2: Answer 1 covers the reference's pre-report cleanup (`ls --mine`, `task ls`) and shows Sam the push contents before pushing, and keeps the remote-branch delete as a separate ask; Answer 2 skips the cleanup check and pushes without showing the log.
s03_receive current vs current2: o1=current o2=current -> counted: current
    o1: Rule on destructive or outward actions needing Sam's approval: Answer 1 asks for the numbering change, branch delete and push separately and shows the push contents first, while Answer 2 bundles delete and push into one approval.
    o2: Both refuse the destructive actions, skip the /tmp file and reply to the sender. Answer 2 splits delete and push into separate approvals, shows the unpushed log first and warns that the PDF work would go with a push.
s04_task_wait current vs split: o1=current o2=current -> counted: current
    o1: Answer 1 covers the full dialog rule set: --persist, never answering a folder-trust dialog, denying a too-tall or unrecognized dialog, and exit 7. Answer 2 omits these and leaves a placeholder brief in its task new command.
    o2: Answer 2 covers the dialog rules more fully: --persist for recurring commands, never answering a folder-trust dialog, and tall-dialog and exit 7 handling. Answer 1 lacks these in its dialog section.
s05_dialog current vs split: o1=current o2=current -> counted: current
    o1: The reference says to answer a repeating linter dialog with the always-allow choice and --persist, and Answer 1 does this while Answer 2 refuses to. Answer 1 also covers accept --close, worktree and branch cleanup, and the ls --mine and task ls check; Answer 2 omits them.
    o2: The reference says to use the always-allow choice with --persist for a recurring linter dialog, and Answer 2 does that while Answer 1 does not. Answer 2 also follows the reference on accept --close and on cleanup (worktree, branch, ls --mine and task ls), which Answer 1 mostly omits.
s05_dialog current vs current2: o1=current2 o2=current2 -> counted: current2
    o1: Both approve the lint dialog with --persist and deny the push with --expect and a task send. Answer 1 is slightly more complete: it has an explicit report to Sam and handles the over-tall request case.
    o2: Both approve the lint dialog with --persist and deny the push with --expect and a task send. Answer 2 adds the explicit untrusted-text rule, a fuller report to Sam, and a safer exit 6 path (read the pane and ask Sam).
s06_pair current vs current2: o1=current2 o2=current2 -> counted: current2
    o1: Answer 2 follows the untrusted-file path rule, files summaries with `note`, and handles an already-idle omp pane. Answer 1 has a sloppy sender-id placeholder in its brief and doesn't consider an idle partner.
    o2: Answer 1's brief is complete and runnable, with the real whoami id, 'Your turn: accept or decline', correct dialog answer/deny with --expect, summary paths read only under the allowed folders, and full cleanup. Answer 2 leaves placeholders and a vague id in the brief, investigates before briefing, and sends PAIR DONE and closes the pane before the merge.
s06_pair current vs split: o1=split o2=current -> split (not counted)
    o1: Answer 1's brief follows pair-brief.md and its rules more closely (decline path, 'Your turn:' on each handoff, no thanks). Answer 2 breaks the 'no thanks' rule and leaves a muddled id line in its brief. Answer 1's garbled phase 4 text kept the margin small.
    o2: Answer 1 closes the pane on a failed spawn and runs the final ls --mine and task ls check. Answer 2 leaves the pane open on exit 5, skips that check, and its brief has a garbled phase 4 that the operator must patch.
s07_live_team current vs split: o1=current o2=split -> split (not counted)
    o1: Answer 1 verifies cleanup with ls --mine and task ls before reporting, as the reference requires, and opens its duel in round 2. Answer 2 never runs that check and is slightly less efficient on rounds.
    o2: Answer 1 keeps control messages to bare 'Your turn:' lines and never uses close --force. Answer 2 puts instructions in its turn messages and allows --force on close.
s07_live_team current vs current2: o1=current2 o2=tie -> split (not counted)
    o1: Answer 1 sends the exact 'Your turn: round N' messages the group-brief protocol requires and records the lead id from whoami; Answer 2 pads those turn messages and adds a non-required name step.
    o2: Both follow the reference live-team protocol with valid commands and the same safety rules. Answer 1's extra operational detail offsets Answer 2's closer match to the reference on the lead id, spawn-failure handling and member-decline cases.
s08_swarm current vs split: o1=current o2=current -> counted: current
    o1: Answer 1 is fully runnable and correctly leaves worker dialogs to the manager that owns them. Answer 2 has the director answering dialogs on panes it did not start, though it adds a few extra cleanup checks.
    o2: Answer 2 writes out the manager and worker briefs and routes worker dialogs correctly (to the manager). Answer 1 has the director answering worker dialogs, which the reference doesn't allow, and leaves the briefs as fill-in steps.
s08_swarm current vs current2: o1=current2 o2=current2 -> counted: current2
    o1: Answer 1's manager brief carries the worker-dialog policy (answer only repo reads or run-folder writes, deny the rest, never answer a folder-trust dialog), which the reference requires. Answer 2's manager brief omits it.
    o2: Answer 2's manager brief tells the manager how to answer or deny worker permission dialogs (never folder-trust). Answer 1's brief leaves that out, so workers could stall.
s09_resume current vs split: o1=current o2=current -> counted: current
    o1: Answer 2 follows the reference on `task accept --close`, the rule against approving a dialog request it cannot see whole, report-before-replace, and worktree and `ls --mine` cleanup. Answer 1 starts a replacement worker without reporting to Sam and skips cleanup.
    o2: Answer 2 starts a replacement worker without reporting to Sam first, and it skips the final ls --mine check and worktree/branch cleanup; Answer 1 follows the close-what-you-start and report-first rules.
s10_draft current vs split: o1=current o2=current -> counted: current
    o1: Both refuse --force and ask Sam. Answer 1 also covers the dialog-is-Sam's rule, reporting the build result to Sam, and leaving Sam's session open. Answer 2 omits the report to Sam.
    o2: Both refuse --force without Sam's explicit yes. Answer 2 also covers the Sam-owned dialog rule, the report to Sam, and leaving the session Sam opened open.

Totals (counted pairs only):
  current vs current2: current 1, current2 3, agreed tie 0, split 1
  current vs split: current 8, split 0, agreed tie 0, split 2

Mean scores (all judgments):
  current         commands=9.1 rules=8.8 completeness=8.9 usefulness=8.4 total=35.2
  noise:current   commands=9.0 rules=8.5 completeness=8.4 usefulness=8.3 total=34.2
  noise:current2  commands=9.1 rules=9.0 completeness=9.0 usefulness=8.6 total=35.7
  split           commands=8.8 rules=8.1 completeness=7.5 usefulness=8.0 total=32.2```

**Re-judged pair.** The split's s07 plan (16,957 characters) went past the first packet limit of 16,000, and one judge
cited "its closing section is cut off". The limit was raised to 40,000 and the packets rebuilt with the same seed
(`key.json` unchanged). Both s07 current-vs-split packets were re-judged; the verdicts above are the new ones. The
outcome is still a split pair, not counted. The old verdicts were: o1 = current ("adds a lead recommendation line, and
its closing section is cut off") and o2 = split ("unescaped nested EOF ... allows --force on close"). They are kept in
`out/run1/verdicts-superseded/`.

## Why it lost (from the judges' reasons)

The split subjects open reference files only when the scenario names that kind of job. In s04, s06, s07 and s08
they read `tasks.md`, `pair.md`, `live-team.md` and `swarm.md`. In s01, s02, s03, s05, s09 and s10 they read none.

The current skill keeps several cross-cutting rules in view on every load. In the split they sit in `tasks.md` or
`dialogs.md`, so those subjects never saw them:
- "Close what you start" and the `ls --mine` / `task ls` check before reporting (cited in s01, s02, s03, s09 and s10).
- "Report to Sam before you start a replacement" (s09).
- The full dialog rules (s04 and s05).

Not every loss comes from unread files. In s08 the split subject read `swarm.md`, `tasks.md` and `dialogs.md`, and
lost because its director answered worker dialogs on panes it did not start (both orders).

In s05 the split subject got two DIALOG notices and never opened `dialogs.md`, even though the receive table points
there. It refused the "always allow" choice with `--persist` for a recurring linter command, which the rules require
("Sam wants the lead to grant those").

## Skill text loaded per scenario (bytes / approx tokens = bytes/4)

SKILL.md counts as always loaded; any other skill file the subject Read is added to it.

| Scenario | current | split | split read |
|---|---|---|---|
| s01_short_send | 33459 / ~8364 | 14070 / ~3517 | (none) |
| s02_long_send | 33459 / ~8364 | 14070 / ~3517 | (none) |
| s03_receive | 33459 / ~8364 | 14070 / ~3517 | (none) |
| s04_task_wait | 33459 / ~8364 | 25862 / ~6465 | layout.md,roles.md,roster.md,tasks.md,worktree.md |
| s05_dialog | 33459 / ~8364 | 14070 / ~3517 | (none) |
| s06_pair | 33459 / ~8364 | 32014 / ~8003 | dialogs.md,duel-brief.md,layout.md,pair-brief.md,pair.md,roles.md,roster.md,worktree.md |
| s07_live_team | 41294 / ~10323 | 34437 / ~8609 | dialogs.md,duel-brief.md,group-brief.md,layout.md,live-team.md,roles.md,roster.md,worktree.md |
| s08_swarm | 40943 / ~10235 | 33379 / ~8344 | dialogs.md,layout.md,manager-brief.md,roles.md,roster.md,swarm.md,tasks.md,worker-brief.md |
| s09_resume | 33459 / ~8364 | 14070 / ~3517 | (none) |
| s10_draft | 33459 / ~8364 | 14070 / ~3517 | (none) |
| **Sum** | 349909 / ~87477 | 210112 / ~52528 | |

The split loaded 40% fewer skill bytes overall: 58% fewer on a core-only scenario,
and 4-19% fewer on pair, live-team and swarm scenarios.

## Cost

| Item | Calls | USD |
|---|---|---|
| Subjects | 25 | 2.42 |
| Judges | 30 | 3.53 |
| Re-judged s07 packets | 2 | 0.30 |
| Smoke test | 1 | 0.02 |
| **Total** | **58** | **6.27** |

The dollar figures are `total_cost_usd` from the CLI, at API rates; this run was on an OAuth login.

## Pointers to agent-ops sections, and where the split would put them

| Pointer | Target in the split |
|---|---|
| hub `rules/delegation-protocol.md:14-16`: "agent-ops (`harness-ops task new`)" | The skill; the command list in core SKILL.md |
| hub `rules/delegation-protocol.md:20`: `agent-ops` skill, "Live team" | Map row in SKILL.md, then `live-team.md` (## Live team) |
| hub `agents/heavy-thinker.md:249`: the agent-ops skill's "Live team" | `live-team.md` (## Live team) |
| hub `skills/lead-researcher/references/team-research.md:25`: `../../agent-ops/roster.md` | `roster.md`, unchanged path |
| `team-research.md:42`: load the agent-ops skill before the first `task new` | The skill |
| `team-research.md:60`: agent-ops rules for a task that fails to start or stops answering | `tasks.md` (## Task or subagent) |
| `team-research.md:132`: `../../agent-ops/SKILL.md`, "Task or subagent", "Live team", "Roles" | SKILL.md map, then `tasks.md`, `live-team.md`, `roles.md` |
| `lead-researcher/SKILL.md:3,30` and `references/planning.md:85`: harness-ops sessions through agent-ops | The skill |
| agent-ops `roster.md:3`: "(SKILL.md, ## Roles)" | Retargeted in the split to "(`roles.md`, ## Roles)" |
| thinking-skills `heavy-think/SKILL.md:204`: the agent-ops skill's Swarm section | `swarm.md` (## Swarm) |
| thinking-skills `heavy-think/references/harness.md:33,63,66`: Live team, Swarm and Roles sections | `live-team.md`, `swarm.md`, `roles.md` |
| thinking-skills `heavy-think/references/live-protocol.md:4`: agent-ops swarm | `swarm.md` |

council, debate and heavy-think are installed from the thinking-skills source
(`~/.ccp/sources/samhvw8--thinking-skills`), not from the hub. The council and debate skill files have no direct agent-ops
section pointer. None of these files were edited.

## Limits of this eval

- In the first judging pass, the verdict files sat in the judges' own restricted folder, so a judge could have read
  another judge's verdict. Judge output was saved as `json`, not `stream-json`, so which files each judge read cannot be
  audited. `run-judges.sh` now writes verdicts to `out/<run>/verdicts/`, outside that folder; the 2 re-judged packets ran
  that way.
- One run per arm per scenario, a sonnet subject and sonnet judges. Each subject wrote a plan; none ran a real
  harness-ops session.

## Not done

- Nothing was copied to the live hub, and there is no commit, push or sync, because the split lost.
- A second split arm was run later, approved by Sam: see "Follow-up: split2" below.

## Files

- `arms/`: both arms, their sha256 lists and `split-identity.txt`
- `scenarios/`, `subject-prompt.md`, `run-subject.sh`, `run-all.sh`, `metrics.py`
- `judge/`: `rubric.md`, `prepare.py`, `run-judges.sh`, `extract_verdict.py`, `tally.py`
- `out/run1/`: plans, transcripts, metrics, packets, verdicts, `key.json`, `tally.txt`

# Follow-up: split2 (2026-11-18)

**Decision: split2 passes the ship rule and was applied to the live hub.** In counted pairs, current scored 3 and
split2 scored 4, with 3 split pairs. split2's 3 counted losses do not exceed the noise floor from run1, which is 3
counted losses for one arm in 5 same-arm pairs. Summed over the 10 scenarios, split2 loads
245637 skill bytes against 349909 for current, 30% fewer.
The rule was written to `out/run2/protocol.txt` before any split2 run or judge.

## The arm

- **Built from the live skill.** `arms/split2/agent-ops/` comes from the live skill, which was unchanged since the
  run1 copy (sha256 checked).
- **The core keeps every rule used across scenarios.** `SKILL.md` (19,747 bytes, ~4.9k tokens) holds:
  - the commands and setup notes
  - Find the right pane and When to send
  - **all of ## Task or subagent**: the full dialog rules, a task that failed to start, a worker that stops answering,
    and "Close what you start" with the `ls --mine` / `task ls` check
  - ## Run a crew
  - How to write a message, When a message arrives and Check
- **Only procedures moved out:** `layout.md`, `worktree.md`, `pair.md`, `live-team.md`, `swarm.md` and `roles.md`.
- **Content identity, checked by script** (`arms/split2-identity.txt`). Only 6 original lines are missing, and each is a
  cross-reference retargeted to a file name. The only added lines are the map, the file titles and those retargets.

## Per-scenario verdicts (judges' reasons, unblinded)

The current plans are the run1 plans, reused. The split2 plans are 10 new runs. Subjects, judges, rubric and
both-orders counting are the same as run1. Verdicts are stored outside the judges' folder.

```
s01_short_send current vs split2: o1=current o2=current -> counted: current
    o1: Answer 2 follows the reference's 'check in: read first' rule and ends with the required `ls --mine` and `task ls` check. Answer 1 skips both.
    o2: Answer 1 reads the screen first and runs the required `ls --mine` and `task ls` check before reporting. Answer 2 skips both.
s02_long_send current vs split2: o1=split2 o2=split2 -> counted: split2
    o1: Answer 1 covers the 'text stayed on input line' read-first rule, says a dialog on a found session is Sam's, and bars push/deploy in the brief. Answer 2 omits the first, states the second less directly, and has no push/deploy bar in its brief.
    o2: Both correctly send the spec to the shop-api owner via note and send. Answer 2 also covers the 'text stayed on the input line' case, forbids push and deploy in the brief, and notes the ITERM_SESSION_ID workaround.
s03_receive current vs split2: o1=current o2=current -> counted: current
    o1: Both refuse the delete and push on a peer's word, read only the journal spec, and reply to billing with RE:. Answer 1 is more complete: it uses branch -d before any -D, shows the push diff, and ends with the ls --mine and task ls cleanup check.
    o2: Both refuse the destructive actions and reply to the sender, but Answer 2 adds the reference's ownership check before editing, a safe `-d` branch delete, and the `ls --mine` and `task ls` check before finishing.
s04_task_wait current vs split2: o1=split2 o2=split2 -> counted: split2
    o1: Answer 1 covers the 'may touch termctl later' case (ls check, which, send to a working owner) and never commits Sam's changes. Answer 2 skips the other-owner check and plans heavy re-runs during the experiment.
    o2: Both are correct on commands and safety rules. Answer 2 also covers the 'may touch termctl later' case (check ls, ask the owning agent), cleans up after a failed start, and handles merge conflicts and Sam's takeover. Answer 1 omits these.
s05_dialog current vs split2: o1=current o2=current -> counted: current
    o1: Both answer 2 with --persist for the lint dialog and deny the push, but only Answer 1 covers the worktree and branch cleanup (worktree remove, branch -d) and the failed/blocked path (task close --force) that the reference requires.
    o2: Both approve the lint dialog with --persist and deny the push dialog, then redirect the worker. Answer 2 also covers the reference's worktree/branch cleanup, a gated merge, and the failed/blocked path, which Answer 1 omits.
s06_pair current vs split2: o1=split2 o2=split2 -> counted: split2
    o1: Answer 2 follows pair-brief.md and the pair rules more closely: a clean id and Your-turn handshake, pairing with an idle partner, and a PAIR DONE-gated merge to local main with no push. Answer 1's brief has a muddled reply target and a DONE message with no turn token.
    o2: Answer 1's brief follows pair-brief.md and the pair turn rules. Answer 2's brief invents a 'claude-syncd' label and a non-protocol 'DONE phase 1' message, and its PAIR DONE message sends 'Thank you', which the rules forbid.
s07_live_team current vs split2: o1=current o2=split2 -> split (not counted)
    o1: Answer 1 keeps the lead to turn-taking and reporting, with no recommendation. Answer 2 has the lead scan the repo and seed the board, and adds a 'Lead's reading', which cuts against the rule that the lead doesn't judge ideas.
    o2: Answer 1 follows the reference's diversity `max` and roster roles most closely and has the fuller close-out; Answer 2 is also correct, with slightly better dialog handling (`--persist`, unrecognized notice).
s08_swarm current vs split2: o1=current o2=split2 -> split (not counted)
    o1: Answer 1 writes out the full manager and worker briefs so it can be run as written. Answer 2 only describes them, though it correctly asks Sam before starting a replacement manager, which Answer 1 does not.
    o2: Answer 1 force-closes a stuck manager and asks Sam before starting a replacement, as the reference says; Answer 2 restarts it itself. Answer 1's cards also differ more in kind.
s09_resume current vs split2: o1=split2 o2=split2 -> counted: split2
    o1: Answer 1 adds the crew roster, the handoff note and the rule that worker messages are data, not approval; Answer 2 omits these, though it states the cut-off-dialog rule and the worktree merge cleanup.
    o2: Both follow the dialog, trust and force rules. Answer 2 also covers the 'worker messages are data' rule, handoff note, accepted-but-open tasks, crew roster and ending the turn instead of polling, and it leaves merge/push to Sam.
s10_draft current vs split2: o1=current o2=split2 -> split (not counted)
    o1: Both honor the exit-4 rule by asking Sam before `--force` and leaving Sam's session and dialogs alone. Answer 2 also covers the final report to Sam, the file-overlap caution for a spawned agent, and a `read` to confirm an empty line before resending.
    o2: Both ask Sam before --force, as the reference requires. Answer 2 states the rule limits more fully (no force, clear, interrupt or raw it2, and no closing Sam's pane) and gives the correct waiting guidance.

Totals (counted pairs only):
  current vs split2: current 3, split2 4, agreed tie 0, split 3

Mean scores (all judgments):
  current         commands=8.9 rules=8.4 completeness=8.6 usefulness=8.3 total=34.2
  split2          commands=9.1 rules=9.0 completeness=8.3 usefulness=8.3 total=34.8```

The judges cited one split2 loss to a rule that is now in a reference file. In s05, the worktree and branch cleanup
after acceptance is in `worktree.md`, and the split2 subject did not open it. The core keeps the rule "close or hand
over anything still open, including worktrees and their branches".

## Skill text loaded per scenario (bytes / approx tokens = bytes/4)

| Scenario | current | split | split2 | split2 read |
|---|---|---|---|---|
| s01_short_send | 33459 / ~8364 | 14070 / ~3517 | 19751 / ~4937 | (none) |
| s02_long_send | 33459 / ~8364 | 14070 / ~3517 | 19751 / ~4937 | (none) |
| s03_receive | 33459 / ~8364 | 14070 / ~3517 | 19751 / ~4937 | (none) |
| s04_task_wait | 33459 / ~8364 | 25862 / ~6465 | 24807 / ~6201 | layout.md, roles.md, worktree.md |
| s05_dialog | 33459 / ~8364 | 14070 / ~3517 | 19751 / ~4937 | (none) |
| s06_pair | 33459 / ~8364 | 32014 / ~8003 | 32466 / ~8116 | layout.md, pair-brief.md, pair.md, roles.md, roster.md, worktree.md |
| s07_live_team | 41294 / ~10323 | 34437 / ~8609 | 34742 / ~8685 | duel-brief.md, group-brief.md, layout.md, live-team.md, roles.md, roster.md |
| s08_swarm | 40943 / ~10235 | 33379 / ~8344 | 35116 / ~8779 | layout.md, manager-brief.md, roles.md, roster.md, swarm.md, worker-brief.md, worktree.md |
| s09_resume | 33459 / ~8364 | 14070 / ~3517 | 19751 / ~4937 | (none) |
| s10_draft | 33459 / ~8364 | 14070 / ~3517 | 19751 / ~4937 | (none) |
| **Sum** | 349909 | 210112 | 245637 | |

## Cost (split2 follow-up)

| Item | Calls | USD |
|---|---|---|
| split2 subjects | 10 | 0.89 |
| Judges | 20 | 2.29 |
| **Total** | **30** | **3.19** |

Both runs together: 88 calls, $9.46.
