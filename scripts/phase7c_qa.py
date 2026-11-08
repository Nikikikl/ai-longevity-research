"""Normalize terminology before calling the frozen Phase 7B lookup."""
import argparse
import json
import re
import unicodedata

from scripts.phase7b_qa import Evidence

DASHES = str.maketrans({ch: "-" for ch in "‐‑‒–—−"})
TERMS = (
    (r"\bcell[ -]age\b", "cellage"),
    (r"\bpubmed (?:id(?:entifier)?|accession)\b", "pmid"),
    (r"\bpartial\s+r\b", "partial correlation"),
    (r"\bq[- ]values?\s+(?:below|less than)\s+", "q < "),
    (r"\b(?:genes were eligible|genes could be analy[sz]ed)\b", "genes were tested"),
    (r"\b(?:people|humans)\s+(?:(?:would|could|will)\s+)?live longer\b", "human lifespan"),
    (r"\b(p14|p16)[\s^_-]*(arf|ink4a)\b", r"\1\2"),
)
GENE_ALIASES = (
    (r"\b(?:tumou?r protein )?p53\b", "tp53"),
    (r"\b(?:htert|telomerase reverse transcriptase|telomerase catalytic subunit)\b", "tert"),
)


def normalize_question(question):
    q = " ".join(unicodedata.normalize("NFKC", question).casefold().translate(DASHES).split())
    for pattern, replacement in TERMS:
        q = re.sub(pattern, replacement, q)

    if "cellage" in q:
        q = re.sub(r"\b(?:show|pull up)\b", "list", q)
        q = re.sub(r"\b(?:entries|annotations)\b", "records", q)
        q = re.sub(r"\bp16(?:ink4a)?\b", "cdkn2a", q)

    # Protein aliases identify the gene for record and RNA-expression lookups.
    if "cellage" in q or ("partial correlation" in q and not re.search(
            r"\bprotein (?:levels?|abundance|expression|concentrations?)\b", q)):
        for pattern, replacement in GENE_ALIASES:
            q = re.sub(pattern, replacement, q)

    if re.search(r"\bpmid\s*:?\s*\d+\b", q) and re.search(
            r"\b(?:rows?|records?|annotations?|ledger)\b", q):
        q = re.sub(r"\b(?:cite[sd]?|references?|indexed)\b", "cited", q)

    if "senescence" in q and re.search(r"\bcaus(?:al|e[sd]?|ing)\b", q):
        q = re.sub(r"\bthis (?:review|audit)\b", "this manual audit", q)

    # A joint q-value question can also mention signs. Preserve its primary intent.
    if "cohort" in q or ("discovery" in q and "validation" in q):
        if not re.search(r"\b(?:q|fdr|threshold)\b", q):
            q = re.sub(r"\b(?:same|matching|concordant) (?:signs?|directions?)\b", "sign agreement", q)
    return q


class NormalizedEvidence(Evidence):
    def ask(self, question):
        return super().ask(normalize_question(question))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("question", help="one narrow English research question")
    args = parser.parse_args()
    print(json.dumps(NormalizedEvidence().ask(args.question), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
