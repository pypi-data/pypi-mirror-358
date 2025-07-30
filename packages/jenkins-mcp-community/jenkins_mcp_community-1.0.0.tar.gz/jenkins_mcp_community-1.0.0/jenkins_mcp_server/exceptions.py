"""Custom exceptions for Jenkins MCP Server.

This module defines all custom exceptions used throughout the Jenkins MCP server,
providing clear error handling and meaningful error messages for different failure scenarios.
"""

from typing import Optional


class JenkinsError(Exception):
    """Base exception for all Jenkins-related errors.
    
    This is the parent class for all Jenkins-specific exceptions in the MCP server.
    It provides a consistent interface for error handling and logging.
    
    Attributes:
        message: Human-readable error message
        details: Optional additional error details
        jenkins_url: Optional Jenkins URL where the error occurred
    """
    
    def __init__(
        self, 
        message: str, 
        details: Optional[str] = None,
        jenkins_url: Optional[str] = None
    ):
        """Initialize Jenkins error.
        
        Args:
            message: Primary error message
            details: Additional error details
            jenkins_url: Jenkins URL where error occurred
        """
        self.message = message
        self.details = details
        self.jenkins_url = jenkins_url
        super().__init__(self.message)
    
    def __str__(self) -> str:
        """Return formatted error message."""
        parts = [self.message]
        if self.details:
            parts.append(f"Details: {self.details}")
        if self.jenkins_url:
            parts.append(f"Jenkins URL: {self.jenkins_url}")
        return " | ".join(parts)


class JenkinsConnectionError(JenkinsError):
    """Raised when unable to connect to Jenkins server.
    
    This exception is raised when the MCP server cannot establish a connection
    to the Jenkins instance, typically due to network issues, incorrect URL,
    or Jenkins server being unavailable.
    """
    pass


class JenkinsAuthenticationError(JenkinsError):
    """Raised when Jenkins authentication fails.
    
    This exception is raised when the provided credentials are invalid,
    expired, or insufficient for the requested operation.
    """
    pass


class JenkinsAuthorizationError(JenkinsError):
    """Raised when user lacks permissions for the requested operation.
    
    This exception is raised when the authenticated user does not have
    sufficient permissions to perform the requested Jenkins operation.
    """
    pass


class JenkinsResourceNotFoundError(JenkinsError):
    """Raised when a requested Jenkins resource is not found.
    
    This exception is raised when attempting to access a Jenkins resource
    (job, build, folder, etc.) that does not exist.
    """
    pass


class JenkinsOperationError(JenkinsError):
    """Raised when a Jenkins operation fails.
    
    This exception is raised when a Jenkins operation fails due to server-side
    issues, invalid parameters, or other operational problems.
    """
    pass


class JenkinsConfigurationError(JenkinsError):
    """Raised when Jenkins server configuration is invalid.
    
    This exception is raised when the Jenkins server configuration
    prevents the requested operation from completing successfully.
    """
    pass


class JenkinsBuildError(JenkinsError):
    """Raised when a Jenkins build operation fails.
    
    This exception is raised when build-related operations fail,
    such as triggering builds, accessing build artifacts, or
    retrieving build information.
    """
    pass


class JenkinsPipelineError(JenkinsError):
    """Raised when a Jenkins pipeline operation fails.
    
    This exception is raised when pipeline-related operations fail,
    such as creating, updating, or executing pipeline jobs.
    """
    pass


class JenkinsValidationError(JenkinsError):
    """Raised when input validation fails.
    
    This exception is raised when user input fails validation
    before being sent to Jenkins, helping to catch errors early.
    """
    pass


class JenkinsTimeoutError(JenkinsError):
    """Raised when a Jenkins operation times out.
    
    This exception is raised when a Jenkins operation takes longer
    than the configured timeout period.
    """
    pass


class JenkinsRateLimitError(JenkinsError):
    """Raised when Jenkins rate limiting is encountered.
    
    This exception is raised when the Jenkins server returns
    rate limiting errors, indicating too many requests.
    """
    pass
