import os
from typing import Dict, Any, List, Optional
from crewai import Agent, Task, Crew, Process
from crewai.agents.cache import SqliteCache
from crewai_tools import WebSearchTool, FileReadTool

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.agents import AnalystAgent, ArchitectAgent, DeveloperAgent, ReviewerAgent
from src.tools import GitHubTool, CodeAnalysisTool
from src.config import Config
from src.error_handler import handle_exceptions, ErrorHandler, ErrorCategory, ErrorSeverity

class DevTeamCrew:
    """
    A CrewAI crew for software development and code review.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        language: str = "Java",
        temperature: float = 0.2,
        config: Optional[Config] = None
    ):
        """
        Initialize the DevTeamCrew.
        
        Args:
            api_key (Optional[str]): Anthropic API key
            model (Optional[str]): Claude model to use
            language (str): Programming language for the team
            temperature (float): Temperature for the language model
            config (Optional[Config]): Configuration object
        """
        self.config = config or Config()
        self.api_key = api_key or self.config.anthropic_api_key
        self.model = model or self.config.model
        self.language = language
        self.temperature = temperature
        
        # Set up cache
        self.cache = SqliteCache(path="crew_cache.db")
        
        # Set up tools
        self.github_tool = GitHubTool(
            token=self.config.github_token,
            owner=self.config.github_owner,
            repo=self.config.github_repo
        )
        
        self.code_analysis_tool = CodeAnalysisTool(language=self.language)
        
        # Initialize agents
        self.analyst = self._create_analyst_agent()
        self.architect = self._create_architect_agent()
        self.developer = self._create_developer_agent()
        self.reviewer = self._create_reviewer_agent()
    
    def _create_analyst_agent(self) -> Agent:
        """
        Create the analyst agent for the crew.
        
        Returns:
            Agent: The analyst agent
        """
        analyst_agent = AnalystAgent(
            api_key=self.api_key,
            model=self.model,
            temperature=self.temperature,
            tools=[WebSearchTool(), FileReadTool()],
            cache=self.cache,
            language=self.language
        )
        
        return analyst_agent.get_agent()
    
    def _create_architect_agent(self) -> Agent:
        """
        Create the architect agent for the crew.
        
        Returns:
            Agent: The architect agent
        """
        architect_agent = ArchitectAgent(
            api_key=self.api_key,
            model=self.model,
            temperature=self.temperature,
            tools=[WebSearchTool(), FileReadTool()],
            cache=self.cache,
            language=self.language
        )
        
        return architect_agent.get_agent()
    
    def _create_developer_agent(self) -> Agent:
        """
        Create the developer agent for the crew.
        
        Returns:
            Agent: The developer agent
        """
        developer_agent = DeveloperAgent(
            api_key=self.api_key,
            model=self.model,
            temperature=self.temperature,
            tools=[WebSearchTool(), FileReadTool(), self.github_tool, self.code_analysis_tool],
            cache=self.cache,
            language=self.language
        )
        
        return developer_agent.get_agent()
    
    def _create_reviewer_agent(self) -> Agent:
        """
        Create the reviewer agent for the crew.
        
        Returns:
            Agent: The reviewer agent
        """
        reviewer_agent = ReviewerAgent(
            api_key=self.api_key,
            model=self.model,
            temperature=self.temperature,
            tools=[WebSearchTool(), FileReadTool(), self.github_tool, self.code_analysis_tool],
            cache=self.cache,
            language=self.language
        )
        
        return reviewer_agent.get_agent()
    
    def _create_analysis_task(self, requirements: str, context: Optional[str] = None) -> Task:
        """
        Create a task for requirements analysis.
        
        Args:
            requirements (str): Project requirements
            context (Optional[str]): Additional context for the analysis
            
        Returns:
            Task: The analysis task
        """
        return Task(
            description=f"""
            Analyze the following requirements for a {self.language} application:
            
            {requirements}
            
            Additional context:
            {context or 'No additional context provided.'}
            
            Your task is to:
            1. Identify all functional requirements
            2. Identify all non-functional requirements
            3. Identify any ambiguities or missing information
            4. Prioritize the requirements
            5. Suggest clarifying questions for any unclear aspects
            
            Provide a detailed analysis that can be used by the architect to design the system.
            """,
            expected_output="A comprehensive analysis of the requirements with all functional and non-functional requirements identified, prioritized, and any ambiguities noted.",
            agent=self.analyst
        )
    
    def _create_architecture_task(self, specifications: str, constraints: Optional[str] = None) -> Task:
        """
        Create a task for architecture design.
        
        Args:
            specifications (str): Project specifications
            constraints (Optional[str]): Technical constraints
            
        Returns:
            Task: The architecture task
        """
        return Task(
            description=f"""
            Design an architecture for a {self.language} application based on these specifications:
            
            {specifications}
            
            Technical constraints:
            {constraints or 'No specific constraints provided.'}
            
            Your task is to:
            1. Create a high-level architecture diagram (in text form)
            2. Define the main components and their responsibilities
            3. Specify the interfaces between components
            4. Choose appropriate design patterns
            5. Address any performance, security, and scalability considerations
            6. Justify your architectural decisions
            
            Make sure your architecture is robust, maintainable, and follows best practices for {self.language} applications.
            """,
            expected_output="A comprehensive architecture design document with component diagrams, interface specifications, design patterns, and justifications for architectural decisions.",
            agent=self.architect
        )
    
    def _create_implementation_task(self, specifications: str, architecture: str) -> Task:
        """
        Create a task for code implementation.
        
        Args:
            specifications (str): Project specifications
            architecture (str): Architecture design
            
        Returns:
            Task: The implementation task
        """
        return Task(
            description=f"""
            Implement {self.language} code based on these specifications:
            
            {specifications}
            
            And this architecture:
            
            {architecture}
            
            Your task is to:
            1. Write clean, maintainable code following best practices for {self.language}
            2. Include appropriate error handling
            3. Add comprehensive comments and documentation
            4. Implement unit tests
            5. Ensure the code follows the specified architecture
            
            Focus on quality, readability, and adherence to the specifications and architecture.
            """,
            expected_output=f"Complete {self.language} code implementing the specified requirements, with documentation and unit tests.",
            agent=self.developer
        )
    
    def _create_review_task(self, code: str, specifications: str) -> Task:
        """
        Create a task for code review.
        
        Args:
            code (str): Code to review
            specifications (str): Original specifications
            
        Returns:
            Task: The review task
        """
        return Task(
            description=f"""
            Review this {self.language} code:
            
            ```{self.language}
            {code}
            ```
            
            Against these specifications:
            
            {specifications}
            
            Your task is to:
            1. Check if the code correctly implements the specifications
            2. Identify any bugs or edge cases that aren't handled
            3. Evaluate code quality (readability, maintainability, etc.)
            4. Look for security vulnerabilities
            5. Identify performance issues
            6. Suggest improvements with specific code examples
            
            Provide a comprehensive review that will help improve the code.
            """,
            expected_output="A detailed code review identifying bugs, issues, and suggestions for improvement, with specific code examples.",
            agent=self.reviewer
        )
    
    @handle_exceptions
    def run_full_development_cycle(
        self,
        requirements: str,
        context: Optional[str] = None,
        constraints: Optional[str] = None,
        process: Process = Process.sequential
    ) -> Dict[str, Any]:
        """
        Run a full development cycle with the crew.
        
        Args:
            requirements (str): Project requirements
            context (Optional[str]): Additional context for the analysis
            constraints (Optional[str]): Technical constraints
            process (Process): Crew process type (sequential or hierarchical)
            
        Returns:
            Dict[str, Any]: Results from each stage of the development cycle
        """
        # Create tasks
        analysis_task = self._create_analysis_task(requirements, context)
        
        # Create crew for analysis
        analysis_crew = Crew(
            agents=[self.analyst],
            tasks=[analysis_task],
            verbose=True,
            process=Process.sequential
        )
        
        # Run analysis
        analysis_result = analysis_crew.kickoff()
        
        # Create architecture task with analysis results
        architecture_task = self._create_architecture_task(
            specifications=analysis_result,
            constraints=constraints
        )
        
        # Create crew for architecture
        architecture_crew = Crew(
            agents=[self.architect],
            tasks=[architecture_task],
            verbose=True,
            process=Process.sequential
        )
        
        # Run architecture design
        architecture_result = architecture_crew.kickoff()
        
        # Create implementation task with analysis and architecture results
        implementation_task = self._create_implementation_task(
            specifications=analysis_result,
            architecture=architecture_result
        )
        
        # Create crew for implementation
        implementation_crew = Crew(
            agents=[self.developer],
            tasks=[implementation_task],
            verbose=True,
            process=Process.sequential
        )
        
        # Run implementation
        implementation_result = implementation_crew.kickoff()
        
        # Create review task with implementation results and analysis
        review_task = self._create_review_task(
            code=implementation_result,
            specifications=analysis_result
        )
        
        # Create crew for review
        review_crew = Crew(
            agents=[self.reviewer],
            tasks=[review_task],
            verbose=True,
            process=Process.sequential
        )
        
        # Run review
        review_result = review_crew.kickoff()
        
        # Return all results
        return {
            "analysis": analysis_result,
            "architecture": architecture_result,
            "implementation": implementation_result,
            "review": review_result
        }
    
    @handle_exceptions
    def run_code_review(
        self,
        code: str,
        specifications: Optional[str] = None
    ) -> str:
        """
        Run a code review with the crew.
        
        Args:
            code (str): Code to review
            specifications (Optional[str]): Original specifications
            
        Returns:
            str: Review results
        """
        # Create review task
        review_task = self._create_review_task(
            code=code,
            specifications=specifications or "No specific specifications provided, focus on code quality, security, and performance."
        )
        
        # Create crew for review
        review_crew = Crew(
            agents=[self.reviewer],
            tasks=[review_task],
            verbose=True,
            process=Process.sequential
        )
        
        # Run review
        review_result = review_crew.kickoff()
        
        return review_result

if __name__ == "__main__":
    # Example usage
    crew = DevTeamCrew(language="Java")
    
    requirements = """
    Create a REST API for a simple task management system with the following features:
    - User registration and authentication
    - Create, read, update, and delete tasks
    - Assign tasks to users
    - Mark tasks as complete
    - Filter tasks by status, assignee, and due date
    - User roles (admin, manager, user)
    """
    
    results = crew.run_full_development_cycle(
        requirements=requirements,
        constraints="Use Spring Boot, Java 17, and PostgreSQL. The API should be secure, scalable, and follow REST best practices."
    )
    
    print("Results:", results)