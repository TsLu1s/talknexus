import streamlit as st

from config import NEW_CONVERSATION_ID, NEW_CONVERSATION_TITLE
from config.constants import ExperimentStatus


def init_session_state() -> None:
    """
    Initialize all session state variables for the AI chatbot.

    This centralizes session state initialization while maintaining
    the same behavior as the original scattered initialization.
    """
    # Current page tracking
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Home"

    # Chat messages
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Conversation chain
    if "conversation" not in st.session_state:
        st.session_state.conversation = None

    # Saved conversations list
    if "saved_conversations" not in st.session_state:
        st.session_state.saved_conversations = []

    # Current conversation tracking
    if "current_conversation_id" not in st.session_state:
        st.session_state.current_conversation_id = NEW_CONVERSATION_ID

    if "conversation_title" not in st.session_state:
        st.session_state.conversation_title = NEW_CONVERSATION_TITLE


def init_rag_session_state() -> None:
    """
    Initialize session state variables for RAG functionality.

    Separated from main init to allow lazy loading of RAG components.
    """
    from core.rag_engine import RAGEngine

    # Core RAG system
    if "rag_system" not in st.session_state:
        st.session_state.rag_system = RAGEngine()

    # RAG chat history: kept apart from the AI chat's "messages",
    # so one page never wipes or saves the other page's chat.
    if "rag_messages" not in st.session_state:
        st.session_state.rag_messages = []

    # Experiment tracking states
    if "target_experiment" not in st.session_state:
        st.session_state.target_experiment = None

    if "previous_experiment" not in st.session_state:
        st.session_state.previous_experiment = ExperimentStatus.NEW.value

    # Experiment whose retriever is in memory, so questions don't reload it from disk
    if "loaded_experiment" not in st.session_state:
        st.session_state.loaded_experiment = None

    if "loaded_config" not in st.session_state:
        st.session_state.loaded_config = {}

    # Model and parameter tracking states
    if "previous_model" not in st.session_state:
        st.session_state.previous_model = None

    if "previous_embedding" not in st.session_state:
        st.session_state.previous_embedding = None

    if "previous_files" not in st.session_state:
        st.session_state.previous_files = None

    if "previous_chunk_size" not in st.session_state:
        st.session_state.previous_chunk_size = None

    if "previous_top_k" not in st.session_state:
        st.session_state.previous_top_k = None
