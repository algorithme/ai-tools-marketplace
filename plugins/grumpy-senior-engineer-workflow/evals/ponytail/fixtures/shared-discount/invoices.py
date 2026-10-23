from pricing import discounted_cents


def line_total(cents, percent, quantity):
    return discounted_cents(cents, percent) * quantity
