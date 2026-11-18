import json
import os
import pickle

import pytest

from core.persistence import ExperimentStore
from core.persistence.experiment_store import is_valid_experiment_name
from core.rag_engine import RAGEngine

PAGES = [
    "The secret project codename is BLUEBIRD.\nIt launches in 2031.",
    "The cafeteria serves soup on Fridays.\nParking is free after six.",
]
CONFIG = {"llm_model": "fake-llm", "embedding_model": "bge-small", "chunk_size": 100, "top_k": 1}


@pytest.fixture
def engine(fake_backend, make_upload):
    engine = RAGEngine()
    engine.process_pdfs([make_upload("facts.pdf", PAGES)], "exp1", child_chunk_size=100, top_k=1)
    return engine


@pytest.mark.parametrize(
    "name, valid",
    [
        ("exp1", True),
        ("My Experiment_2-final", True),
        ("Relatório", True),
        ("x" * 100, True),
        ("", False),
        (" exp", False),
        ("exp ", False),
        ("Report v1.0", False),
        ("../x", False),
        ("a/b", False),
        ("a\\b", False),
        ("x" * 101, False),
        ("name\n", False),
        (None, False),
    ],
)
def test_experiment_name_rules(name, valid):
    assert is_valid_experiment_name(name) is valid


def test_save_and_load_round_trip_returns_the_same_chunks(engine):
    question = "What is the secret project codename?"
    before = [doc.page_content for doc in engine.retriever.invoke(question)]
    assert engine.save_experiment("exp1", CONFIG)

    fresh = RAGEngine()  # a new session: nothing in memory
    loaded, config = fresh.load_experiment("exp1")

    assert loaded and config == CONFIG
    after = [doc.page_content for doc in fresh.retriever.invoke(question)]
    assert after == before
    assert "BLUEBIRD" in after[0]


def test_saved_experiment_is_json_and_a_faiss_index(engine, data_dirs):
    # Before: the whole retriever was pickled, embedding model included (134 MB
    # for a 3-page PDF with bge-small), and loading it could run code.
    assert engine.save_experiment("exp1", CONFIG)

    experiment_dir = data_dirs.experiments / "exp1"
    assert sorted(os.listdir(experiment_dir)) == ["config.json", "documents.json", "index.faiss"]
    assert json.loads((experiment_dir / "config.json").read_text()) == CONFIG
    assert sum(f.stat().st_size for f in experiment_dir.iterdir()) < 1_000_000


def test_legacy_pickle_experiments_are_never_unpickled(data_dirs, pickle_bomb):
    store = ExperimentStore()
    for suffix in ("_config.pkl", "_retriever.pkl"):
        with open(data_dirs.experiments / f"old{suffix}", "wb") as f:
            pickle.dump(pickle_bomb.payload, f)

    assert store.list_all() == []
    assert store.load("old", lambda name: None) == (None, None, None)
    assert not pickle_bomb.marker.exists()


def test_unsafe_names_never_touch_the_disk(data_dirs, engine):
    store = ExperimentStore()

    assert store.save("../evil", engine.retriever, CONFIG) is False
    assert store.load("../evil", lambda name: None) == (None, None, None)
    assert store.delete("../evil") is False
    assert not (data_dirs.experiments.parent / "evil").exists()


def test_index_and_documents_out_of_sync_fail_to_load(engine, data_dirs):
    assert engine.save_experiment("exp1", CONFIG)
    documents_file = data_dirs.experiments / "exp1" / "documents.json"
    documents = json.loads(documents_file.read_text())
    documents["children"] = documents["children"][:-1]
    documents_file.write_text(json.dumps(documents))

    assert RAGEngine().load_experiment("exp1") == (False, {})


def test_list_is_sorted_and_delete_removes_the_folder(engine, data_dirs):
    assert engine.save_experiment("b-exp", CONFIG)
    assert engine.save_experiment("a-exp", CONFIG)

    assert [name for name, _ in engine.list_experiments()] == ["a-exp", "b-exp"]
    assert engine.delete_experiment("a-exp") is True
    assert [name for name, _ in engine.list_experiments()] == ["b-exp"]
    assert not (data_dirs.experiments / "a-exp").exists()
