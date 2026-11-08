"""Build and validate the Phase 7B ledger from the pinned project outputs."""
import argparse
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
MATRIX = "reports/gene_evidence_matrix.csv"
OVERLAP = "reports/gene_overlap_genes.csv"
GO = "reports/go_gene_annotations.csv"
LEDGER = "reports/phase7b_evidence_ledger.csv"
METRICS = "data/phase7b_metrics.json"
AUDITED = {"1029": "CDKN2A", "7015": "TERT", "7157": "TP53"}
# These notes apply to the cited result behind these rows, not the whole paper.
REVIEWED_LINKS = {
    "CellAge:870": ("same_reported_assay", "Sugrue's p53 restoration assay also underlies rows 871 and 872."),
    "CellAge:871": ("same_reported_assay", "Sugrue's p53 restoration assay also underlies rows 870 and 872."),
    "CellAge:872": ("same_reported_assay", "Sugrue's p53 restoration assay also underlies rows 870 and 871."),
    "CellAge:152": ("same_reported_assay", "Kato's p16 delivery assay also underlies rows 153 and 154. Bond (14720514) reports a distinct perturbation."),
    "CellAge:153": ("same_reported_assay", "Kato's p16 delivery assay also underlies rows 152 and 154."),
    "CellAge:154": ("same_reported_assay", "Kato's p16 delivery assay also underlies rows 152 and 153."),
    "CellAge:845": ("same_reported_study", "Bodnar's hTERT transfection study also underlies GAF lines 27897 and 27918."),
    "GAF:27897": ("same_reported_study", "Bodnar's hTERT transfection study also underlies CellAge 845 and GAF line 27918."),
    "GAF:27918": ("same_reported_study", "Bodnar's hTERT transfection study also underlies CellAge 845 and GAF line 27897."),
    "GAF:133817": ("distinct_reported_perturbation", "Binet's p53 depletion in fibroblasts differs from Sugrue's restoration in EJ cells (9275177)."),
    "GAF:289848": ("distinct_reported_perturbation", "Bond's p16 knockdown differs from Kato's protein delivery (9607312). No claim of sample independence."),
}
GO_FIELDS = {
    "entrez_gene_id": "entrez_gene_id", "hgnc_id": "hgnc_id",
    "approved_symbol": "approved_symbol", "go_release": "go_release",
    "gaf_go_id": "gaf_go_id", "go_id": "go_id", "go_term": "go_term",
    "go_status": "status", "db_object_id": "db_object_id", "evidence_code": "evidence_code",
    "gene_product_form_id": "gene_product_form_id", "source_reference": "reference",
    "go_relation": "relation", "go_with_from": "with_from", "go_assigned_by": "assigned_by",
}


def read_csv(path):
    with (ROOT / path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def limitations(row):
    if row["assessment"]:
        return row["assessment"]
    return {
        "GO method reference": "Annotation method; no primary study is identified by this reference.",
        "Bibliographic verification": "Publication identity checked; experimental result not reviewed.",
        "Abstract": "Abstract review only; methods and study-level independence were not fully assessed.",
        "Full text": "Interpret the result in the stated model; the GO annotation is a separate curated assertion.",
    }[row["review_depth"]]


def build():
    matrix = read_csv(MATRIX)
    overlap = {r["entrez_gene_id"]: r for r in read_csv(OVERLAP)}
    go = {r["gaf_line"]: r for r in read_csv(GO) if r["entrez_gene_id"] in AUDITED}
    by_pmid, cellage = defaultdict(list), defaultdict(set)
    ids = set()
    for row in matrix:
        gene, source = row["entrez_gene_id"], row["source"]
        require(AUDITED.get(gene) == row["approved_symbol"] == overlap[gene]["approved_symbol"]
                and row["hgnc_id"] == overlap[gene]["approved_hgnc_id"], f"Gene mismatch: {gene}")
        if source == "CellAge":
            number = row["cellage_record_number"]
            cellage[gene].add(int(number))
            require(row["pmid"] == row["source_reference"], f"CellAge reference mismatch: {number}")
        else:
            require(source == "GO", f"Unknown database: {source}")
            number = row["gaf_line"]
            require(all(row[k] == go[number][v] for k, v in GO_FIELDS.items()), f"GAF mismatch: {number}")
            require(row["pmid"] == row["source_reference"].removeprefix("PMID:")
                    if row["source_reference"].startswith("PMID:") else not row["pmid"],
                    f"GO reference mismatch: {number}")
        row["record_id"] = f"{'GAF' if source == 'GO' else source}:{number}"
        require(row["record_id"] not in ids, f"Duplicate record: {row['record_id']}")
        ids.add(row["record_id"])
        if row["pmid"]:
            by_pmid[row["pmid"]].append(row)

    for gene in AUDITED:
        require(cellage[gene] == set(json.loads(overlap[gene]["cellage_source_record_numbers"])),
                f"Incomplete CellAge records: {gene}")
    require(REVIEWED_LINKS.keys() <= ids, "Missing source for a reviewed relationship")
    result = []
    for row in matrix:
        is_go = row["source"] == "GO"
        reuse = by_pmid.get(row["pmid"], [])
        state, note = REVIEWED_LINKS.get(row["record_id"], ("not_assessed", ""))
        result.append({
            "record_id": row["record_id"],
            **{k: row[k] for k in (
                "entrez_gene_id", "hgnc_id", "approved_symbol", "source", "source_file",
                "source_member", "cellage_record_number", "gaf_line", "go_release",
                "source_reference", "pmid", "doi", "citation_url", "reviewed_text_url",
                "cellage_source_symbol", "cellage_senescence_type", "cellage_cancer_cell",
                "cellage_senescence_effect", "gaf_go_id", "go_id", "go_term", "evidence_code",
                "go_relation", "db_object_id", "gene_product_form_id")},
            "evidence_type": "go_annotation" if is_go else "cellage_perturbation_record",
            "biological_claim": (
                f"{row['go_relation']} {row['go_id']} ({row['go_term']})" if is_go
                else f"{row['cellage_senescence_effect']} senescence (CellAge type: {row['cellage_senescence_type']})"
            ),
            **{k: row[k] for k in ("review_depth", "study_organism", "study_model",
                                  "intervention_or_exposure", "measurements")},
            "reviewed_experimental_result": row["observed_outcome"],
            "known_limitations": limitations(row),
            "pmid_rows_in_ledger": len(reuse) if reuse else "",
            "pmid_sources": "|".join(sorted({r["source"] for r in reuse})),
            "pmid_genes": "|".join(sorted({r["approved_symbol"] for r in reuse})),
            "experiment_link_status": state,
            "experiment_link_note": note,
        })
    return result


def render(rows):
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue().encode("utf-8")


def pinned_file(path, manifest):
    file = ROOT / path
    require(file.stat().st_size == manifest["size_bytes"] and
            hashlib.sha256(file.read_bytes()).hexdigest() == manifest["sha256"],
            f"Pinned input mismatch: {file}")
    return file


def check_raw(rows):
    cell_meta = json.loads((ROOT / "data/raw/cellAge.zip.json").read_text())
    with ZipFile(pinned_file("data/raw/cellAge.zip", cell_meta)) as archive:
        lines = archive.read("cellage3.tsv").decode("utf-8-sig").splitlines()
    raw = list(csv.DictReader((line for line in lines if line.strip()), delimiter="\t"))
    fields = {"Entrez ID": "entrez_gene_id", "Gene symbol": "cellage_source_symbol",
              "Cancer Cell": "cellage_cancer_cell", "Type of senescence": "cellage_senescence_type",
              "Senescence Effect": "cellage_senescence_effect", "Reference": "source_reference"}
    expected = {i for i, row in enumerate(raw, 1) if row["Entrez ID"] in AUDITED}
    require(expected == {int(r["cellage_record_number"]) for r in rows if r["source"] == "CellAge"},
            "Audit does not cover the original CellAge ordinals")
    for row in rows:
        if row["source"] == "CellAge":
            original = raw[int(row["cellage_record_number"]) - 1]
            require(all(original[k] == row[v] for k, v in fields.items()), row["record_id"])

    go_meta = json.loads((ROOT / "data/go_provenance.json").read_text())
    name = "HUMAN-uniprot.gaf.gz"
    pending = {int(r["gaf_line"]): r for r in rows if r["source"] == "GO"}
    with gzip.open(pinned_file(f"data/raw/references/{name}", go_meta["files"][name]),
                   "rt", encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            if number in pending:
                row = pending.pop(number)
                cells = line.rstrip("\n").split("\t")
                fields = {1: "db_object_id", 3: "go_relation", 4: "gaf_go_id",
                          5: "source_reference", 6: "evidence_code", 16: "gene_product_form_id"}
                require(all(cells[i] == row[k] for i, k in fields.items()), row["record_id"])
    require(not pending, f"GAF lines not found: {sorted(pending)}")


def summarize(rows):
    publications = Counter(r["pmid"] for r in rows if r["pmid"])
    by_source = defaultdict(Counter)
    for row in rows:
        if row["pmid"]:
            by_source[row["source"]][row["pmid"]] += 1
    return {
        "source_rows": dict(Counter(r["source"] for r in rows)),
        "pmid_rows": sum(publications.values()),
        "non_pmid_rows": len(rows) - sum(publications.values()),
        "distinct_pmids": len(publications),
        "repeated_pmids": {k: v for k, v in sorted(publications.items()) if v > 1},
        "within_source_repeated_pmids": {
            source: {k: v for k, v in sorted(counts.items()) if v > 1}
            for source, counts in by_source.items()
        },
        "cross_source_pmids": sorted({r["pmid"] for r in rows if "|" in r["pmid_sources"]}),
        "cross_gene_pmids": sorted({r["pmid"] for r in rows if "|" in r["pmid_genes"]}),
    }


def metrics_snapshot(path):
    metrics = json.loads(path.read_text())
    association, prediction = metrics["association"], metrics["prediction"]
    score = association["replication_score"]
    return {
        "source": "reports/phase7_baseline_results.md",
        "protocol_sha256": metrics["protocol_sha256"],
        "donors": {"discovery": metrics["GSE113957"]["eligible"],
                   "validation": metrics["GSE226189"]["eligible"]},
        "replication": {"target": round(score["target"], 5),
                        "matched_median": round(score["matched_median"], 5),
                        "permutation_p": round(association["validation_permutation_p"], 4),
                        "decision_met": association["decision_met"]},
        "prediction": {"ridge_mae": round(prediction["metrics"]["panel_ridge"]["mae"], 2),
                       "median_age_mae": round(prediction["metrics"]["median_age"]["mae"], 2),
                       "matched_median_mae": round(prediction["matched_panel_mae"]["matched_median"], 2)},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare with committed outputs")
    parser.add_argument("--check-raw", action="store_true", help="also verify original CellAge and GAF lines")
    parser.add_argument("--metrics", type=Path, help="also project the supplied Phase 7A aggregate JSON")
    args = parser.parse_args()
    rows = build()
    if args.check_raw:
        check_raw(rows)
    outputs = {LEDGER: render(rows)}
    if args.metrics:
        outputs[METRICS] = (json.dumps(metrics_snapshot(args.metrics), indent=2) + "\n").encode()
    for name, contents in outputs.items():
        file = ROOT / name
        if args.check:
            require(file.read_bytes() == contents, f"Stale output: {name}")
        else:
            file.write_bytes(contents)
    print(json.dumps(summarize(rows), indent=2))


if __name__ == "__main__":
    main()
