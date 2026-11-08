"""Local Streamlit interface for scientific evidence lookup and research chat."""
from html import escape
from pathlib import Path

import streamlit as st

from scripts.local_ai import MAX_PRIOR_QUESTIONS, MAX_QUESTION_CHARS, MODEL, OllamaError, answer_local, check_model
from scripts.research_assistant import answer_question
from web_ui.presentation import answer_html, reference_html

LOCAL_MODE = "Local AI — Experimental"
MAX_LOCAL_TURNS = 6
MODES = {"Research Q&A": "research", "Evidence records": "records", LOCAL_MODE: "local"}
MODE_PHASES = {"Research Q&A": "7C", "Evidence records": "7D", LOCAL_MODE: "8A"}

SCOPE = {
    "Research Q&A": "Phase 7C · English questions about the RNA-seq panel and the TP53, CDKN2A and TERT audit.",
    "Evidence records": "Phase 7D · Use `record <ID>`, `pmid <number>`, `cellage <gene>` or `association <gene>`. "
                        "Gene commands cover FOXO3 and SIRT6.",
    LOCAL_MODE: f"Phase 8A · {MODEL} via Ollama · Experimental answers. Verify claims against the retrieved reports.",
}
EXAMPLES = {
    "Research Q&A": ("What was the sign agreement?",
                     "TERT partial correlations?"),
    "Evidence records": ("pmid 25819580", "record GAF:591445"),
    LOCAL_MODE: ("Why are TERT’s Phase 7A correlations missing?",
                 "Что показал нокдаун SIRT6 в хондроцитах?"),
}
PLACEHOLDERS = {
    "Research Q&A": "Ask a focused research question…",
    "Evidence records": "Enter an evidence command…",
    LOCAL_MODE: "Ask about a gene, study or result…",
}


def submit(question, mode):
    if question := question.strip():
        turns = st.session_state.chat_turns
        if mode == LOCAL_MODE:
            local_indices = [index for index, turn in enumerate(turns) if turn[1] == LOCAL_MODE]
            history = [turns[index][0] for index in local_indices[-MAX_PRIOR_QUESTIONS:]]
            with st.spinner("Searching the reports and querying local Ollama…"):
                result = answer_local(question, history)
            if len(local_indices) >= MAX_LOCAL_TURNS:
                del turns[local_indices[0]]
        else:
            result = answer_question(question, mode=MODES[mode])
        turns.append((question, mode, result))


def submit_input():
    submit(st.session_state.prompt, st.session_state.evidence_mode)


def submit_example(question, mode):
    st.session_state.evidence_mode = mode
    submit(question, mode)


def clear_conversation():
    st.session_state.chat_turns = []
    st.session_state.pop("prompt", None)


def example_buttons(mode, prefix):
    for index, question in enumerate(EXAMPLES[mode]):
        st.button(question, icon=":material/arrow_outward:", width="stretch", key=f"{prefix}-{index}",
                  on_click=submit_example, args=(question, mode))


def welcome():
    st.html(
        '<section class="hero"><div class="hero-copy"><span class="eyebrow">AGING GENOMICS / EVIDENCE</span>'
        '<h1>Longevity Research<br>Assistant</h1>'
        '<p>Explore aging and senescence claims through measured outcomes, curated records and their citations.</p>'
        '</div><span class="hero-art" aria-hidden="true"></span></section>'
    )
    st.html('<div class="examples-heading"><h2>Try an example</h2>'
            '<p>Each example opens in its evidence mode.</p></div>')
    with st.container(key="examples"):
        for column, mode in zip(st.columns(len(MODES), gap="medium"), MODES):
            with column:
                st.html(f'<div class="example-mode">{escape(mode)}</div>')
                example_buttons(mode, mode)


def show_local_answer(result):
    if result.status == "insufficient_evidence":
        st.warning("Insufficient evidence")
    if result.status in {"answered", "insufficient_evidence"}:
        st.html(f'<div class="answer-copy">{escape(result.text)}</div>')
    elif result.status == "citation_error":
        st.warning(result.text)
    else:
        st.error(result.text)
    if result.cited:
        links = "".join(reference_html({"id": passage.id, "url": passage.url}) for passage in result.cited)
        st.html(f'<div class="scientific-answer"><h4>Cited report passages</h4><ul class="references">{links}</ul></div>')
    if result.passages:
        with st.expander("Retrieved evidence"):
            for passage in result.passages:
                st.caption(f"{passage.id} · {passage.heading}")
                st.markdown(f"[{passage.path}, lines {passage.start}–{passage.end}]({passage.url})")
                st.html(f'<div class="answer-copy">{escape(passage.text)}</div>')


def show_turn(index, question, mode, result):
    with st.container(key=f"user-turn-{index}"):
        with st.chat_message("user", avatar=":material/person:"):
            st.html(f'<div class="user-copy">{escape(question)}</div>')
    with st.container(key=f"answer-turn-{index}"):
        with st.chat_message("assistant", avatar=":material/science:"):
            st.html(f'<div class="turn-mode {MODES[mode]}"><span>Phase {MODE_PHASES[mode]}</span>'
                    f'<strong>{escape(mode)}</strong></div>')
            if mode == LOCAL_MODE:
                show_local_answer(result)
            else:
                st.html(answer_html(result))
                with st.expander("Technical details · JSON"):
                    st.json(result, expanded=False)


def main():
    st.set_page_config(page_title="Longevity Research Assistant", page_icon="🧬", layout="wide")
    st.session_state.setdefault("chat_turns", [])
    st.session_state.setdefault("evidence_mode", next(iter(MODES)))
    st.html(Path(__file__).with_name("style.css"))

    turns = st.session_state.chat_turns
    heading = "Longevity Research Assistant" if turns else "Research workspace"
    st.html('<div class="workspace-bar"><div class="brand"><span class="brand-mark" aria-hidden="true"></span>'
            f'<span>{heading}</span></div><span class="local-indicator"><i></i> Local session</span></div>')

    with st.container(key="controls"):
        selector, actions = st.columns([4, 2], vertical_alignment="bottom")
        with selector:
            mode = st.radio("Evidence mode", list(MODES), horizontal=True, key="evidence_mode")
        with actions:
            st.button("Clear conversation", icon=":material/delete_outline:", key="clear",
                      on_click=clear_conversation, disabled=not turns, width="stretch")
        st.caption(SCOPE[mode])
        if mode == LOCAL_MODE:
            try:
                check_model()
            except OllamaError as error:
                st.warning(str(error))
                st.button("Check Ollama again", key="retry-ollama")
            else:
                st.caption(f"Ollama connected · {MODEL} available")

    if turns:
        for index, (question, source_mode, result) in enumerate(turns):
            show_turn(index, question, source_mode, result)
        if turns[-1][1] != LOCAL_MODE and turns[-1][2]["status"] == "unsupported_question":
            st.caption(f"Try a supported example in {mode}")
            example_buttons(mode, "unsupported")
    else:
        welcome()

    st.chat_input(PLACEHOLDERS[mode], key="prompt", max_chars=MAX_QUESTION_CHARS, on_submit=submit_input)


if __name__ == "__main__":
    main()
