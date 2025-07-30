"""Jenkins MCP Server implementation - Community Edition.

This module implements the Jenkins MCP server using FastMCP,
providing essential Jenkins CI/CD integration for AI assistants.

The Community Edition provides core tools for Jenkins operations including:
- Job management (create, list, details)
- Build operations (trigger, status)

All operations follow MCP protocol standards and include comprehensive
error handling, caching, and retry logic for production reliability.
"""

import argparse
import os
from typing import Any, Dict, List, Optional

from loguru import logger
from mcp.server.fastmcp import FastMCP

from jenkins_mcp_server.models import ContentItem, McpResponse
from jenkins_mcp_server.utils.cache import initialize_cache_manager
from jenkins_mcp_server.utils.connection_pool import initialize_connection_pool
from jenkins_mcp_server.utils.logging_helper import setup_logging


# Server instructions for AI assistants
SERVER_INSTRUCTIONS = """
# Jenkins MCP Server - Community Edition

This MCP server provides essential tools for managing Jenkins CI/CD operations and is the preferred mechanism for basic Jenkins automation.

## IMPORTANT: Use MCP Tools for Jenkins Operations

DO NOT use Jenkins CLI commands or direct API calls. Always use the MCP tools provided by this server for Jenkins operations.

## Configuration

The server requires the following environment variables:
- JENKINS_URL: Jenkins server URL (required)
- JENKINS_USERNAME: Jenkins username (required)
- JENKINS_TOKEN: Jenkins API token (required)
- JENKINS_TIMEOUT: Request timeout in seconds (optional, default: 30)

## Usage Notes

- All operations are performed using the configured Jenkins credentials
- The server includes intelligent caching to improve performance
- Connection pooling is used for efficient resource utilization
- Comprehensive error handling with detailed error messages
- Automatic retry logic for transient failures

## Available Tools (Community Edition)

### Core Job and Build Management
1. List jobs: `list_jenkins_jobs(folder_path='optional/folder/path')`
2. Get job details: `get_job_details(job_name='my-job')`
3. Create job: `create_jenkins_job(job_name='my-job', job_type='freestyle')`
4. Trigger build: `trigger_jenkins_build(job_name='my-job', parameters={'key': 'value'})`
5. Monitor build: `get_build_status(job_name='my-job', build_number=123)`

## Best Practices

- Use descriptive job names
- Include meaningful descriptions for jobs
- Use parameters for flexible job execution
- Monitor build status for troubleshooting
- Organize jobs in folders for better management
- Use appropriate timeouts for long-running operations
- Leverage caching for frequently accessed data

## Error Handling

The server provides detailed error messages and automatic retry logic for:
- Connection timeouts and network issues
- Rate limiting and server overload
- Authentication and authorization problems
- Resource not found errors
- Invalid parameter validation

## Security

- All credentials are handled securely
- API tokens are preferred over passwords
- SSL/TLS verification is enforced by default
- Sensitive data is masked in logs
- Input validation prevents injection attacks
"""

SERVER_DEPENDENCIES = [
    'loguru',
    'mcp',
    'pydantic',
    'httpx',
    'python-jenkins',
    'jenkinsapi',
    'cachetools',
    'tenacity',
    'python-dotenv',
]


def create_server() -> FastMCP:
    """Create and configure the Jenkins MCP server instance.
    
    Returns:
        Configured FastMCP server instance
    """
    # Initialize server with instructions
    server = FastMCP(
        name='jenkins-mcp-server-community',
        instructions=SERVER_INSTRUCTIONS,
        dependencies=SERVER_DEPENDENCIES,
    )
    
    # Initialize handlers lazily - they will be created when first tool is called
    _handlers = None
    
    def get_handlers():
        nonlocal _handlers
        if _handlers is None:
            from jenkins_mcp_server.handlers.job_handler import JobHandler
            from jenkins_mcp_server.handlers.build_handler import BuildHandler
            
            _handlers = {
                'job': JobHandler(),
                'build': BuildHandler(),
            }
        return _handlers
    
    # Register job management tools
    @server.tool()
    async def list_jenkins_jobs(
        folder_path: Optional[str] = None,
        include_disabled: bool = True,
        recursive: bool = False,
    ) -> List[ContentItem]:
        """List Jenkins jobs with optional filtering.
        
        Args:
            folder_path: Optional folder path to list jobs from
            include_disabled: Whether to include disabled jobs
            recursive: Whether to recursively list jobs in subfolders
            
        Returns:
            List of job information
        """
        try:
            handlers = get_handlers()
            jobs = await handlers['job'].list_jobs(
                folder_path=folder_path,
                include_disabled=include_disabled,
                recursive=recursive,
            )
            
            return [ContentItem(
                type='text',
                text=f'Found {len(jobs)} jobs:\n' + '\n'.join([
                    f'- {job.name} ({job.job_type}) - {job.url}'
                    for job in jobs
                ])
            )]
            
        except Exception as e:
            logger.error(f'Failed to list jobs: {e}')
            return [ContentItem(
                type='text',
                text=f'Error listing jobs: {str(e)}'
            )]
    
    @server.tool()
    async def get_job_details(
        job_name: str,
        include_builds: bool = True,
        build_limit: int = 10,
    ) -> List[ContentItem]:
        """Get detailed information about a Jenkins job.
        
        Args:
            job_name: Name of the job
            include_builds: Whether to include recent build information
            build_limit: Maximum number of recent builds to include
            
        Returns:
            Detailed job information
        """
        try:
            from jenkins_mcp_server.utils.validation import validate_job_name
            job_name = validate_job_name(job_name)
            
            handlers = get_handlers()
            job_info = await handlers['job'].get_job_details(
                job_name=job_name,
                include_builds=include_builds,
                build_limit=build_limit,
            )
            
            content = [
                f'Job: {job_info.name}',
                f'Type: {job_info.job_type}',
                f'URL: {job_info.url}',
                f'Buildable: {job_info.buildable}',
                f'Disabled: {job_info.disabled}',
            ]
            
            if job_info.description:
                content.append(f'Description: {job_info.description}')
            
            if job_info.last_build:
                content.append(f'Last Build: #{job_info.last_build.get("number", "N/A")}')
            
            if include_builds and job_info.builds:
                content.append(f'\nRecent Builds ({len(job_info.builds)}):')
                for build in job_info.builds[:build_limit]:
                    content.append(f'  - #{build.get("number", "N/A")}: {build.get("url", "N/A")}')
            
            return [ContentItem(
                type='text',
                text='\n'.join(content)
            )]
            
        except Exception as e:
            logger.error(f'Failed to get job details: {e}')
            return [ContentItem(
                type='text',
                text=f'Error getting job details: {str(e)}'
            )]
    
    @server.tool()
    async def create_jenkins_job(
        job_name: str,
        job_type: str = 'freestyle',
        description: Optional[str] = None,
        folder_path: Optional[str] = None,
        config_xml: Optional[str] = None,
    ) -> List[ContentItem]:
        """Create a new Jenkins job.
        
        Args:
            job_name: Name for the new job
            job_type: Type of job (freestyle, pipeline, folder)
            description: Optional job description
            folder_path: Optional folder path to create job in
            config_xml: Optional custom configuration XML
            
        Returns:
            Job creation result
        """
        try:
            from jenkins_mcp_server.utils.validation import validate_job_name
            job_name = validate_job_name(job_name)
            
            handlers = get_handlers()
            result = await handlers['job'].create_job(
                job_name=job_name,
                job_type=job_type,
                description=description,
                folder_path=folder_path,
                config_xml=config_xml,
            )
            
            return [ContentItem(
                type='text',
                text=f'Successfully created job: {result.name}\nURL: {result.url}'
            )]
            
        except Exception as e:
            logger.error(f'Failed to create job: {e}')
            return [ContentItem(
                type='text',
                text=f'Error creating job: {str(e)}'
            )]
    
    # Register build management tools
    @server.tool()
    async def trigger_jenkins_build(
        job_name: str,
        parameters: Optional[Dict[str, Any]] = None,
        wait_for_start: bool = False,
        timeout: int = 60,
    ) -> List[ContentItem]:
        """Trigger a Jenkins build.
        
        Args:
            job_name: Name of the job to build
            parameters: Optional build parameters
            wait_for_start: Whether to wait for build to start
            timeout: Timeout in seconds for waiting
            
        Returns:
            Build trigger result
        """
        try:
            from jenkins_mcp_server.utils.validation import validate_job_name, validate_build_parameters
            job_name = validate_job_name(job_name)
            parameters = validate_build_parameters(parameters or {})
            
            handlers = get_handlers()
            result = await handlers['build'].trigger_build(
                job_name=job_name,
                parameters=parameters or {},
                wait_for_start=wait_for_start,
                timeout=timeout,
            )
            
            content = [
                f'Build triggered for job: {result.job_name}',
                f'Triggered: {result.triggered}',
                f'Message: {result.message}',
            ]
            
            if result.queue_item_id:
                content.append(f'Queue Item ID: {result.queue_item_id}')
            
            if result.build_number:
                content.append(f'Build Number: {result.build_number}')
                content.append(f'Build URL: {result.build_url}')
            
            return [ContentItem(
                type='text',
                text='\n'.join(content)
            )]
            
        except Exception as e:
            logger.error(f'Failed to trigger build: {e}')
            return [ContentItem(
                type='text',
                text=f'Error triggering build: {str(e)}'
            )]
    
    @server.tool()
    async def get_build_status(
        job_name: str,
        build_number: Optional[int] = None,
    ) -> List[ContentItem]:
        """Get Jenkins build status and information.
        
        Args:
            job_name: Name of the job
            build_number: Build number (latest if not specified)
            
        Returns:
            Build status information
        """
        try:
            from jenkins_mcp_server.utils.validation import validate_job_name
            job_name = validate_job_name(job_name)
            
            handlers = get_handlers()
            build_info = await handlers['build'].get_build_info(
                job_name=job_name,
                build_number=build_number,
            )
            
            content = [
                f'Build #{build_info.number} for {build_info.job_name}',
                f'Status: {build_info.result or "RUNNING" if build_info.building else "UNKNOWN"}',
                f'Building: {build_info.building}',
                f'URL: {build_info.url}',
            ]
            
            if build_info.duration:
                content.append(f'Duration: {build_info.duration / 1000:.1f} seconds')
            
            if build_info.timestamp:
                content.append(f'Started: {build_info.timestamp}')
            
            if build_info.built_on:
                content.append(f'Built on: {build_info.built_on}')
            
            if build_info.description:
                content.append(f'Description: {build_info.description}')
            
            return [ContentItem(
                type='text',
                text='\n'.join(content)
            )]
            
        except Exception as e:
            logger.error(f'Failed to get build status: {e}')
            return [ContentItem(
                type='text',
                text=f'Error getting build status: {str(e)}'
            )]
    
    return server
    
    
    return server


# Create the server instance - will be created when imported
app = None

def get_app():
    """Get the FastMCP app instance, creating it if necessary."""
    global app
    if app is None:
        app = create_server()
    return app


def main() -> None:
    """Main entry point for the Jenkins MCP server."""
    parser = argparse.ArgumentParser(description='Jenkins MCP Server')
    parser.add_argument(
        '--jenkins-url',
        help='Jenkins server URL (can also use JENKINS_URL env var)'
    )
    parser.add_argument(
        '--jenkins-username',
        help='Jenkins username (can also use JENKINS_USERNAME env var)'
    )
    parser.add_argument(
        '--jenkins-token',
        help='Jenkins API token (can also use JENKINS_TOKEN env var)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='Request timeout in seconds (default: 30)'
    )
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level (default: INFO)'
    )
    parser.add_argument(
        '--log-file',
        help='Optional log file path'
    )
    parser.add_argument(
        '--cache-size',
        type=int,
        default=1000,
        help='Cache size (default: 1000)'
    )
    parser.add_argument(
        '--max-connections',
        type=int,
        default=20,
        help='Maximum HTTP connections (default: 20)'
    )
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(
        level=args.log_level,
        log_file=args.log_file,
        include_caller=args.log_level == 'DEBUG',
    )
    
    # Set environment variables from command line args
    if args.jenkins_url:
        os.environ['JENKINS_URL'] = args.jenkins_url
    if args.jenkins_username:
        os.environ['JENKINS_USERNAME'] = args.jenkins_username
    if args.jenkins_token:
        os.environ['JENKINS_TOKEN'] = args.jenkins_token
    
    os.environ['JENKINS_TIMEOUT'] = str(args.timeout)
    
    # Validate required environment variables
    required_vars = ['JENKINS_URL', 'JENKINS_USERNAME', 'JENKINS_TOKEN']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f'Missing required environment variables: {", ".join(missing_vars)}')
        logger.error('Please set the following environment variables or use command line arguments:')
        logger.error('- JENKINS_URL: Jenkins server URL')
        logger.error('- JENKINS_USERNAME: Jenkins username')
        logger.error('- JENKINS_TOKEN: Jenkins API token')
        exit(1)
    
    # Initialize cache and connection pool
    initialize_cache_manager(max_size=args.cache_size)
    initialize_connection_pool(max_connections=args.max_connections)
    
    logger.info('Starting Jenkins MCP Server')
    logger.info(f'Jenkins URL: {os.getenv("JENKINS_URL")}')
    logger.info(f'Username: {os.getenv("JENKINS_USERNAME")}')
    logger.info(f'Timeout: {args.timeout}s')
    logger.info(f'Log Level: {args.log_level}')
    
    # Run the server
    app = get_app()
    app.run()


if __name__ == '__main__':
    main()
