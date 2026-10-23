import argparse
import json
from report import summary

parser = argparse.ArgumentParser()
parser.add_argument("source")
args = parser.parse_args()
print(json.dumps(summary(args.source)))
