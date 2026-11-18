import json
import tempfile

import pytest

import core.rag_engine
from config import EMBEDDING_MODELS_FILE
from core.rag_engine import EmbeddingModels, RAGEngine, get_rag_configurations

PAGES = [
    "The secret project codename is BLUEBIRD.\nIt launches in 2031.",
    "The cafeteria serves soup on Fridays.\nParking is free after six.",
]


@pytest.fixture
def engine(fake_backend):
    return RAGEngine()


def test_embedding_models_come_from_the_config_file(monkeypatch):
    # Before: the settings named a missing file, so 4 of the 6 models were never offered.
    monkeypatch.setattr(EmbeddingModels, "_cache", None)

    assert EmbeddingModels.load() == json.loads(EMBEDDING_MODELS_FILE.read_text())
    assert {"bge-small", "bge-large", "snowflake-arctic-embed2:568m"} <= set(EmbeddingModels.load())


def test_upload_name_cannot_escape_the_temp_folder(engine, make_upload, tmp_path, monkeypatch):
    # The browser sends the file name. Before, "../../escaped.pdf" was written
    # two folders above the temporary folder.
    (tmp_path / "tmp").mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path / "tmp"))

    documents = engine._load_pdf_documents([make_upload("../../escaped.pdf", ["hello"])])

    assert "hello" in documents[0].page_content
    assert not (tmp_path / "escaped.pdf").exists()


def test_index_holds_only_document_chunks(engine, make_upload):
    # Before: a "placeholder" text was indexed and could take one of the top-k slots.
    engine.process_pdfs([make_upload("facts.pdf", PAGES)], "exp", child_chunk_size=100, top_k=4)

    vectorstore = engine.retriever.vectorstore
    chunks = [vectorstore.docstore.search(doc_id) for doc_id in vectorstore.index_to_docstore_id.values()]
    assert chunks
    assert all(chunk.page_content != "placeholder" for chunk in chunks)
    assert all(chunk.metadata.get("doc_id") for chunk in chunks)


def test_retriever_returns_the_parent_chunk_with_the_answer(engine, make_upload):
    count = engine.process_pdfs([make_upload("facts.pdf", PAGES)], "exp", child_chunk_size=100, top_k=1)

    assert count == 2  # pages
    documents = engine.retriever.invoke("What is the secret project codename?")
    assert len(documents) == 1
    assert "BLUEBIRD" in documents[0].page_content


def test_process_pdfs_needs_a_name_and_files(engine, make_upload):
    with pytest.raises(ValueError):
        engine.process_pdfs([], "exp")
    with pytest.raises(ValueError):
        engine.process_pdfs([make_upload("a.pdf", ["x"])], "")


def test_retrieval_chain_puts_the_context_in_the_prompt(engine, make_upload, fake_backend):
    engine.process_pdfs([make_upload("facts.pdf", PAGES)], "exp", child_chunk_size=100, top_k=1)
    fake_backend.response = "The codename is BLUEBIRD."

    result = engine.get_retrieval_chain("fake-llm").invoke({"query": "What is the secret project codename?"})

    assert result["result"] == "The codename is BLUEBIRD."
    assert "BLUEBIRD" in fake_backend.prompts[-1]
    assert "cafeteria" not in fake_backend.prompts[-1]
    assert fake_backend.llm_kwargs[-1]["model"] == "fake-llm"


def test_embedding_factory_follows_the_model_config(monkeypatch):
    calls = []
    monkeypatch.setattr(core.rag_engine, "HuggingFaceEmbeddings", lambda **kw: calls.append(("hf", kw)) or "hf")
    monkeypatch.setattr(core.rag_engine, "OllamaEmbeddings", lambda **kw: calls.append(("ollama", kw)) or "ollama")
    monkeypatch.setattr(EmbeddingModels, "_cache", None)
    engine = RAGEngine()

    assert engine._create_embeddings("bge-small") == "hf"
    assert engine._create_embeddings("snowflake-arctic-embed2:568m") == "ollama"
    # No multi_process (it spawned 4 worker processes per call) and no pinned device.
    assert calls[0] == ("hf", {"model_name": "BAAI/bge-small-en-v1.5", "encode_kwargs": {"normalize_embeddings": True}})
    assert calls[1][1]["model"] == "snowflake-arctic-embed2:568m"


def test_rag_configurations_summary():
    class FakeRag:
        def list_experiments(self):
            return [("exp1", {"llm_model": "m", "embedding_model": "bge-small", "chunk_size": 300, "top_k": 4, "total_documents": 2})]

    summary = get_rag_configurations(FakeRag())

    assert "📋 Experiment: exp1" in summary
    assert "• Parent Chunk Size: 1500 characters" in summary
    assert "• Total Uploaded Files: 2" in summary
    assert get_rag_configurations(type("Empty", (), {"list_experiments": lambda self: []})()) is None
