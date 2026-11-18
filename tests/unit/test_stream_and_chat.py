from core.conversation import ConversationManager, get_conversation_chain
from utils.stream_handler import StreamHandler


class FakeContainer:
    def __init__(self):
        self.renders = []

    def markdown(self, text):
        self.renders.append(text)


def stream(tokens):
    container = FakeContainer()
    handler = StreamHandler(container)
    for token in tokens:
        handler.on_llm_new_token(token)
    return container.renders


def test_tokens_are_shown_as_they_arrive():
    assert stream(["Hel", "lo ", "world"]) == ["Hel", "Hello ", "Hello world"]


def test_thinking_section_is_hidden_while_streaming():
    renders = stream(["<think>", "let me", " plan", "</think>", "The answer", " is 42."])

    assert renders[-1] == "The answer is 42."
    assert not any("plan" in text or "think" in text for text in renders)


def test_clean_response_removes_thinking_blocks():
    raw = "<think>\nfirst\n</think>\n\nThe codename<think>second</think> is BLUEBIRD.\n"

    assert StreamHandler.clean_response(raw) == "The codename is BLUEBIRD."


def test_history_reaches_the_model_as_plain_text(fake_backend):
    # Before: return_messages=True put "[HumanMessage(content=...)]" reprs in the prompt.
    chain = get_conversation_chain("fake-llm")
    fake_backend.response = "Hello Ana!"
    chain.run("Hi, I am Ana")
    fake_backend.response = "Your name is Ana."
    chain.run("What is my name?")

    assert fake_backend.prompts[-1] == (
        "Current conversation:\n"
        "Human: Hi, I am Ana\n"
        "Assistant: Hello Ana!\n"
        "Human: What is my name?\n"
        "Assistant:"
    )
    assert fake_backend.llm_kwargs[-1]["model"] == "fake-llm"


def test_temperature_zero_is_kept():
    # Before: `temperature or DEFAULT` turned 0 into the default 0.2.
    assert ConversationManager("m", temperature=0).temperature == 0
    assert ConversationManager("m").temperature == 0.2
