"""Compare confirmed GenAge Human and CellAge genes from the pinned Phase 2 mapping."""

import argparse
import csv
import hashlib
import io
import json
import re
import sys

from scripts.download_data import ROOT, SOURCES
from scripts.harmonize_genes import GENE_ID, MAPPING, REPORT as PHASE2_AUDIT, write_output
from scripts.inspect_data import EXPORTS

GENAGE, CELLAGE = EXPORTS
REPORT = ROOT / "reports" / "gene_overlap.md"
GENES = ROOT / "reports" / "gene_overlap_genes.csv"
FIGURE = ROOT / "reports" / "gene_overlap.svg"
CONFLICT_ID = "100529261"


def verify_mapping(contents, audit):
    pins = re.findall(r"^Generated `data/processed/gene_mapping\.csv` SHA-256 — `([0-9a-f]{64})`\.$",
                      audit, re.MULTILINE)
    if len(pins) != 1:
        raise ValueError("Expected one pinned mapping checksum in the Phase 2 audit.")
    actual = hashlib.sha256(contents).hexdigest()
    if actual != pins[0]:
        raise ValueError("Gene mapping SHA-256 differs from the Phase 2 audit.")
    return actual


def confirmed_sets(rows):
    confirmed = {export.title: {} for export in EXPORTS}
    evidence_seen = {export.title: set() for export in EXPORTS}
    expected_files = {export.title: (export.archive, SOURCES[export.archive][1]) for export in EXPORTS}
    entrez_by_hgnc = {}
    excluded = []
    for row in rows:
        source, gene_id = row["source"], row["source_entrez_id"]
        if expected_files.get(source) != (row["source_archive"], row["source_member"]):
            raise ValueError(f"Unexpected source archive or member for {source} Gene ID {gene_id}.")

        records = json.loads(row["source_record_numbers"])
        if (not isinstance(records, list) or not records
                or any(type(record) is not int or record < 1 for record in records)
                or len(records) != int(row["evidence_count"]) or len(set(records)) != len(records)
                or evidence_seen[source].intersection(records)):
            raise ValueError(f"Invalid or repeated source record ordinals for {source} Gene ID {gene_id}.")
        evidence_seen[source].update(records)

        if row["status"] != "confirmed":
            excluded.append(row)
            continue
        hgnc_id = row["approved_hgnc_id"]
        if (not GENE_ID.fullmatch(gene_id) or row["ncbi_status"] != "current_human"
                or not re.fullmatch(r"HGNC:[1-9][0-9]*", hgnc_id) or not row["approved_symbol"]):
            raise ValueError(f"Incomplete confirmed mapping for {source} Gene ID {gene_id}.")
        if gene_id in confirmed[source]:
            raise ValueError(f"Duplicate confirmed gene in {source}: {gene_id}.")
        if entrez_by_hgnc.setdefault(hgnc_id, gene_id) != gene_id:
            raise ValueError(f"{hgnc_id} maps to different confirmed Entrez Gene IDs.")
        confirmed[source][gene_id] = row
    return confirmed[GENAGE.title], confirmed[CELLAGE.title], excluded


def compare(genage, cellage):
    shared = genage.keys() & cellage.keys()
    for gene_id in sorted(shared, key=int):
        if any(genage[gene_id][field] != cellage[gene_id][field]
               for field in ("approved_hgnc_id", "approved_symbol")):
            raise ValueError(f"Approved HGNC mappings disagree for shared Gene ID {gene_id}.")
    genage_only = genage.keys() - cellage.keys()
    cellage_only = cellage.keys() - genage.keys()
    union = genage.keys() | cellage.keys()
    if (len(genage_only) + len(shared) != len(genage)
            or len(cellage_only) + len(shared) != len(cellage)
            or len(genage_only) + len(shared) + len(cellage_only) != len(union)):
        raise ValueError("Gene set counts do not partition the union.")
    return genage_only, shared, cellage_only, union


def render_genes(genage, cellage, shared):
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(("entrez_gene_id", "approved_hgnc_id", "approved_symbol",
                     "genage_original_symbols", "cellage_original_symbols", "genage_source_genage_ids",
                     "genage_source_archive", "genage_source_member", "genage_source_record_numbers",
                     "cellage_source_archive", "cellage_source_member", "cellage_source_record_numbers",
                     "cellage_evidence_count"))
    for gene_id in sorted(shared, key=int):
        left, right = genage[gene_id], cellage[gene_id]
        writer.writerow((gene_id, left["approved_hgnc_id"], left["approved_symbol"],
                         left["source_symbols"], right["source_symbols"], left["source_genage_ids"],
                         left["source_archive"], left["source_member"], left["source_record_numbers"],
                         right["source_archive"], right["source_member"], right["source_record_numbers"],
                         right["evidence_count"]))
    return stream.getvalue()


def sensitivity(excluded, genage, cellage):
    if (len(excluded) != 1 or excluded[0]["source"] != CELLAGE.title
            or excluded[0]["source_entrez_id"] != CONFLICT_ID
            or excluded[0]["status"] != "conflicting_symbol"):
        raise ValueError("Expected the single Phase 2 CellAge symbol conflict for sensitivity analysis.")

    row = excluded[0]
    scenarios = []
    for field, label in (("id_candidates", "Follow the source Gene ID"),
                         ("other_symbol_candidates", "Follow the source symbol")):
        candidates = json.loads(row[field])
        if len(candidates) != 1:
            raise ValueError(f"Expected one CellAge conflict candidate in {field}.")
        candidate = candidates[0]
        match = re.search(r" \(Gene ID ([1-9][0-9]*)\)$", candidate)
        if not match:
            raise ValueError(f"Missing Entrez Gene ID for hypothetical candidate {candidate}.")
        candidate_id = match[1]
        shared_count = len(genage.keys() & (cellage.keys() | {candidate_id}))
        scenarios.append((label, candidate, candidate_id in genage, shared_count))
    return row, scenarios


def render_report(genage, cellage, groups, conflict, mapping_sha):
    genage_only, shared, cellage_only, union = map(len, groups)
    row, scenarios = conflict
    symbol = ", ".join(json.loads(row["source_symbols"]))
    record_numbers = ", ".join(map(str, json.loads(row["source_record_numbers"])))
    min_shared = min(count for _, _, _, count in scenarios)
    max_shared = max(count for _, _, _, count in scenarios)
    effect = (f"The overlap remains **{shared}** under either candidate."
              if min_shared == max_shared == shared else
              f"The overlap would range from **{min_shared} to {max_shared}** under the candidate assignments.")
    lines = [
        "# Descriptive gene overlap", "",
        f"**{shared} uniquely validated human genes** are present in both HAGR exports.", "",
        "## Confirmed gene sets", "",
        "| Measure | Value |",
        "| --- | ---: |",
        f"| Confirmed GenAge Human genes | {len(genage)} |",
        f"| Confirmed CellAge genes | {len(cellage)} |",
        f"| Shared genes | {shared} |",
        f"| GenAge Human only | {genage_only} |",
        f"| CellAge only | {cellage_only} |",
        f"| Union | {union} |",
        f"| Jaccard similarity (shared / union) | {shared / union:.6f} |",
        f"| GenAge Human genes represented in CellAge | {shared / len(genage):.2%} |",
        f"| CellAge genes represented in GenAge Human | {shared / len(cellage):.2%} |",
        "", "![Horizontal bars for GenAge Human only, shared, and CellAge only gene counts](gene_overlap.svg)", "",
        "## Excluded CellAge record and sensitivity analysis", "",
        f"CellAge reports Gene ID `{row['source_entrez_id']}` with source symbol `{symbol}`. "
        "The Gene ID and source symbol point to different approved HGNC entries. "
        f"The primary comparison excludes this mapping. The original evidence remains in "
        f"`{row['source_archive']}` / `{row['source_member']}`, data record {record_numbers}.",
        "", "| Hypothetical assignment | Candidate from Phase 2 | In confirmed GenAge Human? | Shared genes |",
        "| --- | --- | --- | ---: |",
    ]
    for label, candidate, in_genage, count in scenarios:
        lines.append(f"| {label} | {candidate} | {'Yes' if in_genage else 'No'} | {count} |")
    lines.extend([
        "", f"{effect} These assignments are sensitivity scenarios. The confirmed sets and the gene table "
        "use only the original confirmed mappings.",
        "", "## Methods and traceability", "",
        f"- Verified SHA-256 `{mapping_sha}` for `data/processed/gene_mapping.csv` against the "
        "[Phase 2 audit](gene_identifier_audit.md). The HAGR archive fingerprints are in the "
        "[data inventory](data_inventory.md).",
        "- Matched confirmed, current human genes by Entrez Gene ID and required both approved HGNC ID "
        "and symbol to agree. The three disjoint groups sum to the union.",
        "- The [shared gene table](gene_overlap_genes.csv) lists the original symbols and source ZIP "
        "members. Record numbers are JSON arrays of one-based data record ordinals, excluding the "
        "header and blank lines. Each shared gene appears once. CellAge record counts refer to "
        "experimental evidence associated with that gene.",
        "", "## Scope", "",
        "These counts describe membership in two curated database snapshots. GenAge Human includes "
        "evidence relevant to organismal aging, while CellAge captures gene manipulation evidence for "
        "cellular senescence. Membership reflects curation and available evidence. Causality and "
        "statistical significance are outside this descriptive comparison.", "",
    ])
    return "\n".join(lines)


def render_figure(groups):
    counts = [len(group) for group in groups[:3]]
    labels = ("GenAge Human only", "Shared", "CellAge only")
    scale = max(counts) or 1
    description = ", ".join(f"{label} {count}" for label, count in zip(labels, counts, strict=True))
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 660 198" role="img" aria-labelledby="title desc">',
        '  <title id="title">Confirmed human genes by database membership</title>',
        f'  <desc id="desc">Unique genes. {description}.</desc>',
        '  <rect width="660" height="198" fill="white"/>',
        '  <g fill="#172b3a" font-family="sans-serif" font-size="15">',
        '    <text x="20" y="28" font-size="20" font-weight="bold">Confirmed human genes by database membership</text>',
        '    <path d="M180 44V150H580" fill="none" stroke="#7c8b96"/>',
    ]
    for index, (label, count) in enumerate(zip(labels, counts, strict=True)):
        y = 52 + index * 33
        width = 400 * count / scale
        color = "#116d68" if label == "Shared" else "#557490"
        lines.extend([
            f'    <text x="20" y="{y + 16}">{label}</text>',
            f'    <rect x="180" y="{y}" width="{width:.2f}" height="22" fill="{color}"/>',
            f'    <text x="{188 + width:.2f}" y="{y + 16}">{count}</text>',
        ])
    lines.extend([
        '    <text x="180" y="169" text-anchor="middle">0</text>',
        f'    <text x="580" y="169" text-anchor="middle">{scale}</text>',
        '    <text x="380" y="189" text-anchor="middle">Unique genes</text>',
        '  </g>',
        '</svg>',
        '',
    ])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify all outputs without writing.")
    args = parser.parse_args()
    try:
        contents = MAPPING.read_bytes()
        mapping_sha = verify_mapping(contents, PHASE2_AUDIT.read_text(encoding="utf-8"))
        rows = csv.DictReader(io.StringIO(contents.decode("utf-8"), newline=""), strict=True)
        genage, cellage, excluded = confirmed_sets(rows)
        groups = compare(genage, cellage)
        conflict = sensitivity(excluded, genage, cellage)
        outputs = (
            (REPORT, render_report(genage, cellage, groups, conflict, mapping_sha)),
            (GENES, render_genes(genage, cellage, groups[1])),
            (FIGURE, render_figure(groups)),
        )
        for path, text in outputs:
            if args.check:
                if path.read_bytes() != text.encode("utf-8"):
                    raise ValueError(f"Output differs from regeneration: {path.relative_to(ROOT)}")
            else:
                write_output(path, text)
            print(f"{'Verified' if args.check else 'Wrote'} {path.relative_to(ROOT)}")
    except (OSError, ValueError, KeyError, csv.Error) as error:
        print(f"Overlap analysis failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
