"""Inspect the two official HAGR exports without modifying or joining them."""

import csv
import sys
from collections import defaultdict
from dataclasses import dataclass
from io import TextIOWrapper
from pathlib import Path
from tempfile import NamedTemporaryFile
from zipfile import BadZipFile, ZipFile

from scripts.download_data import RAW_DIR, ROOT, SOURCES, verify_archive

REPORT = ROOT / "reports" / "data_inventory.md"


@dataclass(frozen=True)
class Export:
    title: str
    archive: str
    delimiter: str
    entrez: str
    symbol: str
    identifiers: tuple[str, ...]


EXPORTS = (
    Export("GenAge Human", "human_genes.zip", ",", "entrez gene id",
           "symbol", ("entrez gene id", "symbol", "GenAge ID", "uniprot")),
    Export("CellAge gene manipulations", "cellAge.zip", "\t", "Entrez ID",
           "Gene symbol", ("Entrez ID", "Gene symbol")),
)


def read_table(stream, delimiter):
    reader = csv.reader(stream, delimiter=delimiter, strict=True)
    columns = next(reader, [])
    if not columns or len(columns) != len(set(columns)) or any(not name.strip() for name in columns):
        raise ValueError("Missing, blank, or duplicate column header.")
    rows = []
    blank_lines = 0
    for row in reader:
        if not row:
            blank_lines += 1
            continue
        if len(row) != len(columns):
            raise ValueError(f"Line {reader.line_num}: expected {len(columns)} fields, found {len(row)}.")
        rows.append(tuple(row))
    return columns, rows, blank_lines


def identifier_maps(entrez_values, symbols):
    by_entrez, by_symbol = defaultdict(set), defaultdict(set)
    for entrez, symbol in zip(entrez_values, symbols, strict=True):
        if entrez.strip() and symbol.strip():
            by_entrez[entrez].add(symbol)
            by_symbol[symbol].add(entrez)
    return by_entrez, by_symbol


def inspect(export, raw_dir=RAW_DIR):
    path = raw_dir / export.archive
    url, member = SOURCES[export.archive]
    metadata = verify_archive(path, url)
    with ZipFile(path) as archive:
        members = archive.namelist()
        with TextIOWrapper(archive.open(member), encoding="utf-8", newline="") as stream:
            columns, rows, blank_lines = read_table(stream, export.delimiter)
    values = {name: [row[index] for row in rows] for index, name in enumerate(columns)}
    if missing := set(export.identifiers) - values.keys():
        raise ValueError(f"Expected identifier columns missing in {member}: {sorted(missing)}")

    table_format = "CSV, comma-delimited" if export.delimiter == "," else "TSV, tab-delimited"
    lines = [
        f"## {export.title}", "",
        f"- Source archive: [`{export.archive}`]({metadata['source_url']}) (ZIP, {metadata['size_bytes']:,} bytes).",
        f"- SHA-256: `{metadata['sha256']}`.",
        f"- ZIP members: {', '.join(f'`{name}`' for name in members)}.",
        f"- Inspected table: `{member}` ({table_format}, read as UTF-8).",
        f"- Data records: **{len(rows):,}**. Blank lines skipped: **{blank_lines:,}**.",
        f"- Exact duplicate records beyond the first copy: **{len(rows) - len(set(rows)):,}**.",
        "", "| Column | Missing cells |", "| --- | ---: |",
    ]
    for name, cells in values.items():
        lines.append(f"| `{name}` | {sum(not cell.strip() for cell in cells):,} |")

    lines.extend(["", "| Candidate identifier | Distinct nonblank values | Rows beyond first use |",
                  "| --- | ---: | ---: |"])
    for name in export.identifiers:
        nonblank = [value for value in values[name] if value.strip()]
        lines.append(f"| `{name}` | {len(set(nonblank)):,} | {len(nonblank) - len(set(nonblank)):,} |")

    entrez_values, symbols = values[export.entrez], values[export.symbol]
    by_entrez, by_symbol = identifier_maps(entrez_values, symbols)
    invalid_entrez = sum(
        bool(value.strip()) and not (value.isascii() and value.isdecimal() and int(value) > 0)
        for value in entrez_values
    )
    symbol_whitespace = sum(value != value.strip() for value in symbols)
    lines.extend([
        "",
        f"- Nonblank Entrez values outside positive ASCII integers: **{invalid_entrez:,}**.",
        f"- Symbols with leading or trailing whitespace: **{symbol_whitespace:,}**.",
        f"- Entrez IDs with multiple symbols: **{sum(len(v) > 1 for v in by_entrez.values()):,}**.",
        f"- Symbols with multiple Entrez IDs: **{sum(len(v) > 1 for v in by_symbol.values()):,}**.",
    ])
    return lines, by_entrez, by_symbol


def render_inventory(raw_dir=RAW_DIR):
    genage, genage_entrez, genage_symbols = inspect(EXPORTS[0], raw_dir)
    cellage, cellage_entrez, cellage_symbols = inspect(EXPORTS[1], raw_dir)
    id_disagreements = sum(genage_entrez[key] != cellage_entrez[key]
                           for key in genage_entrez.keys() & cellage_entrez.keys())
    symbol_disagreements = sum(genage_symbols[key] != cellage_symbols[key]
                               for key in genage_symbols.keys() & cellage_symbols.keys())
    lines = [
        "# HAGR data inventory", "",
        "Counts describe the archived exports identified by SHA-256. Missing cells are empty or whitespace-only. "
        "Values such as `Unclear` are retained as reported categories. Exact duplicates compare all parsed "
        "fields, with no normalization.", "",
        *genage, "", *cellage, "", "## Dataset differences and identifier checks", "",
        "- GenAge Human curates candidate genes for human aging and includes evidence from model organisms. "
        "Its `why` field records the basis for inclusion.",
        "- CellAge curates gene manipulation evidence for cellular senescence in human cells. Its table "
        "includes cancer-cell status, senescence type, effect, and reference. Repeated gene identifiers "
        "can represent distinct evidence records.",
        "- Entrez Gene IDs are the candidate shared namespace. `GenAge ID` is a source-specific identifier "
        "and `uniprot` is a protein cross-reference.",
        f"- Exact Entrez IDs present in both exports with different associated symbol sets: **{id_disagreements:,}**.",
        f"- Exact symbols present in both exports with different associated Entrez ID sets: **{symbol_disagreements:,}**.",
        "", "These checks compare literal values. Validate both exports against a versioned human gene "
        "authority before constructing the gene intersection, and review retired IDs, aliases, and conflicts.",
    ]
    return "\n".join(lines) + "\n"


def main():
    try:
        report = render_inventory()
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(mode="w", encoding="utf-8", dir=REPORT.parent,
                                suffix=".tmp", delete=False) as staged:
            staged_path = Path(staged.name)
            try:
                staged.write(report)
                staged.flush()
                staged_path.replace(REPORT)
            finally:
                staged_path.unlink(missing_ok=True)
    except (OSError, ValueError, KeyError, BadZipFile, csv.Error) as error:
        print(f"Inspection failed: {error}", file=sys.stderr)
        return 1
    print(f"Wrote {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
