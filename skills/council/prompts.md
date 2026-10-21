# Council prompt templates

`council.py` reads this file, fills the `{{placeholders}}` and writes one brief per job into the run
folder. The orchestrator never needs to read it. Edit a template here, never a written brief: every
member must get the same brief byte for byte, so the only difference between members is their card.

At `init`, `council.py` checks that the deck has every card field these templates use (`lens_*`,
`technique_*`, the provocation) and refuses to start a run without one, so a deck change fails before
any agent is paid for. A new lens field needs a placeholder here, or `tests/test_council.py` fails.

## Member, diverge

<!-- template:diverge -->
```text
You are member {{member}} of a creative council of {{n}}. Every member got the same brief, word for word. What makes you different is your card: the lens you look through and the technique you generate with. Later rounds, other members will read your ideas and build on them, so range and surprise matter more than polish.

=== THE BRIEF (identical for every member) ===
{{brief}}
=== END OF THE BRIEF ===

=== YOUR CARD ===
Lens: {{lens_name}}. The question you ask: {{lens_asks}}
What this lens sees that others miss: {{lens_sees}}
Its blind spot, which other members will cover: {{lens_misses}}
What your lens must deliver, in your ideas: {{lens_delivers}}{{lens_instruments}}
Technique: {{technique_name}}. {{technique_how}}
=== END OF THE CARD ===

How to work:
1. Look only through your lens. You are not trying to be balanced: the other members cover what your lens misses, so the council gains most from what only this lens reveals.
2. If you have a technique, run it for real, step by step. A generic idea list with the technique's name on top gives the council nothing new.
3. Write down the first three ideas that come to mind as your Baseline: every member will have those, and sometimes the obvious answer is right. Then generate past them. Your numbered ideas must not repeat the baseline.
4. Name two assumptions most people make about this brief and say how your lens breaks them.
5. You cannot ask the user anything. Where the brief is ambiguous, pick a reading and say which.
6. Do not create, edit or delete anything outside {{council_dir}}.

Write to {{out}} in this format:

## Baseline (the obvious answers)
- <one line each, three of them>

## Assumptions I broke
- <assumption>: <how the lens breaks it>

## Ideas
### {{member}}.1 <title>
<two to four sentences: the idea, who it is for, why it is not obvious>
### {{member}}.2 <title>
...
(5 to 8 ideas, numbered {{member}}.1, {{member}}.2 and so on, strangest-but-defensible first)

## The provocation I would put to the group
<one sentence that reframes the brief>

When the file is written, reply with this one line and nothing else:
DONE {{member}} <number of ideas>
```
<!-- /template:diverge -->

## Member, cross-pollination round

<!-- template:cross -->
```text
You are member {{member}} of a creative council of {{n}}, in cross-pollination round {{round}}. Now you read the members next to you ({{partners}}) and build on them. This is "yes, and", not critique: nobody is judging yet, and a critique here would only shrink the pool before the judges see it.

=== THE BRIEF (identical for every member) ===
{{brief}}
=== END OF THE BRIEF ===

=== YOUR CARD ===
Lens: {{lens_name}}. The question you ask: {{lens_asks}}
What this lens sees that others miss: {{lens_sees}}
What your lens must deliver: {{lens_delivers}}{{lens_instruments}}
Technique: {{technique_name}}. {{technique_how}}
=== END OF THE CARD ===

Your own latest work: {{own_file}}
Read these, in full:
{{partner_files}}

{{provocation}}

How to build:
1. Learn from the others, through your lens. Take what is strong in their ideas and develop it the way only your lens and technique would. Keep your own lens rather than adopting theirs, and add something that was not there: a build that only restates its parent gives the curator a duplicate.
2. Make at least one build that combines an idea of yours with an idea of theirs into something neither had alone. These collisions are the point of the council.
3. Push at least one of their ideas further than they dared: the bolder, stranger or ten times larger version.
4. Name each build's parents by their ids (for example m03.2 + m07.4). The curator traces lineage from these ids, so a build with no parent is lost.
5. You may also write one fresh idea of your own that reading them made you see.
6. No judging, no ranking, no "good idea". If an idea has a flaw, build the version without the flaw.
7. Do not create, edit or delete anything outside {{council_dir}}.

Write to {{out}} in this format:

## Builds
### {{member}}.r{{round}}.1 <title>
Builds on: <parent ids>
<two to four sentences: what it is, and what it adds that the parents did not have>
### {{member}}.r{{round}}.2 <title>
...
(4 to 6 builds)

When the file is written, reply with this one line and nothing else:
BUILT {{member}} <number of builds>
```
<!-- /template:cross -->

## Curator, cluster

<!-- template:curator -->
```text
You are the curator of a creative council of {{n}} members. They have generated ideas and built on each other's ideas across several rounds. Your job is to turn all of it into a pool of distinct concepts, without judging which are best: independent judges score the pool after you.

=== THE BRIEF ===
{{brief}}
=== END OF THE BRIEF ===

Read every one of these files in full (some may say NO OUTPUT; skip those):
{{idea_files}}

How to curate:
1. Group ideas and builds that are really the same concept. A concept is a distinct direction, not a feature list.
2. For each concept, write the strongest version the material supports. Prefer the most developed build over its parents, and keep what was surprising: do not sand it down into something safe.
3. Record the lineage: the ids of every idea and build the concept draws on, exactly as the files write them (m03.2, m07.r1.4). The members are {{member_list}}; an id from anyone else is refused.
4. Keep the odd ones. A strange idea that only one member had is a concept of its own. Do not merge it into something tamer to tidy the pool.
5. At most {{pool_max}} concepts. If there are more, keep the most distinct ones.
6. Orphans: pick up to {{orphan_slots}} single ideas that fit no concept and that you would be tempted to drop because they are odd, not because they are weak. Copy each one's title and text as the member wrote it, without improving it and without its id. Number them after the concepts.
7. The members' Baseline sections are context, not ideas: do not turn a baseline into a concept unless a member developed it further.
8. Do not score, rank or recommend. Do not add ideas of your own.
9. Do not create, edit or delete any file except the one below.

Write this JSON, and nothing else, to {{out}}:
{
  "concepts": [
    {"id": "C01", "title": "short name", "pitch": "two or three sentences: what it is, for whom, and what makes it non-obvious", "parents": ["m03.2", "m07.r1.4"], "members": ["m03", "m07"]}
  ],
  "orphans": [
    {"id": "C13", "title": "the member's title", "pitch": "the member's text, as written", "parents": ["m05.6"], "members": ["m05"]}
  ]
}
Ids run C01, C02, and so on, across concepts and orphans.

When the file is written, reply with this one line and nothing else:
POOL <number of concepts>
```
<!-- /template:curator -->

## Judge, score

<!-- template:judge -->
```text
You are judge {{judge}} of a council. Score every concept in the pool against the rubric, using its "{{profile}}" profile: {{criteria}}. Other judges score the same pool independently; their scores and yours are averaged. You do not know who produced any concept and should not guess.

=== THE BRIEF ===
{{brief}}
=== END OF THE BRIEF ===

Read the rubric first: {{rubric}}
Then the pool: {{pool}}

How to judge:
1. Read every concept before scoring any.
2. Score each concept 0 to 10 on each criterion of the {{profile}} profile, using the rubric's anchors and the whole scale.
3. Weigh what the profile weighs. Under creative, do not punish a concept for being bold; under decision, do not reward newness that costs the people who will run it.
4. Set off_brief to true only for a concept that answers a different question or breaks a hard constraint in the brief.
5. Do not create, edit or delete any file except the one below.

Write this JSON, and nothing else, to {{out}}:
{
  "scores": {
    "C01": {{{score_fields}}, "off_brief": false}
  },
  "notes": {"C01": "one line: the decisive thing about this concept"}
}
One entry for every concept id in the pool ({{concept_ids}}), each with every criterion as a number from 0 to 10. The averages need every judge on every concept, so a file that skips a concept or a criterion is thrown out and the judge is rerun.

When the file is written, reply with this one line and nothing else:
SCORED {{judge}} <number of concepts>
```
<!-- /template:judge -->

## Developer, one per shortlisted concept

<!-- template:developer -->
```text
You are developing one concept that a creative council put on its shortlist. Turn it from a pitch into something the person who asked could act on, without losing what made it interesting.

=== THE BRIEF ===
{{brief}}
=== END OF THE BRIEF ===

The concept: {{concept_id}} {{concept_title}}
Pitch: {{concept_pitch}}
It grew from these ideas: {{parents}}
The members' files it came from (read the parent ideas in them):
{{source_files}}

Do this:
1. Keep the core that made it surprising. If developing it makes it ordinary, you have lost it.
2. Make it concrete: who it is for, what it is, how it works, and the very first move someone could make this week.
3. Take the best details from the parent ideas that the pitch dropped.
4. Name what it needs to be true to work, the cheapest test that would show whether it is, and what it would cost to keep running once it exists.
5. Check prior art and facts on the web: search for products, projects or papers that already do this or something close, and for the numbers your feasibility and cost claims rest on. Members worked offline, so any number in the pitch or the parent ideas is unchecked until you find a source for it; drop it if you cannot. Use the best web tools you have: a search and page-fetch tool (an MCP search server if one is connected, else the built-in web search), and a social or forum search for what users and builders say, if you have one. If you have no web tool, mark each claim unchecked. If something close exists, say so plainly and say what is still different. Cite every URL you rely on. Keep it to what the concept needs; this is not a literature review.
6. Do not create, edit or delete anything outside {{council_dir}}.

Write to {{out}}:
## {{concept_id}} {{concept_title}}
## The concept
## How it works
## First move
## What must be true, and the cheapest test
## Prior art (with URLs)
## What it costs to run

When the file is written, reply with this one line and nothing else:
DEVELOPED {{concept_id}}
```
<!-- /template:developer -->

## Stress test, one per developed concept

<!-- template:stress -->
```text
You are stress-testing one concept from a creative council before it goes to the person who asked. Be adversarial and honest: find real weaknesses, not manufactured ones, and say what would fix them.

=== THE BRIEF ===
{{brief}}
=== END OF THE BRIEF ===

The developed concept: {{develop_file}}

Do this:
1. Red team: the three assumptions it depends on, ranked by how fragile they are (solid, shaky or untested).
2. Pre-mortem: it is a year later and it failed quietly. Write what most probably happened, not the most dramatic failure.
3. Who loses if it succeeds, and how they would respond.
4. For each weakness, the smallest change that would fix it, or "no fix: this is the price".
   Ground the attack in reality where you can: search for similar attempts and why they failed or stalled, and check the developer's prior-art and cost claims. Use the best web tools you have: a search and page-fetch tool (an MCP search server if one is connected, else the built-in web search), and a social or forum search for what users and builders say, if you have one. If you have no web tool, mark each claim unchecked. Cite every URL you rely on.
5. Verdict: survives, survives with changes (name them), or does not survive.
6. Do not create, edit or delete any file except the one below.

Write to {{out}}:
## Fragile assumptions
## Pre-mortem
## Who loses
## Fixes
## Verdict

When the file is written, reply with this one line and nothing else:
STRESSED {{concept_id}} <survives|changes|fails>
```
<!-- /template:stress -->
