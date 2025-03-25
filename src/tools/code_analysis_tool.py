import logging
import json
from typing import Dict, Any, List, Optional, Union
from crewai_tools import BaseTool
import re

from ..error_handler import handle_exceptions, ErrorHandler, ErrorCategory, ErrorSeverity

logger = logging.getLogger(__name__)

class CodeAnalysisTool(BaseTool):
    """
    Tool for analyzing code for quality, performance, and security issues.
    """
    
    name: str = "Code Analysis Tool"
    description: str = (
        "A tool for analyzing code quality, performance, and security. "
        "Can detect code smells, potential bugs, performance bottlenecks, "
        "and security vulnerabilities in different programming languages."
    )
    
    def __init__(
        self,
        language: Optional[str] = None
    ):
        """
        Initialize the Code Analysis Tool.
        
        Args:
            language (Optional[str]): Programming language to analyze
        """
        super().__init__()
        self.language = language
    
    @handle_exceptions
    def _run(
        self,
        code: str,
        language: Optional[str] = None,
        analysis_type: str = "all",
        **kwargs
    ) -> Union[str, Dict[str, Any]]:
        """
        Run code analysis.
        
        Args:
            code (str): Code to analyze
            language (Optional[str]): Programming language of the code
            analysis_type (str): Type of analysis to perform (quality, security, performance, or all)
            **kwargs: Additional arguments for specific analysis types
            
        Returns:
            Union[str, Dict[str, Any]]: Analysis results
        """
        code_language = language or self.language
        
        if not code_language:
            return "Language not specified. Please provide a language."
        
        if not code or len(code.strip()) == 0:
            return "No code provided. Please provide code to analyze."
        
        try:
            results = {}
            
            if analysis_type in ["quality", "all"]:
                results["quality"] = self._analyze_code_quality(code, code_language)
            
            if analysis_type in ["security", "all"]:
                results["security"] = self._analyze_security(code, code_language)
            
            if analysis_type in ["performance", "all"]:
                results["performance"] = self._analyze_performance(code, code_language)
            
            if "format" in kwargs and kwargs["format"] == "json":
                return json.dumps(results, indent=2)
            else:
                return self._format_results(results, code_language)
        
        except Exception as e:
            error = ErrorHandler.create_error(
                message=f"Error analyzing code",
                category=ErrorCategory.GENERAL,
                severity=ErrorSeverity.ERROR,
                details={"language": code_language, "analysis_type": analysis_type},
                exception=e
            )
            logger.error(f"Code analysis error: {error}")
            return f"Error analyzing code: {str(e)}"
    
    @handle_exceptions
    def _analyze_code_quality(self, code: str, language: str) -> Dict[str, Any]:
        """
        Analyze code quality.
        
        Args:
            code (str): Code to analyze
            language (str): Programming language of the code
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        # In a production application, this would use a real code analysis tool.
        # For now, we'll use a basic implementation that identifies some common issues.
        
        issues = []
        
        # Check for long lines
        lines = code.split("\n")
        for i, line in enumerate(lines):
            if len(line) > 100:
                issues.append({
                    "type": "style",
                    "description": "Line too long (> 100 characters)",
                    "line": i + 1,
                    "severity": "low"
                })
        
        # Check for TODO comments
        todo_pattern = r"(?i:TODO|FIXME|XXX|BUG|HACK)"
        for i, line in enumerate(lines):
            if re.search(todo_pattern, line):
                issues.append({
                    "type": "maintenance",
                    "description": f"TODO or similar comment found: {line.strip()}",
                    "line": i + 1,
                    "severity": "low"
                })
        
        # Language-specific checks
        if language.lower() == "java":
            # Check for empty catch blocks
            empty_catch_pattern = r"catch\s*\([^)]+\)\s*\{\s*\}"
            for i, line in enumerate(lines):
                if re.search(empty_catch_pattern, line):
                    issues.append({
                        "type": "error_handling",
                        "description": "Empty catch block",
                        "line": i + 1,
                        "severity": "medium"
                    })
            
            # Check for System.out.println usage
            println_pattern = r"System\.out\.println"
            for i, line in enumerate(lines):
                if re.search(println_pattern, line):
                    issues.append({
                        "type": "logging",
                        "description": "Using System.out.println instead of proper logging",
                        "line": i + 1,
                        "severity": "low"
                    })
        
        elif language.lower() == "python":
            # Check for using == with None
            none_eq_pattern = r"==\s*None"
            for i, line in enumerate(lines):
                if re.search(none_eq_pattern, line):
                    issues.append({
                        "type": "idiom",
                        "description": "Using == None instead of is None",
                        "line": i + 1,
                        "severity": "low"
                    })
            
            # Check for bare except
            bare_except_pattern = r"except\s*:"
            for i, line in enumerate(lines):
                if re.search(bare_except_pattern, line):
                    issues.append({
                        "type": "error_handling",
                        "description": "Using bare except clause",
                        "line": i + 1,
                        "severity": "medium"
                    })
        
        # Add more language-specific checks as needed
        
        return {
            "issues": issues,
            "issue_count": len(issues),
            "severity_counts": {
                "high": sum(1 for issue in issues if issue["severity"] == "high"),
                "medium": sum(1 for issue in issues if issue["severity"] == "medium"),
                "low": sum(1 for issue in issues if issue["severity"] == "low")
            }
        }
    
    @handle_exceptions
    def _analyze_security(self, code: str, language: str) -> Dict[str, Any]:
        """
        Analyze code for security vulnerabilities.
        
        Args:
            code (str): Code to analyze
            language (str): Programming language of the code
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        # In a production application, this would use a real security scanning tool.
        # For now, we'll use a basic implementation that identifies some common security issues.
        
        vulnerabilities = []
        
        # Common patterns that could indicate security issues
        patterns = [
            {
                "pattern": r"(?i)password\s*=\s*['\"][^'\"]+['\"]",
                "description": "Hardcoded password",
                "severity": "high",
                "type": "credentials"
            },
            {
                "pattern": r"(?i)api[-_]?key\s*=\s*['\"][^'\"]+['\"]",
                "description": "Hardcoded API key",
                "severity": "high",
                "type": "credentials"
            }
        ]
        
        # Language-specific patterns
        if language.lower() == "java":
            patterns.extend([
                {
                    "pattern": r"(?i)\.executeQuery\([^)]*\+",
                    "description": "Potential SQL injection",
                    "severity": "high",
                    "type": "injection"
                },
                {
                    "pattern": r"(?i)Runtime\.getRuntime\(\)\.exec\(",
                    "description": "Potential command injection",
                    "severity": "high",
                    "type": "injection"
                }
            ])
        
        elif language.lower() == "python":
            patterns.extend([
                {
                    "pattern": r"(?i)eval\(",
                    "description": "Using eval() function",
                    "severity": "high",
                    "type": "code_execution"
                },
                {
                    "pattern": r"(?i)subprocess\.(?:call|Popen|run)\([^)]*shell\s*=\s*True",
                    "description": "Shell=True in subprocess calls",
                    "severity": "high",
                    "type": "injection"
                }
            ])
        
        # Check code against patterns
        lines = code.split("\n")
        for pattern_info in patterns:
            pattern = pattern_info["pattern"]
            for i, line in enumerate(lines):
                if re.search(pattern, line):
                    vulnerabilities.append({
                        "type": pattern_info["type"],
                        "description": pattern_info["description"],
                        "line": i + 1,
                        "severity": pattern_info["severity"],
                        "code": line.strip()
                    })
        
        return {
            "vulnerabilities": vulnerabilities,
            "vulnerability_count": len(vulnerabilities),
            "severity_counts": {
                "critical": sum(1 for vuln in vulnerabilities if vuln["severity"] == "critical"),
                "high": sum(1 for vuln in vulnerabilities if vuln["severity"] == "high"),
                "medium": sum(1 for vuln in vulnerabilities if vuln["severity"] == "medium"),
                "low": sum(1 for vuln in vulnerabilities if vuln["severity"] == "low")
            }
        }
    
    @handle_exceptions
    def _analyze_performance(self, code: str, language: str) -> Dict[str, Any]:
        """
        Analyze code for performance issues.
        
        Args:
            code (str): Code to analyze
            language (str): Programming language of the code
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        # In a production application, this would use a real performance analysis tool.
        # For now, we'll use a basic implementation that identifies some common performance issues.
        
        issues = []
        
        # Common performance issues
        # Language-specific patterns
        if language.lower() == "java":
            # Check for concatenation in loops
            concat_pattern = r"for\s*\([^)]+\)\s*\{[^}]*\+\s*="
            if re.search(concat_pattern, code, re.DOTALL):
                issues.append({
                    "type": "string_manipulation",
                    "description": "String concatenation in a loop. Consider using StringBuilder.",
                    "severity": "medium",
                    "impact": "Can lead to O(n²) time complexity and excessive memory usage."
                })
            
            # Check for excessive object creation in loops
            new_in_loop_pattern = r"for\s*\([^)]+\)\s*\{[^}]*new\s+"
            if re.search(new_in_loop_pattern, code, re.DOTALL):
                issues.append({
                    "type": "object_creation",
                    "description": "Object creation in a loop. Consider reusing objects.",
                    "severity": "medium",
                    "impact": "Can lead to excessive garbage collection and memory pressure."
                })
        
        elif language.lower() == "python":
            # Check for list comprehension vs. append in loops
            append_pattern = r"for\s+[^:]+:[^]]*\.append\("
            if re.search(append_pattern, code, re.DOTALL):
                issues.append({
                    "type": "loop_optimization",
                    "description": "Using .append() in a loop. Consider list comprehension.",
                    "severity": "low",
                    "impact": "List comprehensions are generally faster and more readable."
                })
            
            # Check for using + to concatenate strings in loops
            str_concat_pattern = r"for\s+[^:]+:[^]]*\s*\+\s*="
            if re.search(str_concat_pattern, code, re.DOTALL):
                issues.append({
                    "type": "string_manipulation",
                    "description": "String concatenation in a loop. Consider using join().",
                    "severity": "medium",
                    "impact": "Can lead to O(n²) time complexity and excessive memory usage."
                })
        
        return {
            "issues": issues,
            "issue_count": len(issues),
            "severity_counts": {
                "high": sum(1 for issue in issues if issue["severity"] == "high"),
                "medium": sum(1 for issue in issues if issue["severity"] == "medium"),
                "low": sum(1 for issue in issues if issue["severity"] == "low")
            }
        }
    
    def _format_results(self, results: Dict[str, Any], language: str) -> str:
        """
        Format analysis results as a readable string.
        
        Args:
            results (Dict[str, Any]): Analysis results
            language (str): Programming language of the code
            
        Returns:
            str: Formatted results
        """
        output = f"# Code Analysis Results for {language} code\n\n"
        
        # Quality analysis
        if "quality" in results:
            quality = results["quality"]
            output += "## Code Quality\n\n"
            output += f"Found {quality['issue_count']} issues: "
            output += f"{quality['severity_counts']['high']} high, "
            output += f"{quality['severity_counts']['medium']} medium, "
            output += f"{quality['severity_counts']['low']} low severity.\n\n"
            
            if quality["issues"]:
                output += "### Issues:\n\n"
                for issue in quality["issues"]:
                    output += f"- **{issue['type']}** (Line {issue['line']}, {issue['severity']}): {issue['description']}\n"
            else:
                output += "No quality issues detected.\n"
        
        # Security analysis
        if "security" in results:
            security = results["security"]
            output += "\n## Security Analysis\n\n"
            output += f"Found {security['vulnerability_count']} vulnerabilities: "
            output += f"{security['severity_counts'].get('critical', 0)} critical, "
            output += f"{security['severity_counts']['high']} high, "
            output += f"{security['severity_counts']['medium']} medium, "
            output += f"{security['severity_counts']['low']} low severity.\n\n"
            
            if security["vulnerabilities"]:
                output += "### Vulnerabilities:\n\n"
                for vuln in security["vulnerabilities"]:
                    output += f"- **{vuln['type']}** (Line {vuln['line']}, {vuln['severity']}): {vuln['description']}\n"
                    output += f"  Code: `{vuln['code']}`\n"
            else:
                output += "No security vulnerabilities detected.\n"
        
        # Performance analysis
        if "performance" in results:
            performance = results["performance"]
            output += "\n## Performance Analysis\n\n"
            output += f"Found {performance['issue_count']} issues: "
            output += f"{performance['severity_counts']['high']} high, "
            output += f"{performance['severity_counts']['medium']} medium, "
            output += f"{performance['severity_counts']['low']} low severity.\n\n"
            
            if performance["issues"]:
                output += "### Issues:\n\n"
                for issue in performance["issues"]:
                    output += f"- **{issue['type']}** ({issue['severity']}): {issue['description']}\n"
                    output += f"  Impact: {issue['impact']}\n"
            else:
                output += "No performance issues detected.\n"
        
        return output