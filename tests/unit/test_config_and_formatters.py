import json

from config import HARDWARE_REQUIREMENTS, settings
from core.ollama_client import ModelLibrary
from utils.formatters import create_models_dataframe, format_hardware_requirements, style_dataframe


def test_configured_files_exist():
    # EMBEDDING_MODELS_FILE used to name a file that does not exist.
    for path in (settings.OLLAMA_MODELS_FILE, settings.EMBEDDING_MODELS_FILE, settings.STYLES_FILE):
        assert path.is_file(), path


def test_embedding_models_file_is_complete():
    models = json.loads(settings.EMBEDDING_MODELS_FILE.read_text())

    assert models
    for config in models.values():
        assert config["type"] in {"huggingface", "ollama"}
        assert config["name"] and config["description"]


def test_hardware_requirements_html_lists_every_size():
    html = format_hardware_requirements()

    for size, ram in HARDWARE_REQUIREMENTS.items():
        assert f"<li>{size} models: {ram}</li>" in html


def test_models_table_renders_to_html():
    dataframe = create_models_dataframe(ModelLibrary.get_dataframe_data())

    html = style_dataframe(dataframe).to_html()

    assert 'class="dataframe hover-effect"' in html
    assert "deepseek-r1" in html
