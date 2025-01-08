from langchain.callbacks.base import BaseCallbackHandler
import warnings
warnings.filterwarnings("ignore", category=Warning)

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
        
    def on_llm_new_token(self, token: str, **kwargs):
        """
        Processes each new token from the LLM response stream.
        
        Args:
            token (str): Individual token from the LLM response
            **kwargs: Additional keyword arguments from the callback
        """
        try:
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

