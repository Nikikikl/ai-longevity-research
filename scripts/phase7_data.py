"""Verify and inspect processed GEO fibroblast expression without fitting models."""

import csv
import gzip
import hashlib
import json
import re
import tarfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "data/raw/phase7"
AGE_MIN, AGE_MAX = 22, 89
DETECTION_FRACTION = 0.20
HGNC_FILE = "hgnc_complete_set_2026-10-06.tsv"
PANEL_SHA256 = "01f208e99cbeb5f38369005c537dc86d5bf59d2fcbf04fea1faee5b6f82db11a"


@dataclass(frozen=True)
class Sample:
    accession: str
    title: str
    donor: str
    age: float
    sex: str
    platform: str
    healthy: bool


@dataclass
class Cohort:
    samples: list[Sample]
    gene_ids: list[str]
    values: np.ndarray
    mapping: dict

    def eligible(self):
        return np.array([
            sample.healthy and AGE_MIN <= sample.age <= AGE_MAX
            for sample in self.samples
        ])

    def expression(self):
        """Keep scales cohort-specific. Count denominators include all input genes."""
        if self.mapping["unit"] == "counts":
            return np.log1p(self.values * (1_000_000 / self.values.sum(axis=1))[:, None])
        return np.log1p(self.values)


def verify_file(path, sha256, size=None):
    with path.open("rb") as stream:
        actual = hashlib.file_digest(stream, "sha256").hexdigest()
    if actual != sha256 or (size is not None and path.stat().st_size != size):
        raise ValueError(f"Input does not match its pinned fingerprint: {path.name}")


def validate_samples(samples):
    for attribute in ("accession", "title", "donor"):
        values = [getattr(sample, attribute) for sample in samples]
        if any(not value for value in values) or len(set(values)) != len(samples):
            raise ValueError(f"Missing or repeated sample {attribute}")
    if any(sample.sex not in {"female", "male"} or sample.age < 0 for sample in samples):
        raise ValueError("Invalid age or sex in GEO metadata")
    return samples


def discovery_age(value):
    match = re.fullmatch(r"(\d+)(?:yr(?:(\d+)mos)?)?", value.lower())
    if not match or int(match[2] or 0) > 11:
        raise ValueError(f"Unexpected donor age format: {value}")
    return int(match[1]) + int(match[2] or 0) / 12


def discovery_metadata(path):
    samples = []
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for block in stream.read().split("\n^SAMPLE = ")[1:]:
            accession, *lines = block.splitlines()
            fields = {}
            for line in lines:
                key, _, value = line.partition(" = ")
                if key == "!Sample_characteristics_ch1":
                    key, _, value = value.partition(": ")
                fields[key.lower()] = value
            disease = fields["disease"].lower()
            if disease not in {"normal", "hgps"}:
                raise ValueError(f"Unrecognized disease for {accession}")
            samples.append(Sample(
                accession, fields["!sample_title"], fields["cell id"],
                discovery_age(fields["age"]), fields["sex"].lower(),
                fields["!sample_platform_id"], disease == "normal",
            ))
    return validate_samples(samples)


def validation_metadata(path):
    fields = {}
    with gzip.open(path, "rt", encoding="utf-8", newline="") as stream:
        for key, *values in filter(None, csv.reader(stream, delimiter="\t")):
            if key == "!Sample_characteristics_ch1":
                label = values[0].split(": ", 1)[0]
                prefix = f"{label}: "
                if any(not value.startswith(prefix) for value in values):
                    raise ValueError("Inconsistent GEO characteristic row")
                fields[label] = [value.removeprefix(prefix) for value in values]
            elif key in {"!Sample_geo_accession", "!Sample_title", "!Sample_platform_id"}:
                fields[key] = values
    samples = []
    for accession, title, platform, age, sex, tissue in zip(
        fields["!Sample_geo_accession"], fields["!Sample_title"],
        fields["!Sample_platform_id"], fields["age (years)"], fields["Sex"],
        fields["cell type"], strict=True,
    ):
        donor = re.fullmatch(r"SKIN_AGE\d+_[MF]_GR\d+_(Gt\d+)", title)
        if not donor or tissue != "primary skin fibroblasts":
            raise ValueError(f"Unexpected GESTALT sample: {accession}")
        samples.append(Sample(accession, title, donor[1], int(age), sex.lower(), platform, True))
    return validate_samples(samples)


def hgnc_indices(path):
    indices = {key: defaultdict(set) for key in ("symbol", "prev_symbol", "refseq_accession", "ensembl_gene_id")}
    with path.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            if row["status"] == "Approved" and row["entrez_id"]:
                for key, index in indices.items():
                    for value in filter(None, row[key].split("|")):
                        index[value].add(row["entrez_id"])
    return indices


def map_discovery(symbol, refseq, indices):
    candidates = indices["symbol"].get(symbol) or indices["prev_symbol"].get(symbol, set())
    accessions = indices["refseq_accession"].get(refseq.split(".")[0], set())
    if len(candidates) != 1 or (accessions and accessions != candidates):
        return ""
    return next(iter(candidates))


def unique_mapping(mapped):
    counts = Counter(mapped)
    return [gene_id if gene_id and counts[gene_id] == 1 else "" for gene_id in mapped]


def discovery_expression(path, samples, indices):
    by_title = {sample.title: sample for sample in samples}
    with gzip.open(path, "rt", encoding="utf-8", newline="") as stream:
        reader = csv.reader(stream, delimiter="\t")
        header = next(reader)
        titles = header[8:]
        if header[:8] != ["Transcript ID", "chr", "start", "end", "strand", "Length",
                          "Copies", "Annotation/Divergence"] or set(titles) != by_title.keys():
            raise ValueError("Unexpected FPKM header or sample names")
        ordered = validate_samples([by_title[title] for title in titles])
        values, mapped = [], []
        for row in reader:
            if len(row) != len(header):
                raise ValueError("Incomplete FPKM row")
            mapped.append(map_discovery(row[7].split("|")[0], row[0], indices))
            values.append([float(value) for value in row[8:]])
    return build_cohort(ordered, mapped, np.array(values).T, "FPKM")


def validation_expression(path, samples, indices):
    sample_files = {}
    gene_ids = None
    by_accession = {sample.accession: sample for sample in samples}
    with tarfile.open(path) as archive:
        for member in archive:
            if not member.name.endswith("_geneCOUNT.txt.gz"):
                continue
            accession, _, _ = member.name.partition("_")
            sample = by_accession[accession]
            if not member.isfile() or accession in sample_files:
                raise ValueError(f"Unexpected or repeated count file: {member.name}")
            with gzip.open(archive.extractfile(member), "rt", encoding="utf-8", newline="") as stream:
                reader = csv.reader(stream, delimiter="\t")
                if next(reader) != ["Tracking_ID", f"{sample.title}_COUNT"]:
                    raise ValueError(f"Unexpected count header for {accession}")
                ids, values = [], []
                for gene_id, count in reader:
                    ids.append(gene_id)
                    values.append(int(count))
                if gene_ids is None:
                    gene_ids = ids
                elif ids != gene_ids:
                    raise ValueError(f"Inconsistent count identifiers in {accession}")
                sample_files[accession] = values
    if sample_files.keys() != by_accession.keys() or len(gene_ids) != len(set(gene_ids)):
        raise ValueError("Missing count files or repeated Ensembl identifiers")
    mapped = []
    for gene_id in gene_ids:
        candidates = indices["ensembl_gene_id"].get(gene_id.split(".")[0], set())
        mapped.append(next(iter(candidates)) if len(candidates) == 1 else "")
    return build_cohort(samples, mapped, np.array([sample_files[s.accession] for s in samples]), "counts")


def build_cohort(samples, mapped, values, unit):
    if not np.isfinite(values).all() or (values < 0).any() or np.any(values.sum(axis=1) == 0):
        raise ValueError("Missing, invalid, or empty expression measurements")
    if np.unique(values, axis=0).shape[0] != len(samples):
        raise ValueError("Identical expression profiles require donor review")
    gene_ids = unique_mapping(mapped)
    return Cohort(samples, gene_ids, values, {
        "unit": unit,
        "input_rows": len(mapped),
        "mapped_unique": sum(bool(gene_id) for gene_id in gene_ids),
        "unmapped_rows": mapped.count(""),
        "collision_rows": gene_ids.count("") - mapped.count(""),
    })


def load():
    manifest = json.loads((ROOT / "data/phase7_sources.json").read_text())
    for filename, record in manifest.items():
        verify_file(INPUTS / filename, record["sha256"], record["bytes"])
    reference = json.loads((ROOT / "data/reference_provenance.json").read_text())[HGNC_FILE]
    hgnc = ROOT / "data/raw/references" / HGNC_FILE
    verify_file(hgnc, reference["sha256"], reference["size_bytes"])
    panel_path = ROOT / "reports/gene_overlap_genes.csv"
    verify_file(panel_path, PANEL_SHA256)
    with panel_path.open(encoding="utf-8", newline="") as stream:
        panel = {row["entrez_gene_id"]: row["approved_symbol"] for row in csv.DictReader(stream)}
    if len(panel) != 113:
        raise ValueError("Expected the 113 genes from Phase 3")
    indices = hgnc_indices(hgnc)
    discovery = discovery_expression(
        INPUTS / "GSE113957_fpkm.txt.gz",
        discovery_metadata(INPUTS / "GSE113957_family.soft.gz"), indices,
    )
    validation = validation_expression(
        INPUTS / "GSE226189_RAW.tar",
        validation_metadata(INPUTS / "GSE226189_series_matrix.txt.gz"), indices,
    )
    return panel, discovery, validation


def detectable(values):
    return ((values > 0).mean(axis=0) >= DETECTION_FRACTION) & (np.ptp(values, axis=0) > 0)


def eligible_genes(cohort):
    return {gene_id for gene_id, keep in zip(
        cohort.gene_ids, detectable(cohort.values[cohort.eligible()]), strict=True
    ) if gene_id and keep}


def describe(cohort, panel):
    mapped = set(cohort.gene_ids) - {""}
    eligible = [sample for sample, keep in zip(cohort.samples, cohort.eligible()) if keep]
    healthy = [sample for sample in cohort.samples if sample.healthy]
    ages = np.array([sample.age for sample in eligible])
    expressed = eligible_genes(cohort)
    return {
        **cohort.mapping,
        "samples": len(cohort.samples),
        "healthy": len(healthy),
        "healthy_age_range": [min(s.age for s in healthy), max(s.age for s in healthy)],
        "eligible": len(eligible),
        "age_min_q1_median_q3_max": np.quantile(ages, [0, .25, .5, .75, 1]).tolist(),
        "decades": dict(Counter(int(sample.age) // 10 * 10 for sample in eligible)),
        "sex": dict(Counter(sample.sex for sample in eligible)),
        "platform": dict(Counter(sample.platform for sample in eligible)),
        "mapped_panel": len(mapped & panel.keys()),
        "detectable_panel": len(expressed & panel.keys()),
        "missing_mapping": sorted(panel[g] for g in panel.keys() - mapped),
        "fails_detection": sorted(panel[g] for g in (panel.keys() & mapped) - expressed),
    }


if __name__ == "__main__":
    panel, discovery, validation = load()
    joint = eligible_genes(discovery) & eligible_genes(validation)
    print(json.dumps({
        "GSE113957": describe(discovery, panel),
        "GSE226189": describe(validation, panel),
        "joint_eligible_genes": len(joint),
        "joint_eligible_panel": len(joint & panel.keys()),
        "excluded_panel": sorted(panel[g] for g in panel.keys() - joint),
    }, indent=2))
