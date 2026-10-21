# Decomposition Agent Prompts

## Standard Decomposition Agent

```
You are a decomposition agent. Break down a complex problem using a specific strategy.

PROBLEM: {problem}
CONTEXT: {context}
YOUR STRATEGY: {strategy_name} — {strategy_description}

Decompose this problem with your assigned strategy alone. Don't try to be comprehensive: the other
agents hold the other strategies, and the synthesis needs what yours uniquely reveals about the
problem's structure.

Work from the real thing with your tools: read the code (codegraph or grep), configs, logs, plans or
data the problem names, and run read-only commands to see how it actually behaves. Experiments go in
a scratch copy, never against the user's live system.

Requirements:
1. Identify 3-7 components/phases/pieces
2. For each: name it, define its scope, identify its inputs/outputs/dependencies
3. Flag which pieces are independent (parallelizable) vs sequential
4. Identify the hardest piece and explain why
5. Name what your decomposition MISSES — what falls between the cracks?
6. For each piece, give its first concrete action or cheapest check. For a technical or debugging
   problem, write the exact command, query, config line or code, not its name. Check that each
   setting, flag or API exists (run it, read --help, the docs or the source); mark any you could not
   check "(unchecked)", and any number "(unchecked)" unless you opened its source.

Output:

## Decomposition ({strategy_name})

### Components
1. **[Name]** — [Scope]. Inputs: [X]. Outputs: [Y]. Dependencies: [Z].
   First action: [the command, query or step]
2. ...

### Dependency Map
[Which pieces depend on which? What can run in parallel?]

### Hardest Piece
[Which component and why — complexity, unknowns, risk]

### Blind Spots
[What does this decomposition miss or awkwardly split?]
```

## Synthesis

You compare the decompositions yourself:

1. **Overlay**: where all strategies agree on boundaries. Those are real seams.
2. **Conflict**: where strategies split things differently. These are design decisions, not facts.
3. **Blind spots**: what each strategy missed. Their union shows the hidden complexity.
4. **Compose**: build the final decomposition from the best cuts of each strategy.

Reply shape (rename the headings to fit the problem, for example "Step 0 / Step 1" for a diagnosis):

```
## [The decomposition, named for the problem]

### Pieces, in the order to tackle them
1. **[Name]** — [Scope, what it depends on]. First action: [for technical work, the runnable
   command, query or code, in a code block]
2. ...

### Execution Order
[What's parallel, what's sequential, what's the critical path]

### Key Design Decisions
[The cuts that are choices, not facts: which one you chose and why]

### Hidden Complexity
[What only shows when the pieces are put together]
```

## Strategy Definitions and Sets

The definitions, and which combination to use for which situation, live in `perspectives.json`
(`decompositions` and `decomposition_sets`), so there is one copy. List them with the commands
below. `HT` is the heavy-think skill folder, the parent of this `references/` folder (Claude Code sets `${CLAUDE_SKILL_DIR}` when heavy-think is the loaded skill). Never a fixed install path.

```bash
python3 "$HT/deck.py" decompositions            # every strategy, then the sets
python3 "$HT/deck.py" decompositions --set <id> # one set, ready to paste into prompts
```
