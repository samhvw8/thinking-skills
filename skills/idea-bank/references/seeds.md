---
# Seeds, including but not limited to. Read "How to offer them" below the lists before you offer any:
# the owner's question comes first, and you show a question, never a title or id.
perspectives:
  - id: fault-tree
    title: "Fault tree"
    question: "Pick the wrong conclusion you fear most. What has to happen, alone or in combination, for it to come about?"
    example: "Top event, logic gates, basic events: parts are the minimal sets of events that cause the failure."
    origin: seed
    status: tested
    source: https://en.wikipedia.org/wiki/Fault_tree_analysis
  - id: marr-levels
    title: "Marr's three levels"
    question: "If you described it at several levels, from the problem it solves down to what physically runs it, where do the levels come apart?"
    example: "Computational goal, representation plus algorithm, physical implementation."
    origin: seed
    status: "tested, mixed result"
    source: https://en.wikipedia.org/wiki/David_Marr_(neuroscientist)
  - id: morphological-box
    title: "Morphological box"
    question: "Which choices could each have gone another way on their own, and what were the other ways?"
    example: "Independent parameters, each with its set of possible values; the method is one cell combination."
    origin: seed
    status: "tested, mixed result"
    source: https://en.wikipedia.org/wiki/Morphological_analysis_(problem-solving)
  - id: essential-vs-accidental
    title: "Essential versus accidental"
    question: "What would any solution to this problem need, and what is here only because of the means these authors happened to use?"
    example: "Essential complexity (from the problem) versus accidental complexity (from the chosen means)."
    origin: seed
    status: "tested, mixed result"
    source: https://en.wikipedia.org/wiki/No_Silver_Bullet
  - id: error-entry-chain
    title: "Where error enters"
    question: "Follow the path from the raw input to the reported number. Where does error enter, and how large is each link's share?"
    origin: invented
    status: untested
    source: a session that chose its own angle (wording not yet judged)
  - id: knowledge-sources
    title: "Where the answer's knowledge comes from"
    question: "Which pieces put knowledge into the answer, and is that knowledge fixed in advance or fitted to the data?"
    origin: invented
    status: untested
    source: a session that chose its own angle (wording not yet judged)
  - id: guarantee-chain
    title: "Guarantee chain"
    question: "What does each piece do to the headline guarantee: state it, bound it, pay for it, or check it?"
    origin: invented
    status: untested
    source: a session that chose its own angle (wording not yet judged)
  - id: four-causes
    title: "Aristotle's four causes"
    question: "Ask 'why is it like this?' in as many different senses as you can. Which separate kinds of answer turn up, and what part does each one pick out?"
    example: "Material (data, substrate), form (the defining structure), efficient cause (what moves it), final cause (its purpose)."
    origin: seed
    status: untested
    source: https://plato.stanford.edu/entries/aristotle-causality/
  - id: abstraction-hierarchy
    title: "Means-ends abstraction hierarchy"
    question: "Climb by asking 'why does this part exist?' and descend by asking 'how is it done?'. Where do the rungs of that ladder fall?"
    example: "Five means-ends levels: purpose, abstract function, general function, physical function, physical form."
    origin: seed
    status: untested
    source: https://en.wikipedia.org/wiki/Ecological_interface_design
  - id: function-behaviour-structure
    title: "Function, behaviour, structure"
    question: "Where does what the authors expected it to do differ from what its structure actually makes it do?"
    example: "Function, expected behaviour, actual (derived) behaviour, structure; the gap between expected and actual behaviour is its own part."
    origin: seed
    status: untested
    source: https://en.wikipedia.org/wiki/Function-Behaviour-Structure_ontology
  - id: architecture-views
    title: "Concurrent views (4+1)"
    question: "If different people drew it (the reader, the person who reruns it, the person who extends it), how would their drawings split it differently?"
    example: "Logical, process (concurrency), development (organisation of the work), physical (deployment), scenarios."
    origin: seed
    status: untested
    source: https://www.cs.ubc.ca/~gregor/teaching/papers/4+1view-architecture.pdf
  - id: zoom-levels
    title: "Nested zoom levels (C4)"
    question: "What do you see when you zoom out to its surroundings, and what new parts appear each time you zoom in one level?"
    example: "Context, containers, components, code: parts nested by zoom, not by order."
    origin: seed
    status: untested
    source: https://c4model.com/
  - id: failure-modes
    title: "Failure modes and effects"
    question: "In what ways can this go wrong, and which failures belong together because they hurt the result in the same way?"
    example: "Failure modes grouped by their effect on the result and by how easy they are to detect."
    origin: seed
    status: untested
    source: https://en.wikipedia.org/wiki/Failure_mode_and_effects_analysis
  - id: dependency-clusters
    title: "Dependency clusters (DSM, near-decomposability)"
    question: "Which pieces lean on which, and which keep feeding each other? Where are the ties weak enough to draw a line?"
    example: "Clusters of tightly coupled elements, with boundaries placed where interactions are weakest; feedback loops become visible."
    origin: seed
    status: untested
    source: https://en.wikipedia.org/wiki/Design_structure_matrix
  - id: information-hiding
    title: "Hidden design decisions"
    question: "Which decisions in this method would a follow-up most likely change, and what would have to be walled off so that each change stays local?"
    example: "One part per changeable design decision; a part can touch many processing steps."
    origin: seed
    status: untested
    source: https://www.win.tue.nl/~wstomv/edu/2ip30/references/criteria_for_modularization.pdf
  - id: pace-layers
    title: "Pace layers"
    question: "Which parts would change fast, which slowly, and which hardly ever?"
    example: "Layers by rate of change, from fast (settings, data) to slow (core assumptions, framing)."
    origin: seed
    status: untested
    source: https://en.wikipedia.org/wiki/Shearing_layers
  - id: mechanism-vs-policy
    title: "Mechanism versus policy"
    question: "Which parts are general machinery, and which are the choices plugged into that machinery?"
    example: "Mechanism (reusable capability) versus policy (the decisions about how to use it)."
    origin: seed
    status: untested
    source: https://en.wikipedia.org/wiki/Separation_of_mechanism_and_policy
  - id: triz-contradiction
    title: "Contradictions (TRIZ)"
    question: "Where does improving one thing make another worse, and how does the method escape that trade-off, if it does?"
    example: "Pairs of conflicting parameters, and the inventive move that resolves each pair."
    origin: seed
    status: untested
    source: https://en.wikipedia.org/wiki/TRIZ
  - id: triz-resources
    title: "Resources (TRIZ)"
    question: "What was already lying around (material, energy, space, time, information, side effects), and which of it does the method use or leave unused?"
    example: "Resource types: substance, field, space, time, information, function."
    origin: seed
    status: untested
    source: Altshuller, TRIZ resource analysis (not read this pass)
  - id: mechanism-parts
    title: "Entities, activities, organisation"
    question: "What actually does the work here, what does each doer do, and how does their arrangement produce the result?"
    example: "Phenomenon, component entities, component activities, organisation (incl. levels)."
    origin: seed
    status: untested
    source: https://plato.stanford.edu/entries/science-mechanisms/
  - id: core-and-auxiliaries
    title: "Hard core and auxiliary assumptions"
    question: "What would the authors never give up, and what else must quietly be true for their test to mean what they say?"
    example: "Hard core, protective belt of auxiliary hypotheses, and the positive heuristic that says what to try next."
    origin: seed
    status: untested
    source: https://plato.stanford.edu/entries/lakatos/
  - id: toulmin-argument
    title: "Toulmin argument structure"
    question: "What is the claim, and what has to be accepted, stated or not, to get from the evidence to it?"
    example: "Claim, data (grounds), warrant, backing, qualifier, rebuttal."
    origin: seed
    status: untested
    source: https://en.wikipedia.org/wiki/Toulmin_model_of_argument
  - id: pico
    title: "PICO"
    question: "What exactly is compared with what, on whom, and judged by which result?"
    example: "Population or problem, intervention, comparator, outcome."
    origin: seed
    status: untested
    source: https://en.wikipedia.org/wiki/PICO_process
  - id: estimand
    title: "Estimand attributes"
    question: "What precise quantity does the headline number estimate, and what would you have to specify to pin it down?"
    example: "Population, treatment conditions, variable, handling of intercurrent events, population-level summary."
    origin: seed
    status: untested
    source: https://en.wikipedia.org/wiki/Estimand
  - id: validity-threats
    title: "Validity types"
    question: "Where could the step from the data to the claim break, and do those breaks fall into different kinds?"
    example: "Statistical conclusion, internal, construct and external validity; the external part splits again by units, treatments, outcomes, settings (UTOS)."
    origin: seed
    status: untested
    source: Shadish, Cook and Campbell 2002, Experimental and Quasi-Experimental Designs (not read this pass)
  - id: causal-dag
    title: "Causal graph with mediators"
    question: "If you drew arrows for what causes what, which paths carry the effect, and what else sits on or beside those paths?"
    example: "Treatment, mediators (direct versus indirect path), moderators, confounders, outcome."
    origin: seed
    status: untested
    source: https://en.wikipedia.org/wiki/Mediation_(statistics)
  - id: ablation-contribution
    title: "Contribution by removal"
    question: "If you took pieces away one at a time, which would the result miss most, and which hardly at all?"
    example: "Load-bearing parts versus decorative parts, ranked by marginal contribution."
    origin: seed
    status: untested
    source: https://en.wikipedia.org/wiki/Ablation_(artificial_intelligence)
  - id: control-vs-noise
    title: "Control and noise factors"
    question: "What did the authors set on purpose, and what varied outside their control?"
    example: "Signal, control factors, noise factors, response (the P-diagram)."
    origin: seed
    status: untested
    source: https://en.wikipedia.org/wiki/Robust_parameter_design
  - id: varied-vs-fixed
    title: "Varied, held fixed, left free"
    question: "Between the things compared, what was changed on purpose, what was kept the same, and what was left to drift?"
    example: "Manipulated factors, controls held constant, uncontrolled factors; the claimed effect sits on the one difference."
    origin: seed
    status: untested
    source: https://en.wikipedia.org/wiki/Mill%27s_methods
  - id: control-loop
    title: "Control loop"
    question: "Does it correct itself anywhere? If so, what senses, what compares, what acts, and what pushes it off course?"
    example: "Sensor, reference (setpoint), comparator, effector, disturbance; loops can nest."
    origin: seed
    status: untested
    source: https://en.wikipedia.org/wiki/Perceptual_control_theory
  - id: variation-selection-retention
    title: "Variation, selection, retention"
    question: "If it searches or improves over time: where are new candidates made, what picks among them, and what keeps the winners?"
    example: "Generator, selector, memory: parts by role in an evolutionary search."
    origin: seed
    status: untested
    source: Campbell 1960, Blind variation and selective retention (not read this pass)
  - id: stocks-flows-loops
    title: "Stocks, flows and loops"
    question: "What builds up or drains away over time, what drives it, and where does it feed back on itself?"
    example: "Stocks, inflows and outflows, reinforcing and balancing loops."
    origin: seed
    status: untested
    source: https://en.wikipedia.org/wiki/Stock_and_flow
  - id: bottleneck
    title: "The binding constraint"
    question: "What limits how good the result can get, and how does everything else relate to that limit?"
    example: "The constraint versus everything subordinated to it."
    origin: seed
    status: untested
    source: https://en.wikipedia.org/wiki/Theory_of_constraints
  - id: novel-vs-commodity
    title: "Novel to commodity"
    question: "Which pieces are new here, and which could anyone take off the shelf?"
    example: "Parts by evolution stage: genesis, custom, product, commodity."
    origin: seed
    status: untested
    source: thinking-skills/decks/decompositions.json#value-chain; models.json#wardley-mapping
  - id: icom-roles
    title: "Inputs, controls, outputs, mechanisms"
    question: "For each activity, what goes in, what comes out, what governs it, and what does it run on?"
    example: "Inputs, controls, outputs, mechanisms (ICOM) per activity."
    origin: seed
    status: untested
    source: https://en.wikipedia.org/wiki/IDEF0
  - id: temporal-sequence
    title: "Sequence and prerequisites"
    question: "What has to happen before what?"
    example: "Stages in order, with their prerequisites."
    origin: seed
    status: untested
    source: thinking-skills/decks/decompositions.json#temporal
  - id: levels-of-scale
    title: "Levels of scale"
    question: "What happens at different scales (one unit, units interacting, the whole), and does the story change between them?"
    example: "Micro, meso, macro levels."
    origin: seed
    status: untested
    source: https://en.wikipedia.org/wiki/Level_of_analysis
  - id: known-vs-unknown
    title: "Established versus bet"
    question: "Which parts are settled, and which are the bets the method stands or falls on?"
    example: "Known and easy, known and hard, unknown: parts grouped by confidence."
    origin: seed
    status: untested
    source: thinking-skills/decks/decompositions.json#risk
  - id: iceberg-layers
    title: "Iceberg layers"
    question: "What lies beneath the visible result: what keeps producing it, and what holds that in place?"
    example: "Event, pattern, structure, mental model."
    origin: seed
    status: untested
    source: thinking-skills/decks/models.json#iceberg-model
  - id: viable-system
    title: "Viable system roles"
    question: "Which parts do the work, and which keep that work steered, coordinated and adapting?"
    example: "Systems 1 to 5: operations, coordination, control, intelligence, policy."
    origin: seed
    status: untested
    source: https://en.wikipedia.org/wiki/Viable_system_model
  - id: interrogatives
    title: "Six interrogatives"
    question: "Ask what, how, where, who, when and why separately. Which answers turn up parts the others miss?"
    example: "What, how, where, who, when, why (Zachman columns)."
    origin: seed
    status: untested
    source: https://en.wikipedia.org/wiki/Zachman_Framework

operations:
  - id: split
    title: "Split"
    question: "Through this perspective, which separate jobs does this brick do?"
    records: "the parts in the whole's `parts`, `how: split`"
  - id: join
    title: "Join"
    question: "Which bricks, taped together, make a bigger brick worth naming? Each part keeps its own job."
    records: "a new brick whose `parts` list them, `how: join` (older files say `bind`)"
  - id: fuse
    title: "Fuse"
    question: "Which bricks, melted together, do a job none of them does alone?"
    records: "a new brick with the sources in `parts`, `how: fuse`, and a `note` naming the new job"
  - id: substitute-brick
    title: "Swap the brick"
    question: "What else does this role's job? Search the bank by role tag, then other fields by signature."
    records: "a Mutations row; a Move when it survives"
  - id: substitute-operator
    title: "Swap the operator"
    question: "What if the parts combine as a loop, tree, gate, adversarial pair, distillation or ensemble instead?"
    records: "a Mutations row; a Move when it survives"
  - id: remove
    title: "Remove"
    question: "Drop this brick: does the bet still hold? What does the system lose?"
    records: "a Mutations row; a Move when it survives"
  - id: lift-constraint
    title: "Lift a constraint"
    question: "Which choice was forced by cost, compute, data, tools or a missing technology? Rebuild it as if the limit were gone."
    records: "a Mutations row; a Move when it survives"
  - id: invert
    title: "Invert"
    question: "Reverse the order, the direction of flow, or who does what."
    records: "a Mutations row; a Move when it survives"
  - id: migrate-brick
    title: "Migrate the brick"
    question: "Keep this brick; which field or role could use it?"
    records: "a Mutations row; a Move and a migration row when it survives"
  - id: transfer
    title: "Transfer the bet"
    question: "Apply the same bet to a tension in another field; the bricks may change."
    records: "a Mutations row; a Move when it survives"
  - id: cross-card
    title: "Cross cards"
    question: "Take a brick or operator from another card in the bank."
    records: "a Mutations row; a Move when it survives"
  - id: resolve-contradiction
    title: "Resolve the contradiction"
    question: "Where does the recipe trade X against not-X? Separate them in time, space, scale or condition."
    records: "a Mutations row; a Move when it survives"
  - id: lens-transfer
    title: "See through another view model"
    question: "How would another person or field see this problem? What bottleneck would they name?"
    records: "a Mutations row; a Move when it survives"
  - id: lens-inversion
    title: "Invert the view model"
    question: "Assume the dominant view of the field is wrong. Which solution appears?"
    records: "a Mutations row; a Move when it survives"
  - id: correct-parameter
    title: "Correct a parameter"
    question: "Which number did the parent get wrong (a dose, a threshold, a ratio)?"
    records: "a Mutations row; a Move when it survives"
  - id: relabel
    title: "Relabel"
    question: "Keep the structure; what else could it be for? The new name changes who uses it."
    records: "a Mutations row; a Move when it survives"
  - id: retarget
    title: "Retarget"
    question: "Keep the method; which other outcome could it optimise or be judged by?"
    records: "a Mutations row; a Move when it survives"
---

# Seed perspectives and operations

A perspective is a way of looking (a question); an operation is something you
do to bricks (split, join, fuse, swap, invert, transfer, any other). Every
operation runs through a perspective, and the result records it in `lens`
(`schema.md`, Parts and links). The lists above are seeds, **including but not
limited to**: a session may use the owner's question, a seed, or a new one it
invents. They are not a registry. Nothing is checked against them before you
look.

## How to offer them

The owner's own question always comes first. When the owner names an angle,
use it as asked and do not offer seeds.

With no angle from the owner, pick a good one yourself, or offer a few seed
questions, starting with what could go wrong (`fault-tree`). In a small test
it was the only suggested question that beat letting the session choose on
every source tried. Three others were tested with a mixed result; the rest are
`untested`. Suggested wording:

> Look at this from a new angle. Start from the owner's question if there is
> one. Otherwise pick any angle, including but not limited to the starting
> questions below. You can also invent your own. Follow the parts the angle
> turns up, even if they do not match the example. Label the result in your own
> words.

- Show the **question**, not the title or id. A name reads as a category to fit
  into.
- `example` is where one field usually finds the seams. It is not a set of
  slots to fill: fewer, more or other parts are fine.
- Offer a few questions at a time, never the whole list.
- Label the result from the question that was asked, in the owner's or your own
  words. Use a seed id as the label only when you used that seed's question.

## When a label becomes a file

A free label gets a file only when it recurs: the second time it is used, in
another session or on another source. `idea_index.py` lists free labels with
where each was used. Then write `perspectives/<slug>.md` (`type: Perspective`)
or `operations/<slug>.md` (`type: Operation`) with `origin: invented`
(`schema.md`, Perspective and Operation). A bank file with a seed's id
overrides the seed. A new one that keeps working can be added to this list.

## Fields

- **Perspective:** `id`, `title`, `question`, `example` (optional), `origin`
  (`seed` from a tradition, `invented` by a session), `status` (`tested`,
  `tested, mixed result` or `untested`), `source`.
- **Operation:** `id` (`split`, `join`, `fuse`, or a `move_type` from the
  schema's mutation operators), `title`, `question`, `records` (where its result
  goes). idea-forge's `references/operators.md` has the procedure for each
  mutation operator.
