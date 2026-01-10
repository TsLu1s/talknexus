import json
import logging
import tempfile
import os
from typing import Optional

import torch
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings, OllamaEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import FAISS
from langchain.retrievers import ParentDocumentRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.storage import InMemoryStore

from config import (
    OLLAMA_BASE_URL,
    DEFAULT_TEMPERATURE,
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
        llm_model: str = None,
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

            # Initialize vectorstore
            vectorstore = FAISS.from_texts(
                texts=["placeholder"],
                embedding=embeddings,
            )

            # Calculate chunk sizes
            parent_chunk_size = child_chunk_size * PARENT_CHUNK_MULTIPLIER
            child_overlap = int(child_chunk_size * CHUNK_OVERLAP_RATIO)
            parent_overlap = int(parent_chunk_size * CHUNK_OVERLAP_RATIO)

            # Setup splitters
            parent_splitter = RecursiveCharacterTextSplitter(
                chunk_size=parent_chunk_size,
                chunk_overlap=parent_overlap,
                length_function=len,
                separators=self._separators,
            )

            child_splitter = RecursiveCharacterTextSplitter(
                chunk_size=child_chunk_size,
                chunk_overlap=child_overlap,
                length_function=len,
                separators=self._separators,
            )

            # Setup storage
            self.store = InMemoryStore()

            # Initialize retriever
            self.retriever = ParentDocumentRetriever(
                vectorstore=vectorstore,
                docstore=self.store,
                parent_splitter=parent_splitter,
                child_splitter=child_splitter,
                search_kwargs={"k": top_k},
            )

            # Add documents
            self.retriever.add_documents(documents)

            return len(documents)

        except Exception as e:
            logging.error(f"Error processing PDFs: {str(e)}")
            raise

    def _load_pdf_documents(self, pdf_files: list) -> list:
        """Load documents from PDF files."""
        documents = []
        with tempfile.TemporaryDirectory() as temp_dir:
            for pdf_file in pdf_files:
                temp_path = os.path.join(temp_dir, pdf_file.name)
                with open(temp_path, "wb") as f:
                    f.write(pdf_file.getbuffer())
                loader = PyPDFLoader(temp_path)
                documents.extend(loader.load())
        return documents

    def _create_embeddings(self, embedding_model: str):
        """Create embedding model instance."""
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model_config = EmbeddingModels.get_model_config(embedding_model)

        if model_config.get("type") == EmbeddingModelType.OLLAMA.value:
            return OllamaEmbeddings(
                model=model_config["name"],
                base_url=OLLAMA_BASE_URL,
            )
        else:
            return HuggingFaceEmbeddings(
                model_name=model_config["name"],
                model_kwargs={"device": device},
                encode_kwargs={"normalize_embeddings": True},
                multi_process=True,
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
            retriever, config = self.experiment_store.load(experiment_name)
            if retriever and config:
                self.retriever = retriever
                return True, config
            return False, {}
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