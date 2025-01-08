import streamlit as st
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama
from schema.streamhandler import StreamHandler
from schema.ollama_models_db import get_ollama_models

def get_conversation_chain(model_name: str) -> ConversationChain:
    """
    Initializes LangChain conversation chain with specified model.
    
    Args:
        model_name (str): Name of Ollama model to use
        
    Returns:
        ConversationChain: Configured conversation chain with memory and prompt template
    """
    # Set up Ollama LLM
    llm = Ollama(
        model=model_name,
        temperature=0.2,
        base_url="http://localhost:11434",
        #system_prompt="You are a helpful AI assistant. Keep your answers brief and concise."
    )
        

    prompt = PromptTemplate(
        input_variables=["history", "input"], 
        template="""Current conversation:
                    {history}
                    Human: {input}
                    Assistant:""")

    memory = ConversationBufferMemory(return_messages=True)
    return ConversationChain(llm=llm, memory=memory, prompt=prompt, verbose=True)

def on_model_change():
    """
    Callback function triggered when selected model changes.
    
    Resets conversation state by clearing message history and conversation chain
    to start fresh with new model.
    """
    st.session_state.messages = []
    st.session_state.conversation = None

def run():
    """
    Main function to run the Streamlit chat interface.
    
    Initializes UI components, manages conversation state, handles model selection,
    and processes chat interactions. Implements real-time streaming of model responses
    and maintains chat history.
    """
    st.markdown('''
    <div class="header-container">
        <p class="header-subtitle">🤖 Chat with State-of-the-Art Language Models</p>
    </div>
    ''', unsafe_allow_html=True)

    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'conversation' not in st.session_state:
        st.session_state.conversation = None

    # Get available models
    models = get_ollama_models()
    if not models:
        st.warning(f"Ollama is not running. Make sure to have Ollama API installed")
        return

    # Model selection
    st.subheader("Select a Language Model:")
    col1, _ = st.columns([2, 6])
    with col1:
        model_name = st.selectbox(
            "Model",
            models,
            format_func=lambda x: f'🔮 {x}',
            key="model_select",
            on_change=on_model_change,
            label_visibility="collapsed"
        )

    # Initialize conversation if needed
    if st.session_state.conversation is None:
        st.session_state.conversation = get_conversation_chain(model_name)

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle new user input
    if prompt := st.chat_input(f"Chat with {model_name}"):
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate and display assistant response
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            
            try:
                # Create a new stream handler for this response
                stream_handler = StreamHandler(response_placeholder)
                
                # Temporarily add stream handler to the conversation
                st.session_state.conversation.llm.callbacks = [stream_handler]
                
                # Generate response
                response = st.session_state.conversation.run(prompt)
                
                # Clear the stream handler after generation
                st.session_state.conversation.llm.callbacks = []
                
                # Add response to message history
                st.session_state.messages.append({"role": "assistant", "content": response})
            
            except Exception as e:
                error_message = f"Error generating response: {str(e)}"
                response_placeholder.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})