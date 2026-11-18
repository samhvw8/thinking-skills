---
type: Brick
title: Self-improve from own samples
description: A model makes samples, keeps the good ones and trains on them.
roles: [improve-without-labels]
fields: [machine-learning]
cards: [self-training-card]
parts:
  - { to: generate-candidates, how: split, cut: cost, note: most of the compute }
  - { to: filter-bad-samples, how: split, cut: cost }
  - { to: generate-candidates, how: judge, cut: data-flow }
  - { to: score-samples, how: split, cut: data-flow }
  - { to: filter-bad-samples, cut: data-flow }
---

# Signature
- **Input:** a model and unlabeled prompts
- **Output:** a better model
