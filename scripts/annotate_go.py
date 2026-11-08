"""Describe direct GO Biological Process annotations for the confirmed overlap."""

import argparse
import csv
import gzip
import hashlib
import io
import json
import sys
from collections import Counter, defaultdict
from html import escape
from textwrap import wrap

from scripts import analyze_overlap as overlap
from scripts.download_data import RAW_DIR, ROOT
from scripts.harmonize_genes import HGNC_FILE, MAPPING, PROVENANCE, reference_bytes, split_values, write_output

MANIFEST = ROOT / "data" / "go_provenance.json"
GAF = "HUMAN-uniprot.gaf.gz"
OBO = "go-basic.obo"
BP_ROOT = "GO:0008150"
TOP_COUNT = 12
REPORTS = ROOT / "reports"
ANNOTATION_FIELDS = (
    "entrez_gene_id", "hgnc_id", "approved_symbol", "annotation_db", "db_object_id",
    "gaf_symbol", "gaf_go_id", "go_id", "go_term", "evidence_code", "evidence_category",
    "reference", "relation", "with_from", "taxon", "annotation_date", "assigned_by",
    "annotation_extension", "gene_product_form_id", "gaf_line", "go_release", "status",
)
SUMMARY_FIELDS = ("go_id", "go_term", "unique_genes", "unique_genes_excluding_iea")
EVIDENCE_CATEGORIES = {
    code: category
    for category, codes in (
        ("Experimental", "EXP IDA IPI IMP IGI IEP HTP HDA HMP HGI HEP"),
        ("Phylogenetic", "IBA IBD IKR IRD"),
        ("Computational", "ISS ISO ISA ISM IGC RCA"),
        ("Author statement", "TAS NAS"),
        ("Curatorial statement", "IC ND"),
        ("Electronic", "IEA"),
    )
    for code in codes.split()
}


def verified_overlap():
    contents = MAPPING.read_bytes()
    overlap.verify_mapping(contents, overlap.PHASE2_AUDIT.read_text(encoding="utf-8"))
    rows = csv.DictReader(io.StringIO(contents.decode("utf-8"), newline=""), strict=True)
    genage, cellage, _ = overlap.confirmed_sets(rows)
    shared = overlap.compare(genage, cellage)[1]
    expected = overlap.render_genes(genage, cellage, shared).encode("utf-8")
    actual = overlap.GENES.read_bytes()
    if actual != expected:
        raise ValueError("The Phase 3 shared-gene table differs from the pinned Phase 2 reconstruction.")
    reader = csv.DictReader(io.StringIO(actual.decode("utf-8"), newline=""), strict=True)
    return {row["approved_hgnc_id"]: row for row in reader}, hashlib.sha256(actual).hexdigest()


def map_accessions(genes, stream):
    """Check overlap identities and reject accessions shared by approved HGNC entries."""
    owners = defaultdict(set)
    candidates = {}
    for row in csv.DictReader(stream, delimiter="\t", strict=True):
        if row["status"] != "Approved":
            continue
        hgnc_id = row["hgnc_id"]
        accessions = set(split_values(row["uniprot_ids"]))
        for accession in accessions:
            if not (accession.isascii() and accession.isalnum()):
                raise ValueError(f"Invalid HGNC UniProtKB accession for {hgnc_id}: {accession}.")
            owners[accession].add(hgnc_id)
        if hgnc_id in genes:
            gene = genes[hgnc_id]
            if (hgnc_id in candidates or row["entrez_id"] != gene["entrez_gene_id"]
                    or row["symbol"] != gene["approved_symbol"]):
                raise ValueError(f"Pinned HGNC identity disagrees with the overlap for {hgnc_id}.")
            candidates[hgnc_id] = accessions
    if missing := genes.keys() - candidates.keys():
        raise ValueError(f"Approved HGNC entries missing from pinned snapshot: {sorted(missing)}.")

    lookup, ambiguous = {}, {}
    for hgnc_id, accessions in candidates.items():
        for accession in sorted(accessions):
            if len(owners[accession]) == 1:
                lookup[accession] = hgnc_id
            else:
                ambiguous[accession] = sorted(owners[accession])
    return lookup, candidates, ambiguous


def read_ontology(stream):
    headers, terms = {}, {}
    stanza = ""
    fields = defaultdict(list)
    for line in stream:
        line = line.rstrip("\r\n")
        if not line or line.startswith("!"):
            continue
        if line.startswith("["):
            add_term(stanza, fields, terms)
            stanza, fields = line, defaultdict(list)
        else:
            key, separator, value = line.partition(": ")
            if separator and stanza == "[Term]":
                fields[key].append(value)
            elif separator and not stanza:
                headers[key] = value
    add_term(stanza, fields, terms)
    return headers, terms


def add_term(stanza, fields, terms):
    if (stanza != "[Term]" or fields["namespace"] != ["biological_process"]
            or fields["is_obsolete"] == ["true"]):
        return
    go_id, name = fields["id"][0], fields["name"][0]
    for key in (go_id, *fields["alt_id"]):
        if key in terms:
            raise ValueError(f"Duplicate Biological Process ontology identifier: {key}.")
        terms[key] = go_id, name


def gaf_rows(stream, headers):
    for line_number, line in enumerate(stream, 1):
        if line.startswith("!"):
            key, separator, value = line[1:].strip().partition(":")
            if separator:
                headers[key] = value.strip()
            continue
        fields = line.rstrip("\r\n").split("\t")
        if len(fields) != 17:
            raise ValueError(f"GAF line {line_number} has {len(fields)} fields, expected 17.")
        yield line_number, fields
    if headers.get("gaf-version") != "2.2":
        raise ValueError("Expected a GAF 2.2 header.")


def collect_annotations(rows, lookup, genes, terms, release):
    annotations = []
    for line, fields in rows:
        db, accession, gaf_symbol, relation, source_go, reference, code, with_from, aspect = fields[:9]
        taxon, date, assigned_by, extension, form = fields[12:]
        if (db != "UniProtKB" or accession not in lookup or aspect != "P"
                or taxon.split("|", 1)[0] != "taxon:9606"):
            continue
        gene = genes[lookup[accession]]
        go_id, name = terms.get(source_go, ("", ""))
        if "NOT" in relation.split("|"):
            status = "negated"
        elif code == "ND":
            status = "no_data"
        elif go_id == BP_ROOT or source_go == BP_ROOT:
            status = "root"
        elif not go_id:
            status = "unresolved_term"
        else:
            status = "positive"
        if code not in EVIDENCE_CATEGORIES:
            raise ValueError(f"Unclassified GO evidence code {code} at GAF line {line}.")
        annotations.append(dict(zip(ANNOTATION_FIELDS, (
            gene["entrez_gene_id"], lookup[accession], gene["approved_symbol"], db, accession,
            gaf_symbol, source_go, go_id, name, code, EVIDENCE_CATEGORIES[code], reference,
            relation, with_from, taxon, date, assigned_by, extension, form, line, release, status,
        ), strict=True)))
    return sorted(annotations, key=lambda row: (int(row["entrez_gene_id"]), row["gaf_line"]))


def summarize(annotations):
    by_term, non_iea = defaultdict(set), defaultdict(set)
    covered, covered_non_iea = set(), set()
    codes = Counter()
    names = {}
    for row in annotations:
        if row["status"] != "positive":
            continue
        go_id, gene = row["go_id"], row["hgnc_id"]
        names[go_id] = row["go_term"]
        by_term[go_id].add(gene)
        covered.add(gene)
        codes[row["evidence_code"]] += 1
        if row["evidence_code"] != "IEA":
            non_iea[go_id].add(gene)
            covered_non_iea.add(gene)
    summary = [
        dict(go_id=go_id, go_term=names[go_id], unique_genes=len(members),
             unique_genes_excluding_iea=len(non_iea.get(go_id, ())))
        for go_id, members in by_term.items()
    ]
    summary.sort(key=lambda row: (-row["unique_genes"], row["go_id"]))
    return summary, covered, covered_non_iea, codes


def render_csv(fields, rows):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def render_report(genes, mapping, annotations, stats, manifest, overlap_sha):
    lookup, candidates, ambiguous = mapping
    summary, covered, covered_non_iea, codes = stats
    total = len(genes)
    mapped = set(lookup.values())
    categories = Counter()
    for code, count in codes.items():
        categories[EVIDENCE_CATEGORIES[code]] += count
    statuses = Counter(row["status"] for row in annotations)
    accessions_by_gene = defaultdict(list)
    for accession, hgnc_id in sorted(lookup.items()):
        accessions_by_gene[hgnc_id].append(accession)
    multi = [
        f"{genes[key]['approved_symbol']} ({', '.join(accessions)})"
        for key, accessions in sorted(accessions_by_gene.items()) if len(accessions) > 1
    ]
    ambiguous_labels = [f"{accession} ({', '.join(ids)})" for accession, ids in sorted(ambiguous.items())]

    def symbols(ids):
        return ", ".join(genes[key]["approved_symbol"] for key in sorted(ids)) or "None"

    lines = [
        "# Gene Ontology Biological Process annotations", "",
        f"Direct positive BP annotations were found for **{len(covered)} of {total} shared human genes**.", "",
        "## Identifier mapping and coverage", "",
        f"- {len(mapped)} of {total} genes ({len(mapped) / total:.2%}) had at least one unambiguous HGNC "
        f"UniProtKB cross-reference ({len(lookup)} distinct accessions).",
        f"- Genes with no HGNC UniProtKB cross-reference ({sum(not ids for ids in candidates.values())}): "
        f"{symbols(key for key, ids in candidates.items() if not ids)}.",
        f"- Ambiguous accessions excluded ({len(ambiguous)}): "
        f"{', '.join(ambiguous_labels) or 'None'}.",
        f"- Genes without any unambiguous accession ({total - len(mapped)}): {symbols(genes.keys() - mapped)}.",
        f"- Genes with multiple unambiguous accessions: {', '.join(multi) or 'None'}.",
        "", "| Positive BP annotation policy | Genes covered | Genes without coverage | Unique BP terms | GAF rows |",
        "| --- | ---: | ---: | ---: | ---: |",
        f"| All eligible codes | {len(covered)} ({len(covered) / total:.2%}) | {total - len(covered)} "
        f"| {len(summary)} | {codes.total()} |",
        f"| Exclude IEA | {len(covered_non_iea)} ({len(covered_non_iea) / total:.2%}) "
        f"| {total - len(covered_non_iea)} | {sum(row['unique_genes_excluding_iea'] > 0 for row in summary)} "
        f"| {codes.total() - codes['IEA']} |",
        "",
        f"Genes without eligible positive BP coverage: {symbols(genes.keys() - covered)}. "
        f"After excluding IEA: {symbols(genes.keys() - covered_non_iea)}.",
        "", "## Most frequently annotated direct terms", "",
        "| GO ID | Biological process | Unique genes | Unique genes excluding IEA |",
        "| --- | --- | ---: | ---: |",
    ]
    for row in summary[:TOP_COUNT]:
        name = row["go_term"].replace("|", "\\|")
        lines.append(f"| {row['go_id']} | {name} | {row['unique_genes']} | {row['unique_genes_excluding_iea']} |")
    lines.extend([
        "", "![Top directly annotated GO BP terms by number of unique genes](go_biological_processes.svg)",
        "", "## Evidence and filters", "",
        "The distribution counts eligible positive GAF rows. Multiple rows can support the same gene–term "
        "pair and can cite the same study.", "",
        "| Evidence category | Positive rows | Share | Evidence codes and row counts |",
        "| --- | ---: | ---: | --- |",
    ])
    for category, count in sorted(categories.items()):
        breakdown = ", ".join(f"{code} {n}" for code, n in sorted(codes.items())
                              if EVIDENCE_CATEGORIES[code] == category)
        lines.append(f"| {category} | {count} | {count / codes.total():.2%} | {breakdown} |")
    lines.extend([
        "",
        f"The annotation CSV also retains excluded rows: {statuses['negated']} with NOT, "
        f"{statuses['no_data']} with ND, {statuses['root']} root annotations, and "
        f"{statuses['unresolved_term']} without a resolvable active BP term. These status counts are mutually exclusive.",
        "",
        "- Joined exact GAF UniProtKB object accessions to the pinned complete-set HGNC cross-references. "
        "Validated each HGNC entry against the overlap Entrez ID and approved symbol. Checked accession ownership "
        "against all approved HGNC entries. Gene symbols and isoform suffixes were never used to create mappings. "
        "The RNAcentral and ComplexPortal namespaces are outside this protein mapping.",
        "- Kept GAF aspect P and primary taxon 9606. Counted direct positive annotations to active BP terms. "
        "Recognized alternate GO IDs using the same ontology, excluded the BP root GO:0008150 and ND from coverage, "
        "and kept NOT as a separate status. No ancestor propagation was applied.",
        "- Ranked terms by distinct genes, with ties sorted by GO ID. Multiple proteins or evidence rows for a "
        "gene count once per term. Non-IEA includes phylogenetic, computational, author, and curator evidence as "
        "well as experimental evidence. See the [GO evidence guide](https://geneontology.org/docs/guide-go-evidence-codes/).",
        "", "## Provenance and outputs", "",
        f"Gene Ontology Consortium data from [archive release {manifest['release']}](https://release.geneontology.org/), "
        "© Gene Ontology Consortium, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). "
        "This project filtered and joined the source annotations and aggregated them into derived tables and a figure. "
        "GO data are provided as-is under the [GO citation, license and warranty policy](https://geneontology.org/docs/go-citation-policy/). "
        "For publication cite [Ashburner et al.](https://doi.org/10.1038/75556) and "
        "[The Gene Ontology Consortium](https://doi.org/10.1093/nar/gkaf1292).",
        "", "| Input | Version metadata | Retrieved (UTC) | Bytes | SHA-256 |",
        "| --- | --- | --- | ---: | --- |",
    ])
    for filename, meta in manifest["files"].items():
        version = "<br>".join(f"{key} `{value}`" for key, value in meta["headers"].items())
        lines.append(f"| [{filename}]({meta['source_url']}) | {version} | {meta['retrieved_at_utc']} "
                     f"| {meta['size_bytes']:,} | `{meta['sha256']}` |")
    lines.extend([
        "",
        f"The [Phase 3 shared-gene table](gene_overlap_genes.csv) has SHA-256 `{overlap_sha}`. "
        "HGNC mapping provenance is in the [Phase 2 manifest](../data/reference_provenance.json). "
        "The [GO manifest](../data/go_provenance.json) pins the exact source bytes and file metadata.",
        "",
        "The [annotation CSV](go_gene_annotations.csv) preserves the original GO identifier, UniProtKB "
        "accession, reference, evidence, relation, date, and assigned-by source. Its `gaf_line` is the one-based "
        "line number in the decompressed GAF, including headers. The [term summary](go_process_summary.csv) "
        "gives unique-gene counts for both evidence policies.",
        "", "## Interpretation", "",
        "Coverage depends on the pinned annotation release, the HGNC–UniProtKB cross-references, and the "
        "curation available for each gene and context. Publication and annotation bias favor extensively studied "
        "genes and processes. These ranks describe annotation frequency within the selected genes. Enrichment "
        "would require a justified reference universe and an explicit test. Annotation evidence describes "
        "gene-product associations with processes. Effects of interventions on human lifespan remain a separate "
        "empirical question.", "",
    ])
    return "\n".join(lines)


def render_figure(summary, covered, total):
    top = summary[:TOP_COUNT]
    maximum = max((row["unique_genes"] for row in top), default=1)
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title desc" '
        f'viewBox="0 0 960 {88 + 38 * len(top)}">',
        '  <title id="title">Top direct GO Biological Process annotations</title>',
        f'  <desc id="desc">{covered} of {total} shared genes covered. Bars count unique genes.</desc>',
        '  <rect width="100%" height="100%" fill="white"/>',
        '  <g fill="#172b3a" font-family="sans-serif">',
        '    <text x="20" y="29" font-size="21" font-weight="bold">Top direct GO Biological Process annotations</text>',
        f'    <text x="20" y="53" font-size="14">{covered} of {total} shared genes covered · bars show unique genes · IEA included</text>',
    ]
    for index, row in enumerate(top):
        y = 65 + index * 38
        width = 350 * row["unique_genes"] / maximum
        label = f"{row['go_term']} ({row['go_id']})"
        for line_index, label_line in enumerate(wrap(label, 69, break_long_words=False)):
            lines.append(f'    <text x="20" y="{y + 13 + line_index * 14}" font-size="13">{escape(label_line)}</text>')
        lines.extend([
            f'    <rect x="520" y="{y}" width="{width:.2f}" height="20" fill="#116d68"/>',
            f'    <text x="{529 + width:.2f}" y="{y + 15}" font-size="14">{row["unique_genes"]}</text>',
        ])
    return "\n".join([*lines, "  </g>", "</svg>", ""])


def run():
    genes, overlap_sha = verified_overlap()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    hgnc_meta = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    hgnc = reference_bytes(RAW_DIR, HGNC_FILE, hgnc_meta)
    with io.TextIOWrapper(io.BytesIO(hgnc), encoding="utf-8", newline="") as stream:
        mapping = map_accessions(genes, stream)

    files = manifest["files"]
    obo = reference_bytes(RAW_DIR, OBO, files)
    with io.TextIOWrapper(io.BytesIO(obo), encoding="utf-8", newline="") as stream:
        obo_headers, terms = read_ontology(stream)
    gaf = reference_bytes(RAW_DIR, GAF, files)
    gaf_headers = {}
    with gzip.open(io.BytesIO(gaf), "rt", encoding="utf-8", newline="") as stream:
        annotations = collect_annotations(gaf_rows(stream, gaf_headers), mapping[0], genes, terms, manifest["release"])
    if (gaf_headers != files[GAF]["headers"]
            or any(obo_headers.get(key) != value for key, value in files[OBO]["headers"].items())
            or f"/{obo_headers['data-version']}/" not in gaf_headers["go-version"]):
        raise ValueError("GAF and ontology metadata differ from the matched pinned GO release.")

    stats = summarize(annotations)
    summary, covered, _, _ = stats
    return (
        ("go_biological_processes.md", render_report(genes, mapping, annotations, stats, manifest, overlap_sha)),
        ("go_gene_annotations.csv", render_csv(ANNOTATION_FIELDS, annotations)),
        ("go_process_summary.csv", render_csv(SUMMARY_FIELDS, summary)),
        ("go_biological_processes.svg", render_figure(summary, len(covered), len(genes))),
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify all outputs without writing.")
    args = parser.parse_args()
    try:
        for name, text in run():
            path = REPORTS / name
            if args.check:
                if path.read_bytes() != text.encode("utf-8"):
                    raise ValueError(f"Output differs from regeneration: {name}")
            else:
                write_output(path, text)
            print(f"{'Verified' if args.check else 'Wrote'} {path.relative_to(ROOT)}")
    except (OSError, ValueError, KeyError, EOFError, csv.Error) as error:
        print(f"GO annotation failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
