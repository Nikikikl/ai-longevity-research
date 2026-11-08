# Phase 7A data feasibility and prior work

**Decision.** The two GEO cohorts support separate donor-age association estimates and an internal prediction feasibility test in discovery. Under the fixed mapping and detection rules, 109 of the 113 genes can be assessed in both cohorts. No cross-cohort age predictor was evaluated. See the [frozen protocol](../docs/phase7_research_protocol.md) and [results](phase7_baseline_results.md).

## Input audit

| Item | Discovery: GSE113957 | Validation: GSE226189 |
| --- | --- | --- |
| Source | Coriell dermal fibroblast cell lines | GESTALT primary skin fibroblasts from inner-axilla biopsies |
| Records in processed matrix | 143 | 82 |
| Healthy donor proxies before age restriction | 133 | 82 |
| HGPS excluded | 10 | 0 |
| Healthy ages from GEO metadata | 1–96 | 22–89 |
| Eligible ages and donors | 22–89, n = 97 | 22–89, n = 82 |
| Eligible age Q1 / median / Q3, years | 37 / 60 / 82 | 35 / 52 / 70 |
| Eligible donors per decade, 20s through 80s | 14, 14, 14, 6, 19, 4, 26 | 11, 16, 10, 11, 12, 13, 9 |
| Eligible sex, GEO categories | 26 female, 71 male | 35 female, 47 male |
| Sequencing platform in eligible samples | GPL18573 NextSeq 500 (84), GPL16791 HiSeq 2500 (13) | GPL24676 NovaSeq 6000 (82) |
| Submitted expression | 27,142 rows, representative RefSeq isoform FPKM, HOMER after STAR alignment to hg19 | 57,773 rows per sample, Ensembl gene integer counts from featureCounts after STAR alignment, annotated as hg19 Ensembl v82 in GEO |
| Unique Entrez mappings after exclusions | 24,923 | 39,243 |
| Rows without unique initial mapping / rows dropped in mapping collisions | 2,071 / 148 | 18,526 / 4 |
| Panel mapped / passes detection | 113 / 110 | 112 / 111 |

The discovery publication describes a range ending at 94 in its abstract. The downloaded GEO metadata label one healthy line as age 96. The analysis uses the GEO metadata and excludes ages outside 22–89. SOFT matches all 143 FPKM columns by title. The validation archive contains 82 gene-count files and 82 circular-RNA files. Only the gene counts are used. All count headers match series metadata and all files have the same gene order. No duplicate GSM, repeated donor proxy, identical expression profile, missing numeric value, negative value or empty sample was found. Donor proxies are Coriell cell IDs and GESTALT codes. Distinct recruitment sources support treating the cohorts as independent. The public records do not provide a cross-cohort identity key to verify this at person level. [GSE113957](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE113957), [Fleischer et al.](https://doi.org/10.1186/s13059-018-1599-6), [GSE226189](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE226189), [Tsitsipatis et al.](https://doi.org/10.1111/acel.13915)

Platform and sex are available in discovery. The HiSeq subset comprises ages 30–50, so platform and age coverage differ. The association model adjusts for platform and repeats the score using the larger NextSeq subset. Discovery GEO also reports ethnicity, with incomplete or sparsely represented categories. Validation uses one sequencer platform and records age and sex. Its title groups cover age ranges 22–33, 34–49, 51–66, 65–78 and 80–89. Treating those groups as batch would remove substantial age variation. Neither downloaded metadata file provides a usable per-donor culture passage or sequencing batch field beyond the reported platforms. Differences in recruitment, biopsy location, culture, library preparation, annotation, and age and sex distributions remain plausible sources of between-cohort disagreement. [Validation platform record](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GPL24676)

Joint filtering leaves 16,580 genes, including 109 panel genes and 16,471 possible controls. FGF21 and PON1 fail the discovery detection or variation rule, and TERT fails in both cohorts. SOD2 is excluded by the pinned validation crosswalk. Its counts archive includes ENSG00000112096, labeled SOD2 in Ensembl GRCh37, while the HGNC snapshot lists ENSG00000291237 for this gene. The uniform mapping rule was frozen without historical ID overrides. This exclusion reflects the chosen crosswalk rather than evidence that SOD2 is unexpressed. An annotation-matched crosswalk is a specific future sensitivity analysis. [Ensembl GRCh37 SOD2](https://grch37.ensembl.org/Homo_sapiens/Gene/Summary?g=ENSG00000112096), [coverage and effects ledger](phase7_gene_associations.csv)

## What prior work established

| Primary work | Published approach and relevance |
| --- | --- |
| Fleischer et al. (2018) | Generated the discovery RNA-seq data and used an ensemble of linear discriminant classifiers with leave-one-out evaluation. The paper reports a median chronological-age error of four years for its own analysis. It differs in age range, feature space and validation design from the fixed-panel Ridge baseline here. [DOI 10.1186/s13059-018-1599-6](https://doi.org/10.1186/s13059-018-1599-6) |
| Tsitsipatis et al. (2023) | Profiled cultured primary skin fibroblasts from 82 healthy GESTALT donors and reported age-associated coding and noncoding RNAs by regression. This supplies a separate cohort for comparing gene effects. [DOI 10.1111/acel.13915](https://doi.org/10.1111/acel.13915) |
| Avelar et al. (2020) and Bonnefous et al. (2024) | The former built CellAge from perturbation evidence and compared expression signatures and networks with human aging data. The latter reported a 113-gene GenAge–CellAge overlap in an evolutionary study. Count agreement with our independently derived list does not establish member identity. [Avelar et al.](https://doi.org/10.1186/s13059-020-01990-9), [Bonnefous et al.](https://doi.org/10.1007/s11357-024-01234-9), [Phase 6 comparison](../docs/related_work.md) |
| Xie et al. (2026), SkinAGE | Already combined both GEO cohorts with other fibroblast cohorts in model development. The authors used ComBat, HAGR skin genes and data-driven selection, evaluated multiple models including Elastic Net and a neural network, and used E-MTAB-3037 for external evaluation. The fixed Phase 3 list, separate association estimates and expression-matched benchmark are the focus here. [DOI 10.1186/s12864-025-12469-x](https://doi.org/10.1186/s12864-025-12469-x) |
| Wang et al. (2025) | Estimated donor-specific transcriptional networks across GTEx tissues and reported age-related loss of gene coordination. Network coordination and the gene-wise age effects tested here are different endpoints. [DOI 10.1186/s13073-025-01533-6](https://doi.org/10.1186/s13073-025-01533-6) |
| Tyshkovskiy et al. (2026) and Salignon et al. (2026) | The former included both GEO accessions in a larger harmonized multispecies analysis and developed transcriptomic clocks. The latter used an age-shift learning design and tested transfer across datasets and platforms. Cohort reuse and cross-platform transcriptomic prediction are established research directions. [Multispecies study](https://doi.org/10.1038/s41586-026-10542-3), [Pasta](https://doi.org/10.1002/advs.76740) |
| Zhavoronkov et al. (2026) and Asai et al. (2026) | LongevityBench evaluates aging and omics tasks and the authors fine-tuned domain-specific language models. OpenScholar retrieves and synthesizes scientific literature, with a benchmark for multi-paper citation and answer quality. The proposed project assistant would evaluate the accuracy of claims grounded in a small, versioned local evidence ledger. [LongevityBench, Cell](https://doi.org/10.1016/j.cell.2026.08.026), [OpenScholar, Nature](https://doi.org/10.1038/s41586-025-10072-4) |

The literature search checked the two accessions together, the accession names with GenAge/CellAge and age prediction terms, and the cited works and their methods. We did not identify a report applying this exact pinned panel, donor eligibility, matched controls and separate-cohort replication statistic. The search was targeted, so this is a description of the analysis rather than a priority claim.

## Provenance, reuse and reproduction

The [source manifest](../data/phase7_sources.json) records the exact HTTPS URLs, download dates, byte counts, formats and SHA-256 fingerprints of the four processed GEO files. NCBI applies no restriction itself but cautions that submitters may assert rights. Cite the GEO series and originating papers. This repository distributes code and aggregate statistics. Source files, donor metadata and expression matrices remain in ignored local directories. The file named RAW.tar is GEO's archive of processed count and circular-RNA tables. No FASTQ or alignments were downloaded. [GEO disclaimer](https://www.ncbi.nlm.nih.gov/geo/info/disclaimer.html)

From the repository root, use Python 3.11 and install [the Phase 7 dependency pins](../requirements-phase7.txt) in a separate environment. Save the manifest files to `data/raw/phase7/` under their exact basenames. Use the pinned HGNC file in `data/raw/references/` described in [the earlier reference manifest](../data/reference_provenance.json). The scripts verify these files and the Phase 3 panel before reading expression.

```sh
python3 -m venv .venv/phase7
.venv/phase7/bin/python -m pip install -r requirements-phase7.txt
mkdir -p data/raw/phase7
.venv/phase7/bin/python -c 'import json; print("\n".join(record["url"] for record in json.load(open("data/phase7_sources.json")).values()))' |
  while IFS= read -r url; do
    curl --fail --location --silent --show-error "$url" -o "data/raw/phase7/${url##*/}" || exit 1
  done
.venv/phase7/bin/python -B -m scripts.phase7_data
.venv/phase7/bin/python -B -m scripts.phase7_baseline
.venv/phase7/bin/python -B -m unittest discover -s tests -v
.venv/phase7/bin/python -B -m unittest discover -s tests/phase7 -v
```

The baseline writes aggregate metrics and the regenerated gene ledger under `data/processed/phase7/`. No model weights, individual predictions or individual records are written.
