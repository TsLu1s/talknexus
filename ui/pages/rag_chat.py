import streamlit as st

from config import DEFAULT_CHUNK_SIZE, DEFAULT_TOP_K
from config.constants import ExperimentStatus, MessageRole
from core.ollama_client import get_ollama_models
from core.persistence.experiment_store import EXPERIMENT_NAME_MAX_LENGTH, is_valid_experiment_name
from core.rag_engine import EmbeddingModels, get_rag_configurations
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

    # Check for parameter changes: ask to start the analysis again
    if (
        st.session_state.previous_model != llm_model
        or st.session_state.previous_embedding != embedding_model
        or st.session_state.previous_files != uploaded_files
        or st.session_state.previous_chunk_size != chunk_size
        or st.session_state.previous_top_k != top_k
    ):
        st.session_state.process_ready_checkbox = False

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

    if experiment_name == ExperimentStatus.NEW.value or not is_valid_experiment_name(experiment_name):
        st.error(
            "Experiment names may only use letters, numbers, spaces, '-' and '_' "
            f"(up to {EXPERIMENT_NAME_MAX_LENGTH} characters), and cannot be "
            f"'{ExperimentStatus.NEW.value}'."
        )
        return False

    if not uploaded_files:
        st.error("Please upload PDF files first")
        return False

    with st.spinner("📚 Processing documents..."):
        try:
            # Processing replaces the in-memory retriever, even if it fails halfway
            st.session_state.loaded_experiment = None
            st.session_state.rag_system.process_pdfs(
                uploaded_files,
                experiment_name=experiment_name,
                embedding_model=embedding_model,
                child_chunk_size=chunk_size,
                top_k=top_k,
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

            # The retriever just built is already in memory: no need to reload it.
            st.session_state.loaded_experiment = experiment_name
            st.session_state.loaded_config = config
            st.session_state.rag_messages = []
            # Rerun into the saved experiment; staying on "New Experiment" with
            # the box checked would process the same files again, forever.
            st.session_state.target_experiment = experiment_name

            st.rerun()
            return True

        except Exception as e:
            st.error(f"❌ Error processing documents: {str(e)}")
            return False


def handle_chat_interaction(llm_model: str) -> None:
    """Handle chat interface and interactions."""
    st.markdown("---")

    # Display chat history
    display_chat_history(st.session_state.rag_messages)

    # Handle new prompt
    prompt = st.chat_input("Ask about your documents", key="chat_input")

    if prompt:
        st.session_state.rag_messages.append({
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
                final_response = stream_handler.clean_response(response["result"])

                st.session_state.rag_messages.append({
                    "role": MessageRole.ASSISTANT.value,
                    "content": final_response,
                })

                response_placeholder.markdown(final_response)

            except Exception as e:
                error_msg = f"Error generating response: {str(e)}"
                st.error(error_msg)
                st.session_state.rag_messages.append({
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

    # Select a just-created experiment. Widget state can only be set before the
    # widget is drawn; its `index` argument is ignored once the widget exists.
    just_created = st.session_state.target_experiment in experiment_names
    if just_created:
        st.session_state.experiment_selector = st.session_state.target_experiment
    st.session_state.target_experiment = None

    selected_experiment = st.selectbox(
        "Select Experiment",
        experiment_names,
        key="experiment_selector",
    )

    # Clear messages if experiment changes
    if selected_experiment != st.session_state.previous_experiment:
        st.session_state.rag_messages = []
        st.session_state.previous_experiment = selected_experiment
        if not just_created:
            st.session_state.process_ready_checkbox = False

    is_new_experiment = selected_experiment == ExperimentStatus.NEW.value

    if is_new_experiment:
        uploaded_files, embedding_model, llm_model, chunk_size, top_k = setup_model_selection()
        if not llm_model:
            return

        experiment_name = st.text_input(
            "📝 Name your Experiment",
            key="experiment_name_input",
            placeholder="Enter experiment name",
        ).strip()
    else:
        models = get_ollama_models()
        if not models:
            st.warning("Ollama is not running. Make sure to have Ollama API installed.")
            return

    # Process control
    process_ready = st.checkbox("Start RAG Analysis", key="process_ready_checkbox")

    if not process_ready:
        st.session_state.rag_messages = []
        return

    if is_new_experiment:
        # On success this reruns the page into the saved experiment
        process_documents(
            experiment_name,
            uploaded_files,
            embedding_model,
            chunk_size,
            top_k,
            llm_model,
        )
        return

    if st.session_state.loaded_experiment != selected_experiment:
        with st.spinner(f"📚 Processing: {selected_experiment}"):
            success, config = st.session_state.rag_system.load_experiment(selected_experiment)
        if not success:
            st.error(f"Failed to load experiment: {selected_experiment}")
            return
        st.session_state.loaded_experiment = selected_experiment
        st.session_state.loaded_config = config

    # Answer with the experiment's model, unless it was removed from Ollama since
    llm_model = st.session_state.loaded_config.get("llm_model")
    handle_chat_interaction(llm_model if llm_model in models else models[0])


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