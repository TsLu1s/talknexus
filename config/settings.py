"""
TalkNexus Application Settings

Centralized configuration for URLs, paths, and app-wide settings.
"""

from pathlib import Path

# =============================================================================
# App Metadata
# =============================================================================

APP_VERSION = "1.1.0"
APP_NAME = "TalkNexus"
APP_DESCRIPTION = "Ollama Chatbot Multi-Model & RAG Interface"
APP_AUTHOR = "Luís Fernando da Silva Santos"
APP_LICENSE = "MIT"
APP_REPOSITORY = "https://github.com/TsLu1s/talknexus"


# =============================================================================
# Path Configuration
# =============================================================================

BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"

# Runtime data directories
CONVERSATIONS_DIR = DATA_DIR / "saved_conversations"
EXPERIMENTS_DIR = DATA_DIR / "experiments"

# Config data files
OLLAMA_MODELS_FILE = CONFIG_DIR / "data" / "ollama_models.json"
EMBEDDING_MODELS_FILE = CONFIG_DIR / "data" / "embedding_models.json"

# Styles
STYLES_FILE = BASE_DIR / "ui" / "styles" / "main.css"


# =============================================================================
# Ollama API Configuration
# =============================================================================

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_API_TAGS = f"{OLLAMA_BASE_URL}/api/tags"


# =============================================================================
# LLM Default Settings
# =============================================================================

DEFAULT_TEMPERATURE = 0.2
DEFAULT_CHUNK_SIZE = 300
DEFAULT_TOP_K = 4
PARENT_CHUNK_MULTIPLIER = 5
CHUNK_OVERLAP_RATIO = 0.1


# =============================================================================
# UI Configuration
# =============================================================================

APP_TITLE = "TalkNexus - Ollama Chatbot Multi-Model Interface"
APP_ICON = "🤖"
APP_LAYOUT = "wide"


# =============================================================================
# Conversation Settings
# =============================================================================

CONVERSATION_TITLE_MAX_LENGTH = 40
NEW_CONVERSATION_ID = "New_Conversation"
NEW_CONVERSATION_TITLE = "New Conversation"


# =============================================================================
# Model Filtering
# =============================================================================

MODEL_FILTER_KEYWORDS = ("failed", "embed", "bge")