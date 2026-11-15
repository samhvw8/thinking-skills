# Live protocol

One protocol for every live mode: a team debate (`team-debate.md`) and a live council or team
brainstorm (`team-brainstorm.md`). A swarm adds a manager between you and the workers; the agent-ops
skill's Swarm section covers it. Members are agents that act in turns and can talk to each other.
The transport (how a member is started, reached and closed) changes; the protocol does not.
`harness.md` (Live-team transports) maps each step below onto each transport.

Contents: Roles · Three layers · Shape by size · The session folder · Member protocol block

## Roles

- **Lead**: you. You frame the session, open and close every round, open duels, and write the result.
  You never argue a side or add an idea: that would make you one more voice instead of the judge.
- **Members**: 2-6 named agents, each with its own card, method or role from the mode's playbook.
  Each member gets its model role from `harness.md` (Model tiers, Diversity).

## Three layers

| Layer | What | Rule |
|---|---|---|
| **Record** | One board file per session | Every contribution goes on the board. The result cites the board |
| **Control** | Turns | Only the lead opens and closes rounds. A member's only message to the lead is `DONE round N`, or `BLOCKED round N: <reason>` when it cannot finish the turn |
| **Duel** | A direct channel between 2-3 named members, for one round | A turn token, at most 3 messages each, ends with `DUEL DONE`, outcome on the board |

**Record.** Content lives on the board, not in messages: a file survives compaction, any transport
can read it, and anyone can audit or re-judge the session later. Each member adds one block per turn,
headed `## Round N — <name>`, in a single append. Nobody rewrites the file, because in a round where
everyone writes at once (round 1), a rewrite can erase another member's block. Each harness has its
own append method (harness map, "Append to a shared file"); a harness tool may refuse the obvious
one. So before round 1, every member appends one line, `## Round 0 — <name> ready: <method>`, and the
lead checks that every line arrived. A member with no working append writes to its own file
(`<board>.<name>.md`) for the whole session, and the lead joins it into the board.

**Control.** You open a round with `Your turn: round N` to the members it is for, optionally with one
line of focus (a sharpening question, a provocation). A member reads the board, writes its block, and
sends you `DONE round N`, nothing more. Short control messages fit every transport, keep everything
worth reading in one place, and your turn order stops members talking over each other. You close a
round when every member it was for is done.

**Duel.** When two or three members need to argue or merge something directly, open a duel for one
round: send each of them `DUEL round N: <names in turn order> on <question>`, with the way to reach
each other. Only the member holding the turn token sends; sending passes it to the next in order. At
most 3 messages each. The last message ends with `DUEL DONE`. Each duelist also appends what it
sends to the board, word for word. Then the first-named member appends the outcome (what moved, what
each concedes, what stays disputed), and every duelist sends you `DONE round N`. A duel is the only
time members message each other.

## Shape by size

| Members | Shape | Why |
|---|---|---|
| 2 | Round 1 alone, then a duel; board throughout | Two minds argue best directly; lead turns add nothing |
| 3 | Round 1 alone, then lead turns in a fixed order; optionally one duel between the two who clash most | Turns keep three voices readable; a duel settles the one clash that matters |
| 4-6 | Round 1 alone, then lead turns; board only | Direct talk between four or more becomes a group chat nobody reads |

Round 1 is always alone: every member writes before reading anyone, so the session keeps the
independent answers that later rounds have to beat.

## The session folder

Create `<mode>/<YYYYMMDD-HHMM>-<slug>/` in the working directory (the playbook names `<mode>`). It
holds the brief every member gets, `board.md`, and your own files (baseline, verdict, synthesis).
Give members absolute paths: a member on another harness may start in another folder, and some
harnesses only trust the folder they start in.

## Member protocol block

Paste this into every member's brief, after the mode's own template. Fill `{reach_lead}` and
`{reach_members}` from the transport row in `harness.md`.

```text
How this session runs:
- The board is {board_path}. Everything you contribute goes there; a message only counts as a signal. Add one block per turn in a single append (for example a shell append: cat >> {board_path} <<'EOF' ... EOF), headed "## Round N — {name}". Never rewrite or reorder the file: others may be writing at the same moment. Wrap lines at about 100 characters: some harness readers cut long lines. If a tool refuses your append, find your harness's append method (harness map) or send the lead "BLOCKED round N: no append"; never edit the board in place.
- Act only when the lead gives you a turn ("Your turn: round N"). Read the board, take your turn, append your block, then send the lead exactly "DONE round N" ({reach_lead}). Nobody sees your plain text output.
- In round 1, do not read the board before you write: your first answer must be your own.
- Duel: when the lead names you in a duel, talk directly with the named members only ({reach_members}). Send only while you hold the turn, in the order the lead gave; sending passes the turn on. At most 3 messages each. Append every message you send to the board, word for word. The last message ends with "DUEL DONE". Then the first-named member appends the outcome (what moved, what each concedes, what stays disputed), and each duelist sends the lead "DONE round N".
- Outside a duel, send nothing to other members, and send the lead nothing but "DONE round N". If you cannot finish a turn, send the lead "BLOCKED round N: <reason>" instead. Send each signal once: a reply that says the message is queued means it will arrive, so never resend or force it.
- Edit no file except the board, and start no agents.
```
