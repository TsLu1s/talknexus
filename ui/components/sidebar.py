import streamlit as st

from config import NEW_CONVERSATION_ID, NEW_CONVERSATION_TITLE
from config.constants import ConversationAction
from core.conversation import get_conversation_chain
from core.persistence import ConversationStore


def render_conversation_sidebar(
    conversation_store: ConversationStore,
    on_load_callback=None,
    on_delete_callback=None,
) -> None:
    """
    Render the conversation history sidebar.
    """
    with st.sidebar:
        st.title("Conversation History")

        action_options = [
            ConversationAction.NEW.value,
            ConversationAction.SAVED.value,
        ]

        def on_action_change():
            selected = st.session_state.action_selector
            if selected == ConversationAction.NEW.value:
                _reset_to_new_conversation()

        action_selection = st.selectbox(
            "Choose an action:",
            action_options,
            index=0,
            key="action_selector",
            on_change=on_action_change,
        )

        if action_selection == ConversationAction.SAVED.value:
            _render_saved_conversations(
                conversation_store,
                on_load_callback,
                on_delete_callback,
            )


def _reset_to_new_conversation() -> None:
    """Reset session state to a new conversation."""
    st.session_state.messages = []

    if "model_select" in st.session_state:
        model_name = st.session_state.model_select
        st.session_state.conversation = get_conversation_chain(model_name)
    else:
        st.session_state.conversation = None

    st.session_state.current_conversation_id = NEW_CONVERSATION_ID
    st.session_state.conversation_title = NEW_CONVERSATION_TITLE


def _render_saved_conversations(
    conversation_store: ConversationStore,
    on_load_callback=None,
    on_delete_callback=None,
) -> None:
    """Render the saved conversations list and management UI."""
    saved_conversations = conversation_store.list_all()

    if not saved_conversations:
        st.info("Conversation History is empty.")
        return

    st.session_state.saved_conversations = saved_conversations
    st.markdown("---")

    # Build conversation selection dictionary
    convo_dict = {display_name: convo_id for convo_id, display_name in saved_conversations}
    convo_options = ["Select Conversation"] + list(convo_dict.keys())

    selected_convo = st.selectbox(
        "Select a conversation to load or manage:",
        convo_options,
        index=0,
        key="convo_selector",
    )

    if selected_convo == "Select Conversation":
        return

    selected_id = convo_dict[selected_convo]
    _render_conversation_actions(
        selected_id,
        conversation_store,
        on_load_callback,
        on_delete_callback,
    )


def _render_conversation_actions(
    conversation_id: str,
    conversation_store: ConversationStore,
    on_load_callback=None,
    on_delete_callback=None,
) -> None:
    """Render action buttons for a selected conversation."""
    action_key = f"action_{conversation_id}_index"
    if action_key not in st.session_state:
        st.session_state[action_key] = 0

    convo_action_options = [
        ConversationAction.SELECT.value,
        ConversationAction.CONTINUE.value,
        ConversationAction.DELETE.value,
    ]

    def on_convo_action_change():
        selected_action = st.session_state[f"action_{conversation_id}"]
        if selected_action == ConversationAction.CONTINUE.value:
            _load_conversation(conversation_id, conversation_store)
            st.session_state[action_key] = 0
            if on_load_callback:
                on_load_callback()

    convo_action = st.selectbox(
        "Choose action:",
        convo_action_options,
        index=st.session_state[action_key],
        key=f"action_{conversation_id}",
        on_change=on_convo_action_change,
    )

    if convo_action == ConversationAction.DELETE.value:
        delete_confirm = st.checkbox(
            "✓ Confirm deletion",
            key=f"confirm_delete_{conversation_id}",
        )
        if delete_confirm:
            _delete_conversation(conversation_id, conversation_store)
            st.session_state[action_key] = 0
            if on_delete_callback:
                on_delete_callback()
            st.rerun()


def _load_conversation(
    conversation_id: str,
    conversation_store: ConversationStore,
) -> None:
    """Load a conversation from storage."""
    from core.ollama_client import get_ollama_models

    try:
        data = conversation_store.load(conversation_id)
        if not data:
            st.error(f"Could not load conversation: {conversation_id}")
            return

        # Restore model selection
        available_models = get_ollama_models()
        if "model" in data and data["model"] in available_models:
            st.session_state.model_select = data["model"]

        # Restore messages
        st.session_state.messages = data["messages"]

        # Restore conversation chain
        model_name = data.get("model", st.session_state.get("model_select", ""))
        st.session_state.conversation = get_conversation_chain(model_name)

        # Restore memory if available
        if "memory" in data and data["memory"]:
            st.session_state.conversation.memory.chat_memory.messages = data["memory"]

        # Set conversation tracking
        st.session_state.current_conversation_id = conversation_id
        st.session_state.conversation_title = data.get(
            "title",
            data["messages"][0]["content"][:40] if data["messages"] else NEW_CONVERSATION_TITLE,
        )

        st.session_state.needs_rerun = True

    except Exception as e:
        st.error(f"Error loading conversation: {str(e)}")


def _delete_conversation(
    conversation_id: str,
    conversation_store: ConversationStore,
) -> None:
    """Delete a conversation from storage."""
    try:
        conversation_store.delete(conversation_id)
        _reset_to_new_conversation()
        st.session_state.needs_rerun = True
    except Exception as e:
        st.error(f"Error deleting conversation: {str(e)}")