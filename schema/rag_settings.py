import streamlit as st
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings, OllamaEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import FAISS
from langchain.retrievers import ParentDocumentRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.storage import InMemoryStore
from schema.streamhandler import EMBEDDING_MODELS
from schema.experiments import ExperimentManager
import torch
import tempfile
import os
import logging

import warnings
warnings.filterwarnings("ignore", category=Warning)

class RAG_Settings:
    EMBEDDING_MODELS = EMBEDDING_MODELS
    def __init__(self):
        self.vectorstore = None
        self.store = None
        self._separators = ["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        self.experiment_manager = ExperimentManager()
    def process_pdfs(self, pdf_files, experiment_name: str, embedding_model:str="bge-small", 
                    child_chunk_size:int=50, top_k:int=4, llm_model:str=None):
        """Process PDF files and return document count."""
        if not experiment_name:
            raise ValueError("Experiment name must be provided")
        
        if not pdf_files:
            raise ValueError("No PDF files provided for processing")

        try:
            documents = []
            with tempfile.TemporaryDirectory() as temp_dir:
                for pdf_file in pdf_files:
                    temp_path = os.path.join(temp_dir, pdf_file.name)
                    with open(temp_path, "wb") as f:
                        f.write(pdf_file.getbuffer())
                    loader = PyPDFLoader(temp_path)
                    documents.extend(loader.load())
            
            # Setup embeddings
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model_config = self.EMBEDDING_MODELS[embedding_model]
            
            if model_config["type"] == "ollama":
                embeddings = OllamaEmbeddings(
                    model=model_config["name"],
                    base_url="http://localhost:11434"
                )
            else:
                embeddings = HuggingFaceEmbeddings(
                    model_name=model_config["name"],
                    model_kwargs={'device': device},
                    encode_kwargs={'normalize_embeddings': True},
                    multi_process=True  
                )
            
            # Initialize vectorstore
            vectorstore = FAISS.from_texts(
                texts=["placeholder"],
                embedding=embeddings
            )
            
            # Calculate chunk sizes
            parent_chunk_size = child_chunk_size * 5
            child_overlap = int(child_chunk_size * 0.1)
            parent_overlap = int(parent_chunk_size * 0.1)
            
            # Setup splitters
            parent_splitter = RecursiveCharacterTextSplitter(
                chunk_size=parent_chunk_size,
                chunk_overlap=parent_overlap,
                length_function=len,
                separators=self._separators
            )
            
            child_splitter = RecursiveCharacterTextSplitter(
                chunk_size=child_chunk_size,
                chunk_overlap=child_overlap,
                length_function=len,
                separators=self._separators
            )
            
            # Setup storage
            self.store = InMemoryStore()
            
            # Initialize retriever
            self.retriever = ParentDocumentRetriever(
                vectorstore=vectorstore,
                docstore=self.store,
                parent_splitter=parent_splitter,
                child_splitter=child_splitter,
                search_kwargs={"k": top_k}
            )
            
            # Add documents
            self.retriever.add_documents(documents)
            
            return len(documents)
            
        except Exception as e:
            logging.error(f"Error processing PDFs: {str(e)}")
            raise
    
    def load_experiment(self, experiment_name: str) -> bool:
        """
        Load a saved experiment.
        
        Args:
            experiment_name: Name of the experiment to load
            
        Returns:
            bool: True if loading was successful, False otherwise
        """
        try:
            retriever, config = self.experiment_manager.load_experiment(experiment_name)
            if retriever and config:
                self.retriever = retriever
                return True, config
            return False, {}
        except Exception as e:
            logging.error(f"Error loading experiment {experiment_name}: {str(e)}")
            return False, {}
            
    def list_experiments(self) -> list[tuple[str, dict]]:
        """
        List all saved experiments with their configurations.
        
        Returns:
            list[tuple[str, dict]]: List of tuples containing experiment names and their configurations
        """
        try:
            experiments = self.experiment_manager.list_experiments()
            return experiments
        except Exception as e:
            logging.error(f"Error listing experiments: {str(e)}")
            return []
        
    def delete_experiment(self, experiment_name: str) -> bool:
        """Delete a saved experiment."""
        return self.experiment_manager.delete_experiment(experiment_name)

    def get_retrieval_chain(self, ollama_model: str, stream_handler=None):
        # Set up Ollama LLM
        llm = Ollama(
            model=ollama_model,
            temperature=0.2,
            base_url="http://localhost:11434",
            callbacks=[stream_handler] if stream_handler else None
        )
        
        template = """
        Context: {context}
        Question: {question}
        
        Provide a detailed, well-structured answer based only on the above context.
        """
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        return RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.retriever,  # Using the parent document retriever
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt}
        )


def get_rag_configurations():
    """Get formatted display of all RAG configurations."""
    try:
        experiments = st.session_state.rag_system.list_experiments()
        
        if not experiments:
            return None
            
        all_configs = []
        for experiment_name, config in experiments:
            # Ensure all configuration values exist with proper defaults
            formatted_config = {
                'llm_model': config.get('llm_model', 'N/A'),
                'embedding_model': config.get('embedding_model', 'N/A'),
                'chunk_size': config.get('chunk_size', 0),
                'top_k': config.get('top_k', 0),
                'total_documents': config.get('total_documents', 0)
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
                f"• Parent Chunk Size: {formatted_config['chunk_size'] * 5} characters",
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