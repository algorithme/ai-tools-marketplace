def discounted_cents(cents, percent):
    """Return the discounted unit price in integer cents."""
    if cents < 0 or not 0 <= percent <= 100:
        raise ValueError("invalid price or discount")
    return int(cents * (100 - percent) / 100)
