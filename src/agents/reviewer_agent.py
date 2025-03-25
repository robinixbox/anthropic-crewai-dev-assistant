import logging
from typing import List, Any, Optional, Dict
from crewai.agents.cache import SqliteCache
from crewai_tools import WebSearchTool, FileReadTool

from .base_agent import BaseAgent
from ..error_handler import handle_exceptions

logger = logging.getLogger(__name__)

class ReviewerAgent(BaseAgent):
    """
    Agent specialized in reviewing code, identifying issues, and suggesting improvements.
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
        Initialize the reviewer agent.
        
        Args:
            api_key (Optional[str]): The Anthropic API key
            model (str): The Claude model to use
            temperature (float): The temperature for the language model
            tools (Optional[List[Any]]): The tools available to the agent
            cache (Optional[SqliteCache]): The cache for LLM requests
            verbose (bool): Whether to enable verbose logging
            language (str): The programming language for code review
        """
        # Define specialized role, goal, and backstory for the reviewer
        role = f"Expert en revue de code {language}"
        goal = "Identifier les problèmes potentiels, les failles de sécurité et les optimisations possibles"
        backstory = (
            f"Tu as développé un œil critique pour détecter les bugs subtils, les problèmes de performance "
            f"et les failles de sécurité dans le code {language}. Tu proposes toujours des améliorations constructives. "
            f"Tu as une expérience approfondie dans la détection de problèmes qui échappent "
            f"souvent aux autres développeurs. Tu comprends parfaitement les bonnes pratiques "
            f"et les pièges courants spécifiques à {language} et ses frameworks. "
            f"Ton approche est toujours constructive, en expliquant non seulement ce qui pourrait "
            f"être amélioré, mais aussi pourquoi et comment. Tu es particulièrement attentif aux aspects "
            f"tels que la sécurité, la performance, la lisibilité et la maintenabilité du code."
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
        Get the default tools for the reviewer agent.
        
        Returns:
            List[Any]: Default tools for the reviewer agent
        """
        # Tools specialized for code review
        return [
            WebSearchTool(),
            FileReadTool()
            # Add more specialized tools here as needed
        ]
    
    def update_language(self, language: str) -> None:
        """
        Update the programming language for the reviewer.
        This updates the agent's role and backstory.
        
        Args:
            language (str): The programming language
        """
        self.language = language
        
        # Update the agent's configuration with the new language
        self.update_config(
            role=f"Expert en revue de code {language}",
            backstory=(
                f"Tu as développé un œil critique pour détecter les bugs subtils, les problèmes de performance "
                f"et les failles de sécurité dans le code {language}. Tu proposes toujours des améliorations constructives. "
                f"Tu as une expérience approfondie dans la détection de problèmes qui échappent "
                f"souvent aux autres développeurs. Tu comprends parfaitement les bonnes pratiques "
                f"et les pièges courants spécifiques à {language} et ses frameworks. "
                f"Ton approche est toujours constructive, en expliquant non seulement ce qui pourrait "
                f"être amélioré, mais aussi pourquoi et comment. Tu es particulièrement attentif aux aspects "
                f"tels que la sécurité, la performance, la lisibilité et la maintenabilité du code."
            )
        )
    
    @handle_exceptions
    def review_code(self, code: str, specifications: str) -> Dict[str, Any]:
        """
        Review code based on specifications.
        
        Args:
            code (str): The code to review
            specifications (str): The specifications the code should meet
            
        Returns:
            Dict[str, Any]: A structured review with issues and suggestions
        """
        # In a real implementation, this would be handled by the agent's task
        # For now, we'll just return a placeholder
        return {
            "issues": [
                {"severity": "high", "description": "Example issue 1", "line": 10},
                {"severity": "medium", "description": "Example issue 2", "line": 25},
            ],
            "suggestions": [
                {"description": "Example suggestion 1", "code": "Suggested code 1"},
                {"description": "Example suggestion 2", "code": "Suggested code 2"},
            ],
            "overall_assessment": f"This is a placeholder review for {self.language} code."
        }
    
    @handle_exceptions
    def analyze_security(self, code: str) -> List[Dict[str, Any]]:
        """
        Analyze code for security vulnerabilities.
        
        Args:
            code (str): The code to analyze
            
        Returns:
            List[Dict[str, Any]]: A list of identified security issues
        """
        # In a real implementation, this would be handled by the agent's task
        # For now, we'll just return a placeholder
        return [
            {
                "severity": "critical",
                "vulnerability_type": "Example vulnerability type 1",
                "description": "Example vulnerability description 1",
                "location": "line 15",
                "mitigation": "Example mitigation 1"
            },
            {
                "severity": "high",
                "vulnerability_type": "Example vulnerability type 2",
                "description": "Example vulnerability description 2",
                "location": "line 30",
                "mitigation": "Example mitigation 2"
            }
        ]
    
    @handle_exceptions
    def analyze_performance(self, code: str) -> List[Dict[str, Any]]:
        """
        Analyze code for performance issues.
        
        Args:
            code (str): The code to analyze
            
        Returns:
            List[Dict[str, Any]]: A list of identified performance issues
        """
        # In a real implementation, this would be handled by the agent's task
        # For now, we'll just return a placeholder
        return [
            {
                "severity": "medium",
                "issue_type": "Example performance issue type 1",
                "description": "Example performance issue description 1",
                "location": "line 20",
                "suggestion": "Example suggestion 1"
            },
            {
                "severity": "low",
                "issue_type": "Example performance issue type 2",
                "description": "Example performance issue description 2",
                "location": "line 40",
                "suggestion": "Example suggestion 2"
            }
        ]