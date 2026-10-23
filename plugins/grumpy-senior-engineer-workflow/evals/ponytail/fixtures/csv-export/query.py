def select(records, tenant, start, end):
    """Select one tenant's records in an inclusive date interval."""
    if start > end:
        raise ValueError("inverted date range")
    return sorted((r for r in records if r["tenant"] == tenant
                   and start <= r["date"] <= end), key=lambda r: (r["date"], r["id"]))
