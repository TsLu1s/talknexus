import streamlit as st

from config.constants import MessageRole


def display_chat_history() -> None:
    """Display chat message history from session state."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def handle_chat_input(
    model_name: str,
    conversation_chain,
    stream_handler_class,
    on_response_callback=None,
) -> None:
    """
    Handle chat input and response generation.

    Args:
        model_name: Name of the current model
        conversation_chain: LangChain conversation chain
        stream_handler_class: StreamHandler class for response streaming
        on_response_callback: Optional callback after response generation
    """
    prompt = st.chat_input(f"Chat with {model_name}")

    if prompt:
        # Add user message
        st.session_state.messages.append({
            "role": MessageRole.USER.value,
            "content": prompt,
        })
        with st.chat_message(MessageRole.USER.value):
            st.markdown(prompt)

        # Generate assistant response
        with st.chat_message(MessageRole.ASSISTANT.value):
            response_placeholder = st.empty()

            try:
                stream_handler = stream_handler_class(response_placeholder)
                conversation_chain.llm.callbacks = [stream_handler]

                response = stream_handler.clean_response(
                    conversation_chain.run(prompt)
                )

                conversation_chain.llm.callbacks = []

                st.session_state.messages.append({
                    "role": MessageRole.ASSISTANT.value,
                    "content": response,
                })

                if on_response_callback:
                    on_response_callback()

            except Exception as e:
                error_message = f"Error generating response: {str(e)}"
                response_placeholder.error(error_message)
                st.session_state.messages.append({
                    "role": MessageRole.ASSISTANT.value,
                    "content": error_message,
                })

                if on_response_callback:
                    on_response_callback()


def handle_rag_chat_input(
    rag_system,
    llm_model: str,
    stream_handler_class,
) -> None:
    """
    Handle RAG chat input and response generation.

    Args:
        rag_system: RAGEngine instance
        llm_model: Name of the LLM model
        stream_handler_class: StreamHandler class for response streaming
    """
    prompt = st.chat_input("Ask about your documents", key="chat_input")

    if prompt:
        # Add user message
        st.session_state.messages.append({
            "role": MessageRole.USER.value,
            "content": prompt,
        })
        with st.chat_message(MessageRole.USER.value):
            st.markdown(prompt)

        # Generate assistant response
        with st.chat_message(MessageRole.ASSISTANT.value):
            response_placeholder = st.empty()
            stream_handler = stream_handler_class(response_placeholder)

            try:
                retrieval_chain = rag_system.get_retrieval_chain(
                    llm_model,
                    stream_handler=stream_handler,
                )

                response = retrieval_chain.invoke({"query": prompt})
                final_response = response["result"].strip()

                st.session_state.messages.append({
                    "role": MessageRole.ASSISTANT.value,
                    "content": final_response,
                })

                response_placeholder.markdown(final_response)

            except Exception as e:
                error_msg = f"Error generating response: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": MessageRole.ASSISTANT.value,
                    "content": error_msg,
                })