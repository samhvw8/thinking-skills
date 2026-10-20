---
name: creative
description: "Gets past the model's first, most typical answer on open creative work: names, ideas, campaign angles, hooks, story premises. Use when the user says be creative, more original, less generic, surprise me, or rejects output as boring or obvious. Single agent; for multi-agent runs use heavy-think, council or arena. Not for tasks with one right answer."
---

# Creative

A model's first answer is its mode: the most typical response, because preference
training rewards the familiar (Zhang et al., *Verbalized Sampling*, arXiv 2510.01171).
Telling it to "be extremely creative" or "think like Steve Jobs" barely moves this, and
sometimes makes the ideas more alike. Changing the procedure does: generate many,
push each one further, remove duplicates (Meincke, Mollick & Terwiesch, arXiv 2402.01727).
So this skill changes the method, not the adjectives.

## Skip it when

The task has one right answer, or the user wants the standard thing done well (a
conventional cover letter, a normal API name that matches the codebase). Novelty there is
a cost. Say so in one line and do the normal job.

## Process

1. **Read the brief.** Who it is for, the hard constraints (budget, length, platform,
   tone, existing names), and what "good" means to them. If the user rejected earlier
   output, that output is evidence of the mode; say in a sentence why it was the obvious
   answer. Ask one question only when a missing constraint would change everything;
   otherwise state your reading and go.

2. **Fence the mode.** Before generating, write the 5-10 answers anyone would give first,
   including the ones the user named. These are out of the final result. One may come back
   only if you argue it is still the best, in a line of its own. Fencing works because a
   model that can see its default can step around it; leaving the default unnamed lets it
   creep back in variations.

3. **Generate wide, from several generators.** Pools from different methods overlap little,
   so mixing them beats more of one (Meincke et al.). Use at least three generators from
   `references/generators.md` that fit the task, for example tails sampling, a distant field,
   a constraint, inversion, the user's raw material. Produce short titles only at this
   stage, roughly 20-40 for ideas or names and 5-8 premises for a piece of writing. Label
   each with the generator that made it.

4. **Push and prune.** Go through the pool: make each idea more specific and more
   different from the others; merge any two that share the same core move; drop
   anything inside the fence in disguise (a synonym, a pun on the fenced word).

5. **Select with the rubric.** Score the survivors with the `creative` profile in
   `../heavy-think/references/rubric.md` (novelty 30, value 30, feasibility 20, specificity 10,
   emergence 10), using its anchors and its off-brief rule. The novelty question is the core
   test: would a competent person in this field have come up with it on their own in an
   afternoon? Keep value and feasibility honest: ideas that look novel often fail when
   executed (Si et al., *The Ideation-Execution Gap*). If that file is missing, score
   novelty, value and feasibility 0-10 with those anchors.

6. **Develop the shortlist.** Usually 3-5 items. Make each concrete: who, what, and the
   first move. For a piece of writing, write the one strongest premise in full.
   Then test each item against every hard constraint from step 1, one by one (for a name
   that must work in two languages: say it in both). An item that fails one is cut, not
   flagged. Then check the deliverable as a whole: add up anything with a limit (budget,
   length, time) and confirm the total fits; a stated dislike or preference of the person
   it is for counts as a hard constraint, including for the headline idea. Cut any item you
   would score low on novelty too: a shorter list beats filler.
   The final picks come from at least two different generators; if they all make the same
   move (all puns, all one word type), swap one for the best survivor of another generator.

7. **Check outside yourself where you can.** Your own reading of your ideas is not a
   judge. Where a real check exists, run it and report the result:
   - names: search for collisions where the user's customers would meet the name: the
     local language and the local channels (delivery apps, maps, app stores, the trademark
     office), plus the name with and without its category word ("Nova" and "Nova Coffee").
     Query those platforms directly (`site:` searches, or their own search pages): open-web
     search often misses small-shop listings;
   - writing: grep the draft for the tells listed in `references/generators.md`;
   - "has this been done": one web search per shortlisted idea before calling it new.
   Give a link for every hit. A "no hit" names the queries you ran. When a check finds the
   idea or name already exists, demote or drop it and say so. If you can't run a check,
   say which one and why.

## Output

- **Fence line:** "Skipped the obvious: a, b, c, ..." in one line, so the user sees what
  was ruled out and can pull one back.
- **Shortlist:** each item with its generator, one line on why it is not the obvious
  answer, and its first move. For ideas with a real choice to make, a small table with
  the rubric scores.
- **Writing:** one finished piece, then one line naming two other directions you
  considered. A menu of five half-drafts pushes the creative work back to the user.
- **Checks:** what you ran and what it found (collision hits, tells found and fixed).
- Offer more from the tails if they want a second round; don't dump the whole pool.

## Rules while working

- **Specific beats strange.** Wild is easy and worthless when it ignores the brief. An
  idea that breaks a hard constraint is off-brief, however striking.
- **Show, don't claim.** Never describe your own output as innovative, bold, unique or
  creative; the rubric gives that no points, and the user can judge.
- **Concrete material over adjectives.** Real details from the user's product, data,
  place or people are the cheapest source of originality. Ask for them, or read them
  when they are in the workspace.
- **Keep the user's voice.** Originality in their brand, codebase or story means fresh
  inside their world, not swapped for yours.
- **Collective sameness matters.** AI-assisted work is individually better but collectively
  more alike (Doshi & Hauser, *Science Advances* 2024). Judge the set, not only each
  item: if the shortlist could be one idea in three outfits, go back to step 3.

## When one agent isn't enough

This skill is one agent and costs about one normal answer. Offer a bigger run, and start
it only when the user agrees, since each one spins up many agents:
- **heavy-think** (Brainstorm mode): parallel agents ideate, then a synthesis.
- **council** (full mode): perspectives build on each other, blind judges score on the
  same rubric. For open "how might we" questions that deserve real breadth.
- **arena**: when the user has rejected answers more than once and wants versions to
  compete for one best result.
- **ambition**: when the goal behind the request is bigger than the artifact (ambition's
  Range axis is the same distant-field move used here).
