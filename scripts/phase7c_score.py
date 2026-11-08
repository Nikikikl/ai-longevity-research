"""Apply the Phase 7B scorer to a frozen Phase 7C split."""
import argparse
import hashlib
import json

from scripts.phase7b_ledger import ROOT
from scripts.phase7b_qa import Evidence
from scripts.phase7b_score import evaluate

BENCHMARK = "benchmarks/phase7c_questions.json"
BASELINE_SHA256 = "6f099b4df3fe3a9e782cb7f5912e5a6c0020b776555cc3411b518979987f7a19"
BENCHMARK_SHA256 = "956bbd50e3ba95ef0eda6597f14f9a0e7a57732cf9f55fb2216f07f9bf87a86e"


def verified_bytes(path, digest):
    data = (ROOT / path).read_bytes()
    if hashlib.sha256(data).hexdigest() != digest:
        raise SystemExit(f"Frozen input changed: {path}")
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("method", choices=("baseline", "candidate"))
    parser.add_argument("split", choices=("development", "heldout"))
    args = parser.parse_args()
    verified_bytes("scripts/phase7b_qa.py", BASELINE_SHA256)
    cases = json.loads(verified_bytes(BENCHMARK, BENCHMARK_SHA256))
    cases = [case for case in cases if case["split"] == args.split]
    if args.method == "candidate":
        from scripts.phase7c_qa import NormalizedEvidence

        evidence = NormalizedEvidence()
    else:
        evidence = Evidence()
    print(json.dumps(evaluate(cases, evidence.ask), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
