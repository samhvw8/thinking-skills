# Solve mode

K independent agents solve the same verifiable problem from scratch, and you deliberate over their
work. Deliberation audits the reasoning chains and builds new paths from their fragments, so it can
reach a correct answer that none of the trajectories had (the HeavySkill method, `paper-details.md`).

## When to use

- Mathematical reasoning, algorithmic or competition problems, complex logical deduction.
- Any verifiable task where your confidence is below about 70%.
- Not for subjective or preference questions, or easy ones (above about 90% confidence).

## Stage 1: Parallel reasoning

Spawn K independent agents in one message (at most 6 in flight), model tier `strong` (`harness.md`), none aware of the
others.

| K | When |
|---|------|
| 3 | Standard: most problems |
| 5 | High stakes: competition math, critical correctness |

```
Solve this problem and arrive at a final answer. The derivation is the output: write it out in full,
since it will be audited against other solvers' work. Use whatever approach you find most natural:
algebraic, geometric, constructive, brute force, proof by contradiction.

Problem: {query}

- Reason from first principles.
- Where a step can be checked by running something (a computation, a brute-force search over small
  cases, the code itself), run it in the shell and report the result.
- Mark the final answer clearly. Math: \boxed{answer}. Code: a code block.
```

## Stage 2: Memory cache

1. Collect all K outputs.
2. Shuffle their order, which prevents position bias.
3. If they exceed the token budget, truncate the reasoning and keep the final answers.

## Stage 3: Deliberation (yours)

You do this yourself: the gain comes from one reader comparing every chain, which a delegated agent
would only add to.

1. Classify the query type: math, code, logic, multi-step.
2. Map the answer distribution: which answers appear, and how often.
3. Audit each chain: valid logic, gaps, sign errors, hidden assumptions.
4. Cross-validate: do independent approaches confirm the same result? Run a check where one exists.
5. Stay skeptical: the majority is signal, not proof; a minority answer with tighter logic may be
   right; all of them may be wrong, so re-derive from the fragments when needed.
6. Synthesize the definitive answer.

## Stage 4: Output

The final answer, without meta-analysis unless asked. Math: `\boxed{answer}`. Code: a code block.

## Iterative deliberation

When the first deliberation leaves low confidence or a fundamental disagreement, add your
deliberation as one more trajectory and run Stage 3 again. Stop after 2–3 iterations: performance
degrades beyond that (`compute.md`).

See `compute.md` for cost and K selection, `tensions.md` for consensus vs minority, `landscape.md`
for how this compares with Best-of-N and Self-Consistency.
