# Support data

- `tickets.csv`: one row per ticket for the last 12 weeks (week -11 to week 0).
  `kind` is `new` or `followup` (a customer chasing a ticket that is still open).
  `caused_by_bug` is 1 when engineering traced a new ticket to a product bug.
- `weekly.csv`: tickets opened and closed per week, and tickets still open at the end of the week.

Today the team closes 400 tickets a week, and 900 are open.
