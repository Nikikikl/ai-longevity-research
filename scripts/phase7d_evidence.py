"""Validate and query the focused Phase 7D evidence extension."""
import argparse
from collections import defaultdict
import csv
import gzip
import json
import re
from zipfile import ZipFile

from scripts.phase7b_ledger import GO, LEDGER, OVERLAP, ROOT, pinned_file, read_csv, require
from scripts.phase7b_qa import Evidence
from scripts.phase7b_score import evaluate

EXTENSION = "reports/phase7d_evidence_ledger.csv"
AUDIT = "reports/phase7b_evidence_audit.md"
BENCHMARK = "benchmarks/phase7d_questions.json"
GENES = {"2309": "FOXO3", "51548": "SIRT6"}
CELL_ARCHIVE = "data/raw/cellAge.zip"
GENAGE_ARCHIVE = "data/raw/human_genes.zip"
GO_FIELDS = {
    "entrez_gene_id": "entrez_gene_id", "hgnc_id": "hgnc_id", "approved_symbol": "approved_symbol",
    "go_release": "go_release", "gaf_go_id": "gaf_go_id", "go_id": "go_id", "go_term": "go_term",
    "db_object_id": "db_object_id", "gene_product_form_id": "gene_product_form_id",
    "evidence_code": "evidence_code", "go_relation": "relation", "source_reference": "reference",
}
CELL_FIELDS = {
    "Entrez ID": "entrez_gene_id", "Gene symbol": "cellage_source_symbol",
    "Type of senescence": "cellage_senescence_type", "Cancer Cell": "cellage_cancer_cell",
    "Senescence Effect": "cellage_senescence_effect", "Reference": "source_reference",
}


def archive_rows(path, member, delimiter):
    manifest = json.loads((ROOT / f"{path}.json").read_text())
    with ZipFile(pinned_file(path, manifest)) as archive:
        lines = archive.read(member).decode("utf-8-sig").splitlines()
    return list(csv.DictReader(filter(str.strip, lines), delimiter=delimiter))


def check_extension(prior, extension, raw=False):
    """Compare curated rows with the tracked tables and, optionally, the pinned archives."""
    overlap = {r["entrez_gene_id"]: r for r in read_csv(OVERLAP) if r["entrez_gene_id"] in GENES}
    go = {r["gaf_line"]: r for r in read_csv(GO) if r["entrez_gene_id"] in GENES}
    groups = defaultdict(list)
    for row in prior + extension:
        if row["pmid"]:
            groups[row["pmid"]].append(row)

    require(all(list(r) == list(prior[0]) and None not in r.values() for r in extension),
            "Extension columns differ from the frozen ledger")
    require(len({r["record_id"] for r in prior + extension}) == len(prior) + len(extension),
            "Duplicate ledger record")
    cellage, genage, gaf = {}, {}, {}
    for row in extension:
        gene, record, pmid = row["entrez_gene_id"], row["record_id"], row["pmid"]
        shared = overlap[gene]
        require(row["approved_symbol"] == GENES[gene] == shared["approved_symbol"]
                and row["hgnc_id"] == shared["approved_hgnc_id"], record)
        require(row["known_limitations"] and row["review_depth"], f"Incomplete review: {record}")
        if pmid:
            group = groups[pmid]
            require(pmid.isdecimal() and row["doi"].startswith("10.")
                    and row["citation_url"] == f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                    and all(item["doi"].casefold() == row["doi"].casefold() for item in group), record)
            require(row["pmid_rows_in_ledger"] == str(len(group)) and
                    all(row[f"pmid_{field}"] == "|".join(sorted({item[key] for item in group}))
                        for field, key in (("sources", "source"), ("genes", "approved_symbol"))), record)
        match row["source"]:
            case "CellAge":
                ordinal = int(row["cellage_record_number"])
                require(record == f"CellAge:{ordinal}" and pmid and row["source_reference"] == pmid
                        and (row["source_file"], row["source_member"]) == (CELL_ARCHIVE, "cellage3.tsv")
                        and ordinal in json.loads(shared["cellage_source_record_numbers"]), record)
                cellage[ordinal] = row
            case "GenAge":
                identifier = row["db_object_id"]
                require(record == f"GenAge:{identifier}" and not pmid and not row["source_reference"]
                        and (row["source_file"], row["source_member"]) == (GENAGE_ARCHIVE, "genage_human.csv")
                        and identifier in json.loads(shared["genage_source_genage_ids"]), record)
                genage[identifier] = row
            case "GO":
                line = row["gaf_line"]
                original = go[line]
                require(record == f"GAF:{line}" and pmid and row["source_reference"] == f"PMID:{pmid}"
                        and (row["source_file"], row["source_member"]) == (GO, "HUMAN-uniprot.gaf.gz")
                        and original["status"] == "positive"
                        and all(row[k] == original[v] for k, v in GO_FIELDS.items()), record)
                gaf[int(line)] = row
            case _:
                raise ValueError(f"Unknown source for {record}")

    require(set(cellage) == {n for row in overlap.values()
                             for n in json.loads(row["cellage_source_record_numbers"])}, "Missing CellAge row")
    require(set(genage) == {n for row in overlap.values()
                            for n in json.loads(row["genage_source_genage_ids"])}, "Missing GenAge row")
    if raw:
        cell_rows = archive_rows(CELL_ARCHIVE, "cellage3.tsv", "\t")
        require(set(cellage) == {n for n, row in enumerate(cell_rows, 1) if row["Entrez ID"] in GENES},
                "Original CellAge records differ from the audit")
        for n, row in cellage.items():
            require(all(cell_rows[n - 1][k] == row[v] for k, v in CELL_FIELDS.items()), row["record_id"])
        gen_rows = archive_rows(GENAGE_ARCHIVE, "genage_human.csv", ",")
        for n, original in enumerate(gen_rows, 1):
            if original["entrez gene id"] in GENES:
                row = genage[original["GenAge ID"]]
                require(row["entrez_gene_id"] == original["entrez gene id"]
                        and row["approved_symbol"] == original["symbol"]
                        and row["biological_claim"] == f"GenAge inclusion (why={original['why']})"
                        and n in json.loads(overlap[row["entrez_gene_id"]]["genage_source_record_numbers"]),
                        row["record_id"])
        manifest = json.loads((ROOT / "data/go_provenance.json").read_text())
        name = "HUMAN-uniprot.gaf.gz"
        with gzip.open(pinned_file(f"data/raw/references/{name}", manifest["files"][name]),
                       "rt", encoding="utf-8") as handle:
            for n, line in enumerate(handle, 1):
                if n in gaf:
                    row = gaf.pop(n)
                    cells = line.rstrip("\n").split("\t")
                    fields = {1: "db_object_id", 3: "go_relation", 4: "gaf_go_id", 5: "source_reference",
                              6: "evidence_code", 16: "gene_product_form_id"}
                    require(all(cells[i] == row[k] for i, k in fields.items()), row["record_id"])
        require(not gaf, "Missing original GAF lines")


class ExpandedEvidence(Evidence):
    def __init__(self):
        super().__init__()
        self.rows.update((row["record_id"], row) for row in read_csv(EXTENSION))

    def reference(self, key):
        if key == "P7D:audit":
            return {"id": key, "path": AUDIT, "locator": "#phase-7d-extension"}
        if key.startswith("GenAge:"):
            row = self.rows[key]
            return {"id": key, "path": row["source_file"], "member": row["source_member"],
                    "locator": f"GenAge ID {row['db_object_id']}", "ledger": EXTENSION}
        ref = super().reference(key)
        if key in self.rows and self.rows[key]["entrez_gene_id"] in GENES:
            ref["ledger"] = EXTENSION
        return ref

    def record_answer(self, key):
        row = self.rows.get(key)
        if row is None:
            return self.outside_scope(f"{key} is outside the selected ledger records.", {"record_id": key})
        pmid = row["pmid"]
        references = (key, f"PMID:{pmid}") if pmid else (key,)
        facts = {"record_id": key, "gene": row["approved_symbol"], "source": row["source"],
                 "claim": row["biological_claim"], "pmid": pmid or None, "review_depth": row["review_depth"]}
        reviewed = row["reviewed_experimental_result"]
        prose = f"{key} records {row['biological_claim']}."
        if reviewed:
            prose += f" Reviewed finding: {reviewed}"
        result = self.answer(prose, row["evidence_type"], facts, references, row["known_limitations"])
        result["details"] = {field: row[field] for field in (
            "entrez_gene_id", "hgnc_id", "study_organism", "study_model", "intervention_or_exposure",
            "measurements", "evidence_code", "cellage_cancer_cell", "experiment_link_note") if row[field]}
        return result

    def outside_scope(self, prose, facts, evidence_type="scope_assessment"):
        return self.answer(prose, evidence_type, facts, ("P7D:audit",),
                           "The five-gene ledger indexes selected rows from pinned sources.",
                           "insufficient_evidence")

    def ask(self, question):
        command, _, target = " ".join(question.split()).partition(" ")
        command = command.casefold()
        if command == "record" and (match := re.fullmatch(r"(cellage|genage|gaf):(\d+)", target.casefold())):
            prefix = {"cellage": "CellAge", "genage": "GenAge", "gaf": "GAF"}[match[1]]
            return self.record_answer(f"{prefix}:{match[2]}")
        if command == "pmid" and re.fullmatch(r"[0-9]+", target):
            if any(row["pmid"] == target for row in self.rows.values()):
                return self.citation_answer(target)
            return self.outside_scope(f"PMID {target} is outside the scoped ledger.",
                                      {"pmid": target, "rows": 0}, "citation_audit")
        gene = GENES.get(target, target.upper())
        if gene in GENES.values():
            if command == "cellage":
                return self.cellage_answer(gene, independence=False)
            if command == "association":
                return self.association_answer("partial correlation", gene)
        return self.answer("Use record, pmid, cellage or association for the Phase 7D evidence lookup.",
                           "scope_assessment", {}, ("P7D:audit",),
                           "CellAge and association commands take FOXO3 or SIRT6 by symbol or Entrez ID.",
                           "unsupported_question")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("question", nargs="?", help="one lookup command, such as 'cellage FOXO3'")
    group.add_argument("--check", action="store_true")
    group.add_argument("--check-raw", action="store_true")
    group.add_argument("--score", action="store_true")
    args = parser.parse_args()
    if args.check or args.check_raw:
        extension = read_csv(EXTENSION)
        check_extension(read_csv(LEDGER), extension, raw=args.check_raw)
        print(f"Verified {len(extension)} Phase 7D records.")
    elif args.score:
        cases = json.loads((ROOT / BENCHMARK).read_text())
        print(json.dumps(evaluate(cases, ExpandedEvidence().ask), indent=2, ensure_ascii=False))
    else:
        print(json.dumps(ExpandedEvidence().ask(args.question), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
