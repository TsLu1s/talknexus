import streamlit as st

from config import NEW_CONVERSATION_ID, NEW_CONVERSATION_TITLE, CONVERSATIONS_DIR
from config.constants import MessageRole
from core.ollama_client import get_ollama_models
from core.conversation import get_conversation_chain
from core.persistence import ConversationStore
from utils.stream_handler import StreamHandler
from ui.components.session_state import init_session_state
from ui.components.chat import display_chat_history

import warnings
warnings.filterwarnings("ignore", category=Warning)
warnings.filterwarnings("ignore", message=".*st.rerun.*")


def save_conversation() -> None:
    """Save the current conversation to disk."""
    if not st.session_state.messages:
        return

    store = ConversationStore(str(CONVERSATIONS_DIR))

    # Get memory messages if available
    memory_messages = []
    if st.session_state.conversation:
        memory_messages = st.session_state.conversation.memory.chat_memory.messages

    # Save and update conversation ID
    new_id = store.save(
        conversation_id=st.session_state.current_conversation_id,
        messages=st.session_state.messages,
        model=st.session_state.get("model_select", "unknown"),
        memory_messages=memory_messages,
        title=st.session_state.conversation_title,
    )

    if new_id and st.session_state.current_conversation_id == NEW_CONVERSATION_ID:
        st.session_state.current_conversation_id = new_id
        # Update title from first user message
        first_user_msg = next(
            (msg for msg in st.session_state.messages if msg["role"] == MessageRole.USER.value),
            None,
        )
        if first_user_msg:
            st.session_state.conversation_title = first_user_msg["content"][:40].strip()

    # Refresh saved conversations list
    st.session_state.saved_conversations = store.list_all()


def load_saved_conversation_list() -> None:
    """Load the list of saved conversations."""
    store = ConversationStore(str(CONVERSATIONS_DIR))
    st.session_state.saved_conversations = store.list_all()


def load_conversation(conversation_id: str) -> None:
    """Load a saved conversation."""
    store = ConversationStore(str(CONVERSATIONS_DIR))
    data = store.load(conversation_id)

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
    st.session_state.conversation_title = data.get("title", NEW_CONVERSATION_TITLE)
    st.session_state.needs_rerun = True


def delete_conversation(conversation_id: str) -> None:
    """Delete a saved conversation."""
    store = ConversationStore(str(CONVERSATIONS_DIR))
    store.delete(conversation_id)

    # Reset state
    st.session_state.messages = []
    st.session_state.conversation = None
    st.session_state.current_conversation_id = NEW_CONVERSATION_ID
    st.session_state.conversation_title = NEW_CONVERSATION_TITLE

    load_saved_conversation_list()
    st.session_state.needs_rerun = True


def on_model_change() -> None:
    """Callback when selected model changes."""
    st.session_state.messages = []
    st.session_state.conversation = None
    st.session_state.current_conversation_id = NEW_CONVERSATION_ID
    st.session_state.conversation_title = NEW_CONVERSATION_TITLE


def render_conversation_sidebar() -> None:
    """Render the conversation history sidebar."""
    with st.sidebar:
        st.title("Conversation History")

        action_options = ["🆕 New Conversation", "📂 Saved Conversations"]

        def on_action_change():
            selected = st.session_state.action_selector
            if selected == "🆕 New Conversation":
                st.session_state.messages = []
                if "model_select" in st.session_state:
                    st.session_state.conversation = get_conversation_chain(
                        st.session_state.model_select
                    )
                else:
                    st.session_state.conversation = None
                st.session_state.current_conversation_id = NEW_CONVERSATION_ID
                st.session_state.conversation_title = NEW_CONVERSATION_TITLE

        st.selectbox(
            "Choose an action:",
            action_options,
            index=0,
            key="action_selector",
            on_change=on_action_change,
        )

        if st.session_state.action_selector == "📂 Saved Conversations":
            _render_saved_conversations()


def _render_saved_conversations() -> None:
    """Render saved conversations UI."""
    if st.session_state.saved_conversations:
        st.markdown("---")

        convo_dict = {}
        for item in st.session_state.saved_conversations:
            if len(item) == 3:
                convo_id, display_name, _ = item
            else:
                convo_id, display_name = item
            convo_dict[display_name] = convo_id

        convo_options = ["Select Conversation"] + list(convo_dict.keys())

        selected_convo = st.selectbox(
            "Select a conversation to load or manage:",
            convo_options,
            index=0,
            key="convo_selector",
        )

        if selected_convo != "Select Conversation":
            selected_id = convo_dict[selected_convo]
            _render_conversation_actions(selected_id)
        elif len(st.session_state.saved_conversations) == 0:
            st.info("Conversation History is empty.")
    else:
        st.info("Conversation History is empty.")


def _render_conversation_actions(selected_id: str) -> None:
    """Render action buttons for selected conversation."""
    action_key = f"action_{selected_id}_index"
    if action_key not in st.session_state:
        st.session_state[action_key] = 0

    convo_action_options = [
        "Select Action",
        "📝 Continue Conversation",
        "🗑️ Delete Conversation",
    ]

    def on_convo_action_change():
        selected_action = st.session_state[f"action_{selected_id}"]
        if selected_action == "📝 Continue Conversation":
            load_conversation(selected_id)
            st.session_state[action_key] = 0

    convo_action = st.selectbox(
        "Choose action:",
        convo_action_options,
        index=st.session_state[action_key],
        key=f"action_{selected_id}",
        on_change=on_convo_action_change,
    )

    if convo_action == "🗑️ Delete Conversation":
        delete_confirm = st.checkbox(
            "✓ Confirm deletion",
            key=f"confirm_delete_{selected_id}",
        )
        if delete_confirm:
            delete_conversation(selected_id)
            st.session_state[action_key] = 0
            st.rerun()


def run() -> None:
    """Render the AI chatbot page."""
    init_session_state()

    st.markdown(
        """
    <div class="header-container">
        <p class="header-subtitle">🤖 Chat with State-of-the-Art Language Models</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Load saved conversations on startup
    if not st.session_state.saved_conversations:
        load_saved_conversation_list()

    # Render sidebar
    render_conversation_sidebar()

    # Get available models
    models = get_ollama_models()
    if not models:
        st.warning("Ollama is not running. Make sure to have Ollama API installed")
        return

    # Model selection
    st.subheader("Select a Language Model:")
    col1, _ = st.columns([2, 6])
    with col1:
        model_name = st.selectbox(
            "Model",
            models,
            format_func=lambda x: f"🔮 {x}",
            key="model_select",
            on_change=on_model_change,
            label_visibility="collapsed",
        )

    # Show current conversation title
    st.caption(f"**Current conversation:** {st.session_state.conversation_title}")

    # Initialize conversation if needed
    if st.session_state.conversation is None:
        st.session_state.conversation = get_conversation_chain(model_name)

    # Display chat history
    display_chat_history()

    # Handle new user input
    if prompt := st.chat_input(f"Chat with {model_name}"):
        st.session_state.messages.append({
            "role": MessageRole.USER.value,
            "content": prompt,
        })
        with st.chat_message(MessageRole.USER.value):
            st.markdown(prompt)

        with st.chat_message(MessageRole.ASSISTANT.value):
            response_placeholder = st.empty()

            try:
                stream_handler = StreamHandler(response_placeholder)
                st.session_state.conversation.llm.callbacks = [stream_handler]

                response = stream_handler.clean_response(
                    st.session_state.conversation.run(prompt)
                )

                st.session_state.conversation.llm.callbacks = []

                st.session_state.messages.append({
                    "role": MessageRole.ASSISTANT.value,
                    "content": response,
                })

                save_conversation()

            except Exception as e:
                error_message = f"Error generating response: {str(e)}"
                response_placeholder.error(error_message)
                st.session_state.messages.append({
                    "role": MessageRole.ASSISTANT.value,
                    "content": error_message,
                })
                save_conversation()