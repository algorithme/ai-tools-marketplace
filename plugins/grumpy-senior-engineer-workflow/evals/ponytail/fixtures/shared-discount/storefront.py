from pricing import discounted_cents


def quote(cents, percent, quantity):
    unit = discounted_cents(cents, percent)
    return {"unit_cents": unit, "total_cents": unit * quantity}
