"""Validate HAGR Gene IDs and symbols against pinned HGNC and NCBI snapshots."""

import argparse
import csv
import gzip
import io
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from zipfile import BadZipFile

from scripts.download_data import RAW_DIR, ROOT, SOURCES, fingerprint
from scripts.inspect_data import EXPORTS, load_export

PROVENANCE = ROOT / "data" / "reference_provenance.json"
HGNC_FILE = "hgnc_complete_set_2026-10-06.tsv"
NCBI_FILE = "Homo_sapiens.gene_info.gz"
MAPPING = ROOT / "data" / "processed" / "gene_mapping.csv"
REPORT = ROOT / "reports" / "gene_identifier_audit.md"
GENE_ID = re.compile(r"[1-9][0-9]*")
FIELDS = (
    "source", "source_archive", "source_member", "source_entrez_id", "source_symbols", "source_gene_names",
    "source_genage_ids", "source_record_numbers", "evidence_count", "ncbi_status", "ncbi_symbol",
    "ncbi_hgnc_ids", "status", "symbol_relation", "approved_hgnc_id", "approved_symbol",
    "id_candidates", "other_symbol_candidates", "hgnc_previous_symbols", "hgnc_alias_symbols",
)


def split_values(value):
    return tuple(part for part in value.split("|") if part and part != "-")


@dataclass(frozen=True)
class HgncGene:
    hgnc_id: str
    entrez: str
    symbol: str
    previous: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ()


@dataclass(frozen=True)
class NcbiGene:
    symbol: str
    hgnc_ids: tuple[str, ...]


def table_rows(stream, required):
    reader = csv.DictReader(stream, delimiter="\t", quoting=csv.QUOTE_NONE)
    if not set(required).issubset(reader.fieldnames or []):
        raise ValueError(f"Missing reference columns: {', '.join(required)}")
    for row in reader:
        if None in row or any(row[field] is None for field in required):
            raise ValueError(f"Invalid reference row at line {reader.line_num}")
        yield row


def reference_bytes(raw_dir, filename, provenance):
    path = raw_dir / "references" / filename
    content = path.read_bytes()
    if any(provenance[filename][key] != value for key, value in fingerprint(content).items()):
        raise ValueError(f"{filename} does not match the pinned reference fingerprint")
    return content


def read_references(raw_dir, provenance):
    hgnc = []
    contents = reference_bytes(raw_dir, HGNC_FILE, provenance)
    with io.TextIOWrapper(io.BytesIO(contents), encoding="utf-8", newline="") as stream:
        for row in table_rows(stream, ("status", "hgnc_id", "entrez_id", "symbol", "prev_symbol", "alias_symbol")):
            if row["status"] == "Approved":
                hgnc.append(HgncGene(row["hgnc_id"], row["entrez_id"], row["symbol"],
                                     split_values(row["prev_symbol"]), split_values(row["alias_symbol"])))

    ncbi = {}
    contents = reference_bytes(raw_dir, NCBI_FILE, provenance)
    with gzip.open(io.BytesIO(contents), "rt", encoding="utf-8", newline="") as stream:
        for row in table_rows(stream, ("#tax_id", "GeneID", "Symbol", "dbXrefs")):
            if row["#tax_id"] != "9606":
                continue
            gene_id = row["GeneID"]
            if not GENE_ID.fullmatch(gene_id) or gene_id in ncbi:
                raise ValueError(f"Invalid or duplicate human Gene ID in NCBI reference: {gene_id}")
            ids = {xref.removeprefix("HGNC:") for xref in split_values(row["dbXrefs"])
                   if xref.startswith("HGNC:HGNC:")}
            ncbi[gene_id] = NcbiGene(row["Symbol"], tuple(sorted(ids)))
    if not hgnc or not ncbi:
        raise ValueError("Reference has no approved HGNC entries or no NCBI entries for taxon 9606")
    return hgnc, ncbi


class HgncIndex:
    def __init__(self, genes):
        self.by_id = {}
        self.by_entrez = defaultdict(set)
        self.by_symbol = defaultdict(set)
        for gene in genes:
            if gene.hgnc_id in self.by_id:
                raise ValueError(f"Duplicate HGNC ID in reference: {gene.hgnc_id}")
            self.by_id[gene.hgnc_id] = gene
            if gene.entrez:
                self.by_entrez[gene.entrez].add(gene.hgnc_id)
            for symbol in (gene.symbol, *gene.previous, *gene.aliases):
                self.by_symbol[symbol].add(gene.hgnc_id)

    def describe(self, ids):
        return [
            f"{key} {self.by_id[key].symbol} (Gene ID {self.by_id[key].entrez or 'unavailable'})"
            for key in sorted(ids)
        ]


def classify(gene_id, symbols, hg, ncbi):
    numeric = bool(GENE_ID.fullmatch(gene_id))
    current = ncbi.get(gene_id) if numeric else None
    ncbi_ids = set(current.hgnc_ids) if current else set()
    hgnc_ids = hg.by_entrez.get(gene_id, set()) if numeric else set()
    candidates = hgnc_ids | (ncbi_ids & hg.by_id.keys())
    other_ids = set().union(*(hg.by_symbol.get(symbol, set()) for symbol in symbols)) - candidates
    result = dict(
        ncbi_status="current_human" if current else "absent" if numeric else "invalid",
        ncbi_symbol=current.symbol if current else "",
        ncbi_hgnc_ids=sorted(ncbi_ids),
        symbol_relation="",
        approved_hgnc_id="",
        approved_symbol="",
        id_candidates=hg.describe(candidates),
        other_symbol_candidates=hg.describe(other_ids),
        hgnc_previous_symbols=[],
        hgnc_alias_symbols=[],
    )

    if not numeric:
        result["status"] = "invalid_gene_id"
    elif not current:
        result["status"] = "missing_ncbi"
    elif not candidates:
        result["status"] = "missing_hgnc"
    elif len(candidates) > 1:
        result["status"] = "ambiguous_hgnc"
    elif ncbi_ids != hgnc_ids:
        result["status"] = "nonreciprocal_hgnc"
    else:
        gene = hg.by_id[next(iter(candidates))]
        result.update(hgnc_previous_symbols=list(gene.previous), hgnc_alias_symbols=list(gene.aliases))
        matches = []
        for symbol in symbols:
            if symbol == gene.symbol:
                matches.append("approved")
            elif any(hg.by_id[key].symbol == symbol for key in other_ids):
                matches.append("other_approved")
            elif symbol in gene.previous:
                matches.append("previous")
            elif symbol in gene.aliases:
                matches.append("alias")
            else:
                matches.append("unsupported")
        result["symbol_relation"] = "|".join(matches)
        if set(matches) & {"other_approved", "unsupported"}:
            result["status"] = "conflicting_symbol"
        else:
            result.update(status="confirmed", approved_hgnc_id=gene.hgnc_id, approved_symbol=gene.symbol)
    return result


def map_export(export, hg, ncbi, raw_dir):
    _, member = SOURCES[export.archive]
    _, _, (columns, rows, _) = load_export(export, raw_dir)
    id_index, symbol_index = columns.index(export.entrez), columns.index(export.symbol)
    genage = export.archive == "human_genes.zip"
    name_index = columns.index("name" if genage else "Gene name")
    genage_index = columns.index("GenAge ID") if genage else None
    grouped = defaultdict(list)
    for ordinal, row in enumerate(rows, start=1):
        gene_id = row[id_index]
        # Invalid IDs cannot establish that two records describe the same gene.
        group = (gene_id, 0 if GENE_ID.fullmatch(gene_id) else ordinal)
        grouped[group].append((ordinal, row))

    for (gene_id, _), records in grouped.items():
        symbols = sorted({row[symbol_index] for _, row in records})
        yield {
            "source": export.title,
            "source_archive": export.archive,
            "source_member": member,
            "source_entrez_id": gene_id,
            "source_symbols": symbols,
            "source_gene_names": sorted({row[name_index] for _, row in records}),
            "source_genage_ids": sorted({row[genage_index] for _, row in records}) if genage_index is not None else [],
            "source_record_numbers": [ordinal for ordinal, _ in records],
            "evidence_count": len(records),
            **classify(gene_id, symbols, hg, ncbi),
        }


def render_mapping(records):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, FIELDS, lineterminator="\n")
    writer.writeheader()
    for record in records:
        writer.writerow({key: json.dumps(value, ensure_ascii=False) if isinstance(value, list) else value
                         for key, value in record.items()})
    return stream.getvalue()


def render_report(records, provenance, mapping_sha):
    lines = [
        "# Gene identifier audit", "",
        "The unit of validation is an input Gene ID within each HAGR export. Coverage counts source genes.",
        "", "## Coverage", "",
        "| Source | Evidence records | Source genes | Current human Gene IDs | Confirmed HGNC mappings | Unresolved |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for export in EXPORTS:
        subset = [row for row in records if row["source"] == export.title]
        confirmed = sum(row["status"] == "confirmed" for row in subset)
        evidence = sum(row["evidence_count"] for row in subset)
        current = sum(row["ncbi_status"] == "current_human" for row in subset)
        lines.append(f"| {export.title} | {evidence} | {len(subset)} | {current} | "
                     f"{confirmed} ({confirmed / len(subset):.2%}) | {len(subset) - confirmed} |")

    counts = Counter(row["status"] for row in records)
    lines.extend(["", "### Unresolved classifications", ""])
    for status, label in (
        ("invalid_gene_id", "Invalid or blank Gene ID"),
        ("missing_ncbi", "Absent from the current NCBI taxon 9606 snapshot"),
        ("missing_hgnc", "No approved HGNC candidate by ID"),
        ("ambiguous_hgnc", "Multiple approved HGNC candidates by ID"),
        ("nonreciprocal_hgnc", "Nonreciprocal NCBI–HGNC cross-references"),
        ("conflicting_symbol", "Conflicting or unsupported source symbol"),
    ):
        lines.append(f"- {label} — **{counts[status]}**.")
    if counts["missing_ncbi"]:
        lines.append("- Discontinuation status requires targeted NCBI Gene history review for absent IDs.")
    else:
        lines.append("- Discontinued input Gene IDs — **0**. All valid input IDs were found as current "
                     "human records, so a gene history lookup was unnecessary.")

    lines.extend([
        "", "## Symbol differences and unresolved records", "",
        "Both source records for Gene ID 1490 are shown to document the CTGF/CCN2 check.", "",
        "| Source | Gene ID | Source symbol | Source gene name | HGNC candidate from ID | Symbol relationship | Other symbol candidates | Source records |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ])
    for row in records:
        if row["symbol_relation"] == "approved" and row["status"] == "confirmed" and row["source_entrez_id"] != "1490":
            continue
        columns = [
            row["source"], row["source_entrez_id"], ", ".join(row["source_symbols"]),
            ", ".join(row["source_gene_names"]), ", ".join(row["id_candidates"]),
            row["symbol_relation"].replace("|", ", "),
            ", ".join(row["other_symbol_candidates"]), ", ".join(map(str, row["source_record_numbers"])),
        ]
        lines.append("| " + " | ".join(value.replace("|", "\\|") or "—" for value in columns) + " |")

    lines.extend([
        "", "## Validation and evidence traceability", "",
        "- Accept positive ASCII decimal Gene IDs without leading zeros. Require an exact, current match "
        "in NCBI Gene with taxon 9606.",
        "- Require a unique reciprocal cross-reference between NCBI Gene and an approved HGNC entry. "
        "A source symbol must match the approved symbol, a previous symbol, or an alias for that entry. "
        "A symbol approved for another entry takes precedence as a conflict. Symbol-only matches are "
        "candidate evidence and cannot establish a mapping.",
        "- Keep every experimental record in its original HAGR archive. The CSV lists one row per "
        "source and valid input Gene ID. Its `source_record_numbers` array lists one-based parsed data "
        "record ordinals within the indicated ZIP member, after excluding the header and blank lines. "
        "All list fields are JSON arrays embedded in the CSV.",
        "- Only confirmed rows populate `approved_hgnc_id` and `approved_symbol`. Use the confirmed "
        "subset for a provisional overlap and carry unresolved records as explicit exclusions.",
        "", "## Reference provenance", "",
        "See the [README](../README.md#official-inputs) for HAGR builds and the "
        "[data inventory](data_inventory.md) for the source archive fingerprints. "
        "The [reference manifest](../data/reference_provenance.json) pins the original reference bytes.",
        "", "| Reference | Version | Retrieved (UTC) | Bytes | SHA-256 |",
        "| --- | --- | --- | ---: | --- |",
    ])
    for filename, meta in provenance.items():
        lines.append(f"| [{filename}]({meta['source_url']}) | {meta['version']} | {meta['retrieved_at_utc']} | "
                     f"{meta['size_bytes']:,} | `{meta['sha256']}` |")
    lines.extend([
        "", "The HGNC complete set covers approved entries and records previous symbols and aliases where curated. "
        "The NCBI download is a rolling species file, and only taxon 9606 rows are used. HTTP Last-Modified "
        "and SHA-256 identify the captured NCBI file. The same URL may return a later export.",
        "See the [HGNC archive documentation](https://www.genenames.org/download/archive/) and "
        "[NCBI Gene FTP documentation](https://www.ncbi.nlm.nih.gov/datasets/docs/v2/data-processing/gene-processing/geneftp/).",
        "", f"Generated `data/processed/gene_mapping.csv` SHA-256 — `{mapping_sha}`.", "",
    ])
    return "\n".join(lines)


def write_output(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(dir=path.parent, suffix=".tmp", delete=False) as staged:
        temp = Path(staged.name)
        try:
            staged.write(text.encode("utf-8"))
            staged.close()
            temp.replace(path)
        finally:
            temp.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify existing outputs without writing.")
    args = parser.parse_args()
    try:
        provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        genes, ncbi = read_references(RAW_DIR, provenance)
        hg = HgncIndex(genes)
        records = [row for export in EXPORTS for row in map_export(export, hg, ncbi, RAW_DIR)]
        mapping = render_mapping(records)
        report = render_report(records, provenance, fingerprint(mapping.encode("utf-8"))["sha256"])
        for path, text in ((MAPPING, mapping), (REPORT, report)):
            if args.check:
                if path.read_bytes() != text.encode("utf-8"):
                    raise ValueError(f"Output differs from regeneration: {path.relative_to(ROOT)}")
            else:
                write_output(path, text)
            print(f"{'Verified' if args.check else 'Wrote'} {path.relative_to(ROOT)}")
    except (OSError, ValueError, KeyError, EOFError, csv.Error, BadZipFile) as error:
        print(f"Harmonization failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
