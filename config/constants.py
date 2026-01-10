"""
TalkNexus Constants and Enumerations

Centralized enums and constants for type-safe configuration.
"""

from enum import Enum


class PageName(str, Enum):
    """Application page identifiers."""
    HOME = "Home"
    MODEL_MANAGEMENT = "Language Models Management"
    AI_CONVERSATION = "AI Conversation"
    RAG_CONVERSATION = "RAG Conversation"


class PageIcon(str, Enum):
    """Bootstrap icons for navigation."""
    HOME = "house-door"
    MODEL_MANAGEMENT = "gear"
    AI_CONVERSATION = "chat-dots"
    RAG_CONVERSATION = "file-earmark-text"


class PageBadge(str, Enum):
    """Badge labels for navigation items."""
    INFORMATIVE = "Informative"
    CONFIGURATIONS = "Configurations"
    APPLICATION = "Application"


class MessageRole(str, Enum):
    """Chat message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class EmbeddingModelType(str, Enum):
    """Types of embedding model providers."""
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"


class ExperimentStatus(str, Enum):
    """Status of RAG experiments."""
    NEW = "New Experiment"
    SAVED = "saved"
    LOADED = "loaded"


class ConversationAction(str, Enum):
    """Actions for conversation management."""
    NEW = "🆕 New Conversation"
    SAVED = "📂 Saved Conversations"
    CONTINUE = "📝 Continue Conversation"
    DELETE = "🗑️ Delete Conversation"
    SELECT = "Select Action"


# =============================================================================
# Text Splitter Configuration
# =============================================================================

TEXT_SEPARATORS = ["\n\n", "\n", ".", "!", "?", ",", " ", ""]


# =============================================================================
# Hardware Requirements Display
# =============================================================================

HARDWARE_REQUIREMENTS = {
    "1B-7B": "8GB RAM",
    "8B-13B": "16GB RAM",
    "14B-33B": "32GB RAM",
    "34B+": "64GB+ RAM",
}


# =============================================================================
# Page Configuration Mapping
# =============================================================================

PAGE_CONFIG = {
    PageName.HOME: {
        "icon": PageIcon.HOME,
        "description": "Guidelines & Overview",
        "badge": PageBadge.INFORMATIVE,
    },
    PageName.MODEL_MANAGEMENT: {
        "icon": PageIcon.MODEL_MANAGEMENT,
        "description": "Download Models",
        "badge": PageBadge.CONFIGURATIONS,
    },
    PageName.AI_CONVERSATION: {
        "icon": PageIcon.AI_CONVERSATION,
        "description": "Interactive AI Chat",
        "badge": PageBadge.APPLICATION,
    },
    PageName.RAG_CONVERSATION: {
        "icon": PageIcon.RAG_CONVERSATION,
        "description": "PDF AI Chat Assistant",
        "badge": PageBadge.APPLICATION,
    },
}