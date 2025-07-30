"""Data models for Jenkins MCP Server - Community Edition.

This module defines essential Pydantic models used throughout the Jenkins MCP server,
providing type safety and validation for core Jenkins resources and operations.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator, ConfigDict


class JobStatus(str, Enum):
    """Jenkins job status enumeration."""
    
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'
    UNSTABLE = 'UNSTABLE'
    ABORTED = 'ABORTED'
    NOT_BUILT = 'NOT_BUILT'
    RUNNING = 'RUNNING'
    QUEUED = 'QUEUED'
    UNKNOWN = 'UNKNOWN'


class JobType(str, Enum):
    """Jenkins job type enumeration."""
    
    FREESTYLE = 'freestyle'
    PIPELINE = 'pipeline'
    MULTIBRANCH_PIPELINE = 'multibranch_pipeline'
    FOLDER = 'folder'
    ORGANIZATION_FOLDER = 'organization_folder'
    UNKNOWN = 'unknown'


class BuildResult(str, Enum):
    """Jenkins build result enumeration."""
    
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'
    UNSTABLE = 'UNSTABLE'
    ABORTED = 'ABORTED'
    NOT_BUILT = 'NOT_BUILT'


class QueueItemState(str, Enum):
    """Jenkins queue item state enumeration."""
    
    WAITING = 'waiting'
    BLOCKED = 'blocked'
    BUILDABLE = 'buildable'
    PENDING = 'pending'
    LEFT = 'left'


class JobInfo(BaseModel):
    """Jenkins job information model.
    
    Represents comprehensive information about a Jenkins job,
    including metadata, configuration, and build history.
    """
    
    name: str = Field(description='Job name')
    url: str = Field(description='Job URL')
    full_name: str = Field(description='Full job name including folder path')
    display_name: Optional[str] = Field(None, description='Display name')
    description: Optional[str] = Field(None, description='Job description')
    job_type: JobType = Field(JobType.UNKNOWN, description='Job type')
    buildable: bool = Field(True, description='Whether job can be built')
    color: Optional[str] = Field(None, description='Job status color')
    in_queue: bool = Field(False, description='Whether job is in build queue')
    keep_dependencies: bool = Field(False, description='Whether to keep dependencies')
    next_build_number: int = Field(1, description='Next build number')
    concurrent_build: bool = Field(False, description='Whether concurrent builds allowed')
    disabled: bool = Field(False, description='Whether job is disabled')
    last_build: Optional[Dict[str, Any]] = Field(None, description='Last build information')
    last_completed_build: Optional[Dict[str, Any]] = Field(None, description='Last completed build')
    last_failed_build: Optional[Dict[str, Any]] = Field(None, description='Last failed build')
    last_stable_build: Optional[Dict[str, Any]] = Field(None, description='Last stable build')
    last_successful_build: Optional[Dict[str, Any]] = Field(None, description='Last successful build')
    last_unstable_build: Optional[Dict[str, Any]] = Field(None, description='Last unstable build')
    last_unsuccessful_build: Optional[Dict[str, Any]] = Field(None, description='Last unsuccessful build')
    builds: List[Dict[str, Any]] = Field(default_factory=list, description='Recent builds')
    health_report: List[Dict[str, Any]] = Field(default_factory=list, description='Health reports')
    parameters: List[Dict[str, Any]] = Field(default_factory=list, description='Job parameters')
    scm_info: Optional[Dict[str, Any]] = Field(None, description='SCM information')
    
    model_config = ConfigDict(use_enum_values=True)


class BuildInfo(BaseModel):
    """Jenkins build information model.
    
    Represents comprehensive information about a Jenkins build,
    including status, artifacts, and execution details.
    """
    
    number: int = Field(description='Build number')
    url: str = Field(description='Build URL')
    job_name: str = Field(description='Job name')
    display_name: Optional[str] = Field(None, description='Build display name')
    description: Optional[str] = Field(None, description='Build description')
    result: Optional[BuildResult] = Field(None, description='Build result')
    building: bool = Field(False, description='Whether build is currently running')
    duration: Optional[int] = Field(None, description='Build duration in milliseconds')
    estimated_duration: Optional[int] = Field(None, description='Estimated duration in milliseconds')
    timestamp: Optional[datetime] = Field(None, description='Build start timestamp')
    built_on: Optional[str] = Field(None, description='Node where build was executed')
    change_set: List[Dict[str, Any]] = Field(default_factory=list, description='SCM changes')
    culprits: List[Dict[str, Any]] = Field(default_factory=list, description='Build culprits')
    artifacts: List[Dict[str, Any]] = Field(default_factory=list, description='Build artifacts')
    test_report: Optional[Dict[str, Any]] = Field(None, description='Test results')
    console_output_url: Optional[str] = Field(None, description='Console output URL')
    parameters: List[Dict[str, Any]] = Field(default_factory=list, description='Build parameters')
    causes: List[Dict[str, Any]] = Field(default_factory=list, description='Build causes')
    
    model_config = ConfigDict(use_enum_values=True)


class QueueItemInfo(BaseModel):
    """Jenkins queue item information model.
    
    Represents information about an item in the Jenkins build queue.
    """
    
    id: int = Field(description='Queue item ID')
    task_name: str = Field(description='Task name')
    url: Optional[str] = Field(None, description='Queue item URL')
    why: Optional[str] = Field(None, description='Reason for queuing')
    blocked: bool = Field(False, description='Whether item is blocked')
    buildable: bool = Field(True, description='Whether item is buildable')
    stuck: bool = Field(False, description='Whether item is stuck')
    in_quiet_period: bool = Field(False, description='Whether in quiet period')
    pending: bool = Field(False, description='Whether item is pending')
    params: Optional[str] = Field(None, description='Build parameters')
    buildable_start_milliseconds: Optional[int] = Field(None, description='Buildable start time')
    waiting_start_milliseconds: Optional[int] = Field(None, description='Waiting start time')


class BuildTriggerResult(BaseModel):
    """Build trigger result model.
    
    Represents the result of triggering a Jenkins build.
    """
    
    job_name: str = Field(description='Job name')
    queue_item_id: Optional[int] = Field(None, description='Queue item ID')
    queue_item_url: Optional[str] = Field(None, description='Queue item URL')
    build_number: Optional[int] = Field(None, description='Build number if available')
    build_url: Optional[str] = Field(None, description='Build URL if available')
    triggered: bool = Field(description='Whether trigger was successful')
    message: str = Field(description='Result message')
    parameters: Dict[str, Any] = Field(default_factory=dict, description='Build parameters used')


# Response models for MCP tools
class ContentItem(BaseModel):
    """MCP content item model."""
    
    type: str = Field(description='Content type')
    text: str = Field(description='Content text')


class McpResponse(BaseModel):
    """MCP response model."""
    
    content: List[ContentItem] = Field(description='Response content')
    is_error: bool = Field(False, description='Whether response is an error')
    
    model_config = ConfigDict(
        alias_generator=lambda field_name: field_name.replace('_', ''),
        populate_by_name=True
    )
