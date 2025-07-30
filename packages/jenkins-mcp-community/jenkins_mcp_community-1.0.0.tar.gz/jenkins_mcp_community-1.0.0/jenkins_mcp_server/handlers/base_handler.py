"""Base handler for Jenkins MCP Server.

This module provides the base handler class with common functionality
for all Jenkins operation handlers including connection management,
caching, error handling, and utility methods.

The BaseHandler class serves as the foundation for all Jenkins operations,
providing consistent patterns for authentication, retry logic, and
error handling across all handler implementations.
"""

import os
from typing import Any, Dict, Optional

import jenkins
from jenkinsapi.jenkins import Jenkins as JenkinsAPI
from loguru import logger

from jenkins_mcp_server.exceptions import (
    JenkinsAuthenticationError,
    JenkinsConnectionError,
    JenkinsError,
)
from jenkins_mcp_server.utils.cache import get_cache_manager
from jenkins_mcp_server.utils.connection_pool import get_connection_pool
from jenkins_mcp_server.utils.retry import retry_with_backoff
from jenkins_mcp_server.utils.validation import validate_jenkins_url, validate_credentials


class BaseHandler:
    """Base handler class for Jenkins operations.
    
    This class provides common functionality for all Jenkins handlers including:
    - Connection management with automatic retry
    - Intelligent caching with configurable TTL
    - Comprehensive error handling and logging
    - Input validation and sanitization
    - HTTP connection pooling for performance
    
    All Jenkins handlers should inherit from this class to ensure
    consistent behavior and error handling patterns.
    """
    
    def __init__(self):
        """Initialize the base handler with required dependencies.
        
        Sets up cache manager, connection pool, and Jenkins configuration
        from environment variables. Jenkins clients are initialized lazily
        to avoid unnecessary connections during handler creation.
        """
        self.cache_manager = get_cache_manager()
        self.connection_pool = get_connection_pool()
        
        # Jenkins configuration from environment variables
        self.jenkins_url = self._get_jenkins_url()
        self.username = self._get_jenkins_username()
        self.token = self._get_jenkins_token()
        self.timeout = self._get_jenkins_timeout()
        
        # Jenkins clients (initialized lazily for performance)
        self._jenkins_client: Optional[jenkins.Jenkins] = None
        self._jenkinsapi_client: Optional[JenkinsAPI] = None
    
    def _get_jenkins_url(self) -> str:
        """Get and validate Jenkins URL from environment variables.
        
        Returns:
            Validated Jenkins URL
            
        Raises:
            JenkinsError: If URL is not configured or invalid
        """
        url = os.getenv('JENKINS_URL')
        if not url:
            raise JenkinsError('JENKINS_URL environment variable is required')
        
        return validate_jenkins_url(url)
    
    def _get_jenkins_username(self) -> str:
        """Get Jenkins username from environment.
        
        Returns:
            Jenkins username
            
        Raises:
            JenkinsError: If username is not configured
        """
        username = os.getenv('JENKINS_USERNAME')
        if not username:
            raise JenkinsError('JENKINS_USERNAME environment variable is required')
        
        return username
    
    def _get_jenkins_token(self) -> str:
        """Get Jenkins token from environment.
        
        Returns:
            Jenkins API token
            
        Raises:
            JenkinsError: If token is not configured
        """
        token = os.getenv('JENKINS_TOKEN')
        if not token:
            raise JenkinsError('JENKINS_TOKEN environment variable is required')
        
        return token
    
    async def _get_csrf_crumb(self) -> Optional[Dict[str, str]]:
        """Get CSRF crumb for Jenkins API calls.
        
        Returns:
            Optional[Dict[str, str]]: Dictionary with crumb header and value, 
                                    or None if not available
        """
        try:
            crumb_url = f'{self.jenkins_url}/crumbIssuer/api/json'
            
            # Use direct HTTP request instead of execute_with_retry to avoid recursion
            import httpx
            auth = (self.username, self.token)
            
            async with httpx.AsyncClient() as client:
                response = await client.get(crumb_url, auth=auth, timeout=self.timeout)
                response.raise_for_status()
                crumb_data = response.json()
            
            if crumb_data and 'crumb' in crumb_data and 'crumbRequestField' in crumb_data:
                return {
                    crumb_data['crumbRequestField']: crumb_data['crumb']
                }
            
        except Exception as e:
            logger.debug(f'Failed to get CSRF crumb: {e}')
        
        return None
    
    async def _make_request(self, method: str, url: str, **kwargs) -> Any:
        """Make HTTP request to Jenkins API with authentication.
        
        Args:
            method: HTTP method
            url: Request URL
            **kwargs: Additional request parameters
            
        Returns:
            Response data
        """
        import httpx
        
        # Add authentication
        auth = (self.username, self.token)
        
        # Add CSRF protection for write operations
        headers = kwargs.get('headers', {})
        if method.upper() in ['POST', 'PUT', 'DELETE']:
            crumb = await self._get_csrf_crumb()
            if crumb:
                headers.update(crumb)
        
        kwargs['headers'] = headers
        kwargs['auth'] = auth
        
        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            
            if response.headers.get('content-type', '').startswith('application/json'):
                return response.json()
            else:
                return response.text
    
    async def _make_api_request(self, method: str, url: str, **kwargs) -> Any:
        """Make API request with consistent URL handling.
        
        Args:
            method: HTTP method
            url: Request URL (can be relative or absolute)
            **kwargs: Additional request parameters
            
        Returns:
            Response data
        """
        # Ensure consistent server URL handling
        if not url.startswith('http'):
            # Relative URL - prepend Jenkins server URL
            jenkins_base = self.jenkins_url.rstrip('/')
            url = f"{jenkins_base}/{url.lstrip('/')}"
        
        return await self._make_request(method, url, **kwargs)
    
    def _get_jenkins_timeout(self) -> int:
        """Get Jenkins timeout from environment.
        
        Returns:
            Timeout in seconds
        """
        try:
            return int(os.getenv('JENKINS_TIMEOUT', '30'))
        except ValueError:
            logger.warning('Invalid JENKINS_TIMEOUT value, using default 30 seconds')
            return 30
    
    @property
    def jenkins_client(self) -> jenkins.Jenkins:
        """Get python-jenkins client instance.
        
        Returns:
            Jenkins client instance
            
        Raises:
            JenkinsConnectionError: If connection fails
        """
        if self._jenkins_client is None:
            try:
                validate_credentials(self.username, self.token)
                
                self._jenkins_client = jenkins.Jenkins(
                    url=self.jenkins_url,
                    username=self.username,
                    password=self.token,
                    timeout=self.timeout,
                )
                
                # Test connection
                self._jenkins_client.get_whoami()
                logger.debug(f'Connected to Jenkins at {self.jenkins_url}')
                
            except jenkins.JenkinsException as e:
                if 'Invalid username or password' in str(e):
                    raise JenkinsAuthenticationError(
                        'Invalid Jenkins credentials',
                        details=str(e),
                        jenkins_url=self.jenkins_url,
                    )
                else:
                    raise JenkinsConnectionError(
                        'Failed to connect to Jenkins',
                        details=str(e),
                        jenkins_url=self.jenkins_url,
                    )
            except Exception as e:
                raise JenkinsConnectionError(
                    'Failed to initialize Jenkins client',
                    details=str(e),
                    jenkins_url=self.jenkins_url,
                )
        
        return self._jenkins_client
    
    @property
    def jenkinsapi_client(self) -> JenkinsAPI:
        """Get jenkinsapi client instance.
        
        Returns:
            JenkinsAPI client instance
            
        Raises:
            JenkinsConnectionError: If connection fails
        """
        if self._jenkinsapi_client is None:
            try:
                validate_credentials(self.username, self.token)
                
                self._jenkinsapi_client = JenkinsAPI(
                    baseurl=self.jenkins_url,
                    username=self.username,
                    password=self.token,
                    timeout=self.timeout,
                )
                
                # Test connection
                _ = self._jenkinsapi_client.version
                logger.debug(f'Connected to Jenkins API at {self.jenkins_url}')
                
            except Exception as e:
                if 'Unauthorized' in str(e) or 'authentication' in str(e).lower():
                    raise JenkinsAuthenticationError(
                        'Invalid Jenkins credentials',
                        details=str(e),
                        jenkins_url=self.jenkins_url,
                    )
                else:
                    raise JenkinsConnectionError(
                        'Failed to connect to Jenkins API',
                        details=str(e),
                        jenkins_url=self.jenkins_url,
                    )
        
        return self._jenkinsapi_client
    
    @retry_with_backoff(max_attempts=3)
    async def execute_with_retry(self, operation_name: str, func, *args, **kwargs) -> Any:
        """Execute operation with retry logic.
        
        Args:
            operation_name: Name of the operation for logging
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            JenkinsError: If operation fails after retries
        """
        try:
            logger.debug(f'Executing Jenkins operation: {operation_name}')
            result = func(*args, **kwargs)
            logger.debug(f'Successfully completed operation: {operation_name}')
            return result
            
        except Exception as e:
            logger.error(f'Operation failed: {operation_name} - {e}')
            raise
    
    async def get_cached_or_fetch(
        self,
        cache_key: str,
        fetch_func,
        cache_type: str = 'general',
        *args,
        **kwargs,
    ) -> Any:
        """Get data from cache or fetch if not cached.
        
        Args:
            cache_key: Cache key
            fetch_func: Function to fetch data if not cached
            cache_type: Type of cache to use
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Cached or fetched data
        """
        # Try to get from cache first
        cached_data = await self.cache_manager.get(cache_key, cache_type)
        if cached_data is not None:
            logger.debug(f'Cache hit for key: {cache_key}')
            return cached_data
        
        # Fetch data and cache it
        logger.debug(f'Cache miss for key: {cache_key}, fetching data')
        data = await self.execute_with_retry(
            f'fetch_{cache_key}',
            fetch_func,
            *args,
            **kwargs,
        )
        
        await self.cache_manager.set(cache_key, data, cache_type)
        return data
    
    def _handle_jenkins_exception(self, e: Exception, operation: str) -> JenkinsError:
        """Convert Jenkins exceptions to appropriate MCP exceptions.
        
        Args:
            e: Original exception
            operation: Operation that failed
            
        Returns:
            Appropriate JenkinsError subclass
        """
        error_msg = str(e).lower()
        
        if 'not found' in error_msg or '404' in error_msg:
            from jenkins_mcp_server.exceptions import JenkinsResourceNotFoundError
            return JenkinsResourceNotFoundError(
                f'{operation} failed: Resource not found',
                details=str(e),
                jenkins_url=self.jenkins_url,
            )
        
        if 'unauthorized' in error_msg or 'forbidden' in error_msg or '401' in error_msg:
            return JenkinsAuthenticationError(
                f'{operation} failed: Authentication error',
                details=str(e),
                jenkins_url=self.jenkins_url,
            )
        
        if 'timeout' in error_msg:
            from jenkins_mcp_server.exceptions import JenkinsTimeoutError
            return JenkinsTimeoutError(
                f'{operation} failed: Operation timed out',
                details=str(e),
                jenkins_url=self.jenkins_url,
            )
        
        if 'connection' in error_msg:
            return JenkinsConnectionError(
                f'{operation} failed: Connection error',
                details=str(e),
                jenkins_url=self.jenkins_url,
            )
        
        # Default to generic operation error
        from jenkins_mcp_server.exceptions import JenkinsOperationError
        return JenkinsOperationError(
            f'{operation} failed',
            details=str(e),
            jenkins_url=self.jenkins_url,
        )
    
    def _normalize_job_name(self, job_name: str, folder_path: Optional[str] = None) -> str:
        """Normalize job name with folder path.
        
        Args:
            job_name: Job name
            folder_path: Optional folder path
            
        Returns:
            Normalized job name
        """
        if folder_path:
            return f'{folder_path.strip("/")}/{job_name}'
        return job_name
    
    def _extract_job_info(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and normalize job information from Jenkins API response.
        
        Args:
            job_data: Raw job data from Jenkins API
            
        Returns:
            Normalized job information
        """
        return {
            'name': job_data.get('name', ''),
            'url': job_data.get('url', ''),
            'full_name': job_data.get('fullName', job_data.get('name', '')),
            'display_name': job_data.get('displayName'),
            'description': job_data.get('description'),
            'buildable': job_data.get('buildable', True),
            'color': job_data.get('color'),
            'in_queue': job_data.get('inQueue', False),
            'disabled': job_data.get('disabled', False),
            'last_build': job_data.get('lastBuild'),
            'last_completed_build': job_data.get('lastCompletedBuild'),
            'last_successful_build': job_data.get('lastSuccessfulBuild'),
            'last_failed_build': job_data.get('lastFailedBuild'),
            'builds': job_data.get('builds', []),
            'health_report': job_data.get('healthReport', []),
        }
    
    def _determine_job_type(self, job_data: Dict[str, Any]) -> str:
        """Determine job type from Jenkins API data.
        
        Args:
            job_data: Job data from Jenkins API
            
        Returns:
            Job type string
        """
        class_name = job_data.get('_class', '').lower()
        
        if 'folder' in class_name:
            return 'folder'
        elif 'multibranch' in class_name:
            return 'multibranch_pipeline'
        elif 'pipeline' in class_name or 'workflow' in class_name:
            return 'pipeline'
        elif 'freestyle' in class_name:
            return 'freestyle'
        else:
            return 'unknown'
