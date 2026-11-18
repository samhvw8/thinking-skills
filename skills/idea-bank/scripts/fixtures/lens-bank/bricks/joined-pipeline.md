---
type: Brick
title: Joined pipeline
description: Two steps taped into a bigger brick; each keeps its job.
roles: [run-two-steps]
parts:
  - { to: step-a, how: bind, lens: cost-share }
  - { to: step-b, how: join, lens: cost-share }
---

# Signature
- **Input:** a question
- **Output:** the result of step b
