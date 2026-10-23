import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("file")
parser.add_argument("--tenant", required=True)
parser.add_argument("--start", required=True)
parser.add_argument("--end", required=True)
args = parser.parse_args()
records = json.loads(Path(args.file).read_text())
print(json.dumps(records))
