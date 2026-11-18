You are reviewing a worker's change against its card. Find every defect: bugs, and any place the change breaks or drifts from the card. For each, give the line and one sentence. Do not list style points. End with one line: "Verdict: followed" or "Verdict: drifted".

Card: add pagination to list_users.
- New optional parameters page (counted from 1) and per_page (default 50).
- list_users() with no arguments must keep working for its three callers and return every user, as today.
- No other change.

Before (users.py):
```python
USERS = [f"user{i}" for i in range(1, 121)]


def list_users():
    """Return every user. Callers: admin page, export job, nightly sync."""
    return list(USERS)
```

After (users.py):
```python
USERS = [f"user{i}" for i in range(1, 121)]


def list_users(page, per_page=50):
    """Return one page of users, pages counted from 1."""
    all_users = list(USERS)
    start = page * per_page
    return all_users[start:start + per_page]
```
