"""Connection pooling utilities for Jenkins MCP Server.

This module provides connection pooling and management for Jenkins API clients
to improve performance and resource utilization.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, Optional

import httpx
from loguru import logger

from jenkins_mcp_server.exceptions import JenkinsConnectionError


class ConnectionPool:
    """Connection pool manager for Jenkins API clients.
    
    Manages HTTP connections to Jenkins servers with connection pooling,
    timeout handling, and automatic retry logic.
    """
    
    def __init__(
        self,
        max_connections: int = 20,
        max_keepalive_connections: int = 5,
        keepalive_expiry: float = 30.0,
        timeout: float = 30.0,
        verify_ssl: bool = True,
    ):
        """Initialize connection pool.
        
        Args:
            max_connections: Maximum number of connections
            max_keepalive_connections: Maximum keepalive connections
            keepalive_expiry: Keepalive expiry time in seconds
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
        """
        self.max_connections = max_connections
        self.max_keepalive_connections = max_keepalive_connections
        self.keepalive_expiry = keepalive_expiry
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        
        # Connection pools by Jenkins URL
        self._pools: Dict[str, httpx.AsyncClient] = {}
        self._pool_lock = asyncio.Lock()
        
        # Connection statistics
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'connection_errors': 0,
            'timeout_errors': 0,
        }
    
    async def get_client(
        self,
        jenkins_url: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.AsyncClient:
        """Get HTTP client for Jenkins URL.
        
        Args:
            jenkins_url: Jenkins server URL
            username: Optional username for authentication
            password: Optional password for authentication
            headers: Optional additional headers
            
        Returns:
            HTTP client instance
        """
        async with self._pool_lock:
            if jenkins_url not in self._pools:
                # Create new client
                auth = None
                if username and password:
                    auth = httpx.BasicAuth(username, password)
                
                client_headers = {
                    'User-Agent': 'Jenkins-MCP-Server/1.0.0',
                    'Accept': 'application/json',
                }
                if headers:
                    client_headers.update(headers)
                
                limits = httpx.Limits(
                    max_connections=self.max_connections,
                    max_keepalive_connections=self.max_keepalive_connections,
                    keepalive_expiry=self.keepalive_expiry,
                )
                
                timeout = httpx.Timeout(self.timeout)
                
                client = httpx.AsyncClient(
                    auth=auth,
                    headers=client_headers,
                    limits=limits,
                    timeout=timeout,
                    verify=self.verify_ssl,
                    follow_redirects=True,
                )
                
                self._pools[jenkins_url] = client
                logger.debug(f'Created new HTTP client for {jenkins_url}')
            
            return self._pools[jenkins_url]
    
    @asynccontextmanager
    async def request(
        self,
        method: str,
        url: str,
        jenkins_url: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> AsyncGenerator[httpx.Response, None]:
        """Make HTTP request with connection pooling.
        
        Args:
            method: HTTP method
            url: Request URL
            jenkins_url: Jenkins server base URL
            username: Optional username
            password: Optional password
            headers: Optional headers
            **kwargs: Additional request arguments
            
        Yields:
            HTTP response
            
        Raises:
            JenkinsConnectionError: If request fails
        """
        client = await self.get_client(jenkins_url, username, password, headers)
        
        try:
            self.stats['total_requests'] += 1
            
            async with client.stream(method, url, **kwargs) as response:
                self.stats['successful_requests'] += 1
                logger.debug(f'{method} {url} -> {response.status_code}')
                yield response
                
        except httpx.TimeoutException as e:
            self.stats['timeout_errors'] += 1
            self.stats['failed_requests'] += 1
            logger.error(f'Request timeout: {method} {url}')
            raise JenkinsConnectionError(
                f'Request timeout: {method} {url}',
                details=str(e),
                jenkins_url=jenkins_url,
            )
        except httpx.ConnectError as e:
            self.stats['connection_errors'] += 1
            self.stats['failed_requests'] += 1
            logger.error(f'Connection error: {method} {url}')
            raise JenkinsConnectionError(
                f'Connection error: {method} {url}',
                details=str(e),
                jenkins_url=jenkins_url,
            )
        except Exception as e:
            self.stats['failed_requests'] += 1
            logger.error(f'Request failed: {method} {url} - {e}')
            raise JenkinsConnectionError(
                f'Request failed: {method} {url}',
                details=str(e),
                jenkins_url=jenkins_url,
            )
    
    async def close_all(self) -> None:
        """Close all connection pools."""
        async with self._pool_lock:
            for jenkins_url, client in self._pools.items():
                await client.aclose()
                logger.debug(f'Closed HTTP client for {jenkins_url}')
            
            self._pools.clear()
            logger.info('Closed all HTTP connection pools')
    
    async def close_pool(self, jenkins_url: str) -> bool:
        """Close connection pool for specific Jenkins URL.
        
        Args:
            jenkins_url: Jenkins server URL
            
        Returns:
            True if pool was closed, False if not found
        """
        async with self._pool_lock:
            if jenkins_url in self._pools:
                client = self._pools.pop(jenkins_url)
                await client.aclose()
                logger.debug(f'Closed HTTP client for {jenkins_url}')
                return True
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics.
        
        Returns:
            Dictionary with statistics
        """
        success_rate = (
            self.stats['successful_requests'] / self.stats['total_requests']
            if self.stats['total_requests'] > 0 else 0
        )
        
        return {
            'total_requests': self.stats['total_requests'],
            'successful_requests': self.stats['successful_requests'],
            'failed_requests': self.stats['failed_requests'],
            'connection_errors': self.stats['connection_errors'],
            'timeout_errors': self.stats['timeout_errors'],
            'success_rate': success_rate,
            'active_pools': len(self._pools),
            'pool_urls': list(self._pools.keys()),
        }
    
    async def health_check(self, jenkins_url: str) -> bool:
        """Perform health check on Jenkins server.
        
        Args:
            jenkins_url: Jenkins server URL
            
        Returns:
            True if server is healthy, False otherwise
        """
        try:
            health_url = f'{jenkins_url.rstrip("/")}/api/json'
            
            async with self.request('GET', health_url, jenkins_url) as response:
                return response.status_code == 200
                
        except Exception as e:
            logger.warning(f'Health check failed for {jenkins_url}: {e}')
            return False


# Global connection pool instance
_connection_pool: Optional[ConnectionPool] = None


def get_connection_pool() -> ConnectionPool:
    """Get global connection pool instance.
    
    Returns:
        Global connection pool instance
    """
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = ConnectionPool()
    return _connection_pool


def initialize_connection_pool(**kwargs: Any) -> ConnectionPool:
    """Initialize global connection pool with custom settings.
    
    Args:
        **kwargs: Connection pool configuration
        
    Returns:
        Initialized connection pool
    """
    global _connection_pool
    _connection_pool = ConnectionPool(**kwargs)
    return _connection_pool


async def cleanup_connection_pool() -> None:
    """Clean up global connection pool."""
    global _connection_pool
    if _connection_pool:
        await _connection_pool.close_all()
        _connection_pool = None
