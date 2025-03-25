import logging
from typing import List, Any, Optional, Dict
from crewai.agents.cache import SqliteCache
from crewai_tools import WebSearchTool, FileReadTool

from .base_agent import BaseAgent
from ..error_handler import handle_exceptions

logger = logging.getLogger(__name__)

class AnalystAgent(BaseAgent):
    """
    Agent specialized in analyzing requirements and converting them into clear specifications.
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
        Initialize the analyst agent.
        
        Args:
            api_key (Optional[str]): The Anthropic API key
            model (str): The Claude model to use
            temperature (float): The temperature for the language model
            tools (Optional[List[Any]]): The tools available to the agent
            cache (Optional[SqliteCache]): The cache for LLM requests
            verbose (bool): Whether to enable verbose logging
            language (str): The programming language for the analysis
        """
        # Define specialized role, goal, and backstory for the analyst
        role = f"Analyste des besoins techniques et fonctionnels spécialisé en {language}"
        goal = "Comprendre et formaliser les besoins du projet en spécifications exploitables"
        backstory = (
            f"Tu excelles dans la traduction de demandes vagues en spécifications claires et structurées "
            f"pour des projets {language}. Tu sais poser les bonnes questions pour clarifier les ambiguïtés "
            f"et anticiper les besoins non exprimés. Ton expérience te permet de décomposer des problèmes complexes "
            f"en composants gérables et de prioriser efficacement les fonctionnalités. "
            f"Tu as un talent particulier pour trouver un équilibre entre les besoins des utilisateurs, "
            f"les contraintes techniques et les objectifs commerciaux. "
            f"Tu comprends parfaitement les bonnes pratiques et patterns de conception en {language}."
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
        Get the default tools for the analyst agent.
        
        Returns:
            List[Any]: Default tools for the analyst agent
        """
        # Tools specialized for requirements analysis
        return [
            WebSearchTool(),
            FileReadTool()
            # Add more specialized tools here as needed
        ]
    
    def update_language(self, language: str) -> None:
        """
        Update the programming language for the analyst.
        This updates the agent's role and backstory.
        
        Args:
            language (str): The programming language
        """
        self.language = language
        
        # Update the agent's configuration with the new language
        self.update_config(
            role=f"Analyste des besoins techniques et fonctionnels spécialisé en {language}",
            backstory=(
                f"Tu excelles dans la traduction de demandes vagues en spécifications claires et structurées "
                f"pour des projets {language}. Tu sais poser les bonnes questions pour clarifier les ambiguïtés "
                f"et anticiper les besoins non exprimés. Ton expérience te permet de décomposer des problèmes complexes "
                f"en composants gérables et de prioriser efficacement les fonctionnalités. "
                f"Tu as un talent particulier pour trouver un équilibre entre les besoins des utilisateurs, "
                f"les contraintes techniques et les objectifs commerciaux. "
                f"Tu comprends parfaitement les bonnes pratiques et patterns de conception en {language}."
            )
        )