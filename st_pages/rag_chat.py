import streamlit as st
from schema.streamhandler import StreamHandler
from schema.ollama_models_db import get_ollama_models
from schema.rag_settings import RAG_Settings, get_rag_configurations

import warnings
warnings.filterwarnings("ignore", category=Warning)

def init_session_state():
    """Initialize all session state variables."""
    # Core system states
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = RAG_Settings()

    # Chat and processing states
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'show_chat' not in st.session_state:
        st.session_state.show_chat = False
    if 'process_ready' not in st.session_state:
        st.session_state.process_ready = False
    if 'processing_completed' not in st.session_state:
        st.session_state.processing_completed = False

     # Experiment tracking states
    if 'target_experiment' not in st.session_state:
        st.session_state.target_experiment = None
    if 'previous_experiment' not in st.session_state:
        st.session_state.previous_experiment = "New Experiment"

    # Model and parameter tracking states
    if 'previous_model' not in st.session_state:
        st.session_state.previous_model = None
    if 'previous_embedding' not in st.session_state:
        st.session_state.previous_embedding = None
    if 'previous_files' not in st.session_state:
        st.session_state.previous_files = None
    if 'previous_chunk_size' not in st.session_state:
        st.session_state.previous_chunk_size = None
    if 'previous_top_k' not in st.session_state:
        st.session_state.previous_top_k = None

def setup_model_selection():
    """Setup the embedding and LLM model selection interface."""
    
    models = get_ollama_models()
    if not models:
        st.warning(f"Ollama is not running. Make sure to have Ollama API installed")
        return None, None, None, None, None
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("🤖 Select Models")
        embedding_model = st.selectbox(
            "Select Embedding Model:",
            list(RAG_Settings.EMBEDDING_MODELS.keys()),
            format_func=lambda x: f"{x} - {RAG_Settings.EMBEDDING_MODELS[x]['description']}"
        )
            
        llm_model = st.selectbox(
            "Select Language Model:",
            models,
            format_func=lambda x: f'🔮 {x}'
        )

    with col2:
        st.markdown("📤 Upload Documents")
        uploaded_files = st.file_uploader(
            "Upload one or more PDF files:",
            type=['pdf'],
            accept_multiple_files=True,
            help="Select PDF files to analyze"
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
            value=300,
            step=100,
            help="Size of text chunks for processing. Smaller chunks are more precise but may miss context. Larger chunks preserve more context but may be less precise. (Parent Chunk Size = 5x Child Chunk Size)"
        )

    with slider_col2:
        top_k = st.slider(
            "Number of Parent Documents to Retrieve:",
            min_value=1,
            max_value=15,
            value=4,
            step=1,
            help="Number of most relevant parent documents to retrieve for each query. Higher values provide more context but may introduce noise."
        )

    # Check for changes in model, embedding, or files
    if (st.session_state.previous_model != llm_model or 
        st.session_state.previous_embedding != embedding_model or 
        st.session_state.previous_files != uploaded_files or
        st.session_state.get('previous_chunk_size') != chunk_size,
        st.session_state.get('previous_top_k') != top_k):
        # Reset the process_ready checkbox
        st.session_state.process_ready = False
        st.session_state.show_chat = False
        st.session_state.processing_completed = False
    
    # Update previous states
    st.session_state.previous_model = llm_model
    st.session_state.previous_embedding = embedding_model
    st.session_state.previous_files = uploaded_files
    st.session_state.previous_chunk_size = chunk_size

    return uploaded_files, embedding_model, llm_model, chunk_size, top_k

def process_documents(experiment_name, uploaded_files, embedding_model, chunk_size, top_k, llm_model):
    """Process uploaded documents if conditions are met."""
    # First check experiment name
    if not experiment_name:
        st.error("Please enter an experiment name")
        return False
    
    # Check uploaded files
    if not uploaded_files:
        st.error("Please upload PDF files first")
        return False
        
    # If we have both, proceed with processing
    with st.spinner("📚 Processing documents..."):
        try:
            # Create configuration dictionary with all necessary fields
            st.session_state.rag_system.process_pdfs(
                uploaded_files,
                experiment_name=experiment_name, 
                embedding_model=embedding_model,
                child_chunk_size=chunk_size,
                top_k=top_k,
                llm_model=llm_model
            )
            
            # Ensure all configuration data is properly saved
            customization = {
                "llm_model": llm_model,
                "embedding_model": embedding_model,
                "chunk_size": chunk_size,
                "top_k": top_k,
                "total_documents": len(uploaded_files)
            }
            
            # Save the experiment with complete configuration
            success = st.session_state.rag_system.experiment_manager.save_experiment(
                experiment_name,
                st.session_state.rag_system.retriever,
                customization
            )
            
            if not success:
                st.error("Failed to save experiment configuration")
                return False
                
            st.session_state.show_chat = True
            st.session_state.messages = []
            st.session_state.target_experiment = experiment_name  
            st.session_state.process_ready = True
            st.session_state.processing_completed = True

            # Trigger rerun to update UI
            st.rerun()

            return True
            
        except Exception as e:
            st.error(f"❌ Error processing documents: {str(e)}")
            return False

def handle_chat_interaction(llm_model):
    """Handle chat interface and interactions."""
    st.markdown("---")
    
    # Initialize messages if not present
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Create chat input
    prompt = st.chat_input("Ask about your documents", key="chat_input")

    # Handle new prompt
    if prompt:
        # Add user message
        process_chat_message(prompt, llm_model)
    
def process_chat_message(prompt, llm_model):
    """Process a single chat message and generate response."""
    # Add user message to state and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Create assistant message
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        stream_handler = StreamHandler(response_placeholder)
        
        try:
            retrieval_chain = st.session_state.rag_system.get_retrieval_chain(
                llm_model,
                stream_handler=stream_handler
            )
            
            response = retrieval_chain.invoke({
                "query": prompt
            })
            
            final_response = response["result"].strip()
            
            # Update message history
            st.session_state.messages.append({
                "role": "assistant",
                "content": final_response
            })
            
            # Ensure final response is displayed
            response_placeholder.markdown(final_response)
            
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            st.error(error_msg)
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg
            })

def render_rag_analysis_tab():
    """Render the RAG Analysis tab content."""
    st.markdown("#### 📋 Configuration")
    
    # Display all saved configurations in an expander
    with st.expander("📚 View All Saved RAG Experiments", expanded=False):
        configurations = get_rag_configurations()
        if configurations:
            st.markdown(f"```{configurations}```")
        else:
            st.write("No saved configurations found.")
    
    # Get existing experiments and add "New Experiment" option
    current_experiments = st.session_state.rag_system.list_experiments()
    experiment_names = ["New Experiment"] + [name for name, _ in current_experiments]
        
    # Handle target experiment selection
    if 'target_experiment' in st.session_state and st.session_state.target_experiment in experiment_names:
        initial_index = experiment_names.index(st.session_state.target_experiment)
        selected_experiment = experiment_names[initial_index]
        # Only clear target if it's a different experiment
        if st.session_state.target_experiment != selected_experiment:
            st.session_state.target_experiment = None
    else:
        initial_index = 0
        selected_experiment = experiment_names[initial_index]
    
    selected_experiment = st.selectbox(
        "Select Experiment",
        experiment_names,
        index=initial_index,
        key="experiment_selector"
    )
    
    # Clear messages if experiment selection changes
    if selected_experiment != st.session_state.previous_experiment:
        st.session_state.messages = []
        st.session_state.show_chat = False
        st.session_state.process_ready = False
        st.session_state.previous_experiment = selected_experiment
    
    is_new_experiment = selected_experiment == "New Experiment"
    
    if is_new_experiment:
        # Show model selection and configuration only for new experiments
        uploaded_files, embedding_model, llm_model, chunk_size, top_k = setup_model_selection()
        if not llm_model:  # Ollama not running
            return

        experiment_name = st.text_input(
            "📝 Name your Experiment",
            key="experiment_name_input",
            placeholder="Enter experiment name"
        )
    else:
        experiment_name = selected_experiment
        # For existing experiments, we still need the llm_model
        models = get_ollama_models()
        if not models:
            st.warning("Ollama is not running. Make sure to have Ollama API installed.")
            return
        llm_model = models[0] if models else None
    
    # Process control
    process_ready = st.checkbox(
        "Start RAG Analysis", 
        key="process_ready_checkbox", 
        value=st.session_state.process_ready
    )
    
    if process_ready:
        if not is_new_experiment:
            # Load existing experiment
            with st.spinner(f"📚 Processing: {selected_experiment}"):
                success, config = st.session_state.rag_system.load_experiment(selected_experiment)
                if success:
                    st.session_state.show_chat = True
                    st.session_state.processing_completed = True
                    # Use the LLM model from the saved configuration if available
                    if config and 'llm_model' in config:
                        llm_model = config['llm_model']
                    # Show chat interface immediately after loading
                    handle_chat_interaction(llm_model)
                else:
                    st.error(f"Failed to load experiment: {selected_experiment}")
        else:
            # Validate experiment name for new experiments
            if not experiment_name:
                st.error("Please enter an experiment name")
                return
                
            # Process new experiment
            success = process_documents(
                experiment_name, uploaded_files, embedding_model, chunk_size, top_k, llm_model
            )
            if success:
                st.session_state.show_chat = True
                # Show chat interface immediately after processing
                handle_chat_interaction(llm_model)
    else:
        # Reset states when unchecking the process button
        st.session_state.show_chat = False
        st.session_state.messages = []

def run():
    """Main application function."""

    init_session_state()   # Initialize streamlit session state
    
    """Render the application header."""
    st.markdown('''
    <div class="header-container">
        <p class="header-subtitle">🔍 Powered PDF RAG Assistant </p>
    </div>
    ''', unsafe_allow_html=True)
    
    render_rag_analysis_tab()
