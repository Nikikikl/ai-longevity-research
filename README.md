# AI & Longevity: Exploring Genes Associated with Human Aging

> Which human genes are represented in both the GenAge Human and CellAge databases, and which biological processes are associated with these genes?

This independent computational biology project starts with two curated Human Ageing Genomic Resources (HAGR) exports. GenAge Human assembles candidate genes for human aging, drawing on human and model-organism evidence. CellAge records evidence from gene manipulations in human cells and focuses on cellular senescence. The initial milestone acquires the files and audits their structure and identifiers. The [research plan](docs/research_plan.md) describes the later gene intersection and functional annotation. Machine learning and functional enrichment are outside the initial milestone.

## Official inputs

| Export | Direct download | Archive contents | Release notes |
| --- | --- | --- | --- |
| GenAge Human Genes | [human_genes.zip](https://genomics.senescence.info/genes/human_genes.zip) | Comma-delimited `genage_human.csv` and `release.html` | [Build 21, 2023-08-28](https://genomics.senescence.info/genes/release.html) |
| CellAge gene manipulations | [cellAge.zip](https://genomics.senescence.info/cells/cellAge.zip) | Tab-delimited `cellage3.tsv` and `release.html` | [Build 3, 2023-04-23](https://genomics.senescence.info/cells/release.html) |

The actual archives determine the parsing formats. The [HAGR download index](https://genomics.senescence.info/download.html) describes different delimiters and links to a separate CellAge expression-signature export, which is outside this study. Both URLs point to the current stable downloads. The build labels above were checked against the release notes bundled in the acquired archives. The SHA-256 records identify the exact snapshots even if the URLs later serve different files.

HAGR requires attribution under its published terms and asks users to contact the maintainers before making many queries or retrieving large volumes. Cite de Magalhães et al. (2024) for HAGR and Avelar et al. (2020) for CellAge as listed in the [HAGR terms and citation guidance](https://genomics.senescence.info/legal.html). See the GenAge release notes for the GenAge-specific citation.

## Reproduce the inventory

Run from the repository root with Python 3.11 or newer. The scripts and tests use only the standard library, so no package installation or virtual environment is required.

```sh
python3 -B -m scripts.download_data
python3 -B -m scripts.inspect_data
python3 -B -m unittest discover -s tests -v
```

The downloader saves the original ZIP files under `data/raw/` and records the requested and final URLs, UTC download time, size, and SHA-256 in a JSON file beside each archive. It checks ZIP integrity and verifies existing archives without overwriting them. If only a JSON record is present, the downloader restores the archive only if its bytes match the recorded snapshot. If a download no longer matches, retain the recorded metadata and request the matching export from HAGR or use a retained copy with the recorded checksum.

The inspector verifies the fingerprints, reads the tables directly from the ZIPs, and regenerates [reports/data_inventory.md](reports/data_inventory.md). Keep the JSON provenance records with the report. Git ignores raw ZIPs and generated datasets.

### Manual download

If HTTPS fails in a portable Python installation, point `SSL_CERT_FILE` to a trusted local CA bundle. On this macOS setup, `SSL_CERT_FILE=/etc/ssl/cert.pem` worked. If the downloader remains blocked, open the official download links above in a browser, save the original ZIPs under `data/raw/` using the exact filenames and case, then run:

```sh
python3 -B -m scripts.download_data --register-local
python3 -B -m scripts.inspect_data
```

Manual registration records when the local files were registered. With existing provenance records it checks the archived bytes against the recorded checksums. If both download methods fail, leave the archives absent and record the failure before continuing.

## Reproduce the gene identifier audit

Obtain the two files listed in [data/reference_provenance.json](data/reference_provenance.json) from their official URLs and save them under `data/raw/references/` using the filenames in the manifest. Keep exact copies of the downloaded files. The NCBI URL is updated in place, so reproducing this audit later may require the retained original rather than a fresh download. The script rejects either reference if its SHA-256 or size differs from the manifest.

```sh
python3 -B -m scripts.download_data
python3 -B -m scripts.harmonize_genes
python3 -B -m scripts.harmonize_genes --check
python3 -B -m unittest discover -s tests -v
```

The script writes [reports/gene_identifier_audit.md](reports/gene_identifier_audit.md) and the local `data/processed/gene_mapping.csv`. Only confirmed mappings populate the approved HGNC fields. Each mapping carries the original source identifier, symbol, and record ordinals. The original archives retain the experimental details for all referenced rows. Git ignores the raw references and the generated CSV.

## Reproduce the descriptive gene overlap

Use the existing `data/processed/gene_mapping.csv`. If it is missing, regenerate it with `python3 -B -m scripts.harmonize_genes` using the original pinned local archives and reference snapshots described above. The overlap script checks the mapping SHA-256 against the Phase 2 audit before generating results.

```sh
python3 -B -m scripts.analyze_overlap
python3 -B -m scripts.analyze_overlap --check
python3 -B -m unittest discover -s tests -v
```

The [overlap report](reports/gene_overlap.md) includes the confirmed counts, the [shared gene table](reports/gene_overlap_genes.csv), and a [bar chart](reports/gene_overlap.svg). The shared gene table links each gene to its original GenAge Human and CellAge records. The report keeps the unresolved CellAge mapping separate and tests both hypothetical assignments.

## Reproduce the GO Biological Process annotation

Keep the pinned HGNC snapshot and the Phase 2 mapping available. Save the two official GO files listed in [data/go_provenance.json](data/go_provenance.json) under `data/raw/references/` with their original filenames. The script checks the GO and HGNC file fingerprints and reconstructs the Phase 3 gene table for a byte-for-byte input check.

```sh
python3 -B -m scripts.annotate_go
python3 -B -m scripts.annotate_go --check
python3 -B -m unittest discover -s tests -v
```

The [GO BP report](reports/go_biological_processes.md) documents the release, accession mapping, evidence filters, and coverage. The [annotation table](reports/go_gene_annotations.csv) preserves source line numbers and excluded mapped BP rows. The [term summary](reports/go_process_summary.csv) and [SVG](reports/go_biological_processes.svg) describe direct annotations by unique gene count. Raw GO files remain outside Git.
