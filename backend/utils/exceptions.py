# backend/utils/exceptions.py

"""
Custom exception hierarchy for the social media agent framework.
Provides specific exception types for different failure modes.
"""


class SocialMediaFrameworkError(Exception):
    """Base exception for all framework-specific errors."""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self):
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


class DatabaseError(SocialMediaFrameworkError):
    """Raised when database operations fail."""
    pass


class APIError(SocialMediaFrameworkError):
    """Raised when external API calls fail."""

    def __init__(self, message: str, status_code: int = None, response_body: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body

    def __str__(self):
        msg = self.message
        if self.status_code:
            msg += f" (HTTP {self.status_code})"
        if self.response_body:
            msg += f" - {self.response_body[:200]}"
        return msg


class ValidationError(SocialMediaFrameworkError):
    """Raised when data validation fails."""
    pass


class AgentError(SocialMediaFrameworkError):
    """Raised when agent execution fails."""

    def __init__(self, message: str, agent_name: str = None, task_id: str = None):
        super().__init__(message)
        self.agent_name = agent_name
        self.task_id = task_id

    def __str__(self):
        msg = self.message
        if self.agent_name:
            msg = f"[{self.agent_name}] {msg}"
        if self.task_id:
            msg += f" (task: {self.task_id})"
        return msg


class GuardrailViolationError(ValidationError):
    """Raised when planner output violates guardrails."""

    def __init__(self, message: str, violations: list = None):
        super().__init__(message)
        self.violations = violations or []

    def __str__(self):
        msg = self.message
        if self.violations:
            violations_str = "\n  - " + "\n  - ".join(self.violations)
            msg += f"\n\nViolations:{violations_str}"
        return msg


class MediaGenerationError(APIError):
    """Raised when media generation fails."""
    pass


class PublishingError(APIError):
    """Raised when content publishing fails."""
    pass
