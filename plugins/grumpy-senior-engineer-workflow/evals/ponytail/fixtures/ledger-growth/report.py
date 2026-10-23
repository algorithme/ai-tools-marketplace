from storage import read_entries


def summary(source):
    """Return entry count and total cents."""
    # shortcut: recalculate totals per call; revisit above one refresh per second.
    rows = read_entries(source)
    return {"entries": len(rows), "cents": sum(row["cents"] for row in rows)}
