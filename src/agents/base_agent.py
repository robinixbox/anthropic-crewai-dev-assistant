import logging
from typing import Dict, Any, List, Optional, Union
from crewai import Agent
from crewai.agents.cache import SqliteCache
from crewai_tools import WebSearchTool, FileReadTool
from anthropic import Anthropic

from ..error_handler import handle_exceptions, ErrorHandler, ErrorCategory, ErrorSeverity

logger = logging.getLogger(__name__)

class BaseAgent:
    """
    Base class for all agents in the system.
    Provides common functionality and configuration for CrewAI agents.
    """
    
    def __init__(
        self,
        role: str,
        goal: str,
        backstory: str,
        verbose: bool = True,
        allow_delegation: bool = True,
        temperature: float = 0.2,
        api_key: Optional[str] = None,
        model: str = "claude-3-5-sonnet-20240620",
        tools: Optional[List[Any]] = None,
        cache: Optional[SqliteCache] = None,
        max_iterations: int = 5,
        max_rpm: Optional[int] = None
    ):
        """
        Initialize the base agent with configuration.
        
        Args:
            role (str): The role of the agent
            goal (str): The goal or objective of the agent
            backstory (str): The backstory or background of the agent
            verbose (bool): Whether to enable verbose logging
            allow_delegation (bool): Whether to allow the agent to delegate tasks
            temperature (float): The temperature for the language model
            api_key (Optional[str]): The Anthropic API key
            model (str): The Claude model to use
            tools (Optional[List[Any]]): The tools available to the agent
            cache (Optional[SqliteCache]): The cache for LLM requests
            max_iterations (int): Maximum iterations for tool usage
            max_rpm (Optional[int]): Maximum requests per minute to the API
        """
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.verbose = verbose
        self.allow_delegation = allow_delegation
        self.temperature = temperature
        self.api_key = api_key
        self.model = model
        self.max_iterations = max_iterations
        self.max_rpm = max_rpm
        
        # Set up tools
        self.tools = tools or self._default_tools()
        
        # Set up cache
        self.cache = cache or SqliteCache(path="agent_cache.db")
        
        # Create the CrewAI agent instance
        self.agent = self._create_agent()
        
    @handle_exceptions
    def _default_tools(self) -> List[Any]:
        """
        Get the default tools for the agent.
        Override in subclasses to provide specialized tools.
        
        Returns:
            List[Any]: Default tools for the agent
        """
        return [WebSearchTool(), FileReadTool()]
    
    @handle_exceptions
    def _create_agent(self) -> Agent:
        """
        Create the CrewAI Agent instance.
        
        Returns:
            Agent: The CrewAI Agent instance
        """
        try:
            # Set up Anthropic client for the model
            anthropic_client = Anthropic(api_key=self.api_key) if self.api_key else None
            
            # Create the agent with the configured settings
            agent = Agent(
                role=self.role,
                goal=self.goal,
                backstory=self.backstory,
                verbose=self.verbose,
                allow_delegation=self.allow_delegation,
                temperature=self.temperature,
                tools=self.tools,
                llm_config={
                    "provider": anthropic_client,
                    "model": self.model,
                    "cache": self.cache
                },
                tools_config={
                    "max_iterations": self.max_iterations
                }
            )
            
            logger.info(f"Created agent with role: {self.role}")
            return agent
            
        except Exception as e:
            error = ErrorHandler.create_error(
                message=f"Failed to create agent with role '{self.role}'",
                category=ErrorCategory.CREWAI,
                severity=ErrorSeverity.ERROR,
                details={"role": self.role, "model": self.model},
                exception=e
            )
            logger.error(f"Agent creation error: {error}")
            raise
    
    @handle_exceptions
    def update_config(self, **kwargs) -> None:
        """
        Update the agent's configuration.
        
        Args:
            **kwargs: The configuration parameters to update
        """
        # Update instance variables
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # Recreate the agent with the updated configuration
        self.agent = self._create_agent()
    
    def get_agent(self) -> Agent:
        """
        Get the CrewAI Agent instance.
        
        Returns:
            Agent: The CrewAI Agent instance
        """
        return self.agent
    
    def __str__(self) -> str:
        """
        String representation of the agent.
        
        Returns:
            str: String representation
        """
        return f"{self.__class__.__name__}(role='{self.role}')"