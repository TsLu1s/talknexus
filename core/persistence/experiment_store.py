import json
import logging
import os
import shutil
from typing import Callable, Optional

import faiss
import numpy as np
from langchain_classic.retrievers import ParentDocumentRetriever
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.stores import InMemoryStore

from config import EXPERIMENTS_DIR

EXPERIMENT_NAME_MAX_LENGTH = 100

_INDEX_FILE = "index.faiss"
_DOCUMENTS_FILE = "documents.json"
_CONFIG_FILE = "config.json"


def is_valid_experiment_name(name: str) -> bool:
    """Experiment names become folder names: letters, digits, spaces, '-' and '_' only."""
    return (
        isinstance(name, str)
        and bool(name)
        and name == name.strip()
        and len(name) <= EXPERIMENT_NAME_MAX_LENGTH
        and all(c.isalnum() or c in " -_" for c in name)
    )


class ExperimentStore:
    """
    Manages RAG experiment persistence.

    Each experiment is a folder with the FAISS index plus JSON documents and
    config. Nothing is unpickled, so a tampered folder cannot run code.
    """

    def __init__(self, base_dir: str = None):
        """
        Initialize ExperimentStore.

        Args:
            base_dir: Directory for storing experiments
        """
        self.base_dir = base_dir or str(EXPERIMENTS_DIR)
        os.makedirs(self.base_dir, exist_ok=True)

    def _get_dir(self, experiment_name: str) -> str:
        """Return the folder of an experiment, rejecting unsafe names."""
        if not is_valid_experiment_name(experiment_name):
            raise ValueError(f"Invalid experiment name: {experiment_name!r}")
        return os.path.join(self.base_dir, experiment_name)

    def save(
        self,
        experiment_name: str,
        retriever: ParentDocumentRetriever,
        config: dict,
    ) -> bool:
        """
        Save an experiment with its configuration.

        Returns:
            True if save was successful
        """
        try:
            experiment_dir = self._get_dir(experiment_name)
            os.makedirs(experiment_dir, exist_ok=True)

            vectorstore = retriever.vectorstore
            child_ids = [vectorstore.index_to_docstore_id[i] for i in range(vectorstore.index.ntotal)]
            parent_ids = list(retriever.docstore.yield_keys())
            documents = {
                "children": [
                    [doc_id, _doc_to_dict(vectorstore.docstore.search(doc_id))] for doc_id in child_ids
                ],
                "parents": {
                    doc_id: _doc_to_dict(doc)
                    for doc_id, doc in zip(parent_ids, retriever.docstore.mget(parent_ids), strict=True)
                },
            }

            # Written through Python file I/O so non-ASCII names also work on Windows.
            with open(os.path.join(experiment_dir, _INDEX_FILE), "wb") as f:
                f.write(faiss.serialize_index(vectorstore.index).tobytes())
            _write_json(os.path.join(experiment_dir, _DOCUMENTS_FILE), documents)
            # Config goes last: list_all() only shows experiments that have one.
            _write_json(os.path.join(experiment_dir, _CONFIG_FILE), config)

            return True

        except Exception as e:
            logging.error(f"Error saving experiment {experiment_name}: {str(e)}")
            return False

    def load(
        self,
        experiment_name: str,
        embeddings_factory: Callable[[str], Embeddings],
    ) -> tuple[Optional[FAISS], Optional[InMemoryStore], Optional[dict]]:
        """
        Load a saved experiment.

        Args:
            experiment_name: Name of the experiment to load
            embeddings_factory: Builds the embedding model from its config key

        Returns:
            Tuple of (vectorstore, parent docstore, config) or (None, None, None) on error
        """
        try:
            experiment_dir = self._get_dir(experiment_name)
            config = _read_json(os.path.join(experiment_dir, _CONFIG_FILE))
            documents = _read_json(os.path.join(experiment_dir, _DOCUMENTS_FILE))

            with open(os.path.join(experiment_dir, _INDEX_FILE), "rb") as f:
                index = faiss.deserialize_index(np.frombuffer(f.read(), dtype=np.uint8))

            children = documents["children"]
            if index.ntotal != len(children):
                raise ValueError("index and documents are out of sync")

            vectorstore = FAISS(
                embedding_function=embeddings_factory(config["embedding_model"]),
                index=index,
                docstore=InMemoryDocstore({doc_id: Document(**doc) for doc_id, doc in children}),
                index_to_docstore_id={i: doc_id for i, (doc_id, _) in enumerate(children)},
            )

            docstore = InMemoryStore()
            docstore.mset([(doc_id, Document(**doc)) for doc_id, doc in documents["parents"].items()])

            return vectorstore, docstore, config

        except Exception as e:
            logging.error(f"Error loading experiment {experiment_name}: {str(e)}")
            return None, None, None

    def delete(self, experiment_name: str) -> bool:
        """
        Delete a saved experiment.

        Args:
            experiment_name: Name of the experiment to delete

        Returns:
            True if deletion was successful
        """
        try:
            shutil.rmtree(self._get_dir(experiment_name))
            return True

        except (OSError, ValueError) as e:
            logging.error(f"Error deleting experiment {experiment_name}: {str(e)}")
            return False

    def list_all(self) -> list[tuple[str, dict]]:
        """
        List all experiments with their configurations, sorted by name.

        Returns:
            List of tuples (experiment_name, config)
        """
        experiments = []

        if not os.path.exists(self.base_dir):
            return experiments

        for experiment_name in sorted(os.listdir(self.base_dir)):
            config_path = os.path.join(self.base_dir, experiment_name, _CONFIG_FILE)
            if not is_valid_experiment_name(experiment_name) or not os.path.isfile(config_path):
                continue  # also skips legacy *.pkl experiments, which are never unpickled

            try:
                experiments.append((experiment_name, _read_json(config_path)))
            except (OSError, ValueError) as e:
                logging.error(f"Error loading config for {experiment_name}: {str(e)}")

        return experiments


def _doc_to_dict(doc: Document) -> dict:
    return {"page_content": doc.page_content, "metadata": doc.metadata}


def _write_json(path: str, data) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, default=str)


def _read_json(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)
