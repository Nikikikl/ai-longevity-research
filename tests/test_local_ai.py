import json
from importlib.util import find_spec
from pathlib import Path
import unittest
from unittest.mock import patch

from scripts import local_ai, local_retrieval
from scripts.research_assistant import answer_question


TERT_QUESTION = "Why are the Phase 7A partial correlations for TERT missing?"
FOXO3_QUESTION = "What happened when FOXO3 was knocked down in human dermal fibroblasts?"
FOLLOW_UP = "And what did they find about human longevity?"


def chat_response(answer, status="answered"):
    return {"done": True, "message": {"content": json.dumps({"status": status, "answer": answer})}}


class RetrievalTests(unittest.TestCase):
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
    @patch("scripts.local_ai.HTTPConnection")
    def test_unrelated_question_abstains_without_inference(self, connection):
        result = local_ai.answer_local("How long does it take to bake bread?", [FOXO3_QUESTION])
        self.assertEqual(result.status, "insufficient_evidence")
        self.assertEqual(result.passages, ())
        self.assertEqual(result.cited, ())
        connection.assert_not_called()

    @patch("scripts.local_ai.request")
    def test_only_supplied_passages_can_become_source_cards(self, request):
        valid_id = local_retrieval.retrieve(TERT_QUESTION)[0].id
        for answer, expected in (
            (f"TERT failed the expression filter in both cohorts [{valid_id}].", "answered"),
            (f"A claim [{valid_id}] and an invented citation [P7A-L999-L999].", "citation_error"),
            ("No citation here.", "citation_error"),
            (f"Fake link [{valid_id}](https://example.com).", "citation_error"),
        ):
            with self.subTest(expected=expected, answer=answer):
                request.side_effect = [{"models": [{"name": local_ai.MODEL}]}, chat_response(answer)]
                result = local_ai.answer_local(TERT_QUESTION)
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
            chat_response("These passages lack a human lifespan intervention.", "insufficient_evidence"),
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
                result = local_ai.answer_local(TERT_QUESTION)
                self.assertEqual(result.status, status)
                self.assertEqual(result.cited, ())
                connection.assert_called_with("127.0.0.1", 11434, timeout=local_ai.STATUS_TIMEOUT)

    @patch("scripts.local_ai.HTTPConnection")
    def test_inference_uses_longer_socket_timeout(self, connection):
        response = connection.return_value.getresponse
        response.return_value.status = 200
        response.return_value.read.return_value = json.dumps({"models": [{"name": local_ai.MODEL}]}).encode()
        response.side_effect = [response.return_value, TimeoutError()]
        self.assertEqual(local_ai.answer_local(TERT_QUESTION).status, "timeout")
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
                result = local_ai.answer_local(TERT_QUESTION)
                self.assertEqual(result.status, status)
                self.assertIn(f"ollama pull {local_ai.MODEL}", result.text)
                request.assert_called_once_with("/api/tags", local_ai.STATUS_TIMEOUT)

    @patch("scripts.local_ai.request")
    def test_conversation_and_inference_budgets(self, request):
        previous = ["DO NOT SEND", FOXO3_QUESTION + " " * 500 + "TRUNCATE ME", "Did it change cell morphology?"]
        request.side_effect = [
            {"models": [{"name": local_ai.MODEL}]},
            chat_response("The supplied evidence is insufficient.", "insufficient_evidence"),
        ]
        question = FOLLOW_UP + " " * 1200 + "TRUNCATE ME"
        local_ai.answer_local(question, previous)
        path, timeout, payload = request.call_args.args
        self.assertEqual((path, timeout), ("/api/chat", local_ai.CHAT_TIMEOUT))
        self.assertEqual(payload["model"], local_ai.MODEL)
        self.assertFalse(payload["think"])
        self.assertFalse(payload["stream"])
        self.assertEqual(payload["options"], {"num_ctx": 4096, "num_predict": 384, "temperature": 0.1})
        messages = payload["messages"]
        self.assertEqual([message["role"] for message in messages], ["system", "user"])
        context = json.loads(messages[1]["content"])
        self.assertEqual(len(context["earlier_questions"]), local_ai.MAX_PRIOR_QUESTIONS)
        self.assertEqual(context["earlier_questions"][0], previous[1][:local_ai.MAX_PRIOR_CHARS])
        self.assertEqual(context["question"], question[:local_ai.MAX_QUESTION_CHARS])
        self.assertIn("P7D-L18-L18", {p["id"] for p in context["passages"]})
        self.assertNotIn("TRUNCATE ME", messages[1]["content"])

    @patch("scripts.local_ai.request")
    def test_truncated_or_malformed_answers_are_withheld(self, request):
        for response in ({"done": False}, {"done": True, "message": {"content": "{broken"}}):
            request.side_effect = [{"models": [{"name": local_ai.MODEL}]}, response]
            result = local_ai.answer_local(TERT_QUESTION)
            self.assertEqual(result.status, "invalid_response")
            self.assertEqual(result.cited, ())


@unittest.skipUnless(find_spec("streamlit"), "Install requirements-ui.txt to run Streamlit tests")
class LocalUITests(unittest.TestCase):
    @patch("scripts.local_ai.request")
    def test_ui_shows_trusted_links_and_withholds_invalid_citations(self, request):
        from streamlit.testing.v1 import AppTest

        passage = local_retrieval.retrieve(TERT_QUESTION)[0]
        models = {"models": [{"name": local_ai.MODEL}]}
        good = chat_response(f"TERT failed the filter in both cohorts [{passage.id}].")
        bad = chat_response("An invented claim [P7A-L999-L999].")
        request.side_effect = [models, models, good, models, models, bad, models]
        app = AppTest.from_file(str(local_retrieval.ROOT / "web_ui/app.py")).run()
        app.radio[0].set_value("Local AI — Experimental").run()
        app.chat_input[0].set_value(TERT_QUESTION).run()
        self.assertFalse(app.exception)
        self.assertTrue(any(e.label == "Retrieved evidence" for e in app.expander))
        self.assertTrue(any(passage.url in html.proto.body for html in app.get("html")))
        self.assertTrue(any(passage.url in link.value for link in app.markdown))
        app.chat_input[0].set_value(TERT_QUESTION).run()
        self.assertFalse(app.exception)
        self.assertTrue(any("withheld" in warning.value for warning in app.warning))
        self.assertFalse(any("P7A-L999-L999" in html.proto.body for html in app.get("html")))

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
