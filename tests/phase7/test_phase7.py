import unittest
from collections import defaultdict

import numpy as np

from scripts.phase7_baseline import (
    bh, matched_panels, partial_correlations, predict_ridge, validation_permutation,
)
from scripts.phase7_data import Sample, detectable, discovery_age, map_discovery, unique_mapping, validate_samples


class Phase7DataTests(unittest.TestCase):
    def test_age_formats_and_duplicate_donors(self):
        self.assertEqual(discovery_age("2yr3mos"), 2.25)
        with self.assertRaises(ValueError):
            discovery_age("2yr12mos")
        first = Sample("GSM1", "a", "donor", 50, "female", "GPL1", True)
        second = Sample("GSM2", "b", "donor", 50, "female", "GPL1", True)
        with self.assertRaisesRegex(ValueError, "donor"):
            validate_samples([first, second])

    def test_mapping_rejects_conflicts_and_collisions(self):
        indices = {
            "symbol": {"A": {"1"}},
            "prev_symbol": {"OLD": {"1"}, "AMBIG": {"1", "2"}},
            "refseq_accession": {"NM_1": {"1"}, "NM_2": {"2"}},
        }
        self.assertEqual(map_discovery("OLD", "NM_1.2", indices), "1")
        self.assertEqual(map_discovery("A", "NM_2", indices), "")
        self.assertEqual(map_discovery("AMBIG", "NM_1", indices), "")
        self.assertEqual(unique_mapping(["1", "2", "1", ""]), ["", "2", "", ""])

    def test_detection_requires_variation_and_sufficient_donors(self):
        values = np.ones((6, 3))
        values[:5, 1] = 0
        values[:4, 2] = 0
        np.testing.assert_array_equal(detectable(values), [False, False, True])


class Phase7AnalysisTests(unittest.TestCase):
    def test_partial_r_removes_covariate_and_handles_zero_residual(self):
        sex = np.repeat([0, 1], 4)
        within_sex = np.tile([-2., -1., 1., 2.], 2)
        ages = 40 + sex * 20 + within_sex
        expression = np.column_stack((within_sex + 9 * sex, -within_sex, 10 * sex))
        covariates = np.column_stack((np.ones(len(sex)), sex))
        np.testing.assert_allclose(partial_correlations(expression, ages, covariates), [1, -1, 0])

    def test_bh_retains_original_order(self):
        np.testing.assert_allclose(bh(np.array([.04, .01, .03])), [.04, .03, .04])

    def test_matched_sets_use_distinct_controls_and_repeat_with_seed(self):
        coordinates = np.arange(40, dtype=float)[:, None]
        targets, controls = np.array([0, 1, 2]), np.arange(3, 40)
        draws = matched_panels(coordinates, targets, controls, 10, np.random.default_rng(3))
        np.testing.assert_array_equal(
            draws, matched_panels(coordinates, targets, controls, 10, np.random.default_rng(3)),
        )
        self.assertTrue(all(len(set(draw)) == len(targets) for draw in draws))
        self.assertTrue(np.isin(draws, controls).all())
        self.assertTrue((draws < 35).all())

    def test_validation_permutation_detects_strong_within_sex_alignment(self):
        sex = np.repeat([0, 1], 12)
        age = np.tile(np.arange(12), 2) + 30 + 10 * sex
        covariates = np.column_stack((np.ones(len(sex)), sex))
        groups = defaultdict(list)
        for index, value in enumerate(sex):
            groups[value].append(index)
        pvalue = validation_permutation(
            np.ones(1), age[:, None], age, covariates,
            list(groups.values()), np.random.default_rng(2), draws=99,
        )
        self.assertEqual(pvalue, .01)

    def test_ridge_predictions_do_not_depend_on_other_test_donors(self):
        expression = np.arange(24, dtype=float).reshape(12, 2)
        ages = np.arange(12) + 22
        train, test = np.arange(10), np.array([10, 11])
        features = np.array([0, 1])
        before = predict_ridge(expression, ages, train, test, features)
        expression[11] *= 1_000
        after = predict_ridge(expression, ages, train, test, features)
        self.assertAlmostEqual(before[0], after[0])
        self.assertNotEqual(before[1], after[1])
