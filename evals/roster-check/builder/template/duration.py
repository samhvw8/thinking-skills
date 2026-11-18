def parse_duration(s: str) -> int:
    """Parse a duration like "1h30m" or "90s" into seconds.

    Units h, m, s, in that order, each at most once, each with a whole number.
    Surrounding spaces are ignored. Anything else raises ValueError.
    """
    raise NotImplementedError
