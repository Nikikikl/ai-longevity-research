import json
from pathlib import Path
import subprocess
import sys
import unittest

from scripts.research_assistant import answer_question, reference_links
from web_ui.presentation import answer_html, numerical_findings, reference_html

ROOT = Path(__file__).resolve().parents[1]


class AdapterTests(unittest.TestCase):
    def test_adapter_matches_both_existing_cli_responses(self):
        queries = (
            ("research", "scripts.phase7c_qa", "What were the partial correlations for TERT?"),
            ("records", "scripts.phase7d_evidence", "record GAF:591445"),
        )
        for mode, module, question in queries:
            with self.subTest(mode=mode):
                cli = subprocess.check_output([sys.executable, "-B", "-m", module, question], cwd=ROOT)
                self.assertEqual(answer_question(question, mode=mode), json.loads(cli))

    def test_lookup_does_not_fall_back_to_another_mode(self):
        query = "record GAF:591445"
        self.assertEqual(answer_question(query)["status"], "unsupported_question")
        self.assertEqual(answer_question(query, mode="records")["status"], "answered")
        with self.assertRaises(ValueError):
            answer_question(query, mode="unknown")


class AnswerPresentationTests(unittest.TestCase):
    def test_local_and_public_references_remain_distinct(self):
        local = reference_html({"id": "P7A:gene:7015", "path": "reports/phase7_gene_associations.csv",
                                "locator": "Entrez Gene ID 7015"})
        self.assertIn("P7A:gene:7015", local)
        self.assertIn("Local source", local)
        self.assertIn("Entrez Gene ID 7015", local)
        self.assertNotIn("href=", local)

        linked = reference_html({"id": "GAF:591445", "pmid": "25541994",
                                 "reviewed_text_url": "https://journals.plos.org/plosone/article?id=test&view=1"})
        self.assertIn('href="https://pubmed.ncbi.nlm.nih.gov/25541994/"', linked)
        self.assertIn("id=test&amp;view=1", linked)

    def test_link_resolver_rejects_local_and_malformed_targets(self):
        urls = ("file:///etc/hosts", "http://127.0.0.1:8501", "https://foo.local/",
                "javascript:alert(1)", "https://[malformed", "https://example.org:bad/")
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(reference_links({"url": url}), [])
        url = "https://pubmed.ncbi.nlm.nih.gov/25541994/"
        self.assertEqual(reference_links({"url": url, "reviewed_text_url": url}), [("Public source", url)])

    def test_missing_measurement_is_not_displayed_as_zero(self):
        result = answer_question("What were the partial correlations for TERT?")
        self.assertEqual(list(numerical_findings(result["facts"], result["status"])),
                         [("Discovery partial r", "Not measured"), ("Validation partial r", "Not measured")])
        self.assertEqual(list(numerical_findings({"validation": 0, "decision_met": False}, "answered")),
                         [("Validation donors", "0")])

    def test_statuses_render_without_claims_for_unsupported_questions(self):
        queries = (
            ("research", "What was the sign agreement between cohorts?", "Answered"),
            ("research", "What were the partial correlations for TERT?", "Not measured"),
            ("records", "record GAF:591459", "Insufficient evidence"),
            ("research", "Write me a poem about telescopes", "Unsupported question"),
        )
        for mode, query, label in queries:
            with self.subTest(label=label):
                result = answer_question(query, mode=mode)
                html = answer_html(result)
                self.assertIn(f'class="status {result["status"]}">{label}</span>', html)
                self.assertIn("<h4>Limitations</h4>", html)
                if result["status"] == "unsupported_question":
                    self.assertIn("could not interpret", html)
                    self.assertIn("Scope references", html)
                    self.assertNotIn(result["answer"], html)
                else:
                    self.assertIn("Sources", html)

    def test_markup_in_answer_and_source_is_rendered_as_text(self):
        result = answer_question("What was the sign agreement between cohorts?")
        result["answer"] = "<script>bad()</script>"
        result["references"][0]["locator"] = "<i>source</i>"
        html = answer_html(result)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("&lt;i&gt;source&lt;/i&gt;", html)
        self.assertNotIn("<script>", html)
