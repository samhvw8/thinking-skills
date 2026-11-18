---
type: Idea Card
title: Self-training card
description: A model improves by training on the samples it judges good.
tags: [ideas, card]
field: machine-learning
method: self-improve-from-own-samples
bricks: [generate-candidates, score-samples, filter-bad-samples]
---

# Recipe (layer 4)
Cut: `data-flow`
| Role | Brick (slug) | Signature (input -> output, objective) | Why this brick |
|------|-------------|----------------------------------------|----------------|
| make samples | `generate-candidates` | prompt -> samples | (inferred) |
| score them | score-samples | sample -> score | (inferred) |
| keep the good ones | filter-bad-samples | scored samples -> kept samples | (inferred) |
Operator: sequence
