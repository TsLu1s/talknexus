import streamlit as st
import asyncio
# from langchain_community.llms import Ollama
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from schema.streamhandler import StreamHandler
from schema.ollama_models_db import get_ollama_models
from schema.conversation_history import (get_conversation_chain,
                                         on_model_change,
                                         save_conversation,
                                         load_saved_conversation_list,
                                         load_conversation, 
                                         delete_conversation)

import warnings
warnings.filterwarnings("ignore", category=Warning)
warnings.filterwarnings("ignore", message=".*st.rerun.*")

def run():
    """
    Actual implementation of the chat interface.
    """
    left_column, right_column = st.columns(2)

    async def unmonitored_chat_interface():
        st.markdown('''
        ''', unsafe_allow_html=True)

        # Initialize session state
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'conversation' not in st.session_state:
            st.session_state.conversation = None
        if 'saved_conversations' not in st.session_state:
            st.session_state.saved_conversations = []
        if 'current_conversation_id' not in st.session_state:
            st.session_state.current_conversation_id = "New_Conversation"
        if 'conversation_title' not in st.session_state:
            st.session_state.conversation_title = "New Conversation"
        
        # Load saved conversations on startup
        if not st.session_state.saved_conversations:
            load_saved_conversation_list()
            
        # Show current conversation title (but don't allow editing)
        st.caption(f"**Current conversation:** {st.session_state.conversation_title}")
            
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
                    response = stream_handler.clean_response(st.session_state.conversation.run(prompt))

                    # Clear the stream handler after generation
                    st.session_state.conversation.llm.callbacks = []
                    
                    # Add response to message history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    # Automatically save the conversation after each message
                    save_conversation()
                
                except Exception as e:
                    error_message = f"Error generating response: {str(e)}"
                    response_placeholder.error(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": error_message})
                    
                    # Still try to save even if there was an error
                    save_conversation()

    async def monitored_chat_interface():
        st.markdown('''
        ''', unsafe_allow_html=True)

        # Initialize session state
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'conversation' not in st.session_state:
            st.session_state.conversation = None
        if 'saved_conversations' not in st.session_state:
            st.session_state.saved_conversations = []
        if 'current_conversation_id' not in st.session_state:
            st.session_state.current_conversation_id = "New_Conversation"
        if 'conversation_title' not in st.session_state:
            st.session_state.conversation_title = "New Conversation"
        if 'chaperone' not in st.session_state:
            st.session_state.chaperone = None
        
        # Load saved conversations on startup
        if not st.session_state.saved_conversations:
            load_saved_conversation_list()
        
        # Show current conversation title (but don't allow editing)
        st.caption(f"**Current conversation:** {st.session_state.conversation_title}")
            
        # Initialize conversation if needed
        if st.session_state.conversation is None:
            st.session_state.conversation = get_conversation_chain(model_name)

        #Initialize chaperone agent
        if st.session_state.chaperone is None:
            ChSysPrompt= PromptTemplate.from_file("sys_prompt.txt")
            ChFewShot= PromptTemplate.from_file("few_shot.json")
            st.session_state.chaperone = OllamaLLM(model="llama3.1", temperature=0.5, format="json", prompt=ChSysPrompt)

            '''
            ToDo:
            - define system and few-shot prompts with conversation examples
            - define sample structured output for few-shots
            - tie structured output outcomes to re-prompt OR accept the response
            - create separate chat history variables for monitored model'''
            # st.session_state.chaperone = Ollama(model="llama3.1",
            #                                     temperature=0.2,
            #                                     base_url="http://localhost:11434")

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
                    response = stream_handler.clean_response(st.session_state.conversation.run(prompt))

                    # Check response against chaperone agent
                    ch_respone = await st.session_state.chaperone.

                    # Clear the stream handler after generation
                    st.session_state.conversation.llm.callbacks = []
                    
                    # Add response to message history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    # Automatically save the conversation after each message
                    save_conversation()
                
                except Exception as e:
                    error_message = f"Error generating response: {str(e)}"
                    response_placeholder.error(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": error_message})
                    
                    # Still try to save even if there was an error
                    save_conversation()
    # Get available models
    models = "llama3.1" #get_ollama_models()
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
            format_func=lambda x: f'{x}',
            key="model_select",
            on_change=on_model_change,
            label_visibility="collapsed"
        )
            
    
    with left_column:
        st.subheader("Unmonitored Chatbot")
        asyncio.run(unmonitored_chat_interface())

    with right_column:
        st.subheader("Monitored Chatbot")
        asyncio.run(monitored_chat_interface())