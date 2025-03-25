#!/usr/bin/env python3
"""
Main entry point for the Anthropic CrewAI Dev Assistant application.
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Add the parent directory to the path to allow imports
sys.path.append(str(Path(__file__).parent.parent))

from src.config import Config
from src.ui.app import main as run_app
from src.error_handler import ErrorHandler, ErrorCategory, ErrorSeverity

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('dev_assistant.log')
    ]
)

logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Anthropic CrewAI Dev Assistant')
    
    parser.add_argument('--ui', action='store_true', help='Launch the UI')
    parser.add_argument('--github-workflow', action='store_true', help='Run as a GitHub workflow')
    parser.add_argument('--pr', type=int, help='Pull request number for GitHub workflow')
    parser.add_argument('--repo', type=str, help='Repository name for GitHub workflow')
    parser.add_argument('--owner', type=str, help='Repository owner for GitHub workflow')
    parser.add_argument('--analyze-code', action='store_true', help='Analyze code')
    parser.add_argument('--code-file', type=str, help='File containing code to analyze')
    parser.add_argument('--language', type=str, help='Programming language of the code')
    
    return parser.parse_args()

def run_github_workflow(args):
    """Run the application as a GitHub workflow"""
    logger.info("Running as GitHub workflow")
    
    try:
        from src.tools.github_tool import GitHubTool
        from src.agents import ReviewerAgent
        
        # Check required arguments
        if not args.pr:
            logger.error("Pull request number is required for GitHub workflow")
            return 1
        
        # Get configuration
        config = Config()
        
        # Initialize GitHub tool
        github_tool = GitHubTool(
            token=os.getenv("GITHUB_TOKEN"),
            owner=args.owner or os.getenv("GITHUB_REPOSITORY_OWNER"),
            repo=args.repo or os.getenv("GITHUB_REPOSITORY").split("/")[-1] if os.getenv("GITHUB_REPOSITORY") else None
        )
        
        # Get pull request details
        pr_details = github_tool._run(action="get_pull_request", pr_number=args.pr)
        
        # Get pull request files
        pr_files = github_tool._run(action="get_pull_request_files", pr_number=args.pr)
        
        # Initialize reviewer agent
        reviewer = ReviewerAgent(
            api_key=config.anthropic_api_key,
            model=config.model,
            temperature=config.temperature,
            language=args.language or "Java"
        )
        
        # Review the code in the pull request
        # In a real application, this would process each file and create a detailed review
        for file in pr_files:
            # Review each file
            # This is a placeholder implementation
            pass
        
        # Create a review comment on the pull request
        github_tool._run(
            action="create_pull_request_review",
            pr_number=args.pr,
            body="Automated code review by Anthropic CrewAI Dev Assistant",
            event="COMMENT"
        )
        
        logger.info(f"Successfully completed GitHub workflow for PR #{args.pr}")
        return 0
        
    except Exception as e:
        error = ErrorHandler.create_error(
            message="Failed to run GitHub workflow",
            category=ErrorCategory.GITHUB,
            severity=ErrorSeverity.ERROR,
            exception=e
        )
        logger.error(f"GitHub workflow error: {error}")
        return 1

def analyze_code(args):
    """Analyze code from a file"""
    logger.info("Running code analysis")
    
    try:
        from src.tools.code_analysis_tool import CodeAnalysisTool
        
        # Check required arguments
        if not args.code_file:
            logger.error("Code file is required for code analysis")
            return 1
        
        # Read code file
        try:
            with open(args.code_file, 'r') as f:
                code = f.read()
        except Exception as e:
            logger.error(f"Failed to read code file: {e}")
            return 1
        
        # Initialize code analysis tool
        code_analysis_tool = CodeAnalysisTool(language=args.language or "Java")
        
        # Analyze code
        results = code_analysis_tool._run(code=code, language=args.language or "Java")
        
        # Format and print results
        formatted_results = code_analysis_tool._format_results(results, args.language or "Java")
        print(formatted_results)
        
        logger.info("Successfully completed code analysis")
        return 0
        
    except Exception as e:
        error = ErrorHandler.create_error(
            message="Failed to analyze code",
            category=ErrorCategory.GENERAL,
            severity=ErrorSeverity.ERROR,
            exception=e
        )
        logger.error(f"Code analysis error: {error}")
        return 1

def main():
    """Main entry point"""
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Run the appropriate function based on arguments
    if args.github_workflow:
        return run_github_workflow(args)
    elif args.analyze_code:
        return analyze_code(args)
    else:
        # Default: run the UI
        run_app()
        return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)