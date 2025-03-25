import logging
from typing import List, Dict, Any, Optional
from crewai_tools import BaseTool
from github import Github, GithubException, Repository, Issue, PullRequest
import os

from ..error_handler import handle_exceptions, ErrorHandler, ErrorCategory, ErrorSeverity

logger = logging.getLogger(__name__)

class GitHubTool(BaseTool):
    """
    Tool for interacting with GitHub repositories.
    Provides functionality for repository operations, issues, and pull requests.
    """
    
    name: str = "GitHub Tool"
    description: str = (
        "A tool for interacting with GitHub repositories. "
        "Can be used to get repository information, create issues, create pull requests, "
        "and perform code reviews on pull requests."
    )
    
    def __init__(
        self,
        token: Optional[str] = None,
        owner: Optional[str] = None,
        repo: Optional[str] = None
    ):
        """
        Initialize the GitHub tool.
        
        Args:
            token (Optional[str]): GitHub access token. If None, uses GITHUB_ACCESS_TOKEN env var.
            owner (Optional[str]): GitHub repository owner/organization.
            repo (Optional[str]): GitHub repository name.
        """
        super().__init__()
        self.token = token or os.getenv("GITHUB_ACCESS_TOKEN")
        self.owner = owner or os.getenv("GITHUB_OWNER")
        self.repo = repo or os.getenv("GITHUB_REPO")
        
        if not self.token:
            logger.warning("GitHub token not set. GitHub functionality will be limited.")
        
        # Initialize GitHub client
        self.github = Github(self.token) if self.token else None
        self.repository = None
        
        if self.github and self.owner and self.repo:
            try:
                self.repository = self.github.get_repo(f"{self.owner}/{self.repo}")
                logger.info(f"Successfully connected to GitHub repository: {self.owner}/{self.repo}")
            except GithubException as e:
                error = ErrorHandler.create_error(
                    message=f"Failed to connect to GitHub repository: {self.owner}/{self.repo}",
                    category=ErrorCategory.GITHUB,
                    severity=ErrorSeverity.ERROR,
                    details={"owner": self.owner, "repo": self.repo},
                    exception=e
                )
                logger.error(f"GitHub repository connection error: {error}")
    
    @handle_exceptions
    def _run(self, action: str, **kwargs) -> str:
        """
        Run the GitHub tool with the specified action.
        
        Args:
            action (str): The action to perform. Can be one of:
                - "get_repo_info": Get information about the repository
                - "create_issue": Create a new issue
                - "get_issues": Get issues from the repository
                - "create_pull_request": Create a new pull request
                - "review_pull_request": Review a pull request
                - "get_pull_requests": Get pull requests from the repository
                - "get_file_content": Get content of a file from the repository
                - "create_or_update_file": Create or update a file in the repository
            **kwargs: Additional arguments specific to each action
            
        Returns:
            str: Result of the action
        """
        if not self.github:
            return "GitHub client not initialized. Please provide a valid GitHub token."
        
        if action == "get_repo_info":
            return self._get_repo_info()
        elif action == "create_issue":
            return self._create_issue(**kwargs)
        elif action == "get_issues":
            return self._get_issues(**kwargs)
        elif action == "create_pull_request":
            return self._create_pull_request(**kwargs)
        elif action == "review_pull_request":
            return self._review_pull_request(**kwargs)
        elif action == "get_pull_requests":
            return self._get_pull_requests(**kwargs)
        elif action == "get_file_content":
            return self._get_file_content(**kwargs)
        elif action == "create_or_update_file":
            return self._create_or_update_file(**kwargs)
        else:
            return f"Unknown action: {action}"
    
    @handle_exceptions
    def _get_repo_info(self) -> str:
        """
        Get information about the repository.
        
        Returns:
            str: Repository information
        """
        if not self.repository:
            return "Repository not set. Please provide owner and repo."
        
        try:
            repo = self.repository
            return f"""
            Repository: {repo.full_name}
            Description: {repo.description}
            URL: {repo.html_url}
            Stars: {repo.stargazers_count}
            Forks: {repo.forks_count}
            Open Issues: {repo.open_issues_count}
            Default Branch: {repo.default_branch}
            """
        except GithubException as e:
            error = ErrorHandler.create_error(
                message=f"Failed to get repository information for {self.owner}/{self.repo}",
                category=ErrorCategory.GITHUB,
                severity=ErrorSeverity.ERROR,
                details={"owner": self.owner, "repo": self.repo},
                exception=e
            )
            logger.error(f"GitHub get_repo_info error: {error}")
            return f"Error getting repository information: {str(e)}"
    
    @handle_exceptions
    def _create_issue(self, title: str, body: str, labels: Optional[List[str]] = None) -> str:
        """
        Create a new issue in the repository.
        
        Args:
            title (str): Issue title
            body (str): Issue body
            labels (Optional[List[str]]): Issue labels
            
        Returns:
            str: Result of the action
        """
        if not self.repository:
            return "Repository not set. Please provide owner and repo."
        
        try:
            issue = self.repository.create_issue(
                title=title,
                body=body,
                labels=labels
            )
            return f"Successfully created issue #{issue.number}: {issue.html_url}"
        except GithubException as e:
            error = ErrorHandler.create_error(
                message=f"Failed to create issue in {self.owner}/{self.repo}",
                category=ErrorCategory.GITHUB,
                severity=ErrorSeverity.ERROR,
                details={"title": title, "owner": self.owner, "repo": self.repo},
                exception=e
            )
            logger.error(f"GitHub create_issue error: {error}")
            return f"Error creating issue: {str(e)}"
    
    @handle_exceptions
    def _get_issues(self, state: str = "open", labels: Optional[List[str]] = None, limit: int = 10) -> str:
        """
        Get issues from the repository.
        
        Args:
            state (str): Issue state ("open", "closed", "all")
            labels (Optional[List[str]]): Filter by labels
            limit (int): Maximum number of issues to return
            
        Returns:
            str: Result of the action
        """
        if not self.repository:
            return "Repository not set. Please provide owner and repo."
        
        try:
            issues = self.repository.get_issues(state=state, labels=labels)
            
            result = f"Found {issues.totalCount} {state} issues"
            if labels:
                result += f" with labels: {', '.join(labels)}"
            result += "\n\n"
            
            for i, issue in enumerate(issues[:limit]):
                result += f"#{issue.number}: {issue.title}\n"
                result += f"State: {issue.state}, Created: {issue.created_at}\n"
                result += f"URL: {issue.html_url}\n\n"
                
                if i >= limit - 1:
                    break
            
            return result
        except GithubException as e:
            error = ErrorHandler.create_error(
                message=f"Failed to get issues from {self.owner}/{self.repo}",
                category=ErrorCategory.GITHUB,
                severity=ErrorSeverity.ERROR,
                details={"state": state, "owner": self.owner, "repo": self.repo},
                exception=e
            )
            logger.error(f"GitHub get_issues error: {error}")
            return f"Error getting issues: {str(e)}"
    
    @handle_exceptions
    def _create_pull_request(
        self,
        title: str,
        body: str,
        head: str,
        base: str = "main",
        draft: bool = False
    ) -> str:
        """
        Create a new pull request in the repository.
        
        Args:
            title (str): Pull request title
            body (str): Pull request body
            head (str): Head branch
            base (str): Base branch
            draft (bool): Whether to create as draft
            
        Returns:
            str: Result of the action
        """
        if not self.repository:
            return "Repository not set. Please provide owner and repo."
        
        try:
            pr = self.repository.create_pull(
                title=title,
                body=body,
                head=head,
                base=base,
                draft=draft
            )
            return f"Successfully created pull request #{pr.number}: {pr.html_url}"
        except GithubException as e:
            error = ErrorHandler.create_error(
                message=f"Failed to create pull request in {self.owner}/{self.repo}",
                category=ErrorCategory.GITHUB,
                severity=ErrorSeverity.ERROR,
                details={"title": title, "head": head, "base": base, "owner": self.owner, "repo": self.repo},
                exception=e
            )
            logger.error(f"GitHub create_pull_request error: {error}")
            return f"Error creating pull request: {str(e)}"
    
    @handle_exceptions
    def _review_pull_request(
        self,
        pr_number: int,
        body: str,
        event: str = "COMMENT"
    ) -> str:
        """
        Review a pull request.
        
        Args:
            pr_number (int): Pull request number
            body (str): Review body
            event (str): Review event ("APPROVE", "REQUEST_CHANGES", "COMMENT")
            
        Returns:
            str: Result of the action
        """
        if not self.repository:
            return "Repository not set. Please provide owner and repo."
        
        try:
            pr = self.repository.get_pull(pr_number)
            review = pr.create_review(body=body, event=event)
            return f"Successfully submitted review for pull request #{pr_number}"
        except GithubException as e:
            error = ErrorHandler.create_error(
                message=f"Failed to review pull request #{pr_number} in {self.owner}/{self.repo}",
                category=ErrorCategory.GITHUB,
                severity=ErrorSeverity.ERROR,
                details={"pr_number": pr_number, "event": event, "owner": self.owner, "repo": self.repo},
                exception=e
            )
            logger.error(f"GitHub review_pull_request error: {error}")
            return f"Error reviewing pull request: {str(e)}"
    
    @handle_exceptions
    def _get_pull_requests(self, state: str = "open", limit: int = 10) -> str:
        """
        Get pull requests from the repository.
        
        Args:
            state (str): Pull request state ("open", "closed", "all")
            limit (int): Maximum number of pull requests to return
            
        Returns:
            str: Result of the action
        """
        if not self.repository:
            return "Repository not set. Please provide owner and repo."
        
        try:
            prs = self.repository.get_pulls(state=state)
            
            result = f"Found {prs.totalCount} {state} pull requests\n\n"
            
            for i, pr in enumerate(prs[:limit]):
                result += f"#{pr.number}: {pr.title}\n"
                result += f"State: {pr.state}, Created: {pr.created_at}\n"
                result += f"URL: {pr.html_url}\n\n"
                
                if i >= limit - 1:
                    break
            
            return result
        except GithubException as e:
            error = ErrorHandler.create_error(
                message=f"Failed to get pull requests from {self.owner}/{self.repo}",
                category=ErrorCategory.GITHUB,
                severity=ErrorSeverity.ERROR,
                details={"state": state, "owner": self.owner, "repo": self.repo},
                exception=e
            )
            logger.error(f"GitHub get_pull_requests error: {error}")
            return f"Error getting pull requests: {str(e)}"
    
    @handle_exceptions
    def _get_file_content(self, path: str, ref: Optional[str] = None) -> str:
        """
        Get content of a file from the repository.
        
        Args:
            path (str): File path
            ref (Optional[str]): Branch or commit reference
            
        Returns:
            str: File content
        """
        if not self.repository:
            return "Repository not set. Please provide owner and repo."
        
        try:
            content = self.repository.get_contents(path, ref=ref)
            return content.decoded_content.decode('utf-8')
        except GithubException as e:
            error = ErrorHandler.create_error(
                message=f"Failed to get file content: {path} in {self.owner}/{self.repo}",
                category=ErrorCategory.GITHUB,
                severity=ErrorSeverity.ERROR,
                details={"path": path, "ref": ref, "owner": self.owner, "repo": self.repo},
                exception=e
            )
            logger.error(f"GitHub get_file_content error: {error}")
            return f"Error getting file content: {str(e)}"
    
    @handle_exceptions
    def _create_or_update_file(
        self,
        path: str,
        content: str,
        message: str,
        branch: Optional[str] = None,
        update: bool = False
    ) -> str:
        """
        Create or update a file in the repository.
        
        Args:
            path (str): File path
            content (str): File content
            message (str): Commit message
            branch (Optional[str]): Branch name
            update (bool): Whether to update an existing file
            
        Returns:
            str: Result of the action
        """
        if not self.repository:
            return "Repository not set. Please provide owner and repo."
        
        try:
            if update:
                # Get the existing file to get its SHA
                file = self.repository.get_contents(path, ref=branch)
                result = self.repository.update_file(
                    path=path,
                    message=message,
                    content=content,
                    sha=file.sha,
                    branch=branch
                )
                return f"Successfully updated file {path}"
            else:
                result = self.repository.create_file(
                    path=path,
                    message=message,
                    content=content,
                    branch=branch
                )
                return f"Successfully created file {path}"
        except GithubException as e:
            action = "update" if update else "create"
            error = ErrorHandler.create_error(
                message=f"Failed to {action} file: {path} in {self.owner}/{self.repo}",
                category=ErrorCategory.GITHUB,
                severity=ErrorSeverity.ERROR,
                details={"path": path, "branch": branch, "owner": self.owner, "repo": self.repo},
                exception=e
            )
            logger.error(f"GitHub {action}_file error: {error}")
            return f"Error {action}ing file: {str(e)}"