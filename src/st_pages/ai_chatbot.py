import streamlit as st
# import asyncio
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
from pydantic import BaseModel
import re

import warnings
warnings.filterwarnings("ignore", category=Warning)
warnings.filterwarnings("ignore", message=".*st.rerun.*")

def run():
    """
    Actual implementation of the chat interface.
    """
    left_column, right_column = st.columns(2)

    def unmonitored_chat_interface():
        st.markdown('''
        ''', unsafe_allow_html=True)

        # Initialize session state
        if 'messages_left' not in st.session_state:
            st.session_state.messages_left = []
        if 'conversation_left' not in st.session_state:
            st.session_state.conversation_left = None
        if 'saved_conversations_left' not in st.session_state:
            st.session_state.saved_conversations_left = []
        if 'current_conversation_id_left' not in st.session_state:
            st.session_state.current_conversation_id_left = "New_Conversation"
        if 'conversation_title_left' not in st.session_state:
            st.session_state.conversation_title_left = "New Conversation"
        
        # Load saved conversations on startup
        # if not st.session_state.saved_conversations_left:
        #     load_saved_conversation_list()
            
        # Show current conversation title (but don't allow editing)
        st.caption(f"**Current conversation:** {st.session_state.conversation_title_left}")
            
        # Initialize conversation if needed
        if st.session_state.conversation_left is None:
            st.session_state.conversation_left = get_conversation_chain(model_name, False)

        # Display chat history
        for message in st.session_state.messages_left:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Handle new user input
        #if prompt := st.chat_input(f"Chat with {model_name}"):
        if 'shared_prompt' in st.session_state and st.session_state.shared_prompt:
            prompt = st.session_state.shared_prompt
            # Add user message to history
            st.session_state.messages_left.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate and display assistant response
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                
                try:
                    # Create a new stream handler for this response
                    stream_handler = StreamHandler(response_placeholder)
                    
                    # Temporarily add stream handler to the conversation
                    st.session_state.conversation_left.llm.callbacks = [stream_handler]

                    #Placeholder response                    
                    response_placeholder.info("Generating response...")

                    # # Generate response
                    # response = stream_handler.clean_response(str(st.session_state.conversation_left.invoke(prompt)))

                    #Invoke response
                    response = st.session_state.conversation_left.invoke(prompt)
                    
                    if isinstance(response, dict):
                        response = response.get('response', str(response))
                    elif hasattr(response, 'content'):
                            response = response.content
                    response= str(response)

                    # Clear the stream handler after generation
                    st.session_state.conversation_left.llm.callbacks = []
                    
                    # Add response to message history
                    st.session_state.messages_left.append({"role": "assistant", "content": response})
                    
                    # Automatically save the conversation after each message
                    # save_conversation()
                
                except Exception as e:
                    error_message = f"Error generating response: {str(e)}"
                    response_placeholder.error(error_message)
                    st.session_state.messages_left.append({"role": "assistant", "content": error_message})
                    
                    # Still try to save even if there was an error
                    # save_conversation()

    def monitored_chat_interface():
        st.markdown('''
        ''', unsafe_allow_html=True)

        # Initialize session state
        if 'messages_right' not in st.session_state:
            st.session_state.messages_right = []
        if 'conversation_right' not in st.session_state:
            st.session_state.conversation_right= None
        if 'saved_conversations_right' not in st.session_state:
            st.session_state.saved_conversations_right= []
        if 'current_conversation_id_right' not in st.session_state:
            st.session_state.current_conversation_id_right = "New_Conversation"
        if 'conversation_title_right' not in st.session_state:
            st.session_state.conversation_title_right = "New Conversation"
        if 'chaperone' not in st.session_state:
            st.session_state.chaperone = None
        
        # Load saved conversations on startup
        # if not st.session_state.saved_conversations_right:
        #     load_saved_conversation_list()
        
        # Show current conversation title (but don't allow editing)
        st.caption(f"**Current conversation:** {st.session_state.conversation_title_right}")
            
        # Initialize conversation if needed
        if st.session_state.conversation_right is None:
            st.session_state.conversation_right = get_conversation_chain(model_name, False)

        #Initialize chaperone agent

        try:
            if st.session_state.chaperone is None:
                ChSysPrompt= PromptTemplate.from_file("src/st_pages/sys_prompt.txt")
                ReSysPrompt= PromptTemplate.from_file("src/st_pages/re_prompt.txt")
                # chaperone = OllamaLLM(model="llama3.1", temperature=0.5, format="json", prompt=ChSysPrompt)
                # st.session_state.chaperone = True

                '''
                ToDo:
               -limit rephrased output display to only text within the <rephrase> XML tags
               -curate testing set of true and false examples and run tests on the chaperone.
                
                '''
                # with open("src/st_pages/few_shot.json", encoding='utf-8', errors='ignore') as json_data:
                #     samples = json.load(json_data)

                #Serialize chaperone structured output schema
                class Parasocial_Analysis(BaseModel):
                    brainstorm: str
                    isParasocial: int
                    confidence: float
                #Initialize chaperone agent
                chaperone = OllamaLLM(model="marco-o1",
                                                temperature=0.0,
                                                base_url="http://localhost:11434",
                                                prompt=ChSysPrompt,
                                                keep_alive="5m"
                                                )
                #Serialize chatbot re-prompt structured output schema
                class Rephrase(BaseModel):
                    brainstorm: str
                    rephrase: str

        except Exception as e:
            error_message = f"Error initializing chaperone: {e}"
            response_placeholder.error(error_message)
            st.session_state.messages_right.append({"role": "assistant", "content": error_message})

        # Display chat history
        for message in st.session_state.messages_right:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Handle new user input
        #if prompt := st.chat_input(f"Chat with {model_name}"):
        if 'shared_prompt' in st.session_state and st.session_state.shared_prompt:
            prompt = st.session_state.shared_prompt

            # Add user message to history
            st.session_state.messages_right.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate and display assistant response
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                response_placeholder.info("Generating response...")
                #global response
                
                try:
                    
                    #Extract rephrased re-prompt content from relevant XML tags
                    def extractRephraseXML(response=str):
                        rephrasePattern = re.compile(r'<rephrase>\s*((?:[^"\\]|\\.)*)<\/rephrase>', re.DOTALL)
                        if match := re.search(rephrasePattern, response):
                            rephraseText = match.group(1).strip()
                            rephraseText = rephraseText.replace('\\"', '"').replace('\\n', '\n')
                            return rephraseText
                        return None

                    # Generate response
                    def responseGen(rePrompt=bool, promptText=None):
                        if rePrompt == False:
                            # Re-initialize conversation chain for initial prompt
                            st.session_state.conversation_right = get_conversation_chain(model_name, False)
                            # # Create a new stream handler for this response
                            # stream_handler = StreamHandler(response_placeholder)
                            # # Temporarily add stream handler to the conversation
                            # st.session_state.conversation_right.llm.callbacks = [stream_handler]

                            #Clear callbacks if present
                            st.session_state.conversation_right.llm.callbacks = []

                            #Invoke response
                            response = st.session_state.conversation_right.invoke(prompt)
                            
                            if isinstance(response, dict):
                                return response.get('response', str(response))
                            elif hasattr(response, 'content'):
                                    return response.content
                            return str(response)

                        elif rePrompt == True:
                            # Re-initialize conversation chain for re-prompt
                            st.session_state.conversation_right = get_conversation_chain(model_name, True)
                            # # Create a new stream handler for this response
                            # stream_handler = StreamHandler(response_placeholder)
                            # # Temporarily add stream handler to the conversation
                            # st.session_state.conversation_right.llm.callbacks = [stream_handler]
                            
                            #Clear callbacks if present
                            st.session_state.conversation_right.llm.callbacks = []

                            #Invoke response
                            if promptText:
                                formatted_input = f"{promptText}"
                            else:
                                formatted_input = f"{prompt}"

                            response = st.session_state.conversation_right.invoke(formatted_input, format=Rephrase.model_json_schema())
                            if isinstance(response, dict):
                                return response.get('response', str(response))
                            elif hasattr(response, 'content'):
                                return response.content
                            return str(response)
                        
                    #Generate initial response
                    response = responseGen(False)

                    #Remove brainstorm tags before chaperone scan
                    from schema.streamhandler import StreamHandler
                    cleaned_response = StreamHandler.clean_response(response)
                    print(f"\n=== Initial response ===\n{response}\n")

                    # Check response against chaperone agent for five iterations
                    global isParasocial
                    def ch_run(resp=str):
                        try:
                            ch_response = [None, None, None, None, None]
                         
                            # print(f"conversation: {st.session_state.conversation_right}")
                            
                            # print(f"memory.messages: {st.session_state.conversation_right.memory.chat_memory.messages}")
                            
                            print(f"\nSession messages: {st.session_state.messages_right}\n")
                            
                            message_log = st.session_state.conversation_right.memory.chat_memory.messages
                            for i in range(5):
                                ch_response[i] = chaperone.invoke(f"<|im_start|>user\nDetermine if this conversation is developing a parasocial dynamic: {st.session_state.messages_right}{message_log}{resp}\n<|im_end|>",
                                                        format=Parasocial_Analysis.model_json_schema())
                           
                            # print(ch_response)
                            
                            ch_counter = 0
                            for entry in ch_response:
                                if "\"isParasocial\": 1" in entry:
                                    ch_counter += 1
                                    print(ch_counter)
                            if ch_counter == 5:
                                return True
                            else:
                                return False


                        except Exception as e:
                            error_message = f"Error querying chaperone: {e}"
                            response_placeholder.error(error_message)
                            st.session_state.messages_right.append({"role": "assistant", "content": error_message})
                            return False

                    print(f"\nInitial response: {response}\n")

                    #Scan initial response
                    isParasocial = ch_run(response)
                    print(f"\nisParasocial: {isParasocial}\n")

                    max_retries = 3
                    retry_count = 0
                    final_response = None
                    
                    while retry_count < max_retries:
                        if not isParasocial:
                            #Safe response
                            final_response = cleaned_response
                            break
                        else:
                            #Unsafe response - re-prompt
                            response_placeholder.warning(f"Initial response flagged. Regenerating response... (attempt {retry_count + 1})")

                            #Generate new response
                            new_response = responseGen(True, f"Unsafe prompt: {prompt}")
                            print(f"=== Re-prompted response ===\n{new_response}\n")

                            #Filter for rephrased content only
                            rephrased = extractRephraseXML(new_response)

                            if rephrased:
                                print(f"=== Extracted rephrase ===\n{rephrased}\n")
                                cleaned_response = rephrased
                                #Scan rephrased response
                                isParasocial = ch_run(cleaned_response)
                                print(f"\nisParasocial after rephrase: {isParasocial}\n")
                            else:
                                #no rephrase tags - clean and scan existing response
                                cleaned_response = StreamHandler.clean_response(new_response)
                                isParasocial = ch_run(cleaned_response)

                            retry_count += 1

                    #If no acceptable response after max retries, display the final rephrase attempt
                    if final_response is None:
                        final_response = cleaned_response
                        print(f"\n Using response after {max_retries} retries\n")

                    #Display final response
                    response_placeholder.empty()
                    response_placeholder.markdown(final_response)

                    #Add final response to message history
                    st.session_state.messages_right.append({"role": "assistant",
                                                            "content": final_response
                                                            })
                        
                    # # Add response to message history if there is no parasocial conversation dynamic
                    # def response_check(parasocialFlag=bool, localResponse=str):
                    #     if parasocialFlag == False:
                    #         st.session_state.messages_right.append({"role": "assistant", "content": localResponse})
                    #         # Automatically save the conversation after each successful message
                    #         # save_conversation()
                    #         return False
                    #     elif parasocialFlag == True:
                            
                    #         print(f"\nisParasocial pre re-prompt: {parasocialFlag}\n")
                            
                    #         localResponse = responseGen(True)
                    #         rephraseOnly = extractRephraseXML(localResponse)
                            
                    #         print(f"\nRe-prompted response: {localResponse}\n")
                            
                    #         print(f"\nrephrase tag only: {rephraseOnly}\n")
                            
                    #         parasocialFlag = ch_run(rephraseOnly)
                            
                    #         print(f"\nisParasocial on re-prompt: {parasocialFlag}\n")
                            
                    #         if parasocialFlag == True:
                    #             localReResponse = responseGen(True, rephraseOnly)
                    #             rephraseOnly = str(extractRephraseXML(localReResponse))
                                
                    #             print(f"\n{rephraseOnly}\n")
                                
                    #             parasocialFlag = ch_run(rephraseOnly)
                    #         if parasocialFlag == False:
                    #             #Append acceptable response to message history.
                    #             st.session_state.messages_right.append({"role": "assistant", "content": rephraseOnly})
                    #         return parasocialFlag
                    #         #return response_check(parasocialFlag, localResponse)


                    # while True:
                    #     if isParasocial is not None:
                    #         if response_check(isParasocial, response) == False:
                    #             break
                    #         else:
                    #             pass

                    # # Clear the stream handler after generation
                    # st.session_state.conversation_right.llm.callbacks = []
                    
                
                except Exception as e:
                    error_message = f"Error generating response: {str(e)}"
                    response_placeholder.error(error_message)
                    st.session_state.messages_right.append({"role": "assistant", "content": error_message})
                    
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
            format_func=lambda x: f'{x}',
            key="model_select",
            on_change=on_model_change,
            label_visibility="collapsed"
        )
            
    
    if prompt := st.chat_input(f"Chat with both copies of {model_name}..."):
        st.session_state.shared_prompt = prompt
    with left_column:
        st.subheader("Unmonitored Chatbot")
        unmonitored_chat_interface()
    with right_column:
        st.subheader("Monitored Chatbot")
        monitored_chat_interface()
    if 'shared_prompt' in st.session_state and st.session_state.shared_prompt:
        st.session_state.shared_prompt = None
    