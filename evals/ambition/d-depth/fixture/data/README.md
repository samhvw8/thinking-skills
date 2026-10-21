# customers.csv

One row per customer account, 2025 cohort.

| Column | Meaning |
|--------|---------|
| id | account id |
| region | NA, EU, APAC, LATAM |
| plan | basic, team, business |
| seats | paid seats |
| signup_month | YYYY-MM |
| onboarding_completed | 1 if the account finished onboarding |
| price_increase | 1 if the account got last quarter's price increase |
| support_tickets_90d | tickets in the 90 days before renewal |
| last_login_days | days since last login, measured on the churn date (or today for active accounts) |
| churned | 1 if the account cancelled at renewal |

The team's working theory: churn is an onboarding problem.
