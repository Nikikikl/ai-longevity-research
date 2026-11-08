"""Run the frozen Phase 7A association and chronological-age prediction analyses."""

import csv
import json
import platform
from importlib.metadata import version

import numpy as np
from scipy.spatial.distance import cdist
from scipy.stats import rankdata, t
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, median_absolute_error, r2_score, root_mean_squared_error
from sklearn.model_selection import KFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits

from scripts.phase7_data import ROOT, describe, detectable, eligible_genes, load, verify_file

SEED = 20261108
PROTOCOL_SHA256 = "b6648a56607a9743a0fba4012826c6316151648d99c79ef2d6bd2d895a8ca702"
OUTPUT = ROOT / "data/processed/phase7"


def design(samples):
    platforms = sorted({sample.platform for sample in samples})
    return np.array([
        [1, sample.sex == "female", *(sample.platform == item for item in platforms[1:])]
        for sample in samples
    ], dtype=float)


def selected_data(cohort, genes):
    positions = {gene_id: i for i, gene_id in enumerate(cohort.gene_ids) if gene_id}
    columns = [positions[gene_id] for gene_id in genes]
    mask = cohort.eligible()
    samples = [sample for sample, keep in zip(cohort.samples, mask) if keep]
    raw = cohort.values[np.ix_(mask, columns)]
    transformed = cohort.expression()[np.ix_(mask, columns)]
    return samples, raw, transformed


def unit_length(matrix):
    norms = np.linalg.norm(matrix, axis=0)
    return np.divide(matrix, norms, out=np.zeros_like(matrix), where=norms > 0)


def partial_inputs(expression, ages, covariates):
    if np.linalg.matrix_rank(covariates) != covariates.shape[1]:
        raise ValueError("Rank-deficient association covariates")
    basis = np.linalg.qr(covariates)[0]
    residual_units = []
    for values in (expression, ages):
        residuals = values - basis @ (basis.T @ values)
        tolerance = 32 * np.finfo(float).eps * np.linalg.norm(values, axis=0)
        residuals *= np.linalg.norm(residuals, axis=0) > tolerance
        residual_units.append(unit_length(residuals))
    return tuple(residual_units)


def partial_correlations(expression, ages, covariates):
    expr_unit, age_unit = partial_inputs(expression, ages, covariates)
    return np.clip(age_unit @ expr_unit, -1, 1)


def correlation_pvalues(correlations, n, covariates):
    degrees = n - covariates.shape[1] - 1
    if degrees <= 0:
        raise ValueError("Insufficient residual degrees of freedom")
    with np.errstate(divide="ignore"):
        statistic = np.abs(correlations) * np.sqrt(degrees / (1 - correlations ** 2))
    return 2 * t.sf(statistic, degrees)


def bh(pvalues):
    order = np.argsort(pvalues, kind="stable")
    adjusted = pvalues[order] * len(order) / np.arange(1, len(order) + 1)
    result = np.empty_like(pvalues)
    result[order] = np.minimum(1, np.minimum.accumulate(adjusted[::-1])[::-1])
    return result


def matching_coordinates(raw, transformed, eligible):
    summaries = np.column_stack((transformed.mean(axis=0), (raw > 0).mean(axis=0)))
    ranks = np.zeros_like(summaries)
    ranks[eligible] = rankdata(summaries[eligible], axis=0) / eligible.sum()
    return ranks


def matched_panels(coordinates, targets, controls, size, rng):
    distances = cdist(coordinates[targets], coordinates[controls])
    nearest = controls[np.argsort(distances, axis=1, kind="stable")[:, :32]]
    draws = np.empty((size, len(targets)), dtype=int)
    for panel in draws:
        used = set()
        for target in rng.permutation(len(targets)):
            available = [index for index in nearest[target] if index not in used]
            if not available:
                raise ValueError("No unused expression-matched control in the nearest 32")
            panel[target] = rng.choice(available)
            used.add(panel[target])
    return draws


def reference_summary(target, matched):
    return {
        "target": float(target),
        "matched_median": float(np.median(matched)),
        "matched_95_interval": np.quantile(matched, [.025, .975]).tolist(),
        "matched_95th_percentile": float(np.quantile(matched, .95)),
        "target_percentile_strict": float(np.mean(matched < target)),
    }


def strata(samples, include_platform):
    groups = {}
    for i, sample in enumerate(samples):
        key = (sample.sex, sample.platform) if include_platform else sample.sex
        groups.setdefault(key, []).append(i)
    return list(groups.values())


def validation_permutation(a, expression, ages, covariates, groups, rng, draws=9999):
    expr_unit, age_unit = partial_inputs(expression, ages, covariates)
    projection = expr_unit @ a / len(a)
    observed = age_unit @ projection
    permuted = np.tile(age_unit, (draws, 1))
    for group in groups:
        # Residualized ages are centered by sex and have a fixed norm under these permutations.
        permuted[:, group] = rng.permuted(permuted[:, group], axis=1)
    pvalue = (1 + np.count_nonzero(permuted @ projection >= observed - 1e-14)) / (draws + 1)
    return float(pvalue)


def bootstrap_replication(data, rng, draws=1000):
    scores = []
    for _ in range(draws):
        effects = []
        for expression, ages, covariates, groups in data:
            indices = np.concatenate([rng.choice(group, size=len(group)) for group in groups])
            effects.append(partial_correlations(expression[indices], ages[indices], covariates[indices]))
        scores.append(np.mean(effects[0] * effects[1]))
    return np.quantile(scores, [.025, .975]).tolist()


def association_analysis(panel, discovery, validation, rngs):
    joint = eligible_genes(discovery) & eligible_genes(validation)
    genes = sorted(joint, key=int)
    targets = np.array([i for i, gene_id in enumerate(genes) if gene_id in panel])
    controls = np.array([i for i, gene_id in enumerate(genes) if gene_id not in panel])
    datasets = [selected_data(cohort, genes) for cohort in (discovery, validation)]
    if len(targets) < 80 or min(len(samples) for samples, _, _ in datasets) < 50:
        raise ValueError("The frozen minimum coverage or donor threshold was not met")

    all_eligible = np.ones(len(genes), dtype=bool)
    coordinates, correlations, pvalues, prepared = [], [], [], []
    for samples, raw, expression in datasets:
        ages = np.array([sample.age for sample in samples])
        covariates = design(samples)
        effect = partial_correlations(expression, ages, covariates)
        correlations.append(effect)
        pvalues.append(correlation_pvalues(effect[targets], len(ages), covariates))
        prepared.append((expression[:, targets], ages, covariates, strata(samples, True)))
        coordinates.append(matching_coordinates(raw, expression, all_eligible))

    match_rng, permutation_rng, bootstrap_rng = rngs
    coordinates = np.column_stack(coordinates)
    matched = matched_panels(coordinates, targets, controls, 1000, match_rng)
    a, b = correlations
    product = a * b
    panel_product = product[targets]
    replication = reference_summary(panel_product.mean(), product[matched].mean(axis=1))
    pvalue = validation_permutation(
        a[targets], *prepared[1][:3], strata(datasets[1][0], False), permutation_rng,
    )
    q_a, q_b = map(bh, pvalues)
    d_samples, _, d_expr = datasets[0]
    major = np.array([sample.platform == "GPL18573" for sample in d_samples])
    d_ages = prepared[0][1]
    major_effect = partial_correlations(
        d_expr[major][:, targets], d_ages[major],
        design([sample for sample, keep in zip(d_samples, major) if keep]),
    )
    stats = {
        "genes_tested": len(targets),
        "control_universe": len(controls),
        "replication_score": replication,
        "validation_permutation_p": pvalue,
        "bootstrap_95_interval": bootstrap_replication(prepared, bootstrap_rng),
        "decision_met": bool(replication["target"] > replication["matched_95th_percentile"] and pvalue <= .05),
        "matching_mean_absolute_rank_difference": np.abs(coordinates[matched] - coordinates[targets]).mean(axis=(0, 1)).tolist(),
        "sign_agreement": float(np.mean(panel_product[panel_product != 0] > 0)),
        "both_q_lt_005_concordant": int(np.sum((q_a < .05) & (q_b < .05) & (panel_product > 0))),
        "major_platform_replication_score": float(np.mean(major_effect * b[targets])),
        "discovery_mean_r_squared": reference_summary((a[targets] ** 2).mean(), (a[matched] ** 2).mean(axis=1)),
        "validation_mean_r_squared": reference_summary((b[targets] ** 2).mean(), (b[matched] ** 2).mean(axis=1)),
    }
    effects = {
        genes[index]: (a[index], b[index], pvalues[0][i], pvalues[1][i], q_a[i], q_b[i])
        for i, index in enumerate(targets)
    }
    available = [set(cohort.gene_ids) for cohort in (discovery, validation)]
    detectable_sets = [eligible_genes(cohort) for cohort in (discovery, validation)]
    ledger = []
    for gene_id, symbol in sorted(panel.items(), key=lambda item: item[1]):
        status = [
            "eligible" if gene_id in expressed else "low_detection_or_constant" if gene_id in mapped else "unmapped"
            for mapped, expressed in zip(available, detectable_sets)
        ]
        ledger.append((gene_id, symbol, *status, *effects.get(gene_id, ("",) * 6)))
    return stats, ledger


def predict_ridge(expression, ages, train, test, features):
    pipeline = make_pipeline(StandardScaler(), Ridge(alpha=len(features)))
    pipeline.fit(expression[np.ix_(train, features)], ages[train])
    return pipeline.predict(expression[np.ix_(test, features)])


def prediction_analysis(panel, discovery, validation, rngs):
    joint_mapped = (set(discovery.gene_ids) & set(validation.gene_ids)) - {""}
    genes = sorted(joint_mapped, key=int)
    samples, raw, expression = selected_data(discovery, genes)
    ages = np.array([sample.age for sample in samples])
    covariates = design(samples)
    is_target = np.array([gene_id in panel for gene_id in genes])
    named = {name: np.empty(len(ages)) for name in ("panel_ridge", "mean_age", "median_age", "sex_platform_ols")}
    random_predictions = np.empty((40, len(ages)))
    feature_counts = []
    match_rng, bootstrap_rng = rngs
    splitter = KFold(n_splits=5, shuffle=True, random_state=SEED)
    for train, test in splitter.split(ages):
        keep = detectable(raw[train])
        targets = np.flatnonzero(keep & is_target)
        controls = np.flatnonzero(keep & ~is_target)
        feature_counts.append(len(targets))
        coordinates = matching_coordinates(raw[train], expression[train], keep)
        matched = matched_panels(coordinates, targets, controls, len(random_predictions), match_rng)
        named["panel_ridge"][test] = predict_ridge(expression, ages, train, test, targets)
        named["mean_age"][test] = ages[train].mean()
        named["median_age"][test] = np.median(ages[train])
        coefficients = np.linalg.lstsq(covariates[train], ages[train], rcond=None)[0]
        named["sex_platform_ols"][test] = covariates[test] @ coefficients
        for row, features in zip(random_predictions, matched, strict=True):
            row[test] = predict_ridge(expression, ages, train, test, features)

    metrics = {
        name: {
            "mae": mean_absolute_error(ages, predicted),
            "medae": median_absolute_error(ages, predicted),
            "rmse": root_mean_squared_error(ages, predicted),
            "r2": r2_score(ages, predicted),
        }
        for name, predicted in named.items()
    }
    random_maes = np.abs(random_predictions - ages).mean(axis=1)
    errors = np.abs(named["panel_ridge"] - ages) - np.abs(named["median_age"] - ages)
    draws = bootstrap_rng.integers(len(ages), size=(2000, len(ages)))
    return {
        "donors": len(ages),
        "panel_features_by_fold": feature_counts,
        "metrics": metrics,
        "matched_panel_mae": reference_summary(metrics["panel_ridge"]["mae"], random_maes),
        "fraction_matched_maes_strictly_worse": float(np.mean(random_maes > metrics["panel_ridge"]["mae"])),
        "paired_mae_difference_panel_minus_median": float(errors.mean()),
        "conditional_bootstrap_95_interval": np.quantile(errors[draws].mean(axis=1), [.025, .975]).tolist(),
    }


def main():
    verify_file(ROOT / "docs/phase7_research_protocol.md", PROTOCOL_SHA256)
    panel, discovery, validation = load()
    rngs = [np.random.default_rng(child) for child in np.random.SeedSequence(SEED).spawn(5)]
    with threadpool_limits(limits=1):
        associations, ledger = association_analysis(panel, discovery, validation, rngs[:3])
        prediction = prediction_analysis(panel, discovery, validation, rngs[3:])
    summary = {
        "protocol_sha256": PROTOCOL_SHA256,
        "seed": SEED,
        "software": {"python": platform.python_version(), "machine": platform.machine(), **{
            name: version(name) for name in ("numpy", "scipy", "scikit-learn", "joblib", "threadpoolctl")
        }},
        "GSE113957": describe(discovery, panel),
        "GSE226189": describe(validation, panel),
        "association": associations,
        "prediction": prediction,
    }
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "metrics.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n")
    with (OUTPUT / "phase7_gene_associations.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(("entrez_id", "approved_symbol", "gse113957_status", "gse226189_status",
                         "gse113957_partial_r", "gse226189_partial_r", "gse113957_p", "gse226189_p",
                         "gse113957_q", "gse226189_q"))
        for row in ledger:
            writer.writerow([*row[:4], *(format(value, ".10g") if value != "" else "" for value in row[4:])])
    print(f"Wrote Phase 7A aggregate results to {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
