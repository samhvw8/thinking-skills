def split_bill(total_cents, people):
    """Split total_cents among people as evenly as possible.

    Returns a list of ints, one per person, that sums exactly to total_cents.
    The first people get the extra cents.
    """
    if people <= 0:
        raise ValueError("people must be positive")
    share = round(total_cents / people)
    return [share] * people
