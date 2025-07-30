"""Caching utilities for Jenkins MCP Server.

This module provides intelligent caching mechanisms to improve performance
and reduce load on Jenkins servers while maintaining data freshness.
"""

import asyncio
import time
from typing import Any, Callable, Dict, Optional, TypeVar, Union

from cachetools import TTLCache
from loguru import logger

T = TypeVar('T')


class CacheManager:
    """Intelligent cache manager for Jenkins data.
    
    Provides multiple cache tiers with different TTL values based on
    data volatility and access patterns.
    """
    
    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: int = 300,  # 5 minutes
        job_info_ttl: int = 60,   # 1 minute for job info
        build_info_ttl: int = 30,  # 30 seconds for build info
        server_info_ttl: int = 600,  # 10 minutes for server info
    ):
        """Initialize cache manager.
        
        Args:
            max_size: Maximum number of items in each cache
            default_ttl: Default TTL in seconds
            job_info_ttl: TTL for job information
            build_info_ttl: TTL for build information
            server_info_ttl: TTL for server information
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        
        # Different caches for different data types
        self.job_cache = TTLCache(maxsize=max_size, ttl=job_info_ttl)
        self.build_cache = TTLCache(maxsize=max_size, ttl=build_info_ttl)
        self.server_cache = TTLCache(maxsize=max_size, ttl=server_info_ttl)
        self.general_cache = TTLCache(maxsize=max_size, ttl=default_ttl)
        
        # Cache statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
        }
        
        # Lock for thread safety
        self._lock = asyncio.Lock()
    
    async def get(
        self,
        key: str,
        cache_type: str = 'general',
    ) -> Optional[Any]:
        """Get item from cache.
        
        Args:
            key: Cache key
            cache_type: Type of cache (job, build, server, general)
            
        Returns:
            Cached value or None if not found
        """
        async with self._lock:
            cache = self._get_cache(cache_type)
            
            if key in cache:
                self.stats['hits'] += 1
                logger.debug(f'Cache hit for key: {key}')
                return cache[key]
            else:
                self.stats['misses'] += 1
                logger.debug(f'Cache miss for key: {key}')
                return None
    
    async def set(
        self,
        key: str,
        value: Any,
        cache_type: str = 'general',
        ttl: Optional[int] = None,
    ) -> None:
        """Set item in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            cache_type: Type of cache (job, build, server, general)
            ttl: Optional custom TTL (not supported by TTLCache)
        """
        async with self._lock:
            cache = self._get_cache(cache_type)
            
            # Check if we're evicting an item
            if len(cache) >= cache.maxsize and key not in cache:
                self.stats['evictions'] += 1
            
            cache[key] = value
            logger.debug(f'Cached item with key: {key}')
    
    async def delete(
        self,
        key: str,
        cache_type: str = 'general',
    ) -> bool:
        """Delete item from cache.
        
        Args:
            key: Cache key
            cache_type: Type of cache
            
        Returns:
            True if item was deleted, False if not found
        """
        async with self._lock:
            cache = self._get_cache(cache_type)
            
            if key in cache:
                del cache[key]
                logger.debug(f'Deleted cache key: {key}')
                return True
            return False
    
    async def clear(self, cache_type: Optional[str] = None) -> None:
        """Clear cache(s).
        
        Args:
            cache_type: Specific cache to clear, or None for all caches
        """
        async with self._lock:
            if cache_type:
                cache = self._get_cache(cache_type)
                cache.clear()
                logger.info(f'Cleared {cache_type} cache')
            else:
                self.job_cache.clear()
                self.build_cache.clear()
                self.server_cache.clear()
                self.general_cache.clear()
                logger.info('Cleared all caches')
    
    def _get_cache(self, cache_type: str) -> TTLCache:
        """Get cache instance by type.
        
        Args:
            cache_type: Cache type
            
        Returns:
            Cache instance
        """
        cache_map = {
            'job': self.job_cache,
            'build': self.build_cache,
            'server': self.server_cache,
            'general': self.general_cache,
        }
        return cache_map.get(cache_type, self.general_cache)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = self.stats['hits'] / total_requests if total_requests > 0 else 0
        
        return {
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'evictions': self.stats['evictions'],
            'hit_rate': hit_rate,
            'cache_sizes': {
                'job': len(self.job_cache),
                'build': len(self.build_cache),
                'server': len(self.server_cache),
                'general': len(self.general_cache),
            },
        }


def cache_key(*args: Any, **kwargs: Any) -> str:
    """Generate cache key from arguments.
    
    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        Cache key string
    """
    key_parts = []
    
    # Add positional arguments
    for arg in args:
        if isinstance(arg, (str, int, float, bool)):
            key_parts.append(str(arg))
        else:
            key_parts.append(str(hash(str(arg))))
    
    # Add keyword arguments (sorted for consistency)
    for key, value in sorted(kwargs.items()):
        if isinstance(value, (str, int, float, bool)):
            key_parts.append(f'{key}={value}')
        else:
            key_parts.append(f'{key}={hash(str(value))}')
    
    return ':'.join(key_parts)


def cached(
    cache_manager: CacheManager,
    cache_type: str = 'general',
    key_func: Optional[Callable[..., str]] = None,
) -> Callable:
    """Decorator for caching function results.
    
    Args:
        cache_manager: Cache manager instance
        cache_type: Type of cache to use
        key_func: Optional function to generate cache key
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            # Generate cache key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = f'{func.__name__}:{cache_key(*args, **kwargs)}'
            
            # Try to get from cache
            cached_result = await cache_manager.get(key, cache_type)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_manager.set(key, result, cache_type)
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache_pattern(
    cache_manager: CacheManager,
    pattern: str,
    cache_type: str = 'general',
) -> int:
    """Invalidate cache entries matching a pattern.
    
    Args:
        cache_manager: Cache manager instance
        pattern: Pattern to match (simple string matching)
        cache_type: Type of cache
        
    Returns:
        Number of entries invalidated
    """
    cache = cache_manager._get_cache(cache_type)
    keys_to_delete = [key for key in cache.keys() if pattern in key]
    
    for key in keys_to_delete:
        del cache[key]
    
    logger.info(f'Invalidated {len(keys_to_delete)} cache entries matching pattern: {pattern}')
    return len(keys_to_delete)


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get global cache manager instance.
    
    Returns:
        Global cache manager instance
    """
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def initialize_cache_manager(**kwargs: Any) -> CacheManager:
    """Initialize global cache manager with custom settings.
    
    Args:
        **kwargs: Cache manager configuration
        
    Returns:
        Initialized cache manager
    """
    global _cache_manager
    _cache_manager = CacheManager(**kwargs)
    return _cache_manager
