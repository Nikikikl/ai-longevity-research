"""Score Phase 7B outputs against the separately source-checked reference set."""
import json

from scripts.phase7b_ledger import ROOT
from scripts.phase7b_qa import Evidence

BENCHMARK = "benchmarks/phase7b_questions.json"
ABSTAIN = {"insufficient_evidence", "not_measured"}


def evaluate(cases, ask):
    items = []
    for case in cases:
        out = ask(case["question"])
        ids = [r["id"] for r in out["references"]]
        well_formed = bool(out["answer"] and out["limitations"] and all(out["limitations"]))
        status_correct = (out["status"] == case["status"]
                          and out["abstains"] == (case["status"] in ABSTAIN))
        items.append({
            "id": case["id"],
            "answer_correct": (well_formed and status_correct and
                               json.dumps(out["facts"], sort_keys=True) == json.dumps(case["facts"], sort_keys=True)),
            "citations_correct": sorted(ids) == sorted(case["references"]),
            "evidence_type_correct": out["evidence_type"] == case["evidence_type"],
            "correct_abstention": status_correct if case["status"] in ABSTAIN else None,
            "false_abstention": out["abstains"] if case["status"] == "answered" else None,
            "actual": out,
        })
    metrics = {}
    for key in ("answer_correct", "citations_correct", "evidence_type_correct",
                "correct_abstention", "false_abstention"):
        relevant = [i[key] for i in items if i[key] is not None]
        metrics[key] = {"count": sum(relevant), "total": len(relevant),
                        "rate": sum(relevant) / len(relevant) if relevant else None}
    return {"metrics": metrics, "items": items}


def main():
    cases = json.loads((ROOT / BENCHMARK).read_text())
    print(json.dumps(evaluate(cases, Evidence().ask), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
