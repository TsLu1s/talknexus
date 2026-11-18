"""
Shared fixtures for the TalkNexus test suite.

Every test gets its own temporary data folders, so nothing touches ./data.
`fake_backend` replaces Ollama (LLM, model list, CLI) and the embedding model,
so unit and integration tests run offline in seconds. Only tests marked
`live` (tests/live/) use a real Ollama server and a real embedding model.
"""
import io
import math
import re
import subprocess
import zlib
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from langchain_core.embeddings import Embeddings
from langchain_core.language_models.llms import LLM
from streamlit.testing.v1 import AppTest

import core.conversation
import core.ollama_client
import core.persistence.conversation_store as conversation_store
import core.persistence.experiment_store as experiment_store
import core.rag_engine
import ui.pages.ai_chatbot as ai_chatbot
from core.ollama_client import OllamaClient
from core.rag_engine import RAGEngine

APP_FILE = str(Path(__file__).resolve().parents[1] / "navigation.py")

# Shape of `ollama show <model>` output (Ollama 0.13).
OLLAMA_SHOW_OUTPUT = """  Model
    architecture        llama
    parameters          3.2B
    context length      131072
    embedding length    3072
    quantization        Q4_K_M

  Capabilities
    completion
    tools

  Parameters
    stop    "<|start_header_id|>"
"""


# =============================================================================
# Fakes
# =============================================================================

class KeywordEmbeddings(Embeddings):
    """Bag-of-words vectors: texts that share words end up close, so retrieval is testable."""

    size = 256

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.size
        for word in re.findall(r"[a-z0-9]+", text.lower()):
            vector[zlib.crc32(word.encode()) % self.size] += 1.0
        norm = math.sqrt(sum(x * x for x in vector)) or 1.0
        return [x / norm for x in vector]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)


class FakeBackend:
    """State of the fake Ollama: installed models, next reply, and what it was sent."""

    def __init__(self):
        self.models = ["fake-llm"]
        self.response: Any = "Fake answer"  # an Exception instance makes the LLM fail
        self.prompts: list[str] = []
        self.llm_kwargs: list[dict] = []
        self.cli_calls: list[list[str]] = []


class FakeStreamingLLM(LLM):
    """Stands in for langchain_community's Ollama: streams its reply token by token."""

    backend: Any = None

    @property
    def _llm_type(self) -> str:
        return "fake-streaming"

    def _call(self, prompt, stop=None, run_manager=None, **kwargs) -> str:
        self.backend.prompts.append(prompt)
        response = self.backend.response
        if isinstance(response, Exception):
            raise response
        if run_manager:
            for token in re.findall(r"\S+\s*", response):
                run_manager.on_llm_new_token(token)
        return response


class FakeUpload(io.BytesIO):
    """Mimics Streamlit's UploadedFile: the bytes plus the name the browser sent."""

    def __init__(self, name: str, data: bytes):
        super().__init__(data)
        self.name = name


def make_pdf(pages: list[str]) -> bytes:
    """Write a minimal, valid PDF with one text page per entry (no dependencies)."""
    objects = [b"<< /Type /Catalog /Pages 2 0 R >>"]
    page_ids = [4 + 2 * i for i in range(len(pages))]
    kids = " ".join(f"{pid} 0 R" for pid in page_ids)
    objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {len(pages)} >>".encode())
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    for page_id, text in zip(page_ids, pages, strict=True):
        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 3 0 R >> >> /Contents {page_id + 1} 0 R >>".encode()
        )
        operators = ["BT", "/F1 12 Tf", "72 720 Td", "14 TL"]
        for line in text.split("\n"):
            escaped = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            operators.append(f"({escaped}) Tj T*")
        operators.append("ET")
        stream = "\n".join(operators).encode("latin-1")
        objects.append(b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream")

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf += f"{number} 0 obj\n".encode() + body + b"\nendobj\n"
    xref = len(pdf)
    pdf += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode()
    pdf += b"".join(f"{offset:010d} 00000 n \n".encode() for offset in offsets)
    pdf += f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    return bytes(pdf)


class PickleBomb:
    """Unpickling this creates `marker`: proof that a file was unpickled (code ran)."""

    def __init__(self, marker: Path):
        self.marker = marker

    def __reduce__(self):
        return (open, (str(self.marker), "w"))


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture(autouse=True)
def data_dirs(tmp_path, monkeypatch):
    """Point every store at fresh temporary folders, never at ./data."""
    conversations = tmp_path / "data" / "saved_conversations"
    experiments = tmp_path / "data" / "experiments"
    monkeypatch.setattr(conversation_store, "CONVERSATIONS_DIR", conversations)
    monkeypatch.setattr(ai_chatbot, "CONVERSATIONS_DIR", conversations)
    monkeypatch.setattr(experiment_store, "EXPERIMENTS_DIR", experiments)
    return SimpleNamespace(conversations=conversations, experiments=experiments)


@pytest.fixture
def fake_backend(monkeypatch):
    """Replace Ollama (LLM, model list, `ollama` CLI) and the embedding model with fakes."""
    backend = FakeBackend()

    def fake_ollama(**kwargs):
        backend.llm_kwargs.append(kwargs)
        return FakeStreamingLLM(backend=backend, callbacks=kwargs.get("callbacks"))

    def fake_cli(args, **kwargs):
        backend.cli_calls.append(args)
        stdout = OLLAMA_SHOW_OUTPUT if args[1] == "show" else "success"
        return subprocess.CompletedProcess(args, 0, stdout, "")

    monkeypatch.setattr(core.conversation, "Ollama", fake_ollama)
    monkeypatch.setattr(core.rag_engine, "Ollama", fake_ollama)
    monkeypatch.setattr(OllamaClient, "get_available_models", lambda self: list(backend.models))
    monkeypatch.setattr(
        core.ollama_client,
        "subprocess",
        SimpleNamespace(run=fake_cli, TimeoutExpired=subprocess.TimeoutExpired),
    )
    monkeypatch.setattr(RAGEngine, "_create_embeddings", lambda self, name: KeywordEmbeddings())
    return backend


@pytest.fixture
def keyword_embeddings():
    return KeywordEmbeddings()


@pytest.fixture
def ollama_show_output():
    return OLLAMA_SHOW_OUTPUT


@pytest.fixture(name="make_pdf")
def make_pdf_fixture():
    return make_pdf


@pytest.fixture
def make_upload():
    """Build an uploaded-file stand-in: make_upload("name.pdf", ["page 1", "page 2"])."""
    return lambda name, pages: FakeUpload(name, make_pdf(pages))


@pytest.fixture
def pickle_bomb(tmp_path):
    marker = tmp_path / "pickle_was_loaded"
    return SimpleNamespace(payload=PickleBomb(marker), marker=marker)


@pytest.fixture
def open_page():
    """Start the real app (navigation.py) in Streamlit's test runner and open a page."""

    def _open(page: str, timeout: float = 60) -> AppTest:
        at = AppTest.from_file(APP_FILE, default_timeout=timeout)
        at.run()
        if page != "Home":
            at.button(key=f"nav_{page}").click().run()
        return at

    return _open
