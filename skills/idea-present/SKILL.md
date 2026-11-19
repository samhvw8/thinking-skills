---
name: idea-present
description: "The owner's switch for the idea skills: /idea-present turns present mode on for this conversation (they do the generative steps first), /idea-present off turns it back to the default, absent mode."
disable-model-invocation: true
argument-hint: "[on | off]"
---

# Idea present

The owner typed `/idea-present $ARGUMENTS`.

- Empty or `on`: present mode is **on** for the rest of this conversation.
- `off`: present mode is **off**; the idea skills go back to absent mode.
- Anything else: say the two accepted values and change nothing.

Say in one line which mode is now on, in the owner's chat language. Then continue whatever
was in progress under that mode.

What the mode changes is defined once, in the idea-bank skill ("Presence mode" under
Rules): read `../idea-bank/SKILL.md` if it is not loaded yet. In short:

| | Absent (default) | Present (after `/idea-present`) |
|---|---|---|
| Generative steps (variants, recipe, card, guesses) | Claude does them, best effort | The owner writes first, then Claude |
| co-read | brief mode | brief or deep, as the owner picks |
| idea-forge deal mode, kill-test predictions | offered in one line, not run | run as written |
| Skips | not counted: absence is not a skip | counted in `me/progress.md` |

The switch lives only in this conversation. A new session, or a summary after a
compaction that does not show the switch, starts in the presence default from the
bank's `me/profile.md` (absent when unset).
