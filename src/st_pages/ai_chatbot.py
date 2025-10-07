import streamlit as st
import asyncio
from langchain_community.llms import Ollama
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
            
        # Sidebar for conversation management
        with st.sidebar:
            st.title("Conversation History")
            
            # Action selector with options
            action_options = ["New Conversation", "Saved Conversations"]
            
            # Function to handle action selection
            def on_action_change():
                selected = st.session_state.action_selector
                if selected == "New Conversation":
                    # Reset only the conversation-related state instead of all state
                    st.session_state.messages = []
                    
                    # Properly get a new conversation with the current model
                    if 'model_select' in st.session_state:
                        model_name = st.session_state.model_select
                        st.session_state.conversation = get_conversation_chain(model_name)
                    else:
                        st.session_state.conversation = None
                    
                    # Reset conversation ID and title
                    st.session_state.current_conversation_id = "New_Conversation"
                    st.session_state.conversation_title = "New Conversation"
                            
            # Create a selectbox for actions
            action_selection = st.selectbox(
                "Choose an action:",
                action_options,
                index=0,
                key="action_selector",
                on_change=on_action_change
            )
                    
            # Display saved conversations
            if action_selection == "Saved Conversations":
                if st.session_state.saved_conversations:
                    st.markdown("---")
                    #st.subheader("Saved Conversations")
                
                # Create a dictionary of display names to conversation IDs
                convo_dict = {}
                for item in st.session_state.saved_conversations:
                    if len(item) == 3:  # New format with 3 values
                        convo_id, display_name, _ = item
                    else:  # Old format with 2 values
                        convo_id, display_name = item
                    convo_dict[display_name] = convo_id
                
                # Add a default option
                convo_options = ["Select Conversation"] + list(convo_dict.keys())
                
                # Create a selectbox for choosing conversations
                # Always default to "Select Conversation" (index 0)
                selected_convo = st.selectbox(
                    "Select a conversation to load or manage:",
                    convo_options,
                    index=0,
                    key="convo_selector"
                )
                
                # Handle conversation selection
                if selected_convo != "Select Conversation":
                    selected_id = convo_dict[selected_convo]
                    
                    # Initialize action selector state for this conversation if needed
                    action_key = f"action_{selected_id}_index"
                    if action_key not in st.session_state:
                        st.session_state[action_key] = 0
                    
                    # Show management options for the selected conversation
                    convo_action_options = ["Select Action", "Continue Conversation", "Delete Conversation"]
                    
                    # Callback for conversation action change
                    def on_convo_action_change():
                        selected_action = st.session_state[f"action_{selected_id}"]
                        if selected_action == "Continue Conversation":
                            load_conversation(selected_id)
                            st.session_state[f"action_{selected_id}_index"] = 0
                        elif selected_action == "Delete Conversation":
                            # We don't call delete directly, we show the confirmation checkbox
                            pass
                    
                    convo_action = st.selectbox(
                        "Choose action:",
                        convo_action_options,
                        index=st.session_state[action_key],
                        key=f"action_{selected_id}",
                        on_change=on_convo_action_change
                    )
                    
                    # Only show confirmation checkbox for delete action
                    if convo_action == "Delete Conversation":
                        delete_confirm = st.checkbox("✓ Confirm deletion", key=f"confirm_delete_{selected_id}")
                        if delete_confirm:
                            if st.session_state.get(f"confirm_delete_{selected_id}", False):
                                delete_conversation(selected_id)
                                st.session_state[f"action_{selected_id}_index"] = 0
                                st.rerun()
                else:
                    if len(st.session_state.saved_conversations)==0:
                        st.info("Conversation History is empty.")
                
        
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
                    await asyncio.gather (response = stream_handler.clean_response(st.session_state.conversation.run(prompt)))

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
            
        # Sidebar for conversation management
        with st.sidebar:
            st.title("Conversation History")
            
            # Action selector with options
            action_options = ["New Conversation", "Saved Conversations"]
            
            # Function to handle action selection
            def on_action_change():
                selected = st.session_state.action_selector
                if selected == "New Conversation":
                    # Reset only the conversation-related state instead of all state
                    st.session_state.messages = []
                    
                    # Properly get a new conversation with the current model
                    if 'model_select' in st.session_state:
                        model_name = st.session_state.model_select
                        st.session_state.conversation = get_conversation_chain(model_name)
                    else:
                        st.session_state.conversation = None
                    
                    # Reset conversation ID and title
                    st.session_state.current_conversation_id = "New_Conversation"
                    st.session_state.conversation_title = "New Conversation"
                            
            # Create a selectbox for actions
            action_selection = st.selectbox(
                "Choose an action:",
                action_options,
                index=0,
                key="action_selector",
                on_change=on_action_change
            )
                    
            # Display saved conversations
            if action_selection == "Saved Conversations":
                if st.session_state.saved_conversations:
                    st.markdown("---")
                    #st.subheader("Saved Conversations")
                
                # Create a dictionary of display names to conversation IDs
                convo_dict = {}
                for item in st.session_state.saved_conversations:
                    if len(item) == 3:  # New format with 3 values
                        convo_id, display_name, _ = item
                    else:  # Old format with 2 values
                        convo_id, display_name = item
                    convo_dict[display_name] = convo_id
                
                # Add a default option
                convo_options = ["Select Conversation"] + list(convo_dict.keys())
                
                # Create a selectbox for choosing conversations
                # Always default to "Select Conversation" (index 0)
                selected_convo = st.selectbox(
                    "Select a conversation to load or manage:",
                    convo_options,
                    index=0,
                    key="convo_selector"
                )
                
                # Handle conversation selection
                if selected_convo != "Select Conversation":
                    selected_id = convo_dict[selected_convo]
                    
                    # Initialize action selector state for this conversation if needed
                    action_key = f"action_{selected_id}_index"
                    if action_key not in st.session_state:
                        st.session_state[action_key] = 0
                    
                    # Show management options for the selected conversation
                    convo_action_options = ["Select Action", "Continue Conversation", "Delete Conversation"]
                    
                    # Callback for conversation action change
                    def on_convo_action_change():
                        selected_action = st.session_state[f"action_{selected_id}"]
                        if selected_action == "Continue Conversation":
                            load_conversation(selected_id)
                            st.session_state[f"action_{selected_id}_index"] = 0
                        elif selected_action == "Delete Conversation":
                            # We don't call delete directly, we show the confirmation checkbox
                            pass
                    
                    convo_action = st.selectbox(
                        "Choose action:",
                        convo_action_options,
                        index=st.session_state[action_key],
                        key=f"action_{selected_id}",
                        on_change=on_convo_action_change
                    )
                    
                    # Only show confirmation checkbox for delete action
                    if convo_action == "Delete Conversation":
                        delete_confirm = st.checkbox("✓ Confirm deletion", key=f"confirm_delete_{selected_id}")
                        if delete_confirm:
                            if st.session_state.get(f"confirm_delete_{selected_id}", False):
                                delete_conversation(selected_id)
                                st.session_state[f"action_{selected_id}_index"] = 0
                                st.rerun()
                else:
                    if len(st.session_state.saved_conversations)==0:
                        st.info("Conversation History is empty.")
                
        
        # Show current conversation title (but don't allow editing)
        st.caption(f"**Current conversation:** {st.session_state.conversation_title}")
            
        # Initialize conversation if needed
        if st.session_state.conversation is None:
            st.session_state.conversation = get_conversation_chain(model_name)

        #Initialize chaperone agent
        if st.session_state.chaperone is None:
            ChSysPrompt = PromptTemplate
            '''
            ToDo:
            - define system and few-shot prompts with conversation examples
            - define sample structured output for few-shots
            - tie structured output outcomes to re-prompt OR accept the response'''
            st.session_state.chaperone = Ollama(model="llama3.1",
                                                temperature=0.2,
                                                base_url="http://localhost:11434")

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