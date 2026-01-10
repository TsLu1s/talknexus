import os
import pickle
import logging
from typing import Optional

from langchain.retrievers import ParentDocumentRetriever

from config import EXPERIMENTS_DIR

class ExperimentStore:
    """Manages RAG experiment persistence."""

    def __init__(self, base_dir: str = None):
        """
        Initialize ExperimentStore.

        Args:
            base_dir: Directory for storing experiments
        """
        self.base_dir = base_dir or str(EXPERIMENTS_DIR)
        os.makedirs(self.base_dir, exist_ok=True)

    def _get_paths(self, experiment_name: str) -> tuple[str, str]:
        """
        Get file paths for an experiment.

        Args:
            experiment_name: Name of the experiment

        Returns:
            Tuple of (retriever_path, config_path)
        """
        safe_name = "".join(
            c for c in experiment_name
            if c.isalnum() or c in (" ", "-", "_")
        ).rstrip()

        retriever_path = os.path.join(self.base_dir, f"{safe_name}_retriever.pkl")
        config_path = os.path.join(self.base_dir, f"{safe_name}_config.pkl")

        return retriever_path, config_path

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
            retriever_path, config_path = self._get_paths(experiment_name)

            # Save retriever
            with open(retriever_path, "wb") as f:
                pickle.dump(retriever, f)

            # Save configuration
            with open(config_path, "wb") as f:
                pickle.dump(config, f)

            return True

        except Exception as e:
            logging.error(f"Error saving experiment {experiment_name}: {str(e)}")
            return False

    def load(
        self,
        experiment_name: str,
    ) -> tuple[Optional[ParentDocumentRetriever], Optional[dict]]:
        """
        Load a saved experiment.

        Args:
            experiment_name: Name of the experiment to load

        Returns:
            Tuple of (retriever, config) or (None, None) on error
        """
        try:
            retriever_path, config_path = self._get_paths(experiment_name)

            # Load retriever
            with open(retriever_path, "rb") as f:
                retriever = pickle.load(f)

            # Load configuration
            with open(config_path, "rb") as f:
                config = pickle.load(f)

            return retriever, config

        except Exception as e:
            logging.error(f"Error loading experiment {experiment_name}: {str(e)}")
            return None, None

    def delete(self, experiment_name: str) -> bool:
        """
        Delete a saved experiment.

        Args:
            experiment_name: Name of the experiment to delete

        Returns:
            True if deletion was successful
        """
        try:
            retriever_path, config_path = self._get_paths(experiment_name)

            if os.path.exists(retriever_path):
                os.remove(retriever_path)
            if os.path.exists(config_path):
                os.remove(config_path)

            return True

        except Exception as e:
            logging.error(f"Error deleting experiment {experiment_name}: {str(e)}")
            return False

    def list_all(self) -> list[tuple[str, dict]]:
        """
        List all experiments with their configurations.

        Returns:
            List of tuples (experiment_name, config)
        """
        experiments = []

        try:
            if not os.path.exists(self.base_dir):
                return experiments

            for filename in os.listdir(self.base_dir):
                if not filename.endswith("_config.pkl"):
                    continue

                experiment_name = filename[:-11]  # Remove _config.pkl
                config_path = os.path.join(self.base_dir, filename)

                try:
                    with open(config_path, "rb") as f:
                        config = pickle.load(f)
                        experiments.append((experiment_name, config))
                except (pickle.UnpicklingError, KeyError) as e:
                    logging.error(f"Error loading config for {experiment_name}: {str(e)}")
                    continue

            return experiments

        except Exception as e:
            logging.error(f"Error listing experiments: {str(e)}")
            return []

    def exists(self, experiment_name: str) -> bool:
        """Check if an experiment exists."""
        retriever_path, config_path = self._get_paths(experiment_name)
        return os.path.exists(retriever_path) and os.path.exists(config_path)