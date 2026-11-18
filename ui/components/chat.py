import streamlit as st


def display_chat_history(messages: list[dict]) -> None:
    """Display a chat message history."""
    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
