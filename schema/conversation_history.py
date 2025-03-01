import streamlit as st
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama
from schema.streamhandler import StreamHandler
from schema.ollama_models_db import get_ollama_models

from datetime import datetime
import pickle
import re
import os 

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
                    Assistant:""",)

    memory = ConversationBufferMemory(return_messages=True)
    return ConversationChain(llm=llm, memory=memory, prompt=prompt, verbose=False)

def on_model_change():
    """
    Callback function triggered when selected model changes.
    
    Resets conversation state by clearing message history and conversation chain
    to start fresh with new model.
    """
    st.session_state.messages = []
    st.session_state.conversation = None
    st.session_state.current_conversation_id = "New_Conversation"
    st.session_state.conversation_title = "New Conversation"

def save_conversation():
    """
    Saves the current conversation to disk.
    Uses the first 20 characters of the first prompt as the conversation ID.
    """
    if not st.session_state.messages:
        return
    
    # Create conversations directory if it doesn't exist
    os.makedirs("saved_conversations", exist_ok=True)
    
    # Get or create conversation ID and title from first user message if not already set
    # or if this is the first message being processed
    first_user_message = next((msg for msg in st.session_state.messages if msg["role"] == "user"), None)
    
    if first_user_message and (st.session_state.current_conversation_id == "New_Conversation" or 
                               st.session_state.conversation_title == "New Conversation"):
        first_prompt = first_user_message["content"]
        if first_prompt:
            # Set conversation ID (for file naming)
            convo_id = first_prompt[:40].strip().replace(" ", "_")
            if convo_id:
                st.session_state.current_conversation_id = convo_id
                # Set conversation title (for display)
                st.session_state.conversation_title = first_prompt[:40].strip()
    
    # Use conversation ID for file naming (with timestamp to avoid conflicts)
    file_id = f"{st.session_state.current_conversation_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Save conversation data
    conversation_data = {
        "messages": st.session_state.messages,
        "model": st.session_state.get("model_select", "unknown"),
        "memory": st.session_state.conversation.memory.chat_memory.messages if st.session_state.conversation else [],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "title": st.session_state.conversation_title
    }
    
    # Delete previous version of this conversation if it exists
    for filename in os.listdir("saved_conversations"):
        if filename.startswith(f"{st.session_state.current_conversation_id}_") and filename.endswith(".pkl"):
            try:
                os.remove(f"saved_conversations/{filename}")
            except:
                pass
    
    with open(f"saved_conversations/{file_id}.pkl", "wb") as f:
        pickle.dump(conversation_data, f)
    
    # Update the list of saved conversations
    load_saved_conversation_list()

def load_saved_conversation_list():
    """
    Loads the list of saved conversations from the disk.
    """
    st.session_state.saved_conversations = []
    
    if not os.path.exists("saved_conversations"):
        return
    
    for filename in os.listdir("saved_conversations"):
        if filename.endswith(".pkl"):
            conversation_id = filename[:-4]  # Remove .pkl extension
            try:
                with open(f"saved_conversations/{filename}", "rb") as f:
                    data = pickle.load(f)
                    # Use custom title if available, otherwise use first message
                    if "title" in data:
                        title = data["title"]
                    else:
                        first_msg = next((msg["content"] for msg in data["messages"] if msg["role"] == "user"), "")
                        title = first_msg[:40] + ("..." if len(first_msg) > 40 else "")
                    
                    timestamp = data.get("timestamp", "Unknown date")
                    model = data.get("model", "unknown")
                    
                    display_name = f"{timestamp[:10]} - {model}: {title}"
                    
                    # Use the old format (compatible with existing code)
                    st.session_state.saved_conversations.append((conversation_id, display_name))
            except Exception as e:
                st.error(f"Error loading conversation {conversation_id}: {str(e)}")
    
    # Sort by newest first based on timestamp in filename
    st.session_state.saved_conversations.sort(key=lambda x: x[0], reverse=True)

def load_conversation(conversation_id):
    """
    Loads a saved conversation from disk and sets it as the current conversation.
    
    Args:
        conversation_id (str): ID of the conversation to load
    """
    try:
        with open(f"saved_conversations/{conversation_id}.pkl", "rb") as f:
            data = pickle.load(f)
        
        # Restore model selection
        if "model" in data and data["model"] in get_ollama_models():
            st.session_state.model_select = data["model"]
        
        # Restore messages
        st.session_state.messages = data["messages"]
        
        # Restore conversation with memory
        model_name = data.get("model", st.session_state.model_select)
        st.session_state.conversation = get_conversation_chain(model_name)
        
        # Restore memory if available
        if "memory" in data and data["memory"]:
            st.session_state.conversation.memory.chat_memory.messages = data["memory"]
        
        # Set conversation ID
        st.session_state.current_conversation_id = conversation_id
        
        # Restore title if available
        if "title" in data:
            st.session_state.conversation_title = data["title"]
        else:
            # Find first user message for title
            first_msg = next((msg["content"] for msg in data["messages"] if msg["role"] == "user"), "")
            st.session_state.conversation_title = first_msg[:40].strip()
        st.session_state.needs_rerun = True
        #st.rerun()
    except Exception as e:
        st.error(f"Error loading conversation: {str(e)}")

def delete_conversation(conversation_id):
    """
    Deletes a saved conversation from disk.
    
    Args:
        conversation_id (str): ID of the conversation to delete
    """
    try:
        os.remove(f"saved_conversations/{conversation_id}.pkl")
        # Reset current conversation to new
        st.session_state.messages = []
        st.session_state.conversation = None
        st.session_state.current_conversation_id = "New_Conversation"
        st.session_state.conversation_title = "New Conversation"
        load_saved_conversation_list()
        st.session_state.needs_rerun = True
        #st.rerun()
    except Exception as e:
        st.error(f"Error deleting conversation: {str(e)}")
    