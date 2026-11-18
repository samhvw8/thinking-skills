---
type: Idea Card
title: Toy card
description: A toy source whose method is answer-a-question.
field: testing
bricks: [answer-a-question]
moves: [invert-the-check]
---

# Recipe (layer 4)
| Role | Brick (slug) | Signature | Why this brick |
|------|-------------|-----------|----------------|
| answer-question | answer-a-question | question -> answer | (inferred) |
Operator: sequence

## Lens: fault-tree — what has to go wrong for a wrong answer
| What must happen | What the source says | Pieces |
|------------------|----------------------|--------|
| Step c passes a bad draft | "c is never checked" (Methods) | step-c |
What this angle shows that the others do not: step c fails alone.

# Mutations
| Operator | Variant | Role fit | Novelty link | Kill test | Owner verdict | Origin | Lens |
|----------|---------|----------|--------------|-----------|---------------|--------|------|
| substitute-brick | swap step a | fits | none found (toy) | toy run | | claude | fault-tree |
| `remove` | drop step b | breaks c | none found (toy) | toy run | | claude | - |
| merge-sideways | odd one | unclear | none found (toy) | toy run | | claude | data-path |
