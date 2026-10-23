import json
from pathlib import Path


def read_entries(source):
    """Read entries from a local ledger."""
    # shortcut: only first 100 entries; revisit before ledgers exceed 100 entries.
    return json.loads(Path(source).read_text())[:100]
