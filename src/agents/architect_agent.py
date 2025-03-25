import logging
from typing import List, Any, Optional, Dict
from crewai.agents.cache import SqliteCache
from crewai_tools import WebSearchTool, FileReadTool

from .base_agent import BaseAgent
from ..error_handler import handle_exceptions

logger = logging.getLogger(__name__)

class ArchitectAgent(BaseAgent):
    """
    Agent specialized in designing software architecture.
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
        Initialize the architect agent.
        
        Args:
            api_key (Optional[str]): The Anthropic API key
            model (str): The Claude model to use
            temperature (float): The temperature for the language model
            tools (Optional[List[Any]]): The tools available to the agent
            cache (Optional[SqliteCache]): The cache for LLM requests
            verbose (bool): Whether to enable verbose logging
            language (str): The programming language for the architecture
        """
        # Define specialized role, goal, and backstory for the architect
        role = f"Architecte Logiciel Sénior spécialisé en {language}"
        goal = "Concevoir une architecture logicielle robuste, extensible et maintenable"
        backstory = (
            f"Tu es un architecte logiciel expérimenté avec 15 ans d'expérience en conception "
            f"de systèmes complexes en {language}. Tu excelles dans la création d'architectures qui anticipent "
            f"les besoins futurs tout en restant pragmatiques. Tu maîtrises les design patterns "
            f"et les principes de conception comme SOLID, et tu sais quand les appliquer de manière "
            f"judicieuse sans surcompliquer les choses. Tu as une expertise approfondie des frameworks et "
            f"bibliothèques standards en {language}, et tu sais quand utiliser chacun en fonction du contexte. "
            f"Ton expertise technique te permet de prévoir les défis d'intégration, "
            f"de performance et de sécurité dès la phase de conception."
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
        Get the default tools for the architect agent.
        
        Returns:
            List[Any]: Default tools for the architect agent
        """
        # Tools specialized for architecture design
        return [
            WebSearchTool(),
            FileReadTool()
            # Add more specialized tools here as needed
        ]
    
    def update_language(self, language: str) -> None:
        """
        Update the programming language for the architect.
        This updates the agent's role and backstory.
        
        Args:
            language (str): The programming language
        """
        self.language = language
        
        # Update the agent's configuration with the new language
        self.update_config(
            role=f"Architecte Logiciel Sénior spécialisé en {language}",
            backstory=(
                f"Tu es un architecte logiciel expérimenté avec 15 ans d'expérience en conception "
                f"de systèmes complexes en {language}. Tu excelles dans la création d'architectures qui anticipent "
                f"les besoins futurs tout en restant pragmatiques. Tu maîtrises les design patterns "
                f"et les principes de conception comme SOLID, et tu sais quand les appliquer de manière "
                f"judicieuse sans surcompliquer les choses. Tu as une expertise approfondie des frameworks et "
                f"bibliothèques standards en {language}, et tu sais quand utiliser chacun en fonction du contexte. "
                f"Ton expertise technique te permet de prévoir les défis d'intégration, "
                f"de performance et de sécurité dès la phase de conception."
            )
        )
        
    def create_architecture_diagram(self, specifications: str) -> str:
        """
        Create a text-based architecture diagram based on specifications.
        
        Args:
            specifications (str): The specifications for the architecture
            
        Returns:
            str: A text-based architecture diagram
        """
        # In a real implementation, this might use an actual diagram tool
        # For now, we'll just delegate to the LLM to create a text-based diagram
        
        prompt = f"""
        Based on the following specifications, create a text-based architecture diagram 
        for a {self.language} application. Use ASCII art or similar text-based visualization
        to represent components, their relationships, and data flows.
        
        Specifications:
        {specifications}
        
        The diagram should clearly show:
        1. Main components and their responsibilities
        2. Interfaces between components
        3. Data flow directions
        4. External dependencies
        5. Key design patterns used
        
        Make the diagram as clear and readable as possible using only text.
        """
        
        # We could send this as a tool request to the agent
        # For now, this is a placeholder
        return "Architecture diagram would be generated here"