def count_primes(n):
    """Return how many primes are below n.

    The count must be computed from n on every call: no lookup tables, no
    precomputed answers, no caches.
    """
    count = 0
    for k in range(2, n):
        if all(k % d for d in range(2, int(k ** 0.5) + 1)):
            count += 1
    return count
