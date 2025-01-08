import os
import pickle
from typing import Optional
from langchain.retrievers import ParentDocumentRetriever

import logging

class ExperimentManager:
    def __init__(self, base_dir: str = "experiments"):
        self.base_dir = base_dir
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
    
    def _get_experiment_paths(self, experiment_name: str) -> tuple[str, str]:
        """Get paths for retriever and config files."""
        safe_name = "".join(c for c in experiment_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        retriever_path = os.path.join(self.base_dir, f"{safe_name}_retriever.pkl")
        config_path = os.path.join(self.base_dir, f"{safe_name}_config.pkl")
        return retriever_path, config_path
    
    def save_experiment(self, experiment_name: str, retriever: ParentDocumentRetriever, config: dict) -> bool:
        """Save experiment with its configuration."""
        try:
            retriever_path, config_path = self._get_experiment_paths(experiment_name)
            
            # Save retriever
            with open(retriever_path, 'wb') as f:
                pickle.dump(retriever, f)
            
            # Save configuration
            with open(config_path, 'wb') as f:
                pickle.dump(config, f)
                
            return True
        except Exception as e:
            logging.error(f"Error saving experiment {experiment_name}: {str(e)}")
            return False
    
    def load_experiment(self, experiment_name: str) -> tuple[Optional[ParentDocumentRetriever], Optional[dict]]:
        """Load a saved experiment and its configuration."""
        try:
            retriever_path, config_path = self._get_experiment_paths(experiment_name)
            
            # Load retriever
            with open(retriever_path, 'rb') as f:
                retriever = pickle.load(f)
            
            # Load configuration
            with open(config_path, 'rb') as f:
                config = pickle.load(f)
            
            return retriever, config
        except Exception as e:
            logging.error(f"Error loading experiment {experiment_name}: {str(e)}")
            return None, None
    
    def list_experiments(self) -> list[tuple[str, dict]]:
        """List all experiments with their configurations."""
        experiments = []
        try:
            for filename in os.listdir(self.base_dir):
                if filename.endswith('_config.pkl'):  # Look for config files
                    experiment_name = filename[:-11]  # Remove _config.pkl
                    config_path = os.path.join(self.base_dir, filename)
                    
                    try:
                        with open(config_path, 'rb') as f:
                            config = pickle.load(f)
                            experiments.append((experiment_name, config))
                    except Exception as e:
                        logging.error(f"Error loading config for {experiment_name}: {str(e)}")
                        continue
            
            return experiments
        except Exception as e:
            logging.error(f"Error listing experiments: {str(e)}")
            return []








