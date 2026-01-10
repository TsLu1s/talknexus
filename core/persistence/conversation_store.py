import os
import pickle
from datetime import datetime
from typing import Optional

from config import (
    CONVERSATIONS_DIR,
    CONVERSATION_TITLE_MAX_LENGTH,
    NEW_CONVERSATION_ID,
    NEW_CONVERSATION_TITLE,
)
from config.constants import MessageRole


class ConversationStore:
    """Manages conversation persistence to disk."""

    def __init__(self, base_dir: str = None):
        """
        Initialize ConversationStore.

        Args:
            base_dir: Directory for storing conversations
        """
        self.base_dir = base_dir or str(CONVERSATIONS_DIR)
        os.makedirs(self.base_dir, exist_ok=True)

    def save(
        self,
        conversation_id: str,
        messages: list[dict],
        model: str,
        memory_messages: list = None,
        title: str = None,
    ) -> str:
        """
        Save a conversation to disk.

        Args:
            conversation_id: Unique identifier for the conversation
            messages: List of message dictionaries
            model: Model name used for this conversation
            memory_messages: Optional LangChain memory messages
            title: Optional conversation title

        Returns:
            The file ID used for saving
        """
        if not messages:
            return ""

        # Generate title from first user message if not provided
        if not title or title == NEW_CONVERSATION_TITLE:
            first_user_msg = next(
                (msg for msg in messages if msg["role"] == MessageRole.USER.value),
                None,
            )
            if first_user_msg:
                title = first_user_msg["content"][:CONVERSATION_TITLE_MAX_LENGTH].strip()

        # Generate conversation ID if new
        if conversation_id == NEW_CONVERSATION_ID:
            conversation_id = self._generate_id_from_title(title)

        # Create file ID with timestamp
        file_id = f"{conversation_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Prepare conversation data
        conversation_data = {
            "messages": messages,
            "model": model,
            "memory": memory_messages or [],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "title": title,
        }

        # Remove previous versions of this conversation
        self._remove_previous_versions(conversation_id)

        # Save to file
        filepath = os.path.join(self.base_dir, f"{file_id}.pkl")
        with open(filepath, "wb") as f:
            pickle.dump(conversation_data, f)

        return conversation_id

    def load(self, conversation_id: str) -> Optional[dict]:
        """
        Load a conversation from disk.

        Args:
            conversation_id: ID of the conversation to load

        Returns:
            Conversation data dictionary or None
        """
        filepath = os.path.join(self.base_dir, f"{conversation_id}.pkl")
        try:
            with open(filepath, "rb") as f:
                return pickle.load(f)
        except (FileNotFoundError, pickle.UnpicklingError):
            return None

    def delete(self, conversation_id: str) -> bool:
        """
        Delete a conversation from disk.

        Args:
            conversation_id: ID of the conversation to delete

        Returns:
            True if deletion was successful
        """
        filepath = os.path.join(self.base_dir, f"{conversation_id}.pkl")
        try:
            os.remove(filepath)
            return True
        except OSError:
            return False

    def list_all(self) -> list[tuple[str, str]]:
        """
        List all saved conversations.

        Returns:
            List of tuples (conversation_id, display_name)
        """
        conversations = []

        if not os.path.exists(self.base_dir):
            return conversations

        for filename in os.listdir(self.base_dir):
            if not filename.endswith(".pkl"):
                continue

            conversation_id = filename[:-4]  # Remove .pkl extension
            filepath = os.path.join(self.base_dir, filename)

            try:
                with open(filepath, "rb") as f:
                    data = pickle.load(f)

                title = data.get("title", "")
                if not title:
                    first_msg = next(
                        (msg["content"] for msg in data.get("messages", [])
                         if msg["role"] == MessageRole.USER.value),
                        "",
                    )
                    title = first_msg[:CONVERSATION_TITLE_MAX_LENGTH]
                    if len(first_msg) > CONVERSATION_TITLE_MAX_LENGTH:
                        title += "..."

                timestamp = data.get("timestamp", "Unknown date")
                model = data.get("model", "unknown")
                display_name = f"{timestamp[:10]} - {model}: {title}"

                conversations.append((conversation_id, display_name))

            except (pickle.UnpicklingError, KeyError):
                continue

        # Sort by newest first
        conversations.sort(key=lambda x: x[0], reverse=True)
        return conversations

    def _generate_id_from_title(self, title: str) -> str:
        """Generate a conversation ID from title."""
        if not title:
            return NEW_CONVERSATION_ID
        return title[:CONVERSATION_TITLE_MAX_LENGTH].strip().replace(" ", "_")

    def _remove_previous_versions(self, conversation_id: str) -> None:
        """Remove previous versions of a conversation."""
        if not os.path.exists(self.base_dir):
            return

        for filename in os.listdir(self.base_dir):
            if filename.startswith(f"{conversation_id}_") and filename.endswith(".pkl"):
                try:
                    os.remove(os.path.join(self.base_dir, filename))
                except OSError:
                    pass