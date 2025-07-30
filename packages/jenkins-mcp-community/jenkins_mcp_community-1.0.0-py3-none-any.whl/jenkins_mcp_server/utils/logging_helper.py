"""Logging utilities for Jenkins MCP Server.

This module provides centralized logging configuration and utilities
following best practices for structured logging and observability.
"""

import os
import sys
from typing import Any, Dict, Optional

from loguru import logger


def setup_logging(
    level: str = 'INFO',
    format_string: Optional[str] = None,
    json_format: bool = False,
    include_caller: bool = False,
    log_file: Optional[str] = None,
) -> None:
    """Set up logging configuration for the Jenkins MCP server.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string for log messages
        json_format: Whether to use JSON format for structured logging
        include_caller: Whether to include caller information in logs
        log_file: Optional file path for log output
    """
    # Remove default handler
    logger.remove()
    
    # Determine format
    if format_string is None:
        if json_format:
            format_string = (
                '{"time": "{time:YYYY-MM-DD HH:mm:ss.SSS}", '
                '"level": "{level}", '
                '"module": "{name}", '
                '"function": "{function}", '
                '"line": {line}, '
                '"message": "{message}"}'
            )
        else:
            base_format = (
                '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | '
                '<level>{level: <8}</level> | '
                '<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | '
                '<level>{message}</level>'
            )
            if include_caller:
                format_string = base_format
            else:
                format_string = (
                    '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | '
                    '<level>{level: <8}</level> | '
                    '<level>{message}</level>'
                )
    
    # Add console handler
    logger.add(
        sys.stderr,
        format=format_string,
        level=level,
        colorize=not json_format,
        backtrace=True,
        diagnose=True,
    )
    
    # Add file handler if specified
    if log_file:
        logger.add(
            log_file,
            format=format_string,
            level=level,
            rotation='10 MB',
            retention='7 days',
            compression='gz',
            backtrace=True,
            diagnose=True,
        )
    
    # Set third-party loggers to WARNING to reduce noise
    import logging
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('jenkins').setLevel(logging.WARNING)
    logging.getLogger('jenkinsapi').setLevel(logging.WARNING)


def get_logger(name: str) -> Any:
    """Get a logger instance for the specified module.
    
    Args:
        name: Module name (typically __name__)
        
    Returns:
        Logger instance configured for the module
    """
    return logger.bind(module=name)


def log_jenkins_operation(
    operation: str,
    jenkins_url: str,
    job_name: Optional[str] = None,
    build_number: Optional[int] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Create structured log context for Jenkins operations.
    
    Args:
        operation: Operation being performed
        jenkins_url: Jenkins server URL
        job_name: Optional job name
        build_number: Optional build number
        **kwargs: Additional context data
        
    Returns:
        Dictionary with structured log context
    """
    context = {
        'operation': operation,
        'jenkins_url': jenkins_url,
    }
    
    if job_name:
        context['job_name'] = job_name
    if build_number:
        context['build_number'] = build_number
    
    context.update(kwargs)
    return context


def log_performance_metrics(
    operation: str,
    duration_ms: float,
    success: bool,
    **kwargs: Any,
) -> None:
    """Log performance metrics for operations.
    
    Args:
        operation: Operation name
        duration_ms: Operation duration in milliseconds
        success: Whether operation was successful
        **kwargs: Additional metrics
    """
    metrics = {
        'operation': operation,
        'duration_ms': duration_ms,
        'success': success,
        **kwargs,
    }
    
    logger.info('Performance metrics', **metrics)


def log_error_with_context(
    error: Exception,
    operation: str,
    context: Dict[str, Any],
    include_traceback: bool = True,
) -> None:
    """Log error with structured context.
    
    Args:
        error: Exception that occurred
        operation: Operation that failed
        context: Additional context information
        include_traceback: Whether to include full traceback
    """
    error_context = {
        'operation': operation,
        'error_type': type(error).__name__,
        'error_message': str(error),
        **context,
    }
    
    if include_traceback:
        logger.exception('Operation failed', **error_context)
    else:
        logger.error('Operation failed', **error_context)


def mask_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Mask sensitive data in log context.
    
    Args:
        data: Dictionary that may contain sensitive data
        
    Returns:
        Dictionary with sensitive data masked
    """
    sensitive_keys = {
        'password', 'token', 'secret', 'key', 'credential',
        'auth', 'authorization', 'api_key', 'access_token',
    }
    
    masked_data = {}
    for key, value in data.items():
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            if isinstance(value, str) and len(value) > 4:
                masked_data[key] = f"{value[:2]}{'*' * (len(value) - 4)}{value[-2:]}"
            else:
                masked_data[key] = '***'
        else:
            masked_data[key] = value
    
    return masked_data
