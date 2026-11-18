import json
import logging
import tempfile
import os
from typing import Optional

import faiss
from langchain_classic.chains import RetrievalQA
from langchain_classic.retrievers import ParentDocumentRetriever
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings, OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.stores import InMemoryStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import (
    OLLAMA_BASE_URL,
    DEFAULT_TEMPERATURE,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_TOP_K,
    EMBEDDING_MODELS_FILE,
    PARENT_CHUNK_MULTIPLIER,
    CHUNK_OVERLAP_RATIO,
    TEXT_SEPARATORS,
)
from config.constants import EmbeddingModelType
from core.persistence import ExperimentStore

import warnings
warnings.filterwarnings("ignore", category=Warning)


class EmbeddingModels:
    """Manages embedding model configurations."""

    _cache: Optional[dict] = None

    @classmethod
    def load(cls) -> dict:
        """Load embedding models from JSON configuration."""
        if cls._cache is None:
            try:
                with open(EMBEDDING_MODELS_FILE, "r") as f:
                    cls._cache = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                cls._cache = cls._get_defaults()
        return cls._cache

    @classmethod
    def _get_defaults(cls) -> dict:
        """Return default embedding models if config file missing."""
        return {
            "bge-small": {
                "name": "BAAI/bge-small-en-v1.5",
                "type": "huggingface",
                "description": "Optimized for retrieval tasks, good balance of speed/quality",
            },
            "minilm": {
                "name": "sentence-transformers/all-MiniLM-L6-v2",
                "type": "huggingface",
                "description": "Lightweight, fast, good general purpose model",
            },
        }

    @classmethod
    def get_model_names(cls) -> list[str]:
        """Get list of available embedding model names."""
        return list(cls.load().keys())

    @classmethod
    def get_model_config(cls, name: str) -> dict:
        """Get configuration for a specific embedding model."""
        return cls.load().get(name, {})


class RAGEngine:
    """
    RAG (Retrieval-Augmented Generation) processing engine.

    Handles PDF processing, embedding generation, and document retrieval.
    """

    def __init__(self):
        """Initialize RAG engine."""
        self.vectorstore = None
        self.store = None
        self.retriever = None
        self._separators = TEXT_SEPARATORS
        self.experiment_store = ExperimentStore()

    def process_pdfs(
        self,
        pdf_files: list,
        experiment_name: str,
        embedding_model: str = "bge-small",
        child_chunk_size: int = 50,
        top_k: int = 4,
    ) -> int:
        """
        Process PDF files and create retriever.

        Args:
            pdf_files: List of uploaded PDF file objects
            experiment_name: Name for this experiment
            embedding_model: Name of embedding model to use
            child_chunk_size: Size of child chunks in characters
            top_k: Number of documents to retrieve

        Returns:
            Number of documents processed
        """
        if not experiment_name:
            raise ValueError("Experiment name must be provided")

        if not pdf_files:
            raise ValueError("No PDF files provided for processing")

        try:
            # Load documents
            documents = self._load_pdf_documents(pdf_files)

            # Setup embeddings
            embeddings = self._create_embeddings(embedding_model)

            # Start from an empty index, so no dummy entry takes a top-k slot
            vectorstore = FAISS(
                embedding_function=embeddings,
                index=faiss.IndexFlatL2(len(embeddings.embed_query("dimension probe"))),
                docstore=InMemoryDocstore(),
                index_to_docstore_id={},
            )

            # Setup storage and retriever
            self.store = InMemoryStore()
            self.retriever = self._build_retriever(vectorstore, self.store, child_chunk_size, top_k)

            # Add documents
            self.retriever.add_documents(documents)

            return len(documents)

        except Exception as e:
            logging.error(f"Error processing PDFs: {str(e)}")
            raise

    def _build_retriever(
        self,
        vectorstore: FAISS,
        docstore: InMemoryStore,
        child_chunk_size: int,
        top_k: int,
    ) -> ParentDocumentRetriever:
        """Create the parent/child retriever over a vectorstore and parent docstore."""
        parent_chunk_size = child_chunk_size * PARENT_CHUNK_MULTIPLIER

        return ParentDocumentRetriever(
            vectorstore=vectorstore,
            docstore=docstore,
            parent_splitter=RecursiveCharacterTextSplitter(
                chunk_size=parent_chunk_size,
                chunk_overlap=int(parent_chunk_size * CHUNK_OVERLAP_RATIO),
                length_function=len,
                separators=self._separators,
            ),
            child_splitter=RecursiveCharacterTextSplitter(
                chunk_size=child_chunk_size,
                chunk_overlap=int(child_chunk_size * CHUNK_OVERLAP_RATIO),
                length_function=len,
                separators=self._separators,
            ),
            search_kwargs={"k": top_k},
        )

    def _load_pdf_documents(self, pdf_files: list) -> list:
        """Load documents from PDF files."""
        documents = []
        with tempfile.TemporaryDirectory() as temp_dir:
            for index, pdf_file in enumerate(pdf_files):
                # The browser sends the file name: keep only its last part, so a name
                # like "../../x.pdf" cannot write outside temp_dir.
                temp_path = os.path.join(temp_dir, f"{index}_{os.path.basename(pdf_file.name)}")
                with open(temp_path, "wb") as f:
                    f.write(pdf_file.getbuffer())
                loader = PyPDFLoader(temp_path)
                documents.extend(loader.load())
        return documents

    def _create_embeddings(self, embedding_model: str):
        """Create embedding model instance."""
        model_config = EmbeddingModels.get_model_config(embedding_model)

        if model_config.get("type") == EmbeddingModelType.OLLAMA.value:
            return OllamaEmbeddings(
                model=model_config["name"],
                base_url=OLLAMA_BASE_URL,
            )
        # sentence-transformers picks the device itself (CUDA, Apple MPS or CPU).
        # No multi_process: it started 4 worker processes per call, which made
        # small uploads take tens of seconds.
        return HuggingFaceEmbeddings(
            model_name=model_config["name"],
            encode_kwargs={"normalize_embeddings": True},
        )

    def get_retrieval_chain(self, ollama_model: str, stream_handler=None):
        """
        Create retrieval QA chain.

        Returns:
            Configured RetrievalQA chain
        """
        llm = Ollama(
            model=ollama_model,
            temperature=DEFAULT_TEMPERATURE,
            base_url=OLLAMA_BASE_URL,
            callbacks=[stream_handler] if stream_handler else None,
        )

        template = """
        Context: {context}
        Question: {question}

        Provide a detailed, well-structured answer based only on the above context.
        """

        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"],
        )

        return RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt},
        )

    def save_experiment(
        self,
        experiment_name: str,
        config: dict,
    ) -> bool:
        """Save current experiment state."""
        return self.experiment_store.save(
            experiment_name,
            self.retriever,
            config,
        )

    def load_experiment(self, experiment_name: str) -> tuple[bool, dict]:
        """Load a saved experiment."""
        try:
            vectorstore, docstore, config = self.experiment_store.load(
                experiment_name,
                self._create_embeddings,
            )
            if vectorstore is None:
                return False, {}
            self.retriever = self._build_retriever(
                vectorstore,
                docstore,
                config.get("chunk_size", DEFAULT_CHUNK_SIZE),
                config.get("top_k", DEFAULT_TOP_K),
            )
            return True, config
        except Exception as e:
            logging.error(f"Error loading experiment {experiment_name}: {str(e)}")
            return False, {}

    def list_experiments(self) -> list[tuple[str, dict]]:
        """List all saved experiments."""
        return self.experiment_store.list_all()

    def delete_experiment(self, experiment_name: str) -> bool:
        """Delete a saved experiment."""
        return self.experiment_store.delete(experiment_name)


def get_rag_configurations(rag_system: RAGEngine) -> Optional[str]:
    """
    Get formatted display of all RAG configurations.

    Returns:
        Formatted configuration string or None
    """
    try:
        experiments = rag_system.list_experiments()

        if not experiments:
            return None

        all_configs = []
        for experiment_name, config in experiments:
            formatted_config = {
                "llm_model": config.get("llm_model", "N/A"),
                "embedding_model": config.get("embedding_model", "N/A"),
                "chunk_size": config.get("chunk_size", 0),
                "top_k": config.get("top_k", 0),
                "total_documents": config.get("total_documents", 0),
            }

            display_text = [
                "",
                "--------------------------------------",
                f"📋 Experiment: {experiment_name}",
                "-------------------",
                "🤖 Model Configuration",
                "-------------------",
                f"• LLM Model: {formatted_config['llm_model']}",
                f"• Embedding Model: {formatted_config['embedding_model']}",
                "",
                "📊 Processing Settings",
                "-------------------",
                f"• Child Chunk Size: {formatted_config['chunk_size']} characters",
                f"• Parent Chunk Size: {formatted_config['chunk_size'] * PARENT_CHUNK_MULTIPLIER} characters",
                f"• Top K Documents: {formatted_config['top_k']}",
                "",
                "📚 Document Information",
                "-------------------",
                f"• Total Uploaded Files: {formatted_config['total_documents']}",
                "",
            ]
            all_configs.append("\n".join(display_text))

        return "\n".join(all_configs)

    except Exception as e:
        logging.error(f"Error in get_rag_configurations: {str(e)}")
        return None