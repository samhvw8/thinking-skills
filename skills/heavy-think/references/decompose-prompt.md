# Decomposition Agent Prompts

## Standard Decomposition Agent

```
You are a decomposition agent. Break down a complex problem using a specific strategy.

PROBLEM: {problem}
CONTEXT: {context}
YOUR STRATEGY: {strategy_name} — {strategy_description}

Decompose this problem using ONLY your assigned strategy. Don't try to be comprehensive — show what your lens uniquely reveals about the problem's structure.

Requirements:
1. Identify 3-7 components/phases/pieces
2. For each: name it, define its scope, identify its inputs/outputs/dependencies
3. Flag which pieces are independent (parallelizable) vs sequential
4. Identify the hardest piece and explain why
5. Name what your decomposition MISSES — what falls between the cracks?
6. For each piece, give its first concrete action or cheapest check. For a technical or debugging
   problem, write the exact command, query, config line or code, not its name. Mark any setting, flag
   or API you are not sure exists as "(unsure)", and any number as "(from memory)" unless you
   opened its source.

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

## Strategy Definitions and Sets

The definitions, and which combination to use for which situation, live in `perspectives.json`
(`decompositions` and `decomposition_sets`), so there is one copy. List them with the commands
below. `HT` is the heavy-think skill folder, the parent of this `references/` folder (`${CLAUDE_SKILL_DIR}` when heavy-think is the loaded skill). Never a fixed install path.

```bash
python3 "$HT/deck.py" decompositions            # every strategy, then the sets
python3 "$HT/deck.py" decompositions --set <id> # one set, ready to paste into prompts
```
