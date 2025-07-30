"""Job handler for Jenkins MCP Server.

This module handles Jenkins job-related operations including listing,
creating, updating, and managing Jenkins jobs and folders.
"""

from typing import Any, Dict, List, Optional

from loguru import logger

from jenkins_mcp_server.exceptions import JenkinsOperationError, JenkinsValidationError
from jenkins_mcp_server.handlers.base_handler import BaseHandler
from jenkins_mcp_server.models import JobInfo, JobType
from jenkins_mcp_server.utils.validation import validate_job_name, validate_folder_path


class JobHandler(BaseHandler):
    """Handler for Jenkins job operations.
    
    Provides comprehensive job management functionality including
    listing, creating, updating, and deleting Jenkins jobs.
    """
    
    async def list_jobs(
        self,
        folder_path: Optional[str] = None,
        include_disabled: bool = True,
        recursive: bool = False,
        job_filter: Optional[str] = None,
    ) -> List[JobInfo]:
        """List Jenkins jobs with optional filtering.
        
        Args:
            folder_path: Optional folder path to list jobs from
            include_disabled: Whether to include disabled jobs
            recursive: Whether to recursively list jobs in subfolders
            job_filter: Optional job name filter pattern
            
        Returns:
            List[JobInfo]: List of JobInfo objects representing Jenkins jobs
            
        Raises:
            JenkinsError: If operation fails
        """
        try:
            # Validate folder path if provided
            if folder_path:
                folder_path = validate_folder_path(folder_path)
            
            cache_key = f'jobs:{folder_path or "root"}:{include_disabled}:{recursive}:{job_filter or "all"}'
            
            # Check cache first
            cached_data = await self.cache_manager.get(cache_key, 'job')
            if cached_data is not None:
                logger.debug(f'Cache hit for key: {cache_key}')
                return cached_data
            
            # Fetch data directly since _fetch_jobs is already async
            logger.debug(f'Cache miss for key: {cache_key}, fetching data')
            data = await self._fetch_jobs(
                folder_path=folder_path,
                include_disabled=include_disabled,
                recursive=recursive,
                job_filter=job_filter,
            )
            
            # Cache the result
            await self.cache_manager.set(cache_key, data, 'job')
            return data
            
        except Exception as e:
            raise self._handle_jenkins_exception(e, 'List jobs')
    
    async def _fetch_jobs(
        self,
        folder_path: Optional[str] = None,
        include_disabled: bool = True,
        recursive: bool = False,
        job_filter: Optional[str] = None,
    ) -> List[JobInfo]:
        """Fetch jobs from Jenkins API.
        
        Args:
            folder_path: Optional folder path to list jobs from
            include_disabled: Whether to include disabled jobs in results
            recursive: Whether to recursively list jobs in subfolders
            job_filter: Optional job name filter pattern
            
        Returns:
            List[JobInfo]: List of JobInfo objects representing Jenkins jobs
            
        Raises:
            JenkinsValidationError: If folder path is invalid
            JenkinsOperationError: If job fetching fails
        """
        try:
            if folder_path:
                # Handle folder-specific job listing
                from jenkins_mcp_server.utils.path_utils import (
                    normalize_jenkins_path, 
                    validate_jenkins_path
                )
                
                # Validate and normalize the folder path
                normalized_path = normalize_jenkins_path(folder_path)
                if not validate_jenkins_path(normalized_path):
                    raise JenkinsValidationError(f"Invalid folder path: {folder_path}")
                
                # Use Jenkins client to get folder jobs with proper async handling
                try:
                    folder_job = await self.execute_with_retry(
                        f'get_folder_job:{normalized_path}',
                        self.jenkins_client.get_job,
                        normalized_path
                    )
                    if hasattr(folder_job, 'get_jobs'):
                        jobs_data = await self.execute_with_retry(
                            f'get_folder_jobs:{normalized_path}',
                            folder_job.get_jobs
                        )
                    else:
                        # Fallback: get job info and extract jobs
                        folder_info = await self.execute_with_retry(
                            f'get_folder_info:{normalized_path}',
                            self.jenkins_client.get_job_info,
                            normalized_path
                        )
                        jobs_data = folder_info.get('jobs', [])
                except Exception as e:
                    logger.warning(f'Failed to get jobs from folder {folder_path}: {e}')
                    jobs_data = []
            else:
                # Get top-level jobs using execute_with_retry for proper async handling
                jobs_data = await self.execute_with_retry(
                    'fetch_root_jobs',
                    self.jenkins_client.get_jobs
                )
            
            jobs = []
            
            for job_data in jobs_data:
                # Skip disabled jobs if not requested
                if not include_disabled and job_data.get('color') == 'disabled':
                    continue
                
                # Apply job filter if provided
                if job_filter and job_filter.lower() not in job_data.get('name', '').lower():
                    continue
                
                job_info = self._create_job_info(job_data, folder_path)
                jobs.append(job_info)
                
                # Recursively get jobs from subfolders if requested
                if recursive and job_info.job_type == JobType.FOLDER:
                    subfolder_path = self._normalize_job_name(job_info.name, folder_path)
                    try:
                        subjobs = await self._fetch_jobs(
                            folder_path=subfolder_path,
                            include_disabled=include_disabled,
                            recursive=True,
                            job_filter=job_filter,
                        )
                        jobs.extend(subjobs)
                    except Exception as e:
                        logger.warning(f'Failed to get jobs from subfolder {subfolder_path}: {e}')
            
            logger.info(f'Found {len(jobs)} jobs in {folder_path or "root"}')
            return jobs
            
        except Exception as e:
            logger.error(f'Failed to fetch jobs: {e}')
            raise
    
    def _create_job_info(self, job_data: Dict[str, Any], folder_path: Optional[str] = None) -> JobInfo:
        """Create JobInfo object from Jenkins API data.
        
        Args:
            job_data: Raw job data from Jenkins API
            folder_path: Optional folder path
            
        Returns:
            JobInfo object
        """
        # Extract basic job information
        job_info_data = self._extract_job_info(job_data)
        
        # Determine job type
        job_type_str = self._determine_job_type(job_data)
        try:
            job_type = JobType(job_type_str)
        except ValueError:
            logger.warning(f'Unknown job type: {job_type_str}, using UNKNOWN')
            job_type = JobType.UNKNOWN
        
        # Create JobInfo object
        return JobInfo(
            name=job_info_data['name'],
            url=job_info_data['url'],
            full_name=job_info_data['full_name'],
            display_name=job_info_data['display_name'],
            description=job_info_data['description'],
            job_type=job_type,
            buildable=job_info_data['buildable'],
            color=job_info_data['color'],
            in_queue=job_info_data['in_queue'],
            disabled=job_info_data['disabled'],
            last_build=job_info_data['last_build'],
            last_completed_build=job_info_data['last_completed_build'],
            last_successful_build=job_info_data['last_successful_build'],
            last_failed_build=job_info_data['last_failed_build'],
            builds=job_info_data['builds'],
            health_report=job_info_data['health_report'],
        )
    
    async def get_job_details(
        self,
        job_name: str,
        include_builds: bool = True,
        build_limit: int = 10,
    ) -> JobInfo:
        """Get detailed information about a specific job.
        
        Args:
            job_name: Name of the job
            include_builds: Whether to include build information
            build_limit: Maximum number of builds to include
            
        Returns:
            Detailed JobInfo object
            
        Raises:
            JenkinsError: If operation fails
        """
        try:
            job_name = validate_job_name(job_name)
            
            cache_key = f'job_details:{job_name}:{include_builds}:{build_limit}'
            
            return await self.get_cached_or_fetch(
                cache_key=cache_key,
                fetch_func=self._fetch_job_details,
                cache_type='job',
                job_name=job_name,
                include_builds=include_builds,
                build_limit=build_limit,
            )
            
        except Exception as e:
            raise self._handle_jenkins_exception(e, f'Get job details for {job_name}')
    
    def _fetch_job_details(
        self,
        job_name: str,
        include_builds: bool = True,
        build_limit: int = 10,
    ) -> JobInfo:
        """Fetch detailed job information from Jenkins API.
        
        Args:
            job_name: Name of the job
            include_builds: Whether to include build information
            build_limit: Maximum number of builds to include
            
        Returns:
            JobInfo object with detailed information
        """
        try:
            # Get job information
            job_info = self.jenkins_client.get_job_info(job_name)
            
            # Get additional details if requested
            if include_builds and job_info.get('builds'):
                # Limit the number of builds
                builds = job_info['builds'][:build_limit]
                job_info['builds'] = builds
            
            # Extract job configuration for additional details
            try:
                job_config = self.jenkins_client.get_job_config(job_name)
                # Parse config for parameters, SCM info, etc.
                # This is a simplified version - full XML parsing would be more comprehensive
                job_info['has_parameters'] = '<parameterDefinitions>' in job_config
                job_info['scm_configured'] = '<scm class=' in job_config and 'NullSCM' not in job_config
            except Exception as e:
                logger.warning(f'Failed to get job config for {job_name}: {e}')
            
            return self._create_job_info(job_info)
            
        except Exception as e:
            logger.error(f'Failed to fetch job details for {job_name}: {e}')
            raise
    
    async def create_job(
        self,
        job_name: str,
        job_type: str = 'freestyle',
        description: Optional[str] = None,
        folder_path: Optional[str] = None,
        config_xml: Optional[str] = None,
        **kwargs,
    ) -> JobInfo:
        """Create a new Jenkins job.
        
        Args:
            job_name: Name for the new job
            job_type: Type of job (freestyle, pipeline, folder)
            description: Optional job description
            folder_path: Optional folder path to create job in
            config_xml: Optional custom configuration XML
            **kwargs: Additional job configuration parameters
            
        Returns:
            Created JobInfo object
            
        Raises:
            JenkinsError: If operation fails
        """
        try:
            job_name = validate_job_name(job_name)
            
            if folder_path:
                folder_path = validate_folder_path(folder_path)
                full_job_name = self._normalize_job_name(job_name, folder_path)
            else:
                full_job_name = job_name
            
            # Generate config XML if not provided
            if config_xml is None:
                config_xml = self._generate_job_config(job_type, description, **kwargs)
            
            # Create the job
            await self.execute_with_retry(
                f'create_job_{job_name}',
                self.jenkins_client.create_job,
                full_job_name,
                config_xml,
            )
            
            # Invalidate cache
            await self.cache_manager.delete(f'jobs:{folder_path or "root"}:*', 'job')
            
            # Get the created job details
            return await self.get_job_details(full_job_name)
            
        except Exception as e:
            raise self._handle_jenkins_exception(e, f'Create job {job_name}')
    
    def _generate_job_config(
        self,
        job_type: str,
        description: Optional[str] = None,
        **kwargs,
    ) -> str:
        """Generate job configuration XML.
        
        Args:
            job_type: Type of job
            description: Optional description
            **kwargs: Additional configuration parameters
            
        Returns:
            Job configuration XML
            
        Raises:
            JenkinsValidationError: If job type is unsupported
        """
        if job_type == 'freestyle':
            return self._generate_freestyle_config(description, **kwargs)
        elif job_type == 'pipeline':
            return self._generate_pipeline_config(description, **kwargs)
        elif job_type == 'folder':
            return self._generate_folder_config(description, **kwargs)
        else:
            raise JenkinsValidationError(f'Unsupported job type: {job_type}')
    
    def _generate_freestyle_config(self, description: Optional[str] = None, **kwargs) -> str:
        """Generate freestyle job configuration XML.
        
        Args:
            description: Optional job description
            **kwargs: Additional configuration parameters
            
        Returns:
            Freestyle job configuration XML
        """
        config = f'''<?xml version='1.1' encoding='UTF-8'?>
<project>
  <description>{description or ''}</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <scm class="hudson.scm.NullSCM"/>
  <canRoam>true</canRoam>
  <disabled>false</disabled>
  <blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
  <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
  <triggers/>
  <concurrentBuild>false</concurrentBuild>
  <builders/>
  <publishers/>
  <buildWrappers/>
</project>'''
        return config
    
    def _generate_pipeline_config(self, description: Optional[str] = None, **kwargs) -> str:
        """Generate pipeline job configuration XML.
        
        Args:
            description: Optional job description
            **kwargs: Additional configuration parameters
            
        Returns:
            Pipeline job configuration XML
        """
        script = kwargs.get('script', '''pipeline {
    agent any
    stages {
        stage('Hello') {
            steps {
                echo 'Hello World'
            }
        }
    }
}''')
        
        config = f'''<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job">
  <description>{description or ''}</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps">
    <script>{script}</script>
    <sandbox>true</sandbox>
  </definition>
  <triggers/>
  <disabled>false</disabled>
</flow-definition>'''
        return config
    
    def _generate_folder_config(self, description: Optional[str] = None, **kwargs) -> str:
        """Generate folder configuration XML.
        
        Args:
            description: Optional folder description
            **kwargs: Additional configuration parameters
            
        Returns:
            Folder configuration XML
        """
        config = f'''<?xml version='1.1' encoding='UTF-8'?>
<com.cloudbees.hudson.plugins.folder.Folder plugin="cloudbees-folder">
  <description>{description or ''}</description>
  <properties/>
  <folderViews class="com.cloudbees.hudson.plugins.folder.views.DefaultFolderViewHolder">
    <views>
      <hudson.model.AllView>
        <owner class="com.cloudbees.hudson.plugins.folder.Folder" reference="../../../.."/>
        <name>All</name>
        <filterExecutors>false</filterExecutors>
        <filterQueue>false</filterQueue>
        <properties class="hudson.model.View$PropertyList"/>
      </hudson.model.AllView>
    </views>
    <tabBar class="hudson.views.DefaultViewsTabBar"/>
  </folderViews>
  <healthMetrics/>
</com.cloudbees.hudson.plugins.folder.Folder>'''
        return config
    
    async def update_job(
        self,
        job_name: str,
        config_xml: str,
    ) -> JobInfo:
        """Update an existing Jenkins job.
        
        Args:
            job_name: Name of the job to update
            config_xml: New configuration XML
            
        Returns:
            Updated JobInfo object
            
        Raises:
            JenkinsError: If operation fails
        """
        try:
            job_name = validate_job_name(job_name)
            
            # Update the job
            await self.execute_with_retry(
                f'update_job_{job_name}',
                self.jenkins_client.reconfig_job,
                job_name,
                config_xml,
            )
            
            # Invalidate cache
            await self.cache_manager.delete(f'job_details:{job_name}:*', 'job')
            
            # Get updated job details
            return await self.get_job_details(job_name)
            
        except Exception as e:
            raise self._handle_jenkins_exception(e, f'Update job {job_name}')
    
    async def delete_job(self, job_name: str) -> bool:
        """Delete a Jenkins job.
        
        Args:
            job_name: Name of the job to delete
            
        Returns:
            True if job was deleted successfully
            
        Raises:
            JenkinsError: If operation fails
        """
        try:
            job_name = validate_job_name(job_name)
            
            # Delete the job
            await self.execute_with_retry(
                f'delete_job_{job_name}',
                self.jenkins_client.delete_job,
                job_name,
            )
            
            # Invalidate cache
            await self.cache_manager.delete(f'job_details:{job_name}:*', 'job')
            await self.cache_manager.delete('jobs:*', 'job')
            
            logger.info(f'Successfully deleted job: {job_name}')
            return True
            
        except Exception as e:
            raise self._handle_jenkins_exception(e, f'Delete job {job_name}')
    
    async def enable_job(self, job_name: str) -> JobInfo:
        """Enable a Jenkins job.
        
        Args:
            job_name: Name of the job to enable
            
        Returns:
            Updated JobInfo object
            
        Raises:
            JenkinsError: If operation fails
        """
        try:
            job_name = validate_job_name(job_name)
            
            # Enable the job
            await self.execute_with_retry(
                f'enable_job_{job_name}',
                self.jenkins_client.enable_job,
                job_name,
            )
            
            # Invalidate cache
            await self.cache_manager.delete(f'job_details:{job_name}:*', 'job')
            
            # Get updated job details
            return await self.get_job_details(job_name)
            
        except Exception as e:
            raise self._handle_jenkins_exception(e, f'Enable job {job_name}')
    
    async def disable_job(self, job_name: str) -> JobInfo:
        """Disable a Jenkins job.
        
        Args:
            job_name: Name of the job to disable
            
        Returns:
            Updated JobInfo object
            
        Raises:
            JenkinsError: If operation fails
        """
        try:
            job_name = validate_job_name(job_name)
            
            # Disable the job
            await self.execute_with_retry(
                f'disable_job_{job_name}',
                self.jenkins_client.disable_job,
                job_name,
            )
            
            # Invalidate cache
            await self.cache_manager.delete(f'job_details:{job_name}:*', 'job')
            
            # Get updated job details
            updated_job = await self.get_job_details(job_name)
            
            # Mark as disabled if the color indicates disabled state
            if hasattr(updated_job, 'color') and updated_job.color and 'disabled' in updated_job.color:
                updated_job.disabled = True
            
            return updated_job
            
        except Exception as e:
            raise self._handle_jenkins_exception(e, f'Disable job {job_name}')
