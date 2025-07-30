"""Build handler for Jenkins MCP Server - Community Edition.

This module handles Jenkins build-related operations for the community edition,
focusing on essential build operations: triggering builds and getting build status.
"""

import time
from typing import Any, Dict, Optional

from loguru import logger

from jenkins_mcp_server.handlers.base_handler import BaseHandler
from jenkins_mcp_server.models import BuildInfo, BuildResult, BuildTriggerResult
from jenkins_mcp_server.utils.validation import validate_job_name, validate_build_number, validate_build_parameters


class BuildHandler(BaseHandler):
    """Handler for Jenkins build operations - Community Edition.
    
    Provides essential build management functionality including:
    - Triggering builds with or without parameters
    - Getting build status and information
    """
    
    async def trigger_build(
        self,
        job_name: str,
        parameters: Optional[Dict[str, Any]] = None,
        wait_for_start: bool = False,
        timeout: int = 60,
    ) -> BuildTriggerResult:
        """Trigger a Jenkins build.
        
        Args:
            job_name: Name of the job to build
            parameters: Optional build parameters as key-value pairs
            wait_for_start: Whether to wait for build to start
            timeout: Timeout in seconds for waiting
            
        Returns:
            BuildTriggerResult with trigger status and information
            
        Raises:
            JenkinsError: If operation fails
        """
        try:
            job_name = validate_job_name(job_name)
            parameters = validate_build_parameters(parameters or {})
            
            # Trigger the build with CSRF protection
            if parameters:
                queue_item_id = await self._trigger_build_with_params(job_name, parameters)
            else:
                queue_item_id = await self._trigger_build_simple(job_name)
            
            # Check if build was triggered successfully
            triggered = queue_item_id is not None
            
            result = BuildTriggerResult(
                job_name=job_name,
                queue_item_id=queue_item_id,
                triggered=triggered,
                message=f'Build {"triggered successfully" if triggered else "failed to trigger"} for job {job_name}',
                parameters=parameters,
            )
            
            # Wait for build to start if requested
            if wait_for_start and queue_item_id:
                build_number = await self._wait_for_build_start(job_name, queue_item_id, timeout)
                if build_number:
                    result.build_number = build_number
                    result.build_url = f'{self.jenkins_url}/job/{job_name}/{build_number}/'
            
            return result
            
        except Exception as e:
            logger.error(f'Failed to trigger build: {e}')
            return BuildTriggerResult(
                job_name=job_name or 'unknown',  # Provide default for None
                triggered=False,
                message=f'Failed to trigger build: {str(e)}',
            )
    
    async def get_build_info(
        self,
        job_name: str,
        build_number: Optional[int] = None,
    ) -> BuildInfo:
        """Get Jenkins build information.
        
        Args:
            job_name: Name of the job
            build_number: Build number (latest if not specified)
            
        Returns:
            BuildInfo object with build details
            
        Raises:
            JenkinsError: If operation fails
        """
        try:
            job_name = validate_job_name(job_name)
            
            if build_number is not None:
                build_number = validate_build_number(build_number)
                cache_key = f'build_info:{job_name}:{build_number}'
            else:
                cache_key = f'build_info:{job_name}:latest'
            
            return await self.get_cached_or_fetch(
                cache_key=cache_key,
                fetch_func=self._fetch_build_info,
                cache_type='build',
                job_name=job_name,
                build_number=build_number,
            )
            
        except Exception as e:
            raise self._handle_jenkins_exception(e, f'Get build info for {job_name}')
    
    def _fetch_build_info(self, job_name: str, build_number: Optional[int] = None) -> BuildInfo:
        """Fetch build information from Jenkins API.
        
        Args:
            job_name: Name of the job
            build_number: Build number (latest if not specified)
            
        Returns:
            BuildInfo object with build details
            
        Raises:
            Exception: If build information cannot be retrieved
        """
        try:
            if build_number is None:
                # Get latest build
                job_info = self.jenkins_client.get_job_info(job_name)
                if not job_info.get('lastBuild'):
                    raise Exception(f'No builds found for job {job_name}')
                build_number = job_info['lastBuild']['number']
            
            build_info = self.jenkins_client.get_build_info(job_name, build_number)
            
            return BuildInfo(
                number=build_info['number'],
                url=build_info['url'],
                job_name=job_name,
                display_name=build_info.get('displayName'),
                description=build_info.get('description'),
                result=BuildResult(build_info['result']) if build_info.get('result') else None,
                building=build_info.get('building', False),
                duration=build_info.get('duration'),
                estimated_duration=build_info.get('estimatedDuration'),
                timestamp=build_info.get('timestamp'),
                built_on=build_info.get('builtOn'),
                change_set=build_info.get('changeSet', {}).get('items', []),
                culprits=build_info.get('culprits', []),
                artifacts=build_info.get('artifacts', []),
            )
            
        except Exception as e:
            logger.error(f'Failed to fetch build info: {e}')
            raise
    
    async def _trigger_build_simple(self, job_name: str) -> Optional[int]:
        """Trigger a simple build without parameters.
        
        Args:
            job_name: Name of the job to build
            
        Returns:
            Optional[int]: Queue item ID if successful, None otherwise
        """
        try:
            # Use Jenkins client's build_job method which returns queue item ID
            queue_item_id = await self.execute_with_retry(
                f'trigger_build_{job_name}',
                self.jenkins_client.build_job,
                job_name,
            )
            
            return queue_item_id
            
        except Exception as e:
            logger.error(f'Failed to trigger simple build: {e}')
            return None
    
    async def _trigger_build_with_params(self, job_name: str, parameters: Dict[str, Any]) -> Optional[int]:
        """Trigger a build with parameters.
        
        Args:
            job_name: Name of the job to build
            parameters: Build parameters as key-value pairs
            
        Returns:
            Optional[int]: Queue item ID if successful, None otherwise
        """
        try:
            # Use Jenkins client's build_job method which returns queue item ID
            queue_item_id = await self.execute_with_retry(
                f'trigger_build_{job_name}',
                self.jenkins_client.build_job,
                job_name,
                parameters,
            )
            
            return queue_item_id
            
        except Exception as e:
            logger.error(f'Failed to trigger parameterized build: {e}')
            return None
    
    async def _wait_for_build_start(self, job_name: str, queue_item_id: int, timeout: int) -> Optional[int]:
        """Wait for build to start and return build number.
        
        Args:
            job_name: Name of the job
            queue_item_id: Queue item ID from build trigger
            timeout: Timeout in seconds
            
        Returns:
            Optional[int]: Build number if build started, None otherwise
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                queue_item = self.jenkins_client.get_queue_item(queue_item_id)
                
                if queue_item.get('executable'):
                    return queue_item['executable']['number']
                
                if queue_item.get('cancelled'):
                    logger.warning(f'Build was cancelled for job {job_name}')
                    return None
                
                # Wait before checking again
                time.sleep(2)
                
            except Exception as e:
                logger.warning(f'Error checking queue item {queue_item_id}: {e}')
                time.sleep(2)
        
        logger.warning(f'Timeout waiting for build to start for job {job_name}')
        return None
