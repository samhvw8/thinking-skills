# Generators

Each generator is a different method for leaving the mode. Run at least three that fit the
task; pools from different methods overlap little, which is the point. Every generator needs
an input you can write down (the receipt column). Write it before the ideas: it is what makes
the generator run instead of being a label added afterwards, and it becomes the idea's
receipt line in the output.

Where a deck id is given, the method lives in this skill's `references/techniques.json` (a copy
of the shared deck). Read just that entry, not the whole file: grep it for `"id": "morphological"`
(the part after `techniques.`) with three lines of context. If the file is missing, the
technique's name is enough to run it.

| Generator | Deck id | Use it this way here | Receipt | Good for |
|-----------|---------|----------------------|---------|----------|
| Tails sampling | `techniques.verbalized-sampling` | Keep only candidates you estimate under 0.10 | the pick's p, plus two high-p items you rejected | Anything; strongest on names, jokes, premises |
| Distant field | `techniques.analogy-transfer` | Describe the task with verbs first ("make strangers trust a new tool in ten seconds"), then pick 3-5 fields excellent at those verbs and take their method, not their vocabulary | the verb sentence, the field, the method borrowed | Campaigns, product concepts, structure |
| Morphological box | `techniques.morphological` | Names: language, word type, sound, where the meaning comes from. Campaigns: channel, who acts, timing, mechanic, the asset left behind. Take rows nobody would pick first | the dimensions and the chosen row | Names, campaigns; guarantees structural range |
| Concept fan | — | Ask "why do we want this?" to climb one or two levels (a launch campaign → get people to try a habit app once → get people to restart something they quit), fan out new directions from each higher level, then come back down to concrete ideas. The clever tier sits at the same level of abstraction as the obvious one; climbing gets out of both | the level climbed to and the direction taken | Campaigns, positioning, product ideas |
| Contradiction | `techniques.triz-contradiction` | Name the brief's core contradiction (it must feel trustworthy, but it is new) | "needs X but X causes Y", and how it was separated (time, space, condition, level) | Campaigns, product concepts |
| Synectics | — | Symbolic analogy: compress the subject into a two-word paradox, a "book title" ("patient urgency", "crowded solitude"), and build from it. Personal analogy: be the object and speak as it ("I'm the cup on the back of the bike; what do I dread?") | the paradox, or the first-person line | Names, premises, hooks |
| Ordinary personas | `techniques.ordinary-personas` | Replaces "audience swap": three specific ordinary people, one idea through each one's day | the person (job, place, the moment in their day) | Messaging, UX concepts, campaigns |
| Defects and wishes | `techniques.defect-listing`, `techniques.wish-listing` | The category's real complaints or wishes, when the user gave no material. Real ones beat imagined ones: 1-star app reviews, Reddit threads (one search, counted in step 7's budget); if from memory, say so | the complaint or wish, quoted | Campaigns, features, copy |
| Raw material | — | Mine the user's specifics: the product's odd features, their data, the place, a customer complaint, the commit history | the detail used | Copy, names, stories, pitches |
| Constraint | `techniques.constraint-injection` | For writing and names add form rules too: one syllable, no adjectives, told backwards (Oulipo practice) | the rule | Writing, names, visual concepts |
| Inversion | `techniques.assumption-reversal` | Also flip the goal: what would make it fail, who would hate it | the assumption flipped | Campaigns, positioning, plots |
| Random words | `techniques.random-words` | The model has no randomness of its own, so draw from a real source and print the seed (below). Drop words you don't know; don't redraw to get nicer ones | the seed, the words, and which word led to the idea | Getting unstuck, names |
| Story spine | — | For premises: once upon a time / every day / until one day / because of that / because of that / until finally / ever since. Fill it differently for each premise; the "until one day" must be specific to this character | the "until one day" and "until finally" lines | Premises, plots |
| Combination | — | Collide two earlier ideas from different generators; keep the result only if it is stronger than either | the two parents | Second pass on any pool |
| Exaggerate | — | Push one property to an absurd size, then step back to the largest version that still works | the property and the size | Hooks, product features |

Random words (macOS and Linux; prints the seed so the draw can be checked):

```bash
python3 -c "import random;s=random.randrange(10**6);r=random.Random(s);w=[x for x in open('/usr/share/dict/words').read().split() if x.islower() and 4<=len(x)<=7];print('seed',s,r.sample(w,5))"
```

On Linux `shuf -n5 /usr/share/dict/words` also works. With no dictionary file, use the first
nouns of a news headline you fetched, and say so.

## Writing tells

For prose, grep the draft and replace each hit with the specific thing it stands in for:

`delve, tapestry, testament, realm, vibrant, bustling, whisper(ed|s), symphony of, dance of,
a sense of, palpable, intricate, nestled, beacon, embark, journey (as metaphor), in a world
where, little did, it's not just X it's Y`

The tell is density, not a single word: several of these in one paragraph means the
writing reached for the typical phrase instead of the observed detail. Other structural
tells: three-item lists everywhere, every paragraph ending on a moral, and an em dash or
colon reveal in each sentence.
