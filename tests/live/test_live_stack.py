"""
Live checks: the real app against a real Ollama server and real embedding models.

Run:    pytest -m live
Needs:  Ollama running, plus a small chat model and an Ollama embedding model:
            ollama pull qwen3:0.6b
            ollama pull all-minilm
        (override with TALKNEXUS_LIVE_MODEL and TALKNEXUS_LIVE_OLLAMA_EMBED)
        The HuggingFace model BAAI/bge-small-en-v1.5 (~130 MB) downloads on first run.
Tests skip, instead of failing, when Ollama or a model is missing.
"""
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest
import requests

from config import OLLAMA_BASE_URL
from core.ollama_client import OllamaClient
from core.rag_engine import EmbeddingModels, RAGEngine

pytestmark = pytest.mark.live

CHAT_MODEL = os.environ.get("TALKNEXUS_LIVE_MODEL", "qwen3:0.6b")
OLLAMA_EMBED_MODEL = os.environ.get("TALKNEXUS_LIVE_OLLAMA_EMBED", "all-minilm")
REPO = Path(__file__).resolve().parents[2]
PAGES = [
    "The secret project codename is BLUEBIRD.\nIt launches in 2031 from Lisbon.",
    "The cafeteria serves soup on Fridays.\nParking is free after six.",
]
QUESTION = "What is the secret project codename?"


def installed_models() -> set[str]:
    try:
        tags = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5).json()
    except (requests.RequestException, ValueError):
        pytest.skip(f"Ollama is not running at {OLLAMA_BASE_URL}")
    return {model["name"] for model in tags.get("models", [])}


def require(model: str) -> None:
    if not installed_models() & {model, f"{model}:latest"}:
        pytest.skip(f"Model {model!r} is not pulled (ollama pull {model})")


def test_live_model_details_and_pull():
    require(CHAT_MODEL)
    require(OLLAMA_EMBED_MODEL)
    client = OllamaClient()

    assert CHAT_MODEL in client.get_available_models()
    info = client.get_model_info(CHAT_MODEL)
    assert "• Architecture: N/A" not in info and "• Context Length: N/A" not in info
    success, message = client.pull_model(OLLAMA_EMBED_MODEL)  # already present: quick
    assert success, message


def test_live_chat_page_answers_and_remembers(open_page, data_dirs):
    require(CHAT_MODEL)
    at = open_page("AI Conversation", timeout=600)
    at.selectbox(key="model_select").select(CHAT_MODEL).run()

    at.chat_input[0].set_value("My name is Ana. Reply with one short sentence.").run()
    at.chat_input[0].set_value("What is my name? Answer with the name only.").run()

    assert not at.exception and not at.error
    messages = at.session_state["messages"]
    assert [m["role"] for m in messages] == ["user", "assistant"] * 2
    assert all(m["content"] and "<think>" not in m["content"] for m in messages)
    assert "ana" in messages[-1]["content"].lower()
    assert len(list(data_dirs.conversations.glob("*.json"))) == 1


def test_live_rag_page_with_huggingface_embeddings(open_page, make_pdf, data_dirs):
    require(CHAT_MODEL)
    at = open_page("RAG Conversation", timeout=900)
    [embedding] = [s for s in at.selectbox if s.label == "Select Embedding Model:"]
    embedding.select("bge-small").run()
    [llm] = [s for s in at.selectbox if s.label == "Select Language Model:"]
    llm.select(CHAT_MODEL).run()
    at.file_uploader[0].set_value([("facts.pdf", make_pdf(PAGES), "application/pdf")]).run()
    at.slider[1].set_value(1).run()
    at.text_input(key="experiment_name_input").input("live-exp").run()
    at.checkbox(key="process_ready_checkbox").check().run()

    assert not at.exception and not at.error
    assert at.selectbox(key="experiment_selector").value == "live-exp"
    at.chat_input[0].set_value(QUESTION).run()
    answer = at.session_state["rag_messages"][-1]["content"]
    assert "bluebird" in answer.lower(), answer

    # Reopen the saved experiment in a new session: real embeddings, loaded from disk
    fresh = open_page("RAG Conversation", timeout=900)
    fresh.selectbox(key="experiment_selector").select("live-exp").run()
    fresh.checkbox(key="process_ready_checkbox").check().run()
    fresh.chat_input[0].set_value(QUESTION).run()
    assert not fresh.exception and not fresh.error
    assert "bluebird" in fresh.session_state["rag_messages"][-1]["content"].lower()
    size = sum(f.stat().st_size for f in (data_dirs.experiments / "live-exp").iterdir())
    assert size < 1_000_000  # before: ~134 MB, the embedding model was pickled inside


def test_live_ollama_embeddings_round_trip(make_upload, monkeypatch):
    require(OLLAMA_EMBED_MODEL)
    models = dict(EmbeddingModels.load())
    models["live-ollama"] = {"name": OLLAMA_EMBED_MODEL, "type": "ollama", "description": "live test"}
    monkeypatch.setattr(EmbeddingModels, "_cache", models)
    engine = RAGEngine()

    engine.process_pdfs([make_upload("facts.pdf", PAGES)], "live-ollama", embedding_model="live-ollama", child_chunk_size=100, top_k=1)
    assert engine.save_experiment("live-ollama", {"embedding_model": "live-ollama", "chunk_size": 100, "top_k": 1})
    loaded, _ = (fresh := RAGEngine()).load_experiment("live-ollama")

    assert loaded
    assert "BLUEBIRD" in fresh.retriever.invoke(QUESTION)[0].page_content


def test_live_streamlit_server_starts_and_serves_the_app():
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    server = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "navigation.py", "--server.headless", "true",
         "--server.address", "127.0.0.1", "--server.port", str(port)],
        cwd=REPO,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        deadline = time.time() + 60
        while time.time() < deadline:
            try:
                health = requests.get(f"http://127.0.0.1:{port}/_stcore/health", timeout=2)
                if health.text == "ok":
                    break
            except requests.RequestException:
                time.sleep(0.5)
        else:
            pytest.fail("Streamlit server did not become healthy within 60 s")
        assert requests.get(f"http://127.0.0.1:{port}/", timeout=5).status_code == 200
    finally:
        server.terminate()
        server.wait(timeout=20)
