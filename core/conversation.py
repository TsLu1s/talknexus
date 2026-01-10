from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama

from config import OLLAMA_BASE_URL, DEFAULT_TEMPERATURE


class ConversationManager:
    """Manages LangChain conversation chains."""

    def __init__(
        self,
        model_name: str,
        temperature: float = None,
        base_url: str = None,
    ):
        """
        Initialize ConversationManager.

        Args:
            model_name: Name of the Ollama model to use
            temperature: LLM temperature setting
            base_url: Ollama API base URL
        """
        self.model_name = model_name
        self.temperature = temperature or DEFAULT_TEMPERATURE
        self.base_url = base_url or OLLAMA_BASE_URL
        self._chain: ConversationChain | None = None

    def get_chain(self) -> ConversationChain:
        """
        Get or create the conversation chain.

        Returns:
            Configured ConversationChain instance
        """
        if self._chain is None:
            self._chain = self._create_chain()
        return self._chain

    def _create_chain(self) -> ConversationChain:
        """Create a new conversation chain."""
        llm = Ollama(
            model=self.model_name,
            temperature=self.temperature,
            base_url=self.base_url,
        )

        prompt = PromptTemplate(
            input_variables=["history", "input"],
            template="""Current conversation:
            {history}
            Human: {input}
            Assistant:""",
        )

        memory = ConversationBufferMemory(return_messages=True)

        return ConversationChain(
            llm=llm,
            memory=memory,
            prompt=prompt,
            verbose=False,
        )

    def reset(self) -> None:
        """Reset the conversation chain."""
        self._chain = None


def get_conversation_chain(model_name: str) -> ConversationChain:
    """
    Factory function to create a conversation chain.

    Returns:
        Configured ConversationChain
    """
    manager = ConversationManager(model_name)
    return manager.get_chain()