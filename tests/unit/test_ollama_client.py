import subprocess
from types import SimpleNamespace

import pytest
import requests

import core.ollama_client
from core.ollama_client import ModelLibrary, OllamaClient


class FakeResponse:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload


@pytest.fixture
def cli(monkeypatch):
    """Record `ollama` CLI calls instead of running them."""
    state = SimpleNamespace(calls=[], result=subprocess.CompletedProcess([], 0, "success", ""))

    def fake_run(args, **kwargs):
        state.calls.append(args)
        return state.result

    monkeypatch.setattr(
        core.ollama_client,
        "subprocess",
        SimpleNamespace(run=fake_run, TimeoutExpired=subprocess.TimeoutExpired),
    )
    return state


def test_lists_chat_models_and_hides_embedding_models(monkeypatch):
    payload = {"models": [
        {"name": "llama3.2:latest"},
        {"name": "nomic-embed-text:latest"},
        {"name": "bge-m3:latest"},
        {"name": "qwen3:0.6b"},
    ]}
    monkeypatch.setattr(requests, "get", lambda url, timeout: FakeResponse(200, payload))

    assert OllamaClient().get_available_models() == ["llama3.2:latest", "qwen3:0.6b"]


@pytest.mark.parametrize(
    "response",
    [
        requests.ConnectionError("refused"),
        FakeResponse(500, {"models": []}),
        FakeResponse(200, ValueError("not JSON")),  # another program on port 11434
        FakeResponse(200, ["unexpected"]),
        FakeResponse(200, {"models": [{"no-name": 1}]}),
    ],
)
def test_no_models_when_ollama_is_down_or_answers_oddly(monkeypatch, response):
    def fake_get(url, timeout):
        if isinstance(response, Exception):
            raise response
        return response

    monkeypatch.setattr(requests, "get", fake_get)

    assert OllamaClient().get_available_models() == []


@pytest.mark.parametrize("name", ["llama3.2", "llama3.2:1b", "hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:Q4_K_M"])
def test_pull_passes_the_name_as_one_argument(cli, name):
    success, message = OllamaClient().pull_model(name)

    assert success and message == f"Successfully installed {name}"
    assert cli.calls == [["ollama", "pull", name]]


@pytest.mark.parametrize("name", ["--help", "-v", "llama3.2; rm -rf ~", "two words", "", "a" * 201, "$(whoami)"])
def test_pull_rejects_invalid_names_without_running_anything(cli, name):
    success, message = OllamaClient().pull_model(name)

    assert not success and "Invalid model name" in message
    assert cli.calls == []


def test_pull_reports_ollama_errors(cli):
    cli.result = subprocess.CompletedProcess([], 1, "", "pull model manifest: file does not exist")

    success, message = OllamaClient().pull_model("nope")

    assert not success and "file does not exist" in message


def test_model_info_is_parsed_from_ollama_show(cli, ollama_show_output):
    cli.result = subprocess.CompletedProcess([], 0, ollama_show_output, "")

    info = OllamaClient().get_model_info("llama3.2")

    assert cli.calls == [["ollama", "show", "llama3.2"]]
    for line in [
        "• Architecture: llama",
        "• Parameters: 3.2B",
        "• Quantization: Q4_K_M",
        "• Context Length: 131072",
        "• Embedding Length: 3072",
    ]:
        assert line in info


def test_model_info_unavailable_when_show_fails(cli):
    cli.result = subprocess.CompletedProcess([], 1, "", "model not found")

    assert "Model Information Unavailable" in OllamaClient().get_model_info("ghost")


def test_model_library_rows_have_the_table_columns():
    rows = ModelLibrary.get_dataframe_data()

    assert len(rows) > 100
    assert all(set(row) == {"Model Name", "Description", "Parameter Sizes"} for row in rows)
