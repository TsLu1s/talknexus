"""AI Conversation page end to end: chat, save, history, continue, delete."""
import json

from config import NEW_CONVERSATION_ID
from core.persistence import ConversationStore


def send(at, text):
    at.chat_input[0].set_value(text).run()
    return at


def saved_chats(data_dirs) -> list[dict]:
    if not data_dirs.conversations.exists():
        return []
    return [json.loads(path.read_text()) for path in sorted(data_dirs.conversations.glob("*.json"))]


def contents(messages) -> list[str]:
    return [message["content"] for message in messages]


def start_new_conversation(at):
    at.selectbox(key="action_selector").select("📂 Saved Conversations").run()
    at.selectbox(key="action_selector").select("🆕 New Conversation").run()


def continue_conversation(at, title):
    at.selectbox(key="action_selector").select("📂 Saved Conversations").run()
    conversation_id = next(cid for cid, name in at.session_state["saved_conversations"] if name.endswith(title))
    at.selectbox(key="convo_selector").select(conversation_id).run()
    at.selectbox(key=f"action_{conversation_id}").select("📝 Continue Conversation").run()
    return conversation_id


def test_reply_is_streamed_shown_and_saved(open_page, fake_backend, data_dirs):
    fake_backend.response = "Hello Ana!"
    at = open_page("AI Conversation")

    send(at, "Hi, I am Ana")

    assert not at.exception and not at.error
    assert contents(at.session_state["messages"]) == ["Hi, I am Ana", "Hello Ana!"]
    [chat] = saved_chats(data_dirs)
    assert chat["title"] == "Hi, I am Ana" and chat["model"] == "fake-llm"
    assert not list(data_dirs.conversations.glob("*.pkl"))


def test_reasoning_is_kept_out_of_answer_history_and_file(open_page, fake_backend, data_dirs):
    fake_backend.response = "<think>secret plan</think>Final answer."
    at = open_page("AI Conversation")

    send(at, "First question")
    fake_backend.response = "Second answer."
    send(at, "Second question")

    assert contents(at.session_state["messages"])[1] == "Final answer."
    assert "secret plan" not in fake_backend.prompts[-1]  # history sent with the next prompt
    assert "secret plan" not in json.dumps(saved_chats(data_dirs))


def test_first_message_with_a_slash_works(open_page, fake_backend, data_dirs):
    # Before: the title became the file name, so "/" crashed the page to Home.
    at = open_page("AI Conversation")

    send(at, "what is 1/2?")

    assert not at.exception and not at.error
    assert at.session_state["current_page"] == "AI Conversation"
    assert saved_chats(data_dirs)[0]["title"] == "what is 1/2?"


def test_history_is_sent_to_the_model_as_plain_text(open_page, fake_backend):
    at = open_page("AI Conversation")

    send(at, "My name is Ana")
    send(at, "What is my name?")

    assert "Human: My name is Ana\nAssistant: Fake answer\nHuman: What is my name?" in fake_backend.prompts[-1]
    assert "HumanMessage(" not in fake_backend.prompts[-1]


def test_two_chats_with_the_same_opening_are_both_kept(open_page, fake_backend, data_dirs):
    # Before: the second "Hello" chat silently deleted the first one.
    at = open_page("AI Conversation")
    send(at, "Hello")
    start_new_conversation(at)
    assert at.session_state["messages"] == []

    send(at, "Hello")

    assert len(saved_chats(data_dirs)) == 2
    at.selectbox(key="action_selector").select("📂 Saved Conversations").run()
    assert len(at.selectbox(key="convo_selector").options) == 3  # placeholder + both chats


def test_continue_a_saved_chat_without_duplicating_it(open_page, fake_backend, data_dirs):
    at = open_page("AI Conversation")
    send(at, "Plan a trip to Porto")
    start_new_conversation(at)
    send(at, "Second chat")

    conversation_id = continue_conversation(at, "Plan a trip to Porto")

    assert contents(at.session_state["messages"]) == ["Plan a trip to Porto", "Fake answer"]
    assert at.selectbox(key=f"action_{conversation_id}").value == "Select Action"
    send(at, "Add a day in Braga")
    assert "Human: Plan a trip to Porto" in fake_backend.prompts[-1]  # memory restored
    chats = saved_chats(data_dirs)
    assert len(chats) == 2  # before: continuing added a duplicate entry
    trip = next(chat for chat in chats if chat["title"] == "Plan a trip to Porto")
    assert len(trip["messages"]) == 4


def test_continue_a_chat_whose_model_was_removed(open_page, fake_backend, data_dirs):
    ConversationStore(str(data_dirs.conversations)).save(
        NEW_CONVERSATION_ID,
        [{"role": "user", "content": "Old chat"}, {"role": "assistant", "content": "Old answer"}],
        "removed-model",
    )
    at = open_page("AI Conversation")

    continue_conversation(at, "Old chat")
    send(at, "Still there?")

    assert not at.error
    assert fake_backend.llm_kwargs[-1]["model"] == "fake-llm"  # the selected, installed model


def delete(at, title):
    at.selectbox(key="action_selector").select("📂 Saved Conversations").run()
    conversation_id = next(cid for cid, name in at.session_state["saved_conversations"] if name.endswith(title))
    at.selectbox(key="convo_selector").select(conversation_id).run()
    at.selectbox(key=f"action_{conversation_id}").select("🗑️ Delete Conversation").run()
    at.checkbox(key=f"confirm_delete_{conversation_id}").check().run()


def test_delete_conversations_one_by_one(open_page, fake_backend, data_dirs):
    at = open_page("AI Conversation")
    send(at, "Keep me")
    start_new_conversation(at)
    send(at, "Delete me")

    delete(at, "Delete me")

    assert not at.exception
    assert [chat["title"] for chat in saved_chats(data_dirs)] == ["Keep me"]
    assert at.session_state["messages"] == []
    assert at.selectbox(key="convo_selector").value == "Select Conversation"  # deleted ID not kept

    delete(at, "Keep me")

    assert not at.exception
    assert saved_chats(data_dirs) == []
    assert any("Conversation History is empty" in info.value for info in at.info)


def test_visiting_the_rag_page_keeps_the_chat(open_page, fake_backend, data_dirs):
    # Before: both pages shared one message list; the RAG page emptied it, and the
    # next AI message overwrote the saved chat without its earlier messages.
    at = open_page("AI Conversation")
    send(at, "My name is Ana")
    send(at, "I live in Porto")

    at.button(key="nav_RAG Conversation").click().run()
    at.button(key="nav_AI Conversation").click().run()

    assert len(at.session_state["messages"]) == 4
    send(at, "What do you know?")
    assert len(saved_chats(data_dirs)[0]["messages"]) == 6


def test_model_errors_are_shown_and_saved(open_page, fake_backend, data_dirs):
    fake_backend.response = RuntimeError("model 'x' not found")
    at = open_page("AI Conversation")

    send(at, "Hi")

    assert not at.exception
    assert any("Error generating response: model 'x' not found" in error.value for error in at.error)
    assert saved_chats(data_dirs)[0]["messages"][-1]["content"].startswith("Error generating response")
