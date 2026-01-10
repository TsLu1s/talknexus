import streamlit as st

from config import DEFAULT_CHUNK_SIZE, DEFAULT_TOP_K
from config.constants import ExperimentStatus, MessageRole
from core.ollama_client import get_ollama_models
from core.rag_engine import RAGEngine, EmbeddingModels, get_rag_configurations
from utils.stream_handler import StreamHandler
from ui.components.session_state import init_rag_session_state
from ui.components.chat import display_chat_history

import warnings
warnings.filterwarnings("ignore", category=Warning)


def setup_model_selection():
    """Setup the embedding and LLM model selection interface."""
    models = get_ollama_models()
    if not models:
        st.warning("Ollama is not running. Make sure to have Ollama API installed")
        return None, None, None, None, None

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("📦 Select Models")

        embedding_models = EmbeddingModels.load()
        embedding_model = st.selectbox(
            "Select Embedding Model:",
            list(embedding_models.keys()),
            format_func=lambda x: f"{x} - {embedding_models[x]['description']}",
        )

        llm_model = st.selectbox(
            "Select Language Model:",
            models,
            format_func=lambda x: f"🔮 {x}",
        )

    with col2:
        st.markdown("📤 Upload Documents")
        uploaded_files = st.file_uploader(
            "Upload one or more PDF files:",
            type=["pdf"],
            accept_multiple_files=True,
            help="Select PDF files to analyze",
        )

        if uploaded_files:
            st.markdown(f"*{len(uploaded_files)} files selected*")

    st.markdown("⚙️ Processing Parameters")
    slider_col1, slider_col2 = st.columns(2)

    with slider_col1:
        chunk_size = st.slider(
            "Child Chunk Size (characters):",
            min_value=100,
            max_value=1000,
            value=DEFAULT_CHUNK_SIZE,
            step=100,
            help="Size of text chunks for processing. Smaller chunks are more precise but may miss context.",
        )

    with slider_col2:
        top_k = st.slider(
            "Number of Parent Documents to Retrieve:",
            min_value=1,
            max_value=15,
            value=DEFAULT_TOP_K,
            step=1,
            help="Number of most relevant parent documents to retrieve for each query.",
        )

    # Check for parameter changes
    if (
        st.session_state.previous_model != llm_model
        or st.session_state.previous_embedding != embedding_model
        or st.session_state.previous_files != uploaded_files
        or st.session_state.previous_chunk_size != chunk_size
        or st.session_state.previous_top_k != top_k
    ):
        st.session_state.process_ready = False
        st.session_state.show_chat = False
        st.session_state.processing_completed = False

    # Update previous states
    st.session_state.previous_model = llm_model
    st.session_state.previous_embedding = embedding_model
    st.session_state.previous_files = uploaded_files
    st.session_state.previous_chunk_size = chunk_size
    st.session_state.previous_top_k = top_k

    return uploaded_files, embedding_model, llm_model, chunk_size, top_k


def process_documents(
    experiment_name: str,
    uploaded_files,
    embedding_model: str,
    chunk_size: int,
    top_k: int,
    llm_model: str,
) -> bool:
    """Process uploaded documents."""
    if not experiment_name:
        st.error("Please enter an experiment name")
        return False

    if not uploaded_files:
        st.error("Please upload PDF files first")
        return False

    with st.spinner("📚 Processing documents..."):
        try:
            st.session_state.rag_system.process_pdfs(
                uploaded_files,
                experiment_name=experiment_name,
                embedding_model=embedding_model,
                child_chunk_size=chunk_size,
                top_k=top_k,
                llm_model=llm_model,
            )

            config = {
                "llm_model": llm_model,
                "embedding_model": embedding_model,
                "chunk_size": chunk_size,
                "top_k": top_k,
                "total_documents": len(uploaded_files),
            }

            success = st.session_state.rag_system.save_experiment(experiment_name, config)

            if not success:
                st.error("Failed to save experiment configuration")
                return False

            st.session_state.show_chat = True
            st.session_state.messages = []
            st.session_state.target_experiment = experiment_name
            st.session_state.process_ready = True
            st.session_state.processing_completed = True

            st.rerun()
            return True

        except Exception as e:
            st.error(f"❌ Error processing documents: {str(e)}")
            return False


def handle_chat_interaction(llm_model: str) -> None:
    """Handle chat interface and interactions."""
    st.markdown("---")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    display_chat_history()

    # Handle new prompt
    prompt = st.chat_input("Ask about your documents", key="chat_input")

    if prompt:
        st.session_state.messages.append({
            "role": MessageRole.USER.value,
            "content": prompt,
        })
        with st.chat_message(MessageRole.USER.value):
            st.markdown(prompt)

        with st.chat_message(MessageRole.ASSISTANT.value):
            response_placeholder = st.empty()
            stream_handler = StreamHandler(response_placeholder)

            try:
                retrieval_chain = st.session_state.rag_system.get_retrieval_chain(
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


def render_rag_analysis_tab() -> None:
    """Render the RAG Analysis tab content."""
    st.markdown("#### 📋 Configuration")

    # Display saved configurations
    with st.expander("📚 View All Saved RAG Experiments", expanded=False):
        configurations = get_rag_configurations(st.session_state.rag_system)
        if configurations:
            st.markdown(f"```{configurations}```")
        else:
            st.write("No saved configurations found.")

    # Get existing experiments
    current_experiments = st.session_state.rag_system.list_experiments()
    experiment_names = [ExperimentStatus.NEW.value] + [name for name, _ in current_experiments]

    # Handle target experiment selection
    if (
        "target_experiment" in st.session_state
        and st.session_state.target_experiment in experiment_names
    ):
        initial_index = experiment_names.index(st.session_state.target_experiment)
    else:
        initial_index = 0

    selected_experiment = st.selectbox(
        "Select Experiment",
        experiment_names,
        index=initial_index,
        key="experiment_selector",
    )

    # Clear messages if experiment changes
    if selected_experiment != st.session_state.previous_experiment:
        st.session_state.messages = []
        st.session_state.show_chat = False
        st.session_state.process_ready = False
        st.session_state.previous_experiment = selected_experiment

    is_new_experiment = selected_experiment == ExperimentStatus.NEW.value

    if is_new_experiment:
        uploaded_files, embedding_model, llm_model, chunk_size, top_k = setup_model_selection()
        if not llm_model:
            return

        experiment_name = st.text_input(
            "📝 Name your Experiment",
            key="experiment_name_input",
            placeholder="Enter experiment name",
        )
    else:
        experiment_name = selected_experiment
        models = get_ollama_models()
        if not models:
            st.warning("Ollama is not running. Make sure to have Ollama API installed.")
            return
        llm_model = models[0] if models else None

    # Process control
    process_ready = st.checkbox(
        "Start RAG Analysis",
        key="process_ready_checkbox",
        value=st.session_state.process_ready,
    )

    if process_ready:
        if not is_new_experiment:
            with st.spinner(f"📚 Processing: {selected_experiment}"):
                success, config = st.session_state.rag_system.load_experiment(selected_experiment)
                if success:
                    st.session_state.show_chat = True
                    st.session_state.processing_completed = True
                    if config and "llm_model" in config:
                        llm_model = config["llm_model"]
                    handle_chat_interaction(llm_model)
                else:
                    st.error(f"Failed to load experiment: {selected_experiment}")
        else:
            if not experiment_name:
                st.error("Please enter an experiment name")
                return

            success = process_documents(
                experiment_name,
                uploaded_files,
                embedding_model,
                chunk_size,
                top_k,
                llm_model,
            )
            if success:
                st.session_state.show_chat = True
                handle_chat_interaction(llm_model)
    else:
        st.session_state.show_chat = False
        st.session_state.messages = []


def run() -> None:
    """Render the RAG chat page."""
    init_rag_session_state()

    st.markdown(
        """
    <div class="header-container">
        <p class="header-subtitle">🔍 Powered PDF RAG Assistant </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    render_rag_analysis_tab()