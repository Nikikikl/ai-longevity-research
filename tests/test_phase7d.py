import unittest

from scripts.phase7b_ledger import LEDGER, read_csv
from scripts.phase7d_evidence import EXTENSION, ExpandedEvidence, check_extension


class ExpandedEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence = ExpandedEvidence()

    def test_extension_matches_tracked_source_tables(self):
        check_extension(read_csv(LEDGER), read_csv(EXTENSION))

    def test_pmid_lookup_keeps_claims_across_sources_and_genes(self):
        nagai = self.evidence.ask("pmid 25819580")
        self.assertEqual(nagai["facts"]["sources"], ["CellAge", "GO"])
        self.assertEqual({r["id"] for r in nagai["references"]},
                         {"CellAge:765", "GAF:591460", "GAF:591502", "PMID:25819580"})
        ghosh = self.evidence.ask("pmid 29474172")
        self.assertEqual(ghosh["facts"]["genes"], ["SIRT6", "TP53"])
        self.assertEqual(ghosh["facts"]["rows"], 2)

    def test_membership_without_paper_and_observational_go_claim(self):
        genage = self.evidence.ask("record GenAge:239")
        self.assertEqual(genage["evidence_type"], "genage_membership")
        self.assertIsNone(genage["facts"]["pmid"])
        self.assertEqual(genage["references"][0]["locator"], "GenAge ID 239")
        lifespan = self.evidence.ask("record GAF:591445")
        self.assertEqual(lifespan["details"]["evidence_code"], "IMP")
        self.assertIn("Observational", lifespan["details"]["intervention_or_exposure"])
        self.assertIn("does not demonstrate a causal SIRT6 phenotype", lifespan["limitations"][0])

    def test_scope_limits_an_unreviewed_gaf_line(self):
        output = self.evidence.ask("record GAF:591459")
        self.assertEqual(output["status"], "insufficient_evidence")
        self.assertTrue(output["abstains"])
        self.assertEqual([ref["id"] for ref in output["references"]], ["P7D:audit"])
