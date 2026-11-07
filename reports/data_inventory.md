# HAGR data inventory

Counts describe the archived exports identified by SHA-256. Missing cells are empty or whitespace-only. Values such as `Unclear` are retained as reported categories. Exact duplicates compare all parsed fields, with no normalization.

## GenAge Human

- Source archive: [`human_genes.zip`](https://genomics.senescence.info/genes/human_genes.zip) (ZIP, 9,465 bytes).
- SHA-256: `cd4b1d63c9a3fb9574da8453487ad528622b2ae70b6afcde0c8b372b08c52c7b`.
- ZIP members: `genage_human.csv`, `release.html`.
- Inspected table: `genage_human.csv` (CSV, comma-delimited, read as UTF-8).
- Data records: **307**. Blank lines skipped: **0**.
- Exact duplicate records beyond the first copy: **0**.

| Column | Missing cells |
| --- | ---: |
| `GenAge ID` | 0 |
| `symbol` | 0 |
| `name` | 0 |
| `entrez gene id` | 0 |
| `uniprot` | 1 |
| `why` | 0 |

| Candidate identifier | Distinct nonblank values | Rows beyond first use |
| --- | ---: | ---: |
| `entrez gene id` | 307 | 0 |
| `symbol` | 307 | 0 |
| `GenAge ID` | 307 | 0 |
| `uniprot` | 306 | 0 |

- Nonblank Entrez values outside positive ASCII integers: **0**.
- Symbols with leading or trailing whitespace: **0**.
- Entrez IDs with multiple symbols: **0**.
- Symbols with multiple Entrez IDs: **0**.

## CellAge gene manipulations

- Source archive: [`cellAge.zip`](https://genomics.senescence.info/cells/cellAge.zip) (ZIP, 21,540 bytes).
- SHA-256: `943506acb3715a8d507459d69bc9a64c3e7863c809c62457171de03dc0062845`.
- ZIP members: `cellage3.tsv`, `release.html`.
- Inspected table: `cellage3.tsv` (TSV, tab-delimited, read as UTF-8).
- Data records: **949**. Blank lines skipped: **1**.
- Exact duplicate records beyond the first copy: **0**.

| Column | Missing cells |
| --- | ---: |
| `Entrez ID` | 0 |
| `Gene symbol` | 0 |
| `Gene name` | 0 |
| `Cancer Cell` | 0 |
| `Type of senescence` | 0 |
| `Senescence Effect` | 0 |
| `Reference` | 0 |

| Candidate identifier | Distinct nonblank values | Rows beyond first use |
| --- | ---: | ---: |
| `Entrez ID` | 866 | 83 |
| `Gene symbol` | 866 | 83 |

- Nonblank Entrez values outside positive ASCII integers: **0**.
- Symbols with leading or trailing whitespace: **0**.
- Entrez IDs with multiple symbols: **0**.
- Symbols with multiple Entrez IDs: **0**.

## Dataset differences and identifier checks

- GenAge Human curates candidate genes for human aging and includes evidence from model organisms. Its `why` field records the basis for inclusion.
- CellAge curates gene manipulation evidence for cellular senescence in human cells. Its table includes cancer-cell status, senescence type, effect, and reference. Repeated gene identifiers can represent distinct evidence records.
- Entrez Gene IDs are the candidate shared namespace. `GenAge ID` is a source-specific identifier and `uniprot` is a protein cross-reference.
- Exact Entrez IDs present in both exports with different associated symbol sets: **1**.
- Exact symbols present in both exports with different associated Entrez ID sets: **0**.

These checks compare literal values. Validate both exports against a versioned human gene authority before constructing the gene intersection, and review retired IDs, aliases, and conflicts.
