from langchain.callbacks.base import BaseCallbackHandler
import re
import warnings
warnings.filterwarnings("ignore", category=Warning)
warnings.filterwarnings("ignore", message=".*st.rerun.*")

class StreamHandler(BaseCallbackHandler):
    """
    Custom callback handler for streaming LLM responses token by token.
    
    Attributes:
        container: Streamlit container object for displaying streamed tokens
        text (str): Accumulated response text
    """
    def __init__(self, container):
        self.container = container
        self.text = ""
        self.in_thinking_section = False
        self.buffer = ""
    @staticmethod
    def clean_response(response: str) -> str:
        """Removes '<think>' reasoning parts from the response."""
        response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
        return response.strip()
    
    def on_llm_new_token(self, token: str, **kwargs):
        """
        Processes each new token from the LLM response stream.
        
        Args:
            token (str): Individual token from the LLM response
            **kwargs: Additional keyword arguments from the callback
        """
        try:
            # Check for thinking section markers
            if "<think>" in token:
                self.in_thinking_section = True
                # Only add part of token before <think> if exists
                before_think = token.split("<think>")[0]
                if before_think:
                    self.text += before_think
                # Capture the rest in buffer without displaying
                self.buffer = token[len(before_think):]
                clean_text = self.text
            elif "</think>" in token and self.in_thinking_section:
                self.in_thinking_section = False
                # Add part after </think> if exists
                after_think = token.split("</think>")[1] if len(token.split("</think>")) > 1 else ""
                if after_think:
                    self.text += after_think
                clean_text = self.text
            elif self.in_thinking_section:
                # If in thinking section, add to buffer but don't display
                self.buffer += token
                clean_text = self.text
            else:
                # Normal token processing
                self.text += token
                clean_text = self.text
            
            # Check if we need to clean up AIMessage formatting
            if "AIMessage" in clean_text:
                # Handle complete AIMessage format
                if "content=\"" in clean_text:
                    try:
                        clean_text = clean_text.split("content=\"")[1].rsplit("\"", 1)[0]
                    except IndexError:
                        # If splitting fails, keep the original text
                        pass
                
                # Remove any remaining AIMessage wrapper
                clean_text = (clean_text.replace("AIMessage(", "")
                                        .replace(", additional_kwargs={}", "")
                                        .replace(", response_metadata={})", "")
                                        .replace('{ "data":' , "")
                                        .replace('}' , "")
                )
            #clean_text = self.clean_response(clean_text)
            # Update the display with cleaned text
            self.container.markdown(clean_text)
            
        except Exception as e:
            # Log the error without disrupting the stream
            print(f"Warning in StreamHandler: {str(e)}")
            # Still try to display something to the user
            self.container.markdown(self.text)

EMBEDDING_MODELS = {
    "bge-small": {
        "name": "BAAI/bge-small-en-v1.5",
        "type": "huggingface",
        "description": "Optimized for retrieval tasks, good balance of speed/quality"
    },
    "bge-large": {
        "name": "BAAI/bge-large-en-v1.5",
        "type": "huggingface",
        "description": "Highest quality, but slower and more resource intensive"
    },
    "minilm": {
        "name": "sentence-transformers/all-MiniLM-L6-v2",
        "type": "huggingface",
        "description": "Lightweight, fast, good general purpose model"
    },
    "mpnet": {
        "name": "sentence-transformers/all-mpnet-base-v2",
        "type": "huggingface",
        "description": "Higher quality, slower than MiniLM"
    },
    "e5-small": {
        "name": "intfloat/e5-small-v2",
        "type": "huggingface",
        "description": "Efficient model optimized for semantic search"
    },
    "snowflake-arctic-embed2:568m": {
        "name": "snowflake-arctic-embed2:568m",
        "type": "ollama",
        "description": "Multilingual frontier model with strong performance [Ollama Embedding Model, Download it first]"
    }
}

