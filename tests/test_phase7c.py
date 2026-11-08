import unittest

from scripts.phase7c_qa import NormalizedEvidence, normalize_question


class NormalizedLookupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence = NormalizedEvidence()

    def test_aliases_preserve_entity_and_measurement_boundaries(self):
        self.assertEqual(normalize_question("Partial r for TP53BP1"), "partial correlation for tp53bp1")
        output = self.evidence.ask("Give partial r for p53 protein abundance.")
        self.assertEqual(output["status"], "unsupported_question")
        output = self.evidence.ask("Find partial r for tumor protein p53.")
        self.assertEqual(output["references"][0]["id"], "P7A:gene:7157")

    def test_pubmed_alias_preserves_go_rows(self):
        output = self.evidence.ask("Which annotations cite PubMed accession 16243918?")
        self.assertEqual(output["evidence_type"], "citation_audit")
        self.assertEqual({ref["id"] for ref in output["references"]},
                         {"GAF:289844", "GAF:289847", "PMID:16243918"})

    def test_sign_synonym_does_not_override_q_threshold(self):
        output = self.evidence.ask("Within each cohort, report q-value below 0.05 with concordant signs.")
        self.assertEqual(output["facts"], {"discovery": 48, "validation": 0, "both_concordant": 0})

    def test_protein_names_keep_the_two_cdkn2a_products_distinct(self):
        self.assertEqual(normalize_question("p14-ARF and p16^INK4A"), "p14arf and p16ink4a")
        output = self.evidence.ask("Which Cell Age entries list p14-ARF?")
        self.assertEqual(output["status"], "unsupported_question")
