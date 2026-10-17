"""Generate the d-depth data. Deterministic: rerun gives the same files.

Planted truth: a price increase drives churn, but only for small accounts
(seats <= 5). Onboarding has a small real effect. The team's belief is that
churn is an onboarding problem.
"""
import csv
import math
import random
from pathlib import Path

here = Path(__file__).resolve().parent
rng = random.Random(20261017)
FIELDS = ["id", "region", "plan", "seats", "signup_month", "onboarding_completed",
          "price_increase", "support_tickets_90d", "last_login_days", "churned"]


def row(i):
    seats = rng.choice([1, 2, 3, 4, 5, 8, 12, 20, 40, 80])
    price_increase = int(rng.random() < 0.35)
    onboarding = int(rng.random() < 0.6)
    tickets = min(int(rng.expovariate(0.6)), 12)
    logit = -2.2 + 0.5 * (1 - onboarding) + 0.12 * tickets
    if price_increase and seats <= 5:
        logit += 2.6
    churned = int(rng.random() < 1 / (1 + math.exp(-logit)))
    last_login = int(rng.expovariate(1 / (25 if churned else 9)))
    return {
        "id": f"c{i:05d}", "region": rng.choice(["NA", "EU", "APAC", "LATAM"]),
        "plan": rng.choice(["basic", "team", "business"]), "seats": seats,
        "signup_month": f"2025-{rng.randint(1, 12):02d}",
        "onboarding_completed": onboarding, "price_increase": price_increase,
        "support_tickets_90d": tickets, "last_login_days": last_login, "churned": churned,
    }


def write(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


rows = [row(i) for i in range(3000)]
write(here / "fixture" / "data" / "customers.csv", rows[:2000])
write(here / "holdout.csv", rows[2000:])
