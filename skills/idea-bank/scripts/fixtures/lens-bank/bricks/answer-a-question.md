---
type: Brick
title: Answer a question
description: A method seen as one block, split through several perspectives.
roles: [answer-question]
cards: [toy-card]
parts:
  - { to: step-a, how: split, cut: data-path }
  - { to: step-b, how: split, lens: data-path }
  - { to: step-c, how: split, lens: fault-tree, cut: data-path }
  - { to: step-a, how: judge, lens: what-could-break }
---

# Signature
- **Input:** a question
- **Output:** an answer
