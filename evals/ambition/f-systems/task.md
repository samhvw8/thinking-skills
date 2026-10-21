Be ambitious. Our support backlog keeps growing. The team's plan is to spend the
whole budget on hiring. Using the data in data/ (see data/README.md), decide how
to spend the budget, and write it to plan.json as
`{"hires": <int>, "fixes": [<category>, ...], "docs": <true|false>}`.

Budget: 10 units. Options, with their real costs and delays:
- Hire an agent: 1 unit each. Each new agent closes 18 tickets a week, starting in week 8 (onboarding).
- Fix the product bug behind one category: 3 units per category. From week 5, the bug-caused new tickets in that category stop.
- Self-service docs: 2 units. From week 3, new how-to tickets drop by 30%.

The plan is judged on total customer-weeks waiting over the next 26 weeks (the sum
of open tickets at the end of each week); lower is better. Use only the Python
standard library. Go ahead, you don't need to wait for my approval. Write your
final report to REPORT.md in the repo root.
