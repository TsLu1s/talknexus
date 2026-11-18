"""Drive the real app (navigation.py) in Streamlit's test runner, with a fake Ollama."""
import pytest

PAGES = ["Home", "Language Models Management", "AI Conversation", "RAG Conversation"]


@pytest.mark.parametrize("page", PAGES)
def test_every_page_renders_without_errors(open_page, fake_backend, page):
    at = open_page(page)

    assert not at.exception
    assert not at.error
    assert at.session_state["current_page"] == page


@pytest.mark.parametrize("page", ["AI Conversation", "RAG Conversation"])
def test_chat_pages_explain_that_ollama_is_not_running(open_page, fake_backend, page):
    fake_backend.models = []

    at = open_page(page)

    assert not at.exception
    assert any("Ollama is not running" in warning.value for warning in at.warning)


def test_model_page_lists_installed_models_with_details(open_page, fake_backend):
    fake_backend.models = ["llama3.2:latest"]

    at = open_page("Language Models Management")

    assert [expander.label for expander in at.expander] == ["📦 llama3.2:latest"]
    assert any("• Architecture: llama" in code.value for code in at.code)
    assert any("deepseek-r1" in markdown.value for markdown in at.markdown)  # models library table


def test_model_page_without_models(open_page, fake_backend):
    fake_backend.models = []

    at = open_page("Language Models Management")

    assert not at.exception
    assert any("No models currently installed" in info.value for info in at.info)


def test_download_runs_ollama_pull_with_the_trimmed_name(open_page, fake_backend):
    at = open_page("Language Models Management")

    at.text_input(key="model_input").input("  llama3.2:1b ").run()

    assert ["ollama", "pull", "llama3.2:1b"] in fake_backend.cli_calls
    assert any("Successfully installed llama3.2:1b" in success.value for success in at.success)


def test_download_rejects_option_like_names(open_page, fake_backend):
    at = open_page("Language Models Management")

    at.text_input(key="model_input").input("--insecure").run()

    assert not any(call[1] == "pull" for call in fake_backend.cli_calls)
    assert any("Invalid model name" in error.value for error in at.error)
