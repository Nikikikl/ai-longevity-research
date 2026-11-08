import unittest

from scripts.phase7b_ledger import LEDGER, ROOT, build, render, summarize
from scripts.phase7b_qa import Evidence
from scripts.phase7b_score import evaluate


class EvidenceIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = build()
        cls.evidence = Evidence()

    def test_ledger_regenerates_with_distinct_claims_and_shared_citation(self):
        self.assertEqual(render(self.ledger), (ROOT / LEDGER).read_bytes())
        counts = summarize(self.ledger)
        self.assertEqual(counts["cross_source_pmids"], ["9454332"])
        self.assertEqual(counts["cross_gene_pmids"], ["15149599"])
        bodnar = [r for r in self.ledger if r["pmid"] == "9454332"]
        self.assertEqual(len({r["biological_claim"] for r in bodnar}), 3)
        self.assertEqual({r["experiment_link_status"] for r in bodnar}, {"same_reported_study"})
        self.assertEqual(counts["within_source_repeated_pmids"]["GO"]["9454332"], 2)
        herbig = [r for r in self.ledger if r["pmid"] == "15149599"]
        self.assertEqual({r["experiment_link_status"] for r in herbig}, {"not_assessed"})

    def test_lookup_of_an_unbenchmarked_pmid_preserves_go_terms(self):
        answer = self.evidence.ask("Which GO rows cited PMID:19951988?")
        self.assertEqual(answer["evidence_type"], "citation_audit")
        self.assertEqual({r["id"] for r in answer["references"]},
                         {"GAF:133817", "GAF:133818", "PMID:19951988"})
        self.assertIn("GO:0090399", answer["answer"])
        self.assertIn("GO:0090403", answer["answer"])

    def test_missing_estimate_is_not_a_measured_negative(self):
        missing = self.evidence.ask("Give TERT partial correlation")
        negative = self.evidence.ask("Was SA-β-gal higher in p14ARF-transduced mammary cells?")
        self.assertEqual(missing["status"], "not_measured")
        self.assertIsNone(missing["facts"]["discovery_r"])
        self.assertTrue(missing["abstains"])
        self.assertEqual(negative["status"], "answered")
        self.assertIs(negative["facts"]["sa_beta_gal_increase_detected"], False)
        self.assertFalse(negative["abstains"])

    def test_scope_abstentions_are_structured(self):
        for question in (
            "Would suppressing p53 increase human lifespan?",
            "Is TERT recombination demonstrated by GO:0000722?",
            "Can the manual audit tell us whether PARP1 causes senescence?",
        ):
            with self.subTest(question=question):
                out = self.evidence.ask(question)
                self.assertEqual(out["status"], "insufficient_evidence")
                self.assertTrue(out["abstains"])
                self.assertTrue(out["references"])
                self.assertTrue(out["limitations"])
        unknown = self.evidence.ask("Should I take rapamycin?")
        self.assertEqual(unknown["status"], "unsupported_question")
        self.assertTrue(unknown["abstains"])

    def test_experiment_details_use_primary_citation_and_model(self):
        answer = self.evidence.ask("experiment 7157")
        self.assertEqual(answer["evidence_type"], "primary_experiment")
        self.assertIn("EJ", answer["facts"]["study_model"])
        publication = next(r for r in answer["references"] if r["id"] == "PMID:9275177")
        self.assertEqual(publication["doi"], "10.1073/pnas.94.18.9648")
        self.assertTrue(answer["facts"]["measurements"])


class ScoringTests(unittest.TestCase):
    def test_wrong_status_and_extra_citation_are_not_correct(self):
        case = {"id": "fixture", "question": "fixture?", "status": "not_measured",
                "evidence_type": "primary_experiment", "facts": {"detected": None},
                "references": ["source:1"]}
        output = {"answer": "There is not enough information.", "status": "insufficient_evidence",
                  "evidence_type": "primary_experiment", "facts": {"detected": None},
                  "abstains": True, "limitations": ["No result."],
                  "references": [{"id": "source:1"}, {"id": "unrelated"}]}
        item = evaluate([case], lambda _: output)["items"][0]
        self.assertFalse(item["answer_correct"])
        self.assertFalse(item["citations_correct"])
        self.assertTrue(item["evidence_type_correct"])
        self.assertFalse(item["correct_abstention"])
