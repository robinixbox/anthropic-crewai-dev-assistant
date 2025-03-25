import logging
import traceback
from typing import Dict, Any, Optional, List, Tuple
import json
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """
    Enumeration for error severity levels
    """
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"

class ErrorCategory(Enum):
    """
    Enumeration for categorizing different types of errors
    """
    CONFIGURATION = "Configuration Error"
    API = "API Error"
    NETWORK = "Network Error"
    AUTHENTICATION = "Authentication Error"
    VALIDATION = "Validation Error"
    GITHUB = "GitHub Integration Error"
    LLM = "Language Model Error"
    UI = "User Interface Error"
    GENERAL = "General Error"
    CREWAI = "CrewAI Error"


class AppError:
    """
    Class to represent a structured application error
    """
    def __init__(
        self,
        message: str,
        category: ErrorCategory,
        severity: ErrorSeverity,
        details: Optional[Dict[str, Any]] = None,
        exception: Optional[Exception] = None,
        suggestions: Optional[List[str]] = None
    ):
        self.message = message
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.timestamp = self._get_timestamp()
        self.traceback = self._format_traceback(exception) if exception else None
        self.suggestions = suggestions or self._generate_suggestions(category)
        
        # Log the error
        self._log_error()
    
    def _get_timestamp(self) -> str:
        """Get the current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _format_traceback(self, exception: Exception) -> str:
        """Format the exception traceback"""
        return ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))
    
    def _log_error(self) -> None:
        """Log the error with the appropriate severity level"""
        log_message = f"{self.category.value}: {self.message}"
        
        if self.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message, exc_info=True)
        elif self.severity == ErrorSeverity.ERROR:
            logger.error(log_message, exc_info=True)
        elif self.severity == ErrorSeverity.WARNING:
            logger.warning(log_message)
        elif self.severity == ErrorSeverity.INFO:
            logger.info(log_message)
        elif self.severity == ErrorSeverity.DEBUG:
            logger.debug(log_message)
    
    def _generate_suggestions(self, category: ErrorCategory) -> List[str]:
        """Generate helpful suggestions based on the error category"""
        suggestions = {
            ErrorCategory.CONFIGURATION: [
                "Vérifiez que tous les fichiers de configuration existent et sont correctement formatés",
                "Assurez-vous que les variables d'environnement requises sont définies",
                "Consultez la documentation pour les paramètres de configuration corrects"
            ],
            ErrorCategory.API: [
                "Vérifiez votre connexion internet",
                "Assurez-vous que votre clé API est valide et n'a pas expiré",
                "Vérifiez les quotas et limites de votre compte API"
            ],
            ErrorCategory.NETWORK: [
                "Vérifiez votre connexion internet",
                "Vérifiez si le service distant est disponible",
                "Essayez de réexécuter l'opération plus tard"
            ],
            ErrorCategory.AUTHENTICATION: [
                "Vérifiez que vos informations d'identification sont correctes",
                "Assurez-vous que votre token n'a pas expiré",
                "Vérifiez les permissions associées à votre compte"
            ],
            ErrorCategory.VALIDATION: [
                "Vérifiez le format des données d'entrée",
                "Assurez-vous que toutes les valeurs requises sont fournies",
                "Consultez la documentation pour les formats attendus"
            ],
            ErrorCategory.GITHUB: [
                "Vérifiez votre token d'accès GitHub",
                "Assurez-vous que vous avez les permissions nécessaires sur le dépôt",
                "Vérifiez si GitHub est accessible et opérationnel"
            ],
            ErrorCategory.LLM: [
                "Vérifiez votre clé API Anthropic",
                "Assurez-vous que le modèle demandé est disponible",
                "Vérifiez vos quotas d'utilisation sur la plateforme Anthropic"
            ],
            ErrorCategory.UI: [
                "Essayez de rafraîchir l'interface",
                "Videz le cache de votre navigateur",
                "Redémarrez l'application"
            ],
            ErrorCategory.CREWAI: [
                "Vérifiez la configuration des agents et des tâches",
                "Assurez-vous que les dépendances de CrewAI sont correctement installées",
                "Consultez la documentation CrewAI pour les bonnes pratiques"
            ],
            ErrorCategory.GENERAL: [
                "Consultez les logs pour plus de détails",
                "Vérifiez la documentation pour les procédures de dépannage",
                "Redémarrez l'application et réessayez"
            ]
        }
        
        return suggestions.get(category, ["Consultez la documentation pour plus d'informations"])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the error to a dictionary for serialization"""
        return {
            "message": self.message,
            "category": self.category.value,
            "severity": self.severity.value,
            "details": self.details,
            "timestamp": self.timestamp,
            "traceback": self.traceback,
            "suggestions": self.suggestions
        }
    
    def to_json(self) -> str:
        """Convert the error to a JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    def __str__(self) -> str:
        """String representation of the error"""
        return f"{self.category.value} ({self.severity.value}): {self.message}"


class ErrorHandler:
    """
    Class to manage application errors
    """
    _errors: List[AppError] = []
    
    @classmethod
    def add_error(cls, error: AppError) -> None:
        """
        Add an error to the error list
        
        Args:
            error (AppError): The error to add
        """
        cls._errors.append(error)
    
    @classmethod
    def create_error(
        cls,
        message: str,
        category: ErrorCategory,
        severity: ErrorSeverity,
        details: Optional[Dict[str, Any]] = None,
        exception: Optional[Exception] = None,
        suggestions: Optional[List[str]] = None
    ) -> AppError:
        """
        Create and add a new error
        
        Args:
            message (str): Error message
            category (ErrorCategory): Error category
            severity (ErrorSeverity): Error severity
            details (Optional[Dict[str, Any]]): Additional error details
            exception (Optional[Exception]): The exception that caused the error
            suggestions (Optional[List[str]]): Suggestions for fixing the error
            
        Returns:
            AppError: The created error
        """
        error = AppError(message, category, severity, details, exception, suggestions)
        cls.add_error(error)
        return error
    
    @classmethod
    def get_errors(cls) -> List[AppError]:
        """
        Get all recorded errors
        
        Returns:
            List[AppError]: The list of errors
        """
        return cls._errors
    
    @classmethod
    def get_last_error(cls) -> Optional[AppError]:
        """
        Get the most recent error
        
        Returns:
            Optional[AppError]: The most recent error, or None if no errors
        """
        if cls._errors:
            return cls._errors[-1]
        return None
    
    @classmethod
    def clear_errors(cls) -> None:
        """Clear all recorded errors"""
        cls._errors = []
    
    @classmethod
    def get_error_summary(cls) -> Tuple[int, int, int, int, int]:
        """
        Get a summary of error counts by severity
        
        Returns:
            Tuple[int, int, int, int, int]: Count of (CRITICAL, ERROR, WARNING, INFO, DEBUG) errors
        """
        critical = sum(1 for e in cls._errors if e.severity == ErrorSeverity.CRITICAL)
        error = sum(1 for e in cls._errors if e.severity == ErrorSeverity.ERROR)
        warning = sum(1 for e in cls._errors if e.severity == ErrorSeverity.WARNING)
        info = sum(1 for e in cls._errors if e.severity == ErrorSeverity.INFO)
        debug = sum(1 for e in cls._errors if e.severity == ErrorSeverity.DEBUG)
        
        return (critical, error, warning, info, debug)
    
    @classmethod
    def has_critical_errors(cls) -> bool:
        """
        Check if there are any critical errors
        
        Returns:
            bool: True if there are critical errors, False otherwise
        """
        return any(e.severity == ErrorSeverity.CRITICAL for e in cls._errors)


def handle_exceptions(func):
    """
    Decorator to handle exceptions in functions and convert them to AppErrors
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Determine the error category based on the exception type
            if "anthropic" in str(type(e)).lower():
                category = ErrorCategory.LLM
            elif "github" in str(type(e)).lower():
                category = ErrorCategory.GITHUB
            elif "crewai" in str(type(e)).lower():
                category = ErrorCategory.CREWAI
            elif "connection" in str(e).lower() or "timeout" in str(e).lower():
                category = ErrorCategory.NETWORK
            elif "permission" in str(e).lower() or "unauthorized" in str(e).lower():
                category = ErrorCategory.AUTHENTICATION
            elif "config" in str(e).lower():
                category = ErrorCategory.CONFIGURATION
            elif "validation" in str(e).lower() or "invalid" in str(e).lower():
                category = ErrorCategory.VALIDATION
            else:
                category = ErrorCategory.GENERAL
            
            # Create and log the error
            error = ErrorHandler.create_error(
                message=str(e),
                category=category,
                severity=ErrorSeverity.ERROR,
                exception=e
            )
            
            # Re-raise the exception with additional information
            raise RuntimeError(f"Error: {error}") from e
    
    return wrapper