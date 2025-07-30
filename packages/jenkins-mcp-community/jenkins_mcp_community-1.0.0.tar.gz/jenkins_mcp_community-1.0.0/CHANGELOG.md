# Changelog

All notable changes to the Jenkins MCP Server Community Edition will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-06-30

### Added
- **Community Edition Release**: Open-source version with essential Jenkins integration
- **Core Tools**: 5 essential MCP tools for Jenkins operations
  - `list_jenkins_jobs`: List and filter Jenkins jobs with folder support
  - `get_job_details`: Get detailed job information and build history
  - `create_jenkins_job`: Create freestyle, pipeline, and folder jobs
  - `trigger_jenkins_build`: Trigger builds with or without parameters
  - `get_build_status`: Get build status and information
- **Essential Infrastructure**:
  - FastMCP-based server implementation
  - Pydantic models for type safety
  - Comprehensive error handling and logging
  - Intelligent caching system
  - HTTP connection pooling
  - Retry logic with exponential backoff
  - Input validation and sanitization
- **Authentication**: Secure Jenkins API token authentication
- **Documentation**: Complete README with setup and usage instructions
- **Testing**: Unit and integration test framework
- **Docker Support**: Containerized deployment option

### Changed
- **License**: Changed from proprietary to MIT license for open-source distribution
- **Focus**: Streamlined to essential Jenkins operations for community use
- **Dependencies**: Optimized dependency list for core functionality

### Removed
- Advanced pipeline management features
- System analysis and health monitoring
- Build analytics and performance optimization
- Log streaming and advanced build operations
- Server information and queue monitoring tools

### Technical Details
- **Python**: Requires Python 3.10+
- **Jenkins**: Compatible with Jenkins 2.400+
- **MCP Protocol**: Full Model Context Protocol compliance
- **Architecture**: Modular handler-based design
- **Performance**: Optimized for essential operations

### Migration Notes
- This community edition focuses on the 5 most essential Jenkins operations
- Users requiring advanced features should consider the full enterprise version
- All core functionality remains fully compatible with existing MCP clients
- Configuration and authentication methods remain unchanged

---

**Note**: This community edition represents a focused, open-source version of the Jenkins MCP Server, designed to provide essential Jenkins integration capabilities for AI assistants while maintaining high code quality and reliability standards.
