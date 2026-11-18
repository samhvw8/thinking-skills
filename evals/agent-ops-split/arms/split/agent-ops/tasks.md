# agent-ops: tasks and crews

Part of the agent-ops skill (`SKILL.md` next to this file has the commands and the rules for
sending and receiving).

## Task or subagent

- **Agent tool or `task`-style subagent:** the default for delegating. Cheaper, its result comes back
  to you, and it stops when done.
- **`task new`:** only when the job needs its own visible harness session: a different harness or
  model, work Sam should be able to watch or take over, or a long job that must outlive your turn.
- At most 6 tasks run per owner, nested 2 deep.
- Write the brief as a complete request: the worker has none of your context.
- After starting, end your turn (the `RE: task` message wakes you) or block on `task wait`.
- **The lead owns done.** A worker's `task done --status ok` means ready for you. Check the work,
  then `task accept <id> --close`. A task that reported `failed` or `blocked` cannot be accepted:
  `task send` it another round, or end it with `task close --force <id>`.
- **Same-session review is the default.** Send findings with `task send <id> "..."`. The worker has
  the files loaded, and this opens the next round.
- **Use a blind review** when you need a verdict the worker's own reasoning cannot color:
  `task review <id> --blind --harness claude`. It starts a new session that gets the requirements and the files, not
  the worker's report. Claude Code runs it read-only unless you pass `--command`; other harnesses can change files.
- **A task that failed to start.** `task new` exited 4 or 5 and printed no ID: the task is `failed`,
  its pane is still open, and the worker never got the brief. `read` the pane, get the ID from
  `task ls`, then run `task close --force <id>` in the same turn. Do not leave the pane open while you
  ask Sam: nothing is lost by closing, and a restart is one command. Then tell Sam what blocked it and
  what restarts it. Do not clear the blocker yourself (a trust dialog, a missing key, a draft on the
  line). Exit 6 is a limit (6 running, 2 deep, a busy `--reuse` pane): nothing started.
- **A worker at a permission dialog.** Read `dialogs.md` (next to this file).
- **A worker that stops answering.** `task wait` exits 5 on timeout, and `exited` means the harness is
  gone but its tab is open. `read` the worker once. If it is stuck (out of context, crashed), `task close --force <id>`, tell its crew who is gone, and report to Sam before you
  start a replacement.
- **Close what you start.** An open harness keeps its tab, memory and MCP servers running, and Sam
  should not have to clean up after you. Close each accepted task with `task accept <id> --close`, and
  each `spawn` session with `close <target>` once its job is done. Before you report your own work
  finished, run `ls --mine` and `task ls`, and close or hand over anything still open, including
  worktrees and their branches.

## Run a crew

Workers started together don't know about each other. Start them all first, then send each one the
roster, so they settle interfaces and file ownership between themselves instead of through you:

```bash
harness-ops send <task-id> "Crew: tA (omp, API in .claude/worktrees/api), tB (claude, tests in .claude/worktrees/tests). Message a teammate with agent-ops for anything you need from them; report to me only through task done. No reply needed."
```

A task's ID is also its pane label, so teammates can use it as a target.
