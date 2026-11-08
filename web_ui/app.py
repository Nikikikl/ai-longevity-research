"""Local Streamlit interface for the existing deterministic evidence lookups."""
from html import escape
from pathlib import Path

import streamlit as st

from scripts.research_assistant import answer_question
from web_ui.presentation import answer_html

MODES = {"Research Q&A": "research", "Evidence records": "records"}

SCOPE = {
    "Research Q&A": "Phase 7C · English questions about the RNA-seq panel and the TP53, CDKN2A and TERT audit.",
    "Evidence records": "Phase 7D · Use `record <ID>`, `pmid <number>`, `cellage <gene>` or `association <gene>`. "
                        "Gene commands cover FOXO3 and SIRT6.",
}
EXAMPLES = {
    "Research Q&A": ("What was the sign agreement?",
                     "TERT partial correlations?"),
    "Evidence records": ("pmid 25819580", "record GAF:591445"),
}


def submit(question, mode):
    if question := question.strip():
        result = answer_question(question, mode=MODES[mode])
        st.session_state.chat_turns.append((question, mode, result))


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
        for column, mode in zip(st.columns(2, gap="medium"), MODES):
            with column:
                st.html(f'<div class="example-mode">{escape(mode)}</div>')
                example_buttons(mode, mode)


def show_turn(index, question, mode, result):
    with st.container(key=f"user-turn-{index}"):
        with st.chat_message("user", avatar=":material/person:"):
            st.html(f'<div class="user-copy">{escape(question)}</div>')
    with st.container(key=f"answer-turn-{index}"):
        with st.chat_message("assistant", avatar=":material/science:"):
            st.html(f'<div class="turn-label">{escape(mode)}</div>')
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

    if turns:
        for index, (question, source_mode, result) in enumerate(turns):
            show_turn(index, question, source_mode, result)
        if turns[-1][2]["status"] == "unsupported_question":
            st.caption(f"Try a supported example in {mode}")
            example_buttons(mode, "unsupported")
    else:
        welcome()

    placeholder = "Ask a focused research question…" if mode == "Research Q&A" else "Enter an evidence command…"
    st.chat_input(placeholder, key="prompt", max_chars=1000, on_submit=submit_input)


if __name__ == "__main__":
    main()
