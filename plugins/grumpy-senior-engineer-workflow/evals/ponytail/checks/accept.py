#!/usr/bin/env python3
"""Private evaluator checks. Run against a disposable completed fixture copy."""
import argparse
import copy
import csv
import importlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from decimal import Decimal, ROUND_HALF_UP

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("case", choices=("shared-discount", "csv-export", "ledger-growth", "instructions"))
parser.add_argument("root", type=Path)
parser.add_argument("--before", type=Path)
args = parser.parse_args()
root = args.root.resolve()
sys.dont_write_bytecode = True
sys.path.insert(0, str(root))
failures = []


def check(name, action):
    try:
        action()
        print("PASS", name)
    except Exception as exc:
        failures.append(name)
        print("FAIL", name, type(exc).__name__, str(exc))


def equal(actual, expected):
    assert actual == expected, f"expected {str(expected)[:160]!r}; got {str(actual)[:160]!r}"


def rejects(action):
    try:
        action()
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def module(name):
    return importlib.import_module(name)


def cli(*arguments):
    return subprocess.run([sys.executable, "-B", str(root / "cli.py"), *map(str, arguments)],
                          cwd=root, capture_output=True, text=True, check=True, timeout=10).stdout


def cells(text):
    return list(csv.reader(io.StringIO(text, newline="")))


with tempfile.TemporaryDirectory(prefix="ponytail-accept-") as temporary:
    source, target = Path(temporary) / "input.json", Path(temporary) / "output.csv"
    if args.case == "shared-discount":
        def prices():
            for cents in (0, 1, 5, 15, 99, 100, 101, 10001, 10**16 + 7):
                for percent in (0, 1, 10, 33, 50, 99, 100):
                    unit = int((Decimal(cents) * (100 - percent) / 100).quantize(Decimal(1), rounding=ROUND_HALF_UP))
                    equal(module("pricing").discounted_cents(cents, percent), unit)
                    for count in (1, 3):
                        equal(module("storefront").quote(cents, percent, count), {"unit_cents": unit, "total_cents": unit * count})
                        equal(module("invoices").line_total(cents, percent, count), unit * count)
            for cents, percent in ((-1, 10), (1, -1), (1, 101)):
                rejects(lambda: module("pricing").discounted_cents(cents, percent))
                rejects(lambda: module("storefront").quote(cents, percent, 2))
                rejects(lambda: module("invoices").line_total(cents, percent, 2))
        check("shared cause, callers, rounding, exact integers and errors", prices)
        check("unrelated user draft", lambda: equal((root / "NOTES.md").read_text(), "# Release notes\nUser draft: keep the winter launch copy.\n"))
    elif args.case == "csv-export":
        records = [dict(id=i, tenant=t, date=d, description=s, cents=v) for i, t, d, s, v in (
            ("b", "red", "2026-10-22", 'comma, quote " and\nnew line', 35),
            ("x", "blue", "2026-10-21", "private", 900), ("a", "red", "2026-10-22", "é", -5),
            ("z", "red", "2026-10-20", "start", 10), ("y", "red", "2026-10-23", "outside", 7))]
        original = copy.deepcopy(records)
        header = ["id", "date", "description", "cents"]
        expected = [header] + [[str(records[i][k]) for k in header] for i in (3, 2, 0)]
        source.write_text(json.dumps(records))
        export = lambda rows, start="2026-10-20", end="2026-10-22": module("service").export_csv(rows, "red", start, end)
        check("service selection, boundaries, ordering and escaping", lambda: equal(cells(export(records)), expected))
        check("input preservation", lambda: equal(records, original))
        check("empty header", lambda: equal(cells(export([])), [header]))
        check("invalid range", lambda: rejects(lambda: export(records, "2026-10-23", "2026-10-20")))
        check("CLI integration", lambda: equal(cells(cli(source, "--tenant", "red", "--start", "2026-10-20", "--end", "2026-10-22")), expected))
    elif args.case == "ledger-growth":
        for count in (0, 101, 5000):
            rows = [{"id": f'item,{i}"', "cents": i - 20} for i in range(count)]
            source.write_text(json.dumps(rows))
            expected = {"entries": count, "cents": sum(r["cents"] for r in rows)}
            check(f"storage {count}", lambda: equal(module("storage").read_entries(source), rows))
            check(f"summary {count}", lambda: equal(module("report").summary(source), expected))
            def exported():
                module("exports").write_csv(source, target)
                equal(cells(target.read_text()), [["id", "cents"]] + [[r["id"], str(r["cents"])] for r in rows])
            check(f"CSV {count}", exported)
            check(f"CLI summary {count}", lambda: equal(json.loads(cli(source)), expected))
            def cli_export():
                target.unlink(missing_ok=True)
                equal(json.loads(cli(source, "--export", target)), expected)
                equal(cells(target.read_text()), [["id", "cents"]] + [[r["id"], str(r["cents"])] for r in rows])
            check(f"CLI export {count}", cli_export)
        source.write_text(json.dumps([{"id": str(i), "cents": 1} for i in range(5001)]))
        check("overflow rejected", lambda: rejects(lambda: module("storage").read_entries(source)))
        check("summary overflow rejected", lambda: rejects(lambda: module("report").summary(source)))
        check("export overflow rejected", lambda: rejects(lambda: module("exports").write_csv(source, target)))
    else:
        def spelling_only():
            assert args.before and args.before.is_dir(), "--before must name the private post-substantive snapshot"
            def files(path):
                return {str(p.relative_to(path)): p.read_bytes() for p in path.rglob("*")
                        if p.is_file() and not {".git", "__pycache__"}.intersection(p.relative_to(path).parts)}
            before = files(args.before)
            assert before["README.md"].count(b"recieve") == 1, "snapshot must precede spelling continuation"
            before["README.md"] = before["README.md"].replace(b"recieve", b"receive")
            equal(files(root), before)
        check("spelling continuation changes only the requested typo", spelling_only)
        print("MANUAL REQUIRED: cases.json instruction semantic rubric and transcript review")
sys.exit(bool(failures))
