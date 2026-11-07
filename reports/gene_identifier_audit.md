# Gene identifier audit

The unit of validation is an input Gene ID within each HAGR export. Coverage counts source genes.

## Coverage

| Source | Evidence records | Source genes | Current human Gene IDs | Confirmed HGNC mappings | Unresolved |
| --- | ---: | ---: | ---: | ---: | ---: |
| GenAge Human | 307 | 307 | 307 | 307 (100.00%) | 0 |
| CellAge gene manipulations | 949 | 866 | 866 | 865 (99.88%) | 1 |

### Unresolved classifications

- Invalid or blank Gene ID — **0**.
- Absent from the current NCBI taxon 9606 snapshot — **0**.
- No approved HGNC candidate by ID — **0**.
- Multiple approved HGNC candidates by ID — **0**.
- Nonreciprocal NCBI–HGNC cross-references — **0**.
- Conflicting or unsupported source symbol — **1**.
- Discontinued input Gene IDs — **0**. All valid input IDs were found as current human records, so a gene history lookup was unnecessary.

## Symbol differences and unresolved records

Both source records for Gene ID 1490 are shown to document the CTGF/CCN2 check.

| Source | Gene ID | Source symbol | Source gene name | HGNC candidate from ID | Symbol relationship | Other symbol candidates | Source records |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GenAge Human | 539 | ATP5O | ATP synthase, H+ transporting, mitochondrial F1 complex, O subunit | HGNC:850 ATP5PO (Gene ID 539) | previous | — | 145 |
| GenAge Human | 1490 | CTGF | connective tissue growth factor | HGNC:2500 CCN2 (Gene ID 1490) | previous | — | 205 |
| GenAge Human | 3014 | H2AFX | H2A histone family, member X | HGNC:4739 H2AX (Gene ID 3014) | previous | — | 211 |
| GenAge Human | 406 | ARNTL | aryl hydrocarbon receptor nuclear translocator-like | HGNC:701 BMAL1 (Gene ID 406) | previous | — | 250 |
| CellAge gene manipulations | 1490 | CCN2 | cellular communication network factor 2 | HGNC:2500 CCN2 (Gene ID 1490) | approved | — | 120 |
| CellAge gene manipulations | 100529261 | FNTB | CHURC1-FNTB readthrough | HGNC:42960 CHURC1-FNTB (Gene ID 100529261) | other_approved | HGNC:3785 FNTB (Gene ID 2342) | 290 |
| CellAge gene manipulations | 5245 | PHB | prohibitin | HGNC:8912 PHB1 (Gene ID 5245) | previous | — | 631 |

## Validation and evidence traceability

- Accept positive ASCII decimal Gene IDs without leading zeros. Require an exact, current match in NCBI Gene with taxon 9606.
- Require a unique reciprocal cross-reference between NCBI Gene and an approved HGNC entry. A source symbol must match the approved symbol, a previous symbol, or an alias for that entry. A symbol approved for another entry takes precedence as a conflict. Symbol-only matches are candidate evidence and cannot establish a mapping.
- Keep every experimental record in its original HAGR archive. The CSV lists one row per source and valid input Gene ID. Its `source_record_numbers` array lists one-based parsed data record ordinals within the indicated ZIP member, after excluding the header and blank lines. All list fields are JSON arrays embedded in the CSV.
- Only confirmed rows populate `approved_hgnc_id` and `approved_symbol`. Use the confirmed subset for a provisional overlap and carry unresolved records as explicit exclusions.

## Reference provenance

See the [README](../README.md#official-inputs) for HAGR builds and the [data inventory](data_inventory.md) for the source archive fingerprints. The [reference manifest](../data/reference_provenance.json) pins the original reference bytes.

| Reference | Version | Retrieved (UTC) | Bytes | SHA-256 |
| --- | --- | --- | ---: | --- |
| [hgnc_complete_set_2026-10-06.tsv](https://storage.googleapis.com/public-download-files/hgnc/archive/archive/quarterly/tsv/hgnc_complete_set_2026-10-06.tsv) | Quarterly complete set, 2026-10-06 | 2026-11-07T23:36:05Z | 16,973,125 | `8bf6f686e640dbc864a346484626953621b0500d900d26cd085a35c2782d725d` |
| [Homo_sapiens.gene_info.gz](https://ftp.ncbi.nlm.nih.gov/gene/DATA/GENE_INFO/Mammalia/Homo_sapiens.gene_info.gz) | NCBI Gene daily export, HTTP Last-Modified 2026-11-07T08:31:40Z | 2026-11-07T23:36:07Z | 5,200,612 | `69d0f9f7dcbec4a39596ea3944fb1544ffcef9a872c6cf70a4882327d9db4e6e` |

The HGNC complete set covers approved entries and records previous symbols and aliases where curated. The NCBI download is a rolling species file, and only taxon 9606 rows are used. HTTP Last-Modified and SHA-256 identify the captured NCBI file. The same URL may return a later export.
See the [HGNC archive documentation](https://www.genenames.org/download/archive/) and [NCBI Gene FTP documentation](https://www.ncbi.nlm.nih.gov/datasets/docs/v2/data-processing/gene-processing/geneftp/).

Generated `data/processed/gene_mapping.csv` SHA-256 — `0a5691998d0d592774e96bb8f82e6654cae4a58789c6e76506fc348bb24dfcca`.
