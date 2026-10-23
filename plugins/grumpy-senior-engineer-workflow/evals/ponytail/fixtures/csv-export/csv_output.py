import csv
import io


def render(headers, rows):
    """Return CSV text with a header and correctly escaped fields."""
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)
    return output.getvalue()
