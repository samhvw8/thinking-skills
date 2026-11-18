---
type: Brick
title: Generate, then keep the good ones
description: Make many candidates cheaply, then keep only those a check accepts.
roles: [r-generate-then-filter]
fields: [machine-learning]
parts:
  - { to: generate-candidates, how: bind, cut: functional, note: recurs in two sources }
  - { to: filter-bad-samples, how: bind, cut: functional }
---

# Signature
- **Input:** a generator and a check
- **Output:** accepted candidates
