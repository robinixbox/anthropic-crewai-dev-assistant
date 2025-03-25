import os
import yaml
from typing import Dict, Any, Optional
import logging
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class Config:
    """
    Configuration class for the application.
    Handles loading configuration from YAML files and environment variables.
    """

    def __init__(self, config_dir: str = 'config'):
        """
        Initialize the Config class.
        
        Args:
            config_dir (str): Directory containing configuration files
        """
        # Load environment variables
        load_dotenv()
        
        self.config_dir = config_dir
        self.base_dir = Path(__file__).parent.parent
        self.agents_config = self._load_yaml_config('agents.yaml')
        self.tasks_config = self._load_yaml_config('tasks.yaml')
        
        # LLM configuration
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.model = os.getenv('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20240620')
        self.temperature = float(os.getenv('TEMPERATURE', '0.2'))
        
        # GitHub configuration
        self.github_token = os.getenv('GITHUB_ACCESS_TOKEN')
        self.github_owner = os.getenv('GITHUB_OWNER')
        self.github_repo = os.getenv('GITHUB_REPO')
        
        # Validate required configuration
        self._validate_config()
        
    def _load_yaml_config(self, filename: str) -> Dict[str, Any]:
        """
        Load YAML configuration from file.
        
        Args:
            filename (str): Name of the YAML file to load
            
        Returns:
            Dict[str, Any]: Configuration as a dictionary
        """
        config_path = self.base_dir / self.config_dir / filename
        
        # Vérifier si le fichier existe avant de l'ouvrir
        if not config_path.exists():
            logger.error(f"Configuration file not found: {config_path}")
            return {}
            
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            return config if config else {}
        except Exception as e:
            logger.error(f"Error loading configuration from {config_path}: {e}")
            return {}
            
    def _validate_config(self) -> None:
        """
        Validate that all required configuration variables are set.
        Raises a ValueError if any required configuration is missing.
        """
        if not self.anthropic_api_key:
            logger.warning("ANTHROPIC_API_KEY not set in environment variables. LLM functionality will not work.")
            
        if not self.github_token:
            logger.warning("GITHUB_ACCESS_TOKEN not set. GitHub integration will not work.")
            
        if not self.agents_config:
            logger.warning("Agents configuration not loaded. Check agents.yaml file.")
            
        if not self.tasks_config:
            logger.warning("Tasks configuration not loaded. Check tasks.yaml file.")
    
    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific agent.
        
        Args:
            agent_name (str): Name of the agent
            
        Returns:
            Dict[str, Any]: Agent configuration
        """
        return self.agents_config.get(agent_name, {})
    
    def get_task_config(self, task_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific task.
        
        Args:
            task_name (str): Name of the task
            
        Returns:
            Dict[str, Any]: Task configuration
        """
        return self.tasks_config.get(task_name, {})
    
    def format_agent_config(self, agent_name: str, **kwargs) -> Dict[str, Any]:
        """
        Format agent configuration with variable substitution.
        
        Args:
            agent_name (str): Name of the agent
            **kwargs: Variables to substitute in the configuration
            
        Returns:
            Dict[str, Any]: Formatted agent configuration
        """
        config = self.get_agent_config(agent_name)
        formatted_config = {}
        
        for key, value in config.items():
            if isinstance(value, str):
                formatted_config[key] = value.format(**kwargs)
            else:
                formatted_config[key] = value
                
        return formatted_config
    
    def format_task_config(self, task_name: str, **kwargs) -> Dict[str, Any]:
        """
        Format task configuration with variable substitution.
        
        Args:
            task_name (str): Name of the task
            **kwargs: Variables to substitute in the configuration
            
        Returns:
            Dict[str, Any]: Formatted task configuration
        """
        config = self.get_task_config(task_name)
        formatted_config = {}
        
        for key, value in config.items():
            if isinstance(value, str):
                formatted_config[key] = value.format(**kwargs)
            else:
                formatted_config[key] = value
                
        return formatted_config