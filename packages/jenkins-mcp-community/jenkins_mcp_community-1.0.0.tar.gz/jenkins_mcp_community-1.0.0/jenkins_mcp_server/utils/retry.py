"""Retry utilities for Jenkins MCP Server.

This module provides intelligent retry mechanisms with exponential backoff
for handling transient failures when communicating with Jenkins servers.
"""

import asyncio
import random
from functools import wraps
from typing import Any, Callable, List, Optional, Type, TypeVar, Union

from loguru import logger
from tenacity import (
    AsyncRetrying,
    RetryError,
    before_sleep_log,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from jenkins_mcp_server.exceptions import (
    JenkinsConnectionError,
    JenkinsRateLimitError,
    JenkinsTimeoutError,
)

T = TypeVar('T')


def retry_with_backoff(
    max_attempts: int = 3,
    min_wait: float = 1.0,
    max_wait: float = 60.0,
    exponential_base: int = 2,
    jitter: bool = True,
    retry_on: Optional[Union[Type[Exception], List[Type[Exception]]]] = None,
) -> Callable:
    """Decorator for retrying functions with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        min_wait: Minimum wait time between retries in seconds
        max_wait: Maximum wait time between retries in seconds
        exponential_base: Base for exponential backoff
        jitter: Whether to add random jitter to wait times
        retry_on: Exception types to retry on
        
    Returns:
        Decorator function
    """
    if retry_on is None:
        retry_on = [
            JenkinsConnectionError,
            JenkinsTimeoutError,
            JenkinsRateLimitError,
        ]
    elif not isinstance(retry_on, list):
        retry_on = [retry_on]
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> T:
            retry_condition = retry_if_exception_type(tuple(retry_on))
            
            wait_strategy = wait_exponential(
                multiplier=min_wait,
                min=min_wait,
                max=max_wait,
                exp_base=exponential_base,
            )
            
            if jitter:
                # Add jitter to prevent thundering herd
                original_wait = wait_strategy
                
                def jittered_wait(retry_state):
                    wait_time = original_wait(retry_state)
                    jitter_amount = wait_time * 0.1 * random.random()
                    return wait_time + jitter_amount
                
                wait_strategy = jittered_wait
            
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(max_attempts),
                wait=wait_strategy,
                retry=retry_condition,
                before_sleep=before_sleep_log(logger, 'WARNING'),
                reraise=True,
            ):
                with attempt:
                    logger.debug(
                        f'Attempting {func.__name__} (attempt {attempt.retry_state.attempt_number})'
                    )
                    return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            # For synchronous functions, convert to async temporarily
            async def async_func():
                return func(*args, **kwargs)
            
            return asyncio.run(async_func())
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class RetryManager:
    """Advanced retry manager with circuit breaker pattern.
    
    Provides intelligent retry logic with circuit breaker functionality
    to prevent cascading failures and improve system resilience.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_failure_rate: float = 0.5,
    ):
        """Initialize retry manager.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Time to wait before attempting recovery
            expected_failure_rate: Expected failure rate threshold
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_failure_rate = expected_failure_rate
        
        # Circuit breaker state
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.circuit_open = False
        
        # Statistics
        self.total_attempts = 0
        self.successful_attempts = 0
        self.failed_attempts = 0
    
    async def execute_with_retry(
        self,
        func: Callable[..., T],
        *args: Any,
        max_attempts: int = 3,
        **kwargs: Any,
    ) -> T:
        """Execute function with retry and circuit breaker logic.
        
        Args:
            func: Function to execute
            *args: Function arguments
            max_attempts: Maximum retry attempts
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If all retry attempts fail or circuit is open
        """
        # Check circuit breaker
        if self.circuit_open:
            if asyncio.get_event_loop().time() - self.last_failure_time < self.recovery_timeout:
                raise Exception('Circuit breaker is open - too many recent failures')
            else:
                # Attempt to close circuit
                self.circuit_open = False
                self.failure_count = 0
                logger.info('Circuit breaker attempting recovery')
        
        last_exception = None
        
        for attempt in range(max_attempts):
            try:
                self.total_attempts += 1
                
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                # Success - reset failure count
                self.successful_attempts += 1
                self.failure_count = 0
                
                logger.debug(f'Function {func.__name__} succeeded on attempt {attempt + 1}')
                return result
                
            except Exception as e:
                last_exception = e
                self.failed_attempts += 1
                self.failure_count += 1
                self.last_failure_time = asyncio.get_event_loop().time()
                
                logger.warning(
                    f'Function {func.__name__} failed on attempt {attempt + 1}: {e}'
                )
                
                # Check if we should open circuit breaker
                if self.failure_count >= self.failure_threshold:
                    self.circuit_open = True
                    logger.error('Circuit breaker opened due to excessive failures')
                    break
                
                # Wait before retry (except on last attempt)
                if attempt < max_attempts - 1:
                    wait_time = min(2 ** attempt, 30)  # Exponential backoff, max 30s
                    await asyncio.sleep(wait_time)
        
        # All attempts failed
        if last_exception:
            raise last_exception
        else:
            raise Exception(f'Function {func.__name__} failed after {max_attempts} attempts')
    
    def get_stats(self) -> dict:
        """Get retry manager statistics.
        
        Returns:
            Dictionary with statistics
        """
        success_rate = (
            self.successful_attempts / self.total_attempts
            if self.total_attempts > 0 else 0
        )
        
        return {
            'total_attempts': self.total_attempts,
            'successful_attempts': self.successful_attempts,
            'failed_attempts': self.failed_attempts,
            'success_rate': success_rate,
            'failure_count': self.failure_count,
            'circuit_open': self.circuit_open,
            'last_failure_time': self.last_failure_time,
        }
    
    def reset(self) -> None:
        """Reset retry manager state."""
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.circuit_open = False
        self.total_attempts = 0
        self.successful_attempts = 0
        self.failed_attempts = 0
        logger.info('Retry manager state reset')


def should_retry_exception(exception: Exception) -> bool:
    """Determine if an exception should trigger a retry.
    
    Args:
        exception: Exception to evaluate
        
    Returns:
        True if exception should trigger retry, False otherwise
    """
    # Always retry on connection and timeout errors
    if isinstance(exception, (JenkinsConnectionError, JenkinsTimeoutError)):
        return True
    
    # Retry on rate limiting with backoff
    if isinstance(exception, JenkinsRateLimitError):
        return True
    
    # Don't retry on authentication/authorization errors
    from jenkins_mcp_server.exceptions import (
        JenkinsAuthenticationError,
        JenkinsAuthorizationError,
        JenkinsValidationError,
    )
    
    if isinstance(exception, (
        JenkinsAuthenticationError,
        JenkinsAuthorizationError,
        JenkinsValidationError,
    )):
        return False
    
    # For HTTP errors, retry on 5xx but not 4xx
    if hasattr(exception, 'response'):
        status_code = getattr(exception.response, 'status_code', None)
        if status_code:
            return 500 <= status_code < 600
    
    # Default to not retrying unknown exceptions
    return False


async def retry_with_circuit_breaker(
    func: Callable[..., T],
    *args: Any,
    max_attempts: int = 3,
    circuit_breaker: Optional[RetryManager] = None,
    **kwargs: Any,
) -> T:
    """Execute function with retry and circuit breaker.
    
    Args:
        func: Function to execute
        *args: Function arguments
        max_attempts: Maximum retry attempts
        circuit_breaker: Optional circuit breaker instance
        **kwargs: Function keyword arguments
        
    Returns:
        Function result
    """
    if circuit_breaker is None:
        circuit_breaker = RetryManager()
    
    return await circuit_breaker.execute_with_retry(
        func, *args, max_attempts=max_attempts, **kwargs
    )
