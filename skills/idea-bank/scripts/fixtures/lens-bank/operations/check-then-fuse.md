---
type: Operation
title: Check then fuse
description: Split twice through two perspectives, fuse what checks the same thing, then invert the order.
origin: invented
source: card:toy-card
parts:
  - { to: fuse, order: 3 }
  - { to: split, order: 1, lens: fault-tree }
  - { to: split, order: 2, lens: what-goes-unchecked }
  - { to: invert, order: 4, lens: fault-tree }
---

# Steps
Split by the feared wrong conclusion, split again by what goes unchecked, fuse the overlap, invert.
