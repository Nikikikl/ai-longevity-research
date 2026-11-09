import json
from importlib.util import find_spec
from pathlib import Path
import unittest
from unittest.mock import patch

from scripts import local_ai, local_retrieval
from scripts.research_assistant import answer_question


TERT_QUESTION = "Why are the Phase 7A partial correlations for TERT missing?"
MODEL_TERT_QUESTION = "Why are the partial correlations for TERT missing?"
FOXO3_QUESTION = "What happened when FOXO3 was knocked down in human dermal fibroblasts?"
FOLLOW_UP = "And what did they find about human longevity?"


def chat_response(answer, source_ids=(), *, status="answered"):
    content = json.dumps({"status": status, "answer": answer, "source_ids": source_ids})
    return {"done": True, "message": {"content": content}}


class RetrievalTests(unittest.TestCase):
    def test_overlap_questions_prefer_the_comparison_and_prior_art(self):
        for question, first in (
            ("что за результат в 113 генов мы нашли", "V2-L7-L7"),
            ("Что означает пересечение GenAge и CellAge?", "V2-L11-L11"),
            ("What did the 113 shared genes tell us?", "V2-L11-L11"),
        ):
            with self.subTest(question=question):
                passages = local_retrieval.retrieve(question)
                self.assertEqual(passages[0].id, first)
                self.assertTrue({"V2-L7-L7", "V2-L11-L11", "V2-L15-L15"} <= {p.id for p in passages})

    def test_project_summary_keeps_the_overlap_and_panel_result_together(self):
        for question in (
            "Какие главные результаты нашего исследования?",
            "What were the main findings of our research?",
        ):
            with self.subTest(question=question):
                passage = local_retrieval.retrieve(question)[0]
                self.assertEqual(passage.id, "V2-L7-L7")
                self.assertIn("matching a previously published count", passage.text)
                self.assertIn("did not outperform expression-matched controls", passage.text)

    def test_gene_overview_includes_distinct_evidence_types(self):
        for question in ("суть гена foxo3", "What is the function of FOXO3?"):
            with self.subTest(question=question):
                passages = local_retrieval.retrieve(question)
                self.assertEqual(passages[0].id, "V2-L52-L52")
                self.assertTrue({"P7D-L16-L16", "P7D-L18-L18"} <= {p.id for p in passages})
        focused = local_retrieval.retrieve("What is the role of FOXO3 in human longevity?")
        self.assertEqual(focused[0].id, "P7D-L18-L18")

    def test_113_gene_panel_with_an_explicit_rna_seq_question_keeps_specific_evidence(self):
        passages = local_retrieval.retrieve("Did the 113-gene RNA-seq panel outperform matched controls?")
        self.assertIn("V2-L23-L23", {p.id for p in passages})

    def test_relevance_and_determinism(self):
        cases = (
            ("What happened when researchers restored p53 in EJ carcinoma cells?", "GENES-L31-L31"),
            (TERT_QUESTION, "P7A-L17-L17"),
            (FOXO3_QUESTION, "P7D-L16-L16"),
            ("Доказывает ли нокдаун SIRT6 в хондроцитах репликативное старение?", "P7D-L22-L22"),
        )
        for question, expected in cases:
            with self.subTest(question=question):
                result = local_retrieval.retrieve(question)
                self.assertEqual(result[0].id, expected)
                self.assertEqual(result, local_retrieval.retrieve(question))
                self.assertLessEqual(len(result), local_retrieval.MAX_PASSAGES)
                self.assertLessEqual(sum(len(p.text) for p in result), local_retrieval.MAX_EVIDENCE_CHARS)

    def test_links_and_ids_point_to_actual_lines(self):
        passages = local_retrieval.read_passages()
        self.assertEqual({p.path for p in passages}, set(local_retrieval.REPORTS.values()))
        self.assertEqual(len({p.id for p in passages}), len(passages))
        for passage in passages:
            with self.subTest(id=passage.id):
                path = Path(local_retrieval.ROOT, passage.path)
                source = "\n".join(path.read_text(encoding="utf-8").splitlines()[passage.start - 1:passage.end])
                self.assertEqual(passage.text, local_retrieval.MARKDOWN_LINK.sub(r"\1", source))
                self.assertLessEqual(len(passage.text), local_retrieval.MAX_PASSAGE_CHARS)
                self.assertEqual(passage.id, f"{passage.id.split('-')[0]}-L{passage.start}-L{passage.end}")
                anchor = f"L{passage.start}"
                if passage.end != passage.start:
                    anchor += f"-L{passage.end}"
                self.assertEqual(
                    passage.url,
                    "https://github.com/Nikikikl/ai-longevity-research/blob/"
                    f"ba0365a234d4b0b4bf16bc8aa5ce5049dbf7819a/{passage.path}"
                    f"?plain=1#{anchor}",
                )

    def test_follow_up_uses_prior_gene_and_current_topic(self):
        result = local_retrieval.retrieve(FOLLOW_UP, [FOXO3_QUESTION])
        self.assertEqual(result[0].id, "P7D-L18-L18")
        self.assertIn("rs2802292", result[0].text)
        result = local_retrieval.retrieve(
            "Did it replicate?", ["What were the Phase 7A discovery and validation partial correlations for TP53?"]
        )
        self.assertIn("P7A-L17-L17", {p.id for p in result})


class LocalAnswerTests(unittest.TestCase):
    @patch("scripts.local_ai.request")
    def test_phase7a_panel_counts_keep_their_denominators(self, request):
        for question in (
            "How many of the original panel genes were eligible in both RNA-seq cohorts, "
            "and what did that comparison actually measure?",
            "How many of the 113 genes passed eligibility in both cohorts?",
            "What does 63 out of 109 mean?",
            "Did only 63 genes pass the expression filter?",
            "В фазе 7А чем 109 генов, прошедших отбор, отличаются от 63 генов с совпавшим направлением связи?",
        ):
            with self.subTest(question=question):
                result = local_ai.answer_local(question)
                self.assertEqual(result.status, "answered")
                if question.startswith("В"):
                    self.assertIn("109 из 113", result.text)
                    self.assertIn("63 из 109", result.text)
                else:
                    self.assertIn("109 of 113", result.text)
                    self.assertIn("63 of 109", result.text)
                self.assertTrue({"V2-L21-L21", "V2-L23-L23"} <= {p.id for p in result.cited})
                if "actually measure" in question:
                    self.assertIn("donor chronological age", result.text)
                    self.assertIn("expression abundance and detection", result.text.casefold())
        request.assert_not_called()

    @patch("scripts.local_ai.request")
    def test_phase7a_panel_methods_distinguish_outcome_and_matching(self, request):
        for question in (
            "Was chronological age or expression abundance the outcome of the Phase 7A association analysis?",
            "What variables were used to match the control panels?",
        ):
            with self.subTest(question=question):
                result = local_ai.answer_local(question)
                self.assertEqual(result.status, "answered")
                self.assertIn("donor chronological age", result.text)
                self.assertIn("expression abundance and detection", result.text.casefold())
                self.assertIn("sequencing platform in discovery", result.text)
                self.assertTrue({"V2-L21-L21", "V2-L23-L23", "P7A-L34-L34"} <= {p.id for p in result.cited})
        request.assert_not_called()

    @patch("scripts.local_ai.request")
    def test_phase7a_matched_comparison_reports_the_frozen_rule_and_scope(self, request):
        result = local_ai.answer_local("What did the Phase 7A matched-panel comparison find, and what are its limitations?")
        self.assertEqual(result.status, "answered")
        for text in ("0.00464", "0.00685", "prespecified decision rule", "these two cohorts", "co-expression"):
            self.assertIn(text, result.text)
        self.assertEqual({p.id for p in result.cited}, {"V2-L23-L23", "P7A-L34-L34"})
        request.assert_not_called()

    def test_phase7a_panel_route_leaves_unrelated_metrics_and_scopes_alone(self):
        for question in (
            "What does 22 out of 30 mean?",
            "What variables were used to match the control panels in a mouse experiment?",
            "Did Phase 7A Ridge prediction outperform expression-matched panels?",
        ):
            with self.subTest(question=question):
                self.assertIsNone(local_ai.phase7a_panel_answer(question, False))

    @patch("scripts.local_ai.request")
    def test_phase7a_missing_estimates_use_the_frozen_ledger(self, request):
        cases = (
            ("В таблице Phase 7A для TERT пустые значения. Их надо читать как нулевую корреляцию?",
             "P7A-CSV-L103-L103", ("не оценивалась", "измеренный ноль", "фильтр экспрессии")),
            (TERT_QUESTION, "P7A-CSV-L103-L103", ("not estimated", "measured zero", "expression filter")),
            ("In Phase 7A, do blank correlation estimates for FGF21 mean zero?",
             "P7A-CSV-L29-L29", ("not estimated", "passed eligibility", "expression filter")),
            ("Как в Phase 7A для TERT отличить измеренный ноль от отсутствующей оценки корреляции?",
             "P7A-CSV-L103-L103", ("не оценивалась", "измеренный ноль", "фильтр экспрессии")),
        )
        for question, source, phrases in cases:
            with self.subTest(question=question):
                result = local_ai.answer_local(question)
                self.assertEqual(result.status, "answered")
                self.assertEqual(result.cited[0].id, source)
                self.assertNotIn("r =", result.text)
                for phrase in phrases:
                    self.assertIn(phrase, result.text)
                if question == TERT_QUESTION:
                    self.assertIn("P7A-L17-L17", {p.id for p in result.cited})
        request.assert_not_called()

    @patch("scripts.local_ai.request")
    def test_phase7a_measured_near_zero_stays_a_measurement(self, request):
        result = local_ai.answer_local(
            "Was the Phase 7A discovery partial correlation for CDKN2A a measured value near zero?"
        )
        self.assertEqual(result.status, "answered")
        self.assertIn("r = -0.001464046161", result.text)
        self.assertNotIn("not estimated", result.text)
        source = result.cited[0]
        self.assertEqual(source.id, "P7A-CSV-L15-L15")
        self.assertTrue(source.url.endswith("/reports/phase7_gene_associations.csv?plain=1#L15"))
        self.assertIn("1029,CDKN2A,eligible,eligible,-0.001464046161", source.text)
        request.assert_not_called()

    @patch("scripts.local_ai.request")
    def test_phase7a_gene_outside_the_ledger_abstains(self, request):
        result = local_ai.answer_local("What were the Phase 7A partial correlations for CFTR?")
        self.assertEqual(result.status, "insufficient_evidence")
        self.assertIn("no row for CFTR", result.text)
        self.assertEqual([p.id for p in result.cited], ["P7A-L7-L7"])
        request.assert_not_called()

    @patch("scripts.local_ai.request")
    def test_russian_cell_terminology_is_scoped_to_relevant_questions(self, request):
        for question, expect_glossary in (
            ("Что показал нокдаун SIRT6 в хондроцитах?", True),
            ("Что означает пересечение GenAge и CellAge?", False),
        ):
            with self.subTest(question=question):
                request.side_effect = [
                    {"models": [{"name": local_ai.MODEL}]},
                    chat_response("Недостаточно данных.", status="insufficient_evidence"),
                ]
                local_ai.answer_local(question)
                system_prompt = request.call_args.args[2]["messages"][0]["content"]
                self.assertEqual("повреждение ДНК" in system_prompt, expect_glossary)

    @patch("scripts.local_ai.HTTPConnection")
    def test_unrelated_question_abstains_without_inference(self, connection):
        for question in ("How long does it take to bake bread?", "What temperature should I use to bake sourdough bread?",
                         "пока", "Какие главные результаты исследования сна?"):
            with self.subTest(question=question):
                result = local_ai.answer_local(question, [FOXO3_QUESTION])
                self.assertEqual(result.status, "insufficient_evidence")
                self.assertEqual(result.passages, ())
                self.assertEqual(result.cited, ())
        connection.assert_not_called()

    @patch("scripts.local_ai.request")
    def test_only_supplied_passages_can_become_source_cards(self, request):
        valid_id = local_retrieval.retrieve(MODEL_TERT_QUESTION)[0].id
        for answer, ids, expected in (
            ("TERT failed the expression filter in both cohorts.", [valid_id], "answered"),
            ("This is a claim.", [valid_id, "P7A-L999-L999"], "citation_error"),
            ("This is a claim.", ["P7D-L22-L22"], "citation_error"),
            ("No citation here.", [], "citation_error"),
            (f"Inline reference ({valid_id}).", [valid_id], "citation_error"),
            (f"Fake link [{valid_id}](https://example.com).", [valid_id], "citation_error"),
        ):
            with self.subTest(expected=expected, answer=answer):
                response = chat_response(answer, ids)
                request.side_effect = [{"models": [{"name": local_ai.MODEL}]}, response, response]
                result = local_ai.answer_local(MODEL_TERT_QUESTION)
                self.assertEqual(result.status, expected)
                if expected == "answered":
                    self.assertEqual(result.text, answer)
                    self.assertEqual(result.cited, (result.passages[0],))
                else:
                    self.assertEqual(result.cited, ())
                    self.assertNotEqual(result.text, answer)
                self.assertTrue(result.passages)

    @patch("scripts.local_ai.request")
    def test_model_can_abstain_when_excerpts_do_not_support_a_conclusion(self, request):
        request.side_effect = [
            {"models": [{"model": local_ai.MODEL}]},
            chat_response("These passages lack a human lifespan intervention.", status="insufficient_evidence"),
        ]
        result = local_ai.answer_local("Does TERT help people live longer?")
        self.assertEqual(result.status, "insufficient_evidence")
        self.assertTrue(result.passages)
        self.assertEqual(result.cited, ())

    @patch("scripts.local_ai.HTTPConnection")
    def test_missing_service_and_timeouts(self, connection):
        for error, status in (
            (ConnectionRefusedError(), "unavailable"), (PermissionError(), "unavailable"),
            (TimeoutError(), "timeout"),
        ):
            with self.subTest(status=status):
                connection.return_value.request.side_effect = error
                result = local_ai.answer_local(MODEL_TERT_QUESTION)
                self.assertEqual(result.status, status)
                self.assertEqual(result.cited, ())
                connection.assert_called_with("127.0.0.1", 11434, timeout=local_ai.STATUS_TIMEOUT)

    @patch("scripts.local_ai.HTTPConnection")
    def test_inference_uses_longer_socket_timeout(self, connection):
        response = connection.return_value.getresponse
        response.return_value.status = 200
        response.return_value.read.return_value = json.dumps({"models": [{"name": local_ai.MODEL}]}).encode()
        response.side_effect = [response.return_value, TimeoutError()]
        self.assertEqual(local_ai.answer_local(MODEL_TERT_QUESTION).status, "timeout")
        connection.assert_called_with("127.0.0.1", 11434, timeout=local_ai.CHAT_TIMEOUT)
        self.assertEqual(connection.call_count, 2)

    @patch("scripts.local_ai.request")
    def test_missing_and_remote_models_prevent_chat(self, request):
        for models, status in (
            ([], "missing_model"),
            ([{"name": local_ai.MODEL, "remote_host": "https://example.com"}], "remote_model"),
        ):
            with self.subTest(status=status):
                request.reset_mock()
                request.return_value = {"models": models}
                result = local_ai.answer_local(MODEL_TERT_QUESTION)
                self.assertEqual(result.status, status)
                self.assertIn(f"ollama pull {local_ai.MODEL}", result.text)
                request.assert_called_once_with("/api/tags", local_ai.STATUS_TIMEOUT)

    @patch("scripts.local_ai.request")
    def test_conversation_and_inference_budgets(self, request):
        previous = ["DO NOT SEND", FOXO3_QUESTION + " " * 500 + "TRUNCATE ME", "Did it change cell morphology?"]
        request.side_effect = [
            {"models": [{"name": local_ai.MODEL}]},
            chat_response("The supplied evidence is insufficient.", status="insufficient_evidence"),
        ]
        question = FOLLOW_UP + " " * 1200 + "TRUNCATE ME"
        local_ai.answer_local(question, previous)
        path, timeout, payload = request.call_args.args
        self.assertEqual((path, timeout), ("/api/chat", local_ai.CHAT_TIMEOUT))
        self.assertEqual(payload["model"], local_ai.MODEL)
        self.assertFalse(payload["think"])
        self.assertFalse(payload["stream"])
        self.assertEqual(payload["options"], {"num_ctx": 4096, "num_predict": 384, "temperature": 0})
        messages = payload["messages"]
        self.assertEqual([message["role"] for message in messages], ["system", "user"])
        context = json.loads(messages[1]["content"])
        self.assertEqual(len(context["earlier_questions"]), local_ai.MAX_PRIOR_QUESTIONS)
        self.assertEqual(context["earlier_questions"][0], previous[1][:local_ai.MAX_PRIOR_CHARS])
        self.assertEqual(context["question"], question[:local_ai.MAX_QUESTION_CHARS])
        retrieved = local_retrieval.retrieve(context["question"], context["earlier_questions"])
        self.assertEqual(context["primary_excerpt"]["id"], retrieved[0].id)
        self.assertNotIn("TRUNCATE ME", messages[1]["content"])
        schema = payload["format"]
        self.assertEqual(set(schema["required"]), {"status", "answer", "source_ids"})
        ids = [p["id"] for p in (context["primary_excerpt"], *context["other_excerpts"])]
        self.assertIn("P7D-L18-L18", ids)
        self.assertEqual(schema["properties"]["source_ids"]["items"]["enum"], ids)
        self.assertEqual(schema["properties"]["source_ids"]["maxItems"], len(ids))

    @patch("scripts.local_ai.request")
    def test_truncated_or_malformed_answers_are_withheld_after_one_correction(self, request):
        for response in (
            {"done": False},
            {"done": True, "message": {"content": "{broken"}},
            {"done": True, "message": {"content": '{"status":"answered","answer":"Legacy response"}'}},
            chat_response("Invalid source_ids type", [17]),
        ):
            with self.subTest(response=response):
                request.reset_mock()
                request.side_effect = [{"models": [{"name": local_ai.MODEL}]}, response, response]
                result = local_ai.answer_local(MODEL_TERT_QUESTION)
                self.assertEqual(result.status, "invalid_response")
                self.assertEqual(result.cited, ())
                self.assertTrue(result.passages)
                self.assertEqual(request.call_count, 3)

    @patch("scripts.local_ai.request")
    def test_correction_reuses_evidence_and_accepts_only_valid_replacement(self, request):
        passage = local_retrieval.retrieve(MODEL_TERT_QUESTION)[0]
        request.side_effect = [
            {"models": [{"name": local_ai.MODEL}]},
            chat_response("Discard this failed answer.", ["P7A-L999-L999"]),
            chat_response("TERT failed the filter in both cohorts.", [passage.id]),
        ]
        result = local_ai.answer_local(MODEL_TERT_QUESTION)
        self.assertEqual(result.status, "answered")
        self.assertEqual(result.cited, (passage,))
        self.assertEqual(result.text, "TERT failed the filter in both cohorts.")
        self.assertEqual(request.call_count, 3)
        original, correction = (call.args for call in request.call_args_list[1:])
        self.assertEqual(correction[:2], ("/api/chat", local_ai.CORRECTION_TIMEOUT))
        self.assertLess(correction[1], original[1])
        self.assertEqual(correction[2]["format"], original[2]["format"])
        self.assertEqual(correction[2]["messages"][1:], original[2]["messages"][1:])
        self.assertIn("failed validation", correction[2]["messages"][0]["content"])
        self.assertNotIn("Discard this failed answer.", str(correction[2]))


@unittest.skipUnless(find_spec("streamlit"), "Install requirements-ui.txt to run Streamlit tests")
class LocalUITests(unittest.TestCase):
    @patch("scripts.local_ai.request")
    def test_ui_shows_trusted_links_and_withholds_invalid_citations(self, request):
        from streamlit.testing.v1 import AppTest

        passage = local_retrieval.retrieve(MODEL_TERT_QUESTION)[0]
        models = {"models": [{"name": local_ai.MODEL}]}
        good = chat_response("TERT failed the filter in both cohorts.", [passage.id])
        bad = chat_response("An invented claim.", ["P7A-L999-L999"])
        request.side_effect = [models, models, good, models, models, bad, bad, models]
        app = AppTest.from_file(str(local_retrieval.ROOT / "web_ui/app.py")).run()
        app.radio[0].set_value("Local AI — Experimental").run()
        app.chat_input[0].set_value(MODEL_TERT_QUESTION).run()
        self.assertFalse(app.exception)
        self.assertTrue(any(e.label == "Retrieved evidence" for e in app.expander))
        self.assertTrue(any(passage.url in html.proto.body for html in app.get("html")))
        self.assertTrue(any(passage.url in link.value for link in app.markdown))
        app.chat_input[0].set_value(MODEL_TERT_QUESTION).run()
        self.assertFalse(app.exception)
        self.assertTrue(any("withheld" in warning.value for warning in app.warning))
        self.assertFalse(any("P7A-L999-L999" in html.proto.body for html in app.get("html")))
        self.assertFalse(any("An invented claim" in html.proto.body for html in app.get("html")))

    @patch("scripts.local_ai.check_model")
    def test_existing_modes_never_contact_ollama(self, check_model):
        from streamlit.testing.v1 import AppTest

        app = AppTest.from_file(str(local_retrieval.ROOT / "web_ui/app.py")).run()
        for label, mode, question in (
            ("Research Q&A", "research", TERT_QUESTION),
            ("Evidence records", "records", "record GAF:591445"),
            ("Research Q&A", "research", "Did it replicate?"),
        ):
            with self.subTest(mode=mode, question=question):
                app.radio[0].set_value(label).run()
                app.chat_input[0].set_value(question).run()
                self.assertFalse(app.exception)
                self.assertEqual(app.session_state.chat_turns[-1][2], answer_question(question, mode=mode))
        check_model.assert_not_called()

    @patch("scripts.local_ai.check_model")
    @patch("scripts.local_ai.answer_local")
    def test_local_history_is_bounded_and_clear_resets_it(self, answer, check_model):
        from streamlit.testing.v1 import AppTest
        from web_ui.app import LOCAL_MODE, MAX_LOCAL_TURNS

        answer.return_value = local_ai.LocalAnswer("insufficient_evidence", "No matching passages.")
        app = AppTest.from_file(str(local_retrieval.ROOT / "web_ui/app.py")).run()
        app.chat_input[0].set_value(TERT_QUESTION).run()
        app.radio[0].set_value(LOCAL_MODE).run()
        self.assertIn(f"Ollama connected · {local_ai.MODEL} available", [c.value for c in app.caption])
        for index in range(MAX_LOCAL_TURNS + 1):
            app.chat_input[0].set_value(f"Local question {index}").run()
            self.assertFalse(app.exception)
        turns = app.session_state.chat_turns
        self.assertEqual(len(turns), MAX_LOCAL_TURNS + 1)
        self.assertEqual(turns[0][0], TERT_QUESTION)
        self.assertEqual(turns[1][0], "Local question 1")
        self.assertEqual(answer.call_args_list[0].args, ("Local question 0", []))
        self.assertEqual(answer.call_args.args[1], ["Local question 4", "Local question 5"])
        app.button(key="clear").click().run()
        self.assertEqual(app.session_state.chat_turns, [])
        app.chat_input[0].set_value(FOLLOW_UP).run()
        answer.assert_called_with(FOLLOW_UP, [])
