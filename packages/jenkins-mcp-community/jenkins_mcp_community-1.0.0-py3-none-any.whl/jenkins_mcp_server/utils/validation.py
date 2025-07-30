"""Validation utilities for Jenkins MCP Server.

This module provides comprehensive validation functions for Jenkins-related
data and parameters to ensure data integrity and prevent security issues.

The validation functions cover:
- Jenkins URLs and connection parameters
- Job names and folder paths
- Build numbers and parameters
- User credentials and tokens
- Input sanitization and normalization

All validation functions raise JenkinsValidationError with descriptive
messages to help with debugging and error handling.
"""

import re
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

from pydantic import ValidationError

from jenkins_mcp_server.exceptions import JenkinsValidationError


def validate_folder_path(folder_path: str) -> str:
    """Validate and normalize Jenkins folder path.
    
    Validates folder path format, checks for invalid characters,
    and normalizes the path for consistent usage across the system.
    
    Args:
        folder_path: Jenkins folder path to validate (e.g., 'team/project')
        
    Returns:
        str: Normalized and validated folder path
        
    Raises:
        JenkinsValidationError: If folder path contains invalid characters
                               or uses reserved names
    """
    if not folder_path:
        return ""
    
    from jenkins_mcp_server.utils.path_utils import normalize_jenkins_path, validate_jenkins_path
    
    normalized_path = normalize_jenkins_path(folder_path)
    if not validate_jenkins_path(normalized_path):
        raise JenkinsValidationError(f"Invalid folder path: {folder_path}")
    
    return normalized_path


def validate_jenkins_url(url: str) -> str:
    """Validate and normalize Jenkins server URL.
    
    Ensures the URL is properly formatted, uses supported protocols,
    and normalizes trailing slashes for consistent usage.
    
    Args:
        url: Jenkins server URL to validate (e.g., 'http://jenkins:8080')
        
    Returns:
        str: Normalized and validated Jenkins URL
        
    Raises:
        JenkinsValidationError: If URL format is invalid or uses unsupported protocol
    """
    if not url:
        raise JenkinsValidationError('Jenkins URL cannot be empty')
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = f'http://{url}'
    
    try:
        parsed = urlparse(url)
        
        if not parsed.netloc:
            raise JenkinsValidationError(f'Invalid Jenkins URL: {url}')
        
        # Normalize URL (remove trailing slash)
        normalized_url = f'{parsed.scheme}://{parsed.netloc}'
        if parsed.path and parsed.path != '/':
            normalized_url += parsed.path.rstrip('/')
        
        return normalized_url
        
    except Exception as e:
        raise JenkinsValidationError(f'Invalid Jenkins URL: {url}') from e


def validate_job_name(job_name: str) -> str:
    """Validate Jenkins job name.
    
    Args:
        job_name: Job name to validate
        
    Returns:
        Validated job name
        
    Raises:
        JenkinsValidationError: If job name is invalid
    """
    if not job_name:
        raise JenkinsValidationError('Job name cannot be empty')
    
    if not isinstance(job_name, str):
        raise JenkinsValidationError('Job name must be a string')
    
    # Check for invalid characters
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in invalid_chars:
        if char in job_name:
            raise JenkinsValidationError(
                f'Job name contains invalid character: {char}'
            )
    
    # Check length
    if len(job_name) > 255:
        raise JenkinsValidationError('Job name is too long (max 255 characters)')
    
    # Check for reserved names
    reserved_names = ['.', '..', 'api', 'view', 'computer', 'people', 'queue']
    if job_name.lower() in reserved_names:
        raise JenkinsValidationError(f'Job name is reserved: {job_name}')
    
    return job_name.strip()


def validate_folder_path(folder_path: str) -> str:
    """Validate Jenkins folder path.
    
    Args:
        folder_path: Folder path to validate
        
    Returns:
        Validated folder path
        
    Raises:
        JenkinsValidationError: If folder path is invalid
    """
    if not folder_path:
        return ''
    
    if not isinstance(folder_path, str):
        raise JenkinsValidationError('Folder path must be a string')
    
    # Normalize path separators
    folder_path = folder_path.replace('\\', '/')
    
    # Remove leading/trailing slashes
    folder_path = folder_path.strip('/')
    
    if not folder_path:
        return ''
    
    # Validate each path component
    components = folder_path.split('/')
    for component in components:
        if not component:
            raise JenkinsValidationError('Folder path contains empty component')
        validate_job_name(component)  # Use same validation as job names
    
    return folder_path


def validate_build_number(build_number: Union[int, str]) -> int:
    """Validate Jenkins build number.
    
    Args:
        build_number: Build number to validate
        
    Returns:
        Validated build number as integer
        
    Raises:
        JenkinsValidationError: If build number is invalid
    """
    try:
        build_num = int(build_number)
        if build_num < 1:
            raise JenkinsValidationError('Build number must be positive')
        return build_num
    except (ValueError, TypeError) as e:
        raise JenkinsValidationError(f'Invalid build number: {build_number}') from e


def validate_build_parameters(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Validate Jenkins build parameters.
    
    Args:
        parameters: Build parameters to validate
        
    Returns:
        Validated parameters dictionary
        
    Raises:
        JenkinsValidationError: If parameters are invalid
    """
    if not isinstance(parameters, dict):
        raise JenkinsValidationError('Build parameters must be a dictionary')
    
    validated_params = {}
    
    for key, value in parameters.items():
        # Validate parameter name
        if not isinstance(key, str):
            raise JenkinsValidationError('Parameter names must be strings')
        
        if not key.strip():
            raise JenkinsValidationError('Parameter names cannot be empty')
        
        # Validate parameter name format
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', key):
            raise JenkinsValidationError(
                f'Invalid parameter name format: {key}'
            )
        
        # Convert value to string (Jenkins expects string parameters)
        if value is None:
            validated_params[key] = ''
        elif isinstance(value, bool):
            validated_params[key] = 'true' if value else 'false'
        else:
            validated_params[key] = str(value)
    
    return validated_params


def validate_pipeline_script(script: str) -> str:
    """Validate Jenkins pipeline script.
    
    Args:
        script: Pipeline script to validate
        
    Returns:
        Validated pipeline script
        
    Raises:
        JenkinsValidationError: If script is invalid
    """
    if not script:
        raise JenkinsValidationError('Pipeline script cannot be empty')
    
    if not isinstance(script, str):
        raise JenkinsValidationError('Pipeline script must be a string')
    
    # Basic syntax checks
    script = script.strip()
    
    # Check for required pipeline structure
    if not script.startswith('pipeline'):
        raise JenkinsValidationError(
            'Pipeline script must start with "pipeline" block'
        )
    
    # Check for balanced braces (basic check)
    open_braces = script.count('{')
    close_braces = script.count('}')
    
    if open_braces != close_braces:
        raise JenkinsValidationError(
            'Pipeline script has unbalanced braces'
        )
    
    return script


def validate_credentials(username: str, password: str) -> tuple[str, str]:
    """Validate Jenkins credentials.
    
    Args:
        username: Username to validate
        password: Password/token to validate
        
    Returns:
        Tuple of validated (username, password)
        
    Raises:
        JenkinsValidationError: If credentials are invalid
    """
    if not username:
        raise JenkinsValidationError('Username cannot be empty')
    
    if not password:
        raise JenkinsValidationError('Password/token cannot be empty')
    
    if not isinstance(username, str):
        raise JenkinsValidationError('Username must be a string')
    
    if not isinstance(password, str):
        raise JenkinsValidationError('Password/token must be a string')
    
    # Basic username validation
    username = username.strip()
    if not username:
        raise JenkinsValidationError('Username cannot be empty after trimming')
    
    # Check for invalid characters in username
    if any(char in username for char in ['\n', '\r', '\t']):
        raise JenkinsValidationError('Username contains invalid characters')
    
    return username, password


def validate_timeout(timeout: Union[int, float]) -> float:
    """Validate timeout value.
    
    Args:
        timeout: Timeout value in seconds
        
    Returns:
        Validated timeout as float
        
    Raises:
        JenkinsValidationError: If timeout is invalid
    """
    try:
        timeout_val = float(timeout)
        if timeout_val <= 0:
            raise JenkinsValidationError('Timeout must be positive')
        if timeout_val > 3600:  # 1 hour max
            raise JenkinsValidationError('Timeout cannot exceed 1 hour')
        return timeout_val
    except (ValueError, TypeError) as e:
        raise JenkinsValidationError(f'Invalid timeout value: {timeout}') from e


def validate_page_parameters(page: Optional[int] = None, per_page: Optional[int] = None) -> tuple[int, int]:
    """Validate pagination parameters.
    
    Args:
        page: Page number (1-based)
        per_page: Items per page
        
    Returns:
        Tuple of validated (page, per_page)
        
    Raises:
        JenkinsValidationError: If parameters are invalid
    """
    # Default values
    if page is None:
        page = 1
    if per_page is None:
        per_page = 50
    
    # Validate page number
    try:
        page = int(page)
        if page < 1:
            raise JenkinsValidationError('Page number must be positive')
        if page > 10000:  # Reasonable upper limit
            raise JenkinsValidationError('Page number is too large')
    except (ValueError, TypeError) as e:
        raise JenkinsValidationError(f'Invalid page number: {page}') from e
    
    # Validate per_page
    try:
        per_page = int(per_page)
        if per_page < 1:
            raise JenkinsValidationError('Items per page must be positive')
        if per_page > 1000:  # Reasonable upper limit
            raise JenkinsValidationError('Items per page is too large (max 1000)')
    except (ValueError, TypeError) as e:
        raise JenkinsValidationError(f'Invalid per_page value: {per_page}') from e
    
    return page, per_page


def validate_json_data(data: Any, schema: Optional[Dict[str, Any]] = None) -> Any:
    """Validate JSON data against optional schema.
    
    Args:
        data: Data to validate
        schema: Optional JSON schema for validation
        
    Returns:
        Validated data
        
    Raises:
        JenkinsValidationError: If data is invalid
    """
    if schema is None:
        return data
    
    try:
        # Basic schema validation (simplified)
        if 'type' in schema:
            expected_type = schema['type']
            
            type_map = {
                'string': str,
                'integer': int,
                'number': (int, float),
                'boolean': bool,
                'array': list,
                'object': dict,
            }
            
            if expected_type in type_map:
                expected_python_type = type_map[expected_type]
                if not isinstance(data, expected_python_type):
                    raise JenkinsValidationError(
                        f'Expected {expected_type}, got {type(data).__name__}'
                    )
        
        return data
        
    except Exception as e:
        raise JenkinsValidationError(f'JSON validation failed: {e}') from e


def sanitize_input(input_str: str, max_length: int = 1000) -> str:
    """Sanitize user input string.
    
    Args:
        input_str: Input string to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
        
    Raises:
        JenkinsValidationError: If input is invalid
    """
    if not isinstance(input_str, str):
        raise JenkinsValidationError('Input must be a string')
    
    # Remove control characters
    sanitized = ''.join(char for char in input_str if ord(char) >= 32 or char in '\t\n\r')
    
    # Trim whitespace
    sanitized = sanitized.strip()
    
    # Check length
    if len(sanitized) > max_length:
        raise JenkinsValidationError(f'Input too long (max {max_length} characters)')
    
    return sanitized
