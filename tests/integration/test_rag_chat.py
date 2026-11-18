"""RAG Conversation page end to end: upload, process, chat, reopen, switch."""
import json
import os
from collections import Counter

import pytest

from core.rag_engine import RAGEngine

PAGES = [
    "The secret project codename is BLUEBIRD.\nIt launches in 2031.",
    "The cafeteria serves soup on Fridays.\nParking is free after six.",
]
QUESTION = "What is the secret project codename?"


@pytest.fixture
def calls(monkeypatch):
    """Count processing and loading; stop a processing loop instead of hanging."""
    counter = Counter()
    for method in ("process_pdfs", "load_experiment"):
        original = getattr(RAGEngine, method)

        def counted(self, *args, _original=original, _method=method, **kwargs):
            counter[_method] += 1
            if counter["process_pdfs"] > 3:
                raise RuntimeError("documents processed again and again")
            return _original(self, *args, **kwargs)

        monkeypatch.setattr(RAGEngine, method, counted)
    return counter


def create_experiment(at, make_pdf, name="exp1", files=None, top_k=None):
    at.file_uploader[0].set_value(files or [("facts.pdf", make_pdf(PAGES), "application/pdf")]).run()
    if top_k:
        at.slider[1].set_value(top_k).run()
    at.text_input(key="experiment_name_input").input(name).run()
    at.checkbox(key="process_ready_checkbox").check().run()
    return at


def ask(at, question):
    at.chat_input[0].set_value(question).run()
    return at


def test_new_experiment_is_processed_once_and_opens_the_chat(open_page, fake_backend, make_pdf, calls, data_dirs):
    # Before: the page reran into "New Experiment" with the box still checked and
    # processed the same files again, forever; the chat never opened.
    at = open_page("RAG Conversation")

    create_experiment(at, make_pdf)

    assert not at.exception and not at.error
    assert calls["process_pdfs"] == 1
    assert at.selectbox(key="experiment_selector").value == "exp1"
    assert len(at.chat_input) == 1
    assert sorted(os.listdir(data_dirs.experiments / "exp1")) == ["config.json", "documents.json", "index.faiss"]


def test_questions_use_the_documents_without_reloading_them(open_page, fake_backend, make_pdf, calls):
    at = open_page("RAG Conversation")
    create_experiment(at, make_pdf, top_k=1)
    fake_backend.response = "<think>looking it up</think>The codename is BLUEBIRD."

    ask(at, QUESTION)
    fake_backend.response = "In 2031."
    ask(at, "When does it launch?")

    assert not at.exception and not at.error
    assert calls == Counter(process_pdfs=1)  # before: every question reloaded the experiment
    messages = at.session_state["rag_messages"]
    assert [m["content"] for m in messages] == [QUESTION, "The codename is BLUEBIRD.", "When does it launch?", "In 2031."]
    assert "BLUEBIRD" in fake_backend.prompts[0] and "cafeteria" not in fake_backend.prompts[0]


@pytest.mark.parametrize("name", ["Report v1.0", "New Experiment", "../evil"])
def test_unsafe_experiment_names_are_rejected_before_processing(open_page, fake_backend, make_pdf, calls, data_dirs, name):
    at = open_page("RAG Conversation")

    create_experiment(at, make_pdf, name=name)

    assert not at.exception
    assert calls["process_pdfs"] == 0
    assert any("Experiment names may only use" in error.value for error in at.error)
    assert os.listdir(data_dirs.experiments) == []


def test_saved_experiment_reopens_in_a_new_session(open_page, fake_backend, make_pdf, calls):
    create_experiment(open_page("RAG Conversation"), make_pdf, name="exp1")
    fresh = open_page("RAG Conversation")  # e.g. the next day, new browser tab

    fresh.selectbox(key="experiment_selector").select("exp1").run()
    assert len(fresh.chat_input) == 0  # waits for "Start RAG Analysis"
    fresh.checkbox(key="process_ready_checkbox").check().run()
    ask(fresh, QUESTION)
    ask(fresh, "And again?")

    assert not fresh.exception and not fresh.error
    assert calls["load_experiment"] == 1  # loaded once, not once per question
    assert [m["role"] for m in fresh.session_state["rag_messages"]] == ["user", "assistant"] * 2
    assert fake_backend.llm_kwargs[-1]["model"] == "fake-llm"


def test_choosing_new_experiment_again_waits_for_the_user(open_page, fake_backend, make_pdf, calls):
    at = open_page("RAG Conversation")
    create_experiment(at, make_pdf, name="exp1")

    at.selectbox(key="experiment_selector").select("New Experiment").run()

    assert at.checkbox(key="process_ready_checkbox").value is False
    assert not at.error  # before: "Please enter an experiment name" appeared at once
    assert calls["process_pdfs"] == 1


def test_rag_and_ai_chat_histories_stay_separate(open_page, fake_backend, make_pdf, data_dirs):
    at = open_page("AI Conversation")
    at.chat_input[0].set_value("AI question").run()
    at.button(key="nav_RAG Conversation").click().run()
    create_experiment(at, make_pdf)
    ask(at, "RAG question")

    at.button(key="nav_AI Conversation").click().run()

    assert [m["content"] for m in at.session_state["messages"]] == ["AI question", "Fake answer"]
    saved = [json.loads(p.read_text()) for p in data_dirs.conversations.glob("*.json")]
    assert "RAG question" not in json.dumps(saved)


def test_broken_pdf_shows_an_error(open_page, fake_backend, make_pdf, calls, data_dirs):
    at = open_page("RAG Conversation")

    create_experiment(at, make_pdf, files=[("broken.pdf", b"this is not a pdf", "application/pdf")])

    assert not at.exception
    assert any("Error processing documents" in error.value for error in at.error)
    assert os.listdir(data_dirs.experiments) == []
