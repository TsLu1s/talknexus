import json
import os
import pickle
from types import SimpleNamespace

import pytest
from langchain_core.messages import AIMessage, HumanMessage

import core.persistence.conversation_store as conversation_store_module
from config import NEW_CONVERSATION_ID
from core.persistence import ConversationStore


def chat(*contents: str) -> list[dict]:
    """Alternate user / assistant messages."""
    return [
        {"role": "user" if i % 2 == 0 else "assistant", "content": content}
        for i, content in enumerate(contents)
    ]


@pytest.fixture
def store(tmp_path):
    return ConversationStore(str(tmp_path / "conversations"))


def test_new_conversation_gets_a_random_id_and_a_title(store):
    conversation_id = store.save(NEW_CONVERSATION_ID, chat("Hello there", "Hi!"), "llama3.2")

    assert len(conversation_id) == 32
    data = store.load(conversation_id)
    assert data["title"] == "Hello there"
    assert data["messages"] == chat("Hello there", "Hi!")
    assert data["model"] == "llama3.2"


def test_files_are_plain_json(store):
    conversation_id = store.save(NEW_CONVERSATION_ID, chat("Hello"), "m")

    assert os.listdir(store.base_dir) == [f"{conversation_id}.json"]
    with open(os.path.join(store.base_dir, f"{conversation_id}.json"), encoding="utf-8") as f:
        assert json.load(f)["messages"][0]["content"] == "Hello"


def test_chats_with_the_same_opening_words_are_kept_apart(store):
    # Before: the file name was the title, and saving one chat deleted every
    # file starting with "<title>_", so these chats destroyed each other.
    first = store.save(NEW_CONVERSATION_ID, chat("Hello", "A"), "m")
    second = store.save(NEW_CONVERSATION_ID, chat("Hello", "B"), "m")
    third = store.save(NEW_CONVERSATION_ID, chat("Hello world", "C"), "m")
    store.save(first, chat("Hello", "A", "more", "A2"), "m")

    assert len({first, second, third}) == 3
    assert store.load(first)["messages"][-1]["content"] == "A2"
    assert store.load(second)["messages"][-1]["content"] == "B"
    assert store.load(third)["messages"][-1]["content"] == "C"
    assert len(store.list_all()) == 3


def test_saving_again_updates_the_same_entry(store):
    # Before: continuing a loaded chat created a second history entry each time.
    conversation_id = store.save(NEW_CONVERSATION_ID, chat("Plan a trip"), "m")

    assert store.save(conversation_id, chat("Plan a trip", "Sure", "To Porto"), "m") == conversation_id
    assert [cid for cid, _ in store.list_all()] == [conversation_id]
    assert len(store.load(conversation_id)["messages"]) == 3


@pytest.mark.parametrize("first_message", ["what is 1/2?", "../escaped", "..\\..\\x", "a:b*c?", "/etc/passwd"])
def test_any_first_message_is_saved_inside_the_store(store, first_message):
    # Before: "/" in the first message crashed the chat page, and "../" wrote
    # the file outside the conversations folder.
    conversation_id = store.save(NEW_CONVERSATION_ID, chat(first_message, "ok"), "m")

    assert os.listdir(store.base_dir) == [f"{conversation_id}.json"]
    assert os.listdir(os.path.dirname(store.base_dir)) == ["conversations"]
    assert store.load(conversation_id)["title"] == first_message


@pytest.mark.parametrize("bad_id", ["../x", "abc", "", "0" * 31, "g" * 32, "../" + "0" * 32, None])
def test_ids_that_could_escape_the_folder_are_rejected(store, bad_id):
    assert store.load(bad_id) is None
    assert store.delete(bad_id) is False
    with pytest.raises(ValueError):
        store.save(bad_id, chat("hi"), "m")


def test_memory_messages_round_trip(store):
    memory = [HumanMessage(content="My name is Ana"), AIMessage(content="Hi Ana")]
    conversation_id = store.save(
        NEW_CONVERSATION_ID, chat("My name is Ana", "Hi Ana"), "m", memory_messages=memory
    )

    assert store.load(conversation_id)["memory"] == memory


def test_list_is_newest_first(store, monkeypatch):
    # Before: "newest first" actually sorted by title, alphabetically.
    timestamps = iter(["2026-01-01 10:00:00", "2026-03-01 10:00:00", "2026-02-01 10:00:00"])
    fake_now = SimpleNamespace(strftime=lambda fmt: next(timestamps))
    monkeypatch.setattr(conversation_store_module, "datetime", SimpleNamespace(now=lambda: fake_now))

    for title in ("old", "newest", "middle"):
        store.save(NEW_CONVERSATION_ID, chat(title), "m")

    assert [name.split(": ")[1] for _, name in store.list_all()] == ["newest", "middle", "old"]


def test_corrupt_and_foreign_files_are_skipped(store):
    good = store.save(NEW_CONVERSATION_ID, chat("good"), "m")
    for filename, content in [
        ("f" * 32 + ".json", "{not json"),
        ("e" * 32 + ".json", "[1, 2]"),
        ("notes.txt", "hello"),
    ]:
        with open(os.path.join(store.base_dir, filename), "w", encoding="utf-8") as f:
            f.write(content)

    assert [cid for cid, _ in store.list_all()] == [good]
    assert store.load("f" * 32) is None
    assert store.load("e" * 32) is None


def test_legacy_pickle_files_are_never_unpickled(store, pickle_bomb):
    # Before: every .pkl in the folder was unpickled, so a planted file ran code.
    with open(os.path.join(store.base_dir, "Hello_20240101_000000.pkl"), "wb") as f:
        pickle.dump(pickle_bomb.payload, f)

    assert store.list_all() == []
    assert store.load("Hello_20240101_000000") is None
    assert not pickle_bomb.marker.exists()


def test_empty_conversation_is_not_saved(store):
    assert store.save(NEW_CONVERSATION_ID, [], "m") == ""
    assert os.listdir(store.base_dir) == []


def test_delete(store):
    conversation_id = store.save(NEW_CONVERSATION_ID, chat("bye"), "m")

    assert store.delete(conversation_id) is True
    assert store.list_all() == []
    assert store.delete(conversation_id) is False
