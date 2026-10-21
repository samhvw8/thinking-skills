---
name: debate
description: "Live multi-agent debate: named teammates argue with each other by message, you moderate and synthesize what survived — not one agent simulating both sides. Use when the user types /debate or wants a decision pressure-tested by opposing positions — debate this, argue both sides, steelman, red-team, devil's advocate. Live mode needs a harness with live teams (Claude Code agent teams) and the main session; elsewhere it runs written rounds of sub-agents and says so. Not for simple questions, mechanical tasks, or when one analysis suffices."
---

# Debate

The entry point for a live team debate. The playbook, the spawn template and the role for each
format live in one place, heavy-think's `../heavy-think/references/team-debate.md`. Read it before you
spawn anyone and follow it: this file only routes there, so the two cannot drift apart.

Check first, and if either fails, say so before doing anything else:

- You are the main session (a sub-agent cannot spawn teammates).
- Your harness has live teams. Today that is Claude Code with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`;
  `../heavy-think/references/harness.md` lists what each harness has.

When one fails, the playbook's Fallback runs a simulated version; tell the user it is simulated.

The deck behind the playbook: `python3 "$SKILL_DIR/../heavy-think/deck.py" debates` (`SKILL_DIR`: this file's folder) prints the
formats and the evidence-backed rules the playbook is built on.

Done means: the transcript folder holds the baseline and the verdict, the user has the verdict
compared against the alone-first answers, and every teammate is shut down.

## Related

- [heavy-think](../heavy-think/SKILL.md): Debate is also an escalation there
- [council](../council/SKILL.md): expand a question with "yes, and" instead of pressure-testing it
