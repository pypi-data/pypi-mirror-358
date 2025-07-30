"""Path utilities for Jenkins folder and job handling."""

import re
from typing import List, Optional
from urllib.parse import quote


def normalize_jenkins_path(path: str) -> str:
    """Normalize Jenkins folder/job path.
    
    Args:
        path: Raw path string
        
    Returns:
        Normalized path string
    """
    if not path:
        return ""
    
    # Remove leading/trailing slashes and spaces
    path = path.strip().strip('/')
    
    # Replace multiple slashes with single slash
    path = re.sub(r'/+', '/', path)
    
    return path


def jenkins_path_to_url_path(path: str) -> str:
    """Convert Jenkins folder path to URL path format.
    
    Args:
        path: Jenkins folder path (e.g., "folder1/folder2")
        
    Returns:
        URL path format (e.g., "job/folder1/job/folder2")
    """
    if not path:
        return ""
    
    normalized = normalize_jenkins_path(path)
    if not normalized:
        return ""
    
    # Split path and add 'job/' prefix to each segment
    segments = normalized.split('/')
    url_segments = []
    
    for segment in segments:
        if segment:  # Skip empty segments
            # URL encode the segment to handle special characters
            encoded_segment = quote(segment, safe='')
            url_segments.extend(['job', encoded_segment])
    
    return '/'.join(url_segments)


def url_path_to_jenkins_path(url_path: str) -> str:
    """Convert URL path format back to Jenkins folder path.
    
    Args:
        url_path: URL path format (e.g., "job/folder1/job/folder2")
        
    Returns:
        Jenkins folder path (e.g., "folder1/folder2")
    """
    if not url_path:
        return ""
    
    # Split by '/' and extract segments that come after 'job'
    segments = url_path.split('/')
    jenkins_segments = []
    
    i = 0
    while i < len(segments):
        if segments[i] == 'job' and i + 1 < len(segments):
            # Next segment is the actual folder/job name
            jenkins_segments.append(segments[i + 1])
            i += 2
        else:
            i += 1
    
    return '/'.join(jenkins_segments)


def validate_jenkins_path(path: str) -> bool:
    """Validate Jenkins folder/job path.
    
    Args:
        path: Path to validate
        
    Returns:
        True if path is valid, False otherwise
    """
    if not path:
        return True  # Empty path is valid (root)
    
    normalized = normalize_jenkins_path(path)
    
    # Check for invalid characters
    invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '\\']
    if any(char in normalized for char in invalid_chars):
        return False
    
    # Check for reserved names
    reserved_names = ['con', 'prn', 'aux', 'nul', 'com1', 'com2', 'com3', 'com4', 
                     'com5', 'com6', 'com7', 'com8', 'com9', 'lpt1', 'lpt2', 
                     'lpt3', 'lpt4', 'lpt5', 'lpt6', 'lpt7', 'lpt8', 'lpt9']
    
    segments = normalized.split('/')
    for segment in segments:
        if segment.lower() in reserved_names:
            return False
        
        # Check segment length (Jenkins has limits)
        if len(segment) > 255:
            return False
    
    return True


def get_parent_path(path: str) -> Optional[str]:
    """Get parent path of a Jenkins folder/job path.
    
    Args:
        path: Jenkins path
        
    Returns:
        Parent path or None if at root
    """
    if not path:
        return None
    
    normalized = normalize_jenkins_path(path)
    if '/' not in normalized:
        return None  # Already at root level
    
    return '/'.join(normalized.split('/')[:-1])


def get_path_segments(path: str) -> List[str]:
    """Get path segments from Jenkins path.
    
    Args:
        path: Jenkins path
        
    Returns:
        List of path segments
    """
    if not path:
        return []
    
    normalized = normalize_jenkins_path(path)
    return [segment for segment in normalized.split('/') if segment]


def join_jenkins_paths(*paths: str) -> str:
    """Join multiple Jenkins paths.
    
    Args:
        *paths: Path segments to join
        
    Returns:
        Joined path
    """
    segments = []
    
    for path in paths:
        if path:
            segments.extend(get_path_segments(path))
    
    return '/'.join(segments)


def is_nested_path(path: str, parent: str) -> bool:
    """Check if path is nested under parent path.
    
    Args:
        path: Path to check
        parent: Parent path
        
    Returns:
        True if path is nested under parent
    """
    if not parent:
        return True  # Everything is under root
    
    if not path:
        return False  # Root is not under any parent
    
    normalized_path = normalize_jenkins_path(path)
    normalized_parent = normalize_jenkins_path(parent)
    
    return normalized_path.startswith(normalized_parent + '/')
