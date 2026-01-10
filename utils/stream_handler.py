import re

from langchain.callbacks.base import BaseCallbackHandler

import warnings
warnings.filterwarnings("ignore", category=Warning)
warnings.filterwarnings("ignore", message=".*st.rerun.*")


class StreamHandler(BaseCallbackHandler):
    """
    Custom callback handler for streaming LLM responses.

    Handles token-by-token streaming with support for filtering
    thinking sections (e.g., <think>...</think> tags).

    Attributes:
        container: Streamlit container for displaying streamed tokens
        text: Accumulated response text
    """

    def __init__(self, container):
        """
        Initialize StreamHandler.

        Args:
            container: Streamlit container object for displaying tokens
        """
        self.container = container
        self.text = ""
        self.in_thinking_section = False
        self.buffer = ""

    @staticmethod
    def clean_response(response: str) -> str:
        """
        Remove '<think>' reasoning parts from the response.

        Args:
            response: Raw response text

        Returns:
            Cleaned response without thinking sections
        """
        response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL)
        return response.strip()

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """
        Process each new token from the LLM response stream.

        Args:
            token: Individual token from the LLM response
            **kwargs: Additional keyword arguments from the callback
        """
        try:
            clean_text = self._process_token(token)
            clean_text = self._clean_ai_message_format(clean_text)
            self.container.markdown(clean_text)

        except Exception as e:
            # Log error without disrupting stream
            print(f"Warning in StreamHandler: {str(e)}")
            self.container.markdown(self.text)

    def _process_token(self, token: str) -> str:
        """Process token and handle thinking sections."""
        if "<think>" in token:
            self.in_thinking_section = True
            before_think = token.split("<think>")[0]
            if before_think:
                self.text += before_think
            self.buffer = token[len(before_think):]

        elif "</think>" in token and self.in_thinking_section:
            self.in_thinking_section = False
            parts = token.split("</think>")
            if len(parts) > 1:
                after_think = parts[1]
                if after_think:
                    self.text += after_think

        elif self.in_thinking_section:
            self.buffer += token

        else:
            self.text += token

        return self.text

    def _clean_ai_message_format(self, text: str) -> str:
        """Clean up AIMessage formatting artifacts."""
        if "AIMessage" not in text:
            return text

        # Handle complete AIMessage format
        if 'content="' in text:
            try:
                text = text.split('content="')[1].rsplit('"', 1)[0]
            except IndexError:
                pass

        # Remove remaining AIMessage wrapper artifacts
        cleanup_patterns = [
            "AIMessage(",
            ", additional_kwargs={}",
            ", response_metadata={})",
            '{ "data":',
            "}",
        ]

        for pattern in cleanup_patterns:
            text = text.replace(pattern, "")

        return text