---
name: debate
description: "Live multi-agent debate: named debaters argue with each other in turns and direct duels, you moderate and synthesize what survived — not one agent simulating both sides. Use when the user types /debate or wants a decision pressure-tested by opposing positions — debate this, argue both sides, steelman, red-team, devil's advocate. Live mode needs a live-team transport (harness map: harness-ops sessions, agent teams or omp named tasks); without one it runs written rounds of sub-agents and says so. Not for simple questions, mechanical tasks, or when one analysis suffices."
---

# Debate

The entry point for a live team debate. The playbook, the spawn template and the role for each
format live in one place, heavy-think's `../heavy-think/references/team-debate.md`, on the shared
live protocol in `../heavy-think/references/live-protocol.md`. Read both before you start anyone and
follow them: this file only routes there, so they cannot drift apart.

Check first, and if it fails, say so before doing anything else: your session has a live-team
transport. `../heavy-think/references/harness.md` (Live-team transports) lists them and their limits,
for example that Claude Code agent teams work only from the main session.

Without one, the playbook's Fallback runs a simulated version; tell the user it is simulated.

The deck behind the playbook: `python3 "$SKILL_DIR/deck/deck.py" debates` (`SKILL_DIR`: this file's folder) prints the
formats and the evidence-backed rules the playbook is built on.

Done means: the transcript folder holds the baseline and the verdict, the user has the verdict
compared against the alone-first answers, and every debater is shut down.

## Related

- [heavy-think](../heavy-think/SKILL.md): Debate is also an escalation there
- [council](../council/SKILL.md): expand a question with "yes, and" instead of pressure-testing it
