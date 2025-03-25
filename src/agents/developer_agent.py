import logging
from typing import List, Any, Optional, Dict
from crewai.agents.cache import SqliteCache
from crewai_tools import WebSearchTool, FileReadTool

from .base_agent import BaseAgent
from ..error_handler import handle_exceptions

logger = logging.getLogger(__name__)

class DeveloperAgent(BaseAgent):
    """
    Agent specialized in implementing high-quality code based on specifications and architecture.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-5-sonnet-20240620",
        temperature: float = 0.2,
        tools: Optional[List[Any]] = None,
        cache: Optional[SqliteCache] = None,
        verbose: bool = True,
        language: str = "Java"
    ):
        """
        Initialize the developer agent.
        
        Args:
            api_key (Optional[str]): The Anthropic API key
            model (str): The Claude model to use
            temperature (float): The temperature for the language model
            tools (Optional[List[Any]]): The tools available to the agent
            cache (Optional[SqliteCache]): The cache for LLM requests
            verbose (bool): Whether to enable verbose logging
            language (str): The programming language to develop in
        """
        # Define specialized role, goal, and backstory for the developer
        role = f"Développeur Sénior spécialisé en {language}"
        goal = "Transformer les spécifications en code de haute qualité suivant les meilleures pratiques"
        backstory = (
            f"Tu es un développeur méticuleux qui produit un code {language} propre, bien documenté et testé. "
            f"Tu maîtrises les design patterns et les principes SOLID. Ton code est toujours "
            f"accompagné de tests unitaires complets et d'une documentation claire. "
            f"Tu excelles dans l'implémentation de fonctionnalités complexes de manière "
            f"élégante et performante. Tu es également très attentif à la qualité du code, "
            f"à sa lisibilité et à sa maintenabilité à long terme. Tu as une connaissance approfondie "
            f"de l'écosystème {language}, des frameworks populaires et des meilleures pratiques actuelles."
        )
        
        # Initialize the base agent
        super().__init__(
            role=role,
            goal=goal,
            backstory=backstory,
            verbose=verbose,
            allow_delegation=True,
            temperature=temperature,
            api_key=api_key,
            model=model,
            tools=tools,
            cache=cache
        )
        
        self.language = language
    
    @handle_exceptions
    def _default_tools(self) -> List[Any]:
        """
        Get the default tools for the developer agent.
        
        Returns:
            List[Any]: Default tools for the developer agent
        """
        # Tools specialized for code development
        return [
            WebSearchTool(),
            FileReadTool()
            # Add more specialized tools here as needed
        ]
    
    def update_language(self, language: str) -> None:
        """
        Update the programming language for the developer.
        This updates the agent's role and backstory.
        
        Args:
            language (str): The programming language
        """
        self.language = language
        
        # Update the agent's configuration with the new language
        self.update_config(
            role=f"Développeur Sénior spécialisé en {language}",
            backstory=(
                f"Tu es un développeur méticuleux qui produit un code {language} propre, bien documenté et testé. "
                f"Tu maîtrises les design patterns et les principes SOLID. Ton code est toujours "
                f"accompagné de tests unitaires complets et d'une documentation claire. "
                f"Tu excelles dans l'implémentation de fonctionnalités complexes de manière "
                f"élégante et performante. Tu es également très attentif à la qualité du code, "
                f"à sa lisibilité et à sa maintenabilité à long terme. Tu as une connaissance approfondie "
                f"de l'écosystème {language}, des frameworks populaires et des meilleures pratiques actuelles."
            )
        )
    
    @handle_exceptions
    def generate_code(self, specifications: str, architecture: str) -> str:
        """
        Generate code based on specifications and architecture.
        
        Args:
            specifications (str): The specifications for the code
            architecture (str): The architecture design
            
        Returns:
            str: The generated code
        """
        # In a real implementation, this would be handled by the agent's task
        # For now, we'll just return a placeholder
        return f"Generated {self.language} code would be here"
    
    @handle_exceptions
    def generate_unit_tests(self, code: str) -> str:
        """
        Generate unit tests for the given code.
        
        Args:
            code (str): The code to test
            
        Returns:
            str: The generated unit tests
        """
        # In a real implementation, this would be handled by the agent's task
        # For now, we'll just return a placeholder
        return f"Generated {self.language} unit tests would be here"
    
    @handle_exceptions
    def fix_code_issues(self, code: str, issues: str) -> str:
        """
        Fix issues in the code.
        
        Args:
            code (str): The code to fix
            issues (str): Description of the issues to fix
            
        Returns:
            str: The fixed code
        """
        # In a real implementation, this would be handled by the agent's task
        # For now, we'll just return a placeholder
        return f"Fixed {self.language} code would be here"