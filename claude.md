# Claude Code Configuration

## Project Overview
**Name**: Elastic What's New Generator  
**Purpose**: Automated presentation and Instruqt lab generation for quarterly Elastic feature releases  
**Domains**: Search, Observability, Security, All Domains (unified)  

## Development Approach
- **Test-Driven Development (TDD)**: Write tests first, then implement
- **Modular Architecture**: Separate concerns into focused components
- **Configuration-Driven**: YAML/JSON configs for reusability across domains
- **AI-First**: Leverage Claude and Elastic MCP for content generation
- **Observable by Design**: Full OpenTelemetry instrumentation for self-monitoring

## Development Scope Constraints
**Current Phase**: MVP Development Only
**Future Enhancements**: Documented in docs/future-enhancements.md
**Do NOT implement**: Feedback loops, content governance, multi-modal generation until explicitly requested

## Current Sprint Focus
- Core feature classification and content generation
- Basic presentation and lab creation
- OpenTelemetry instrumentation
- Multi-domain support

## Code Preferences
```python
# Preferred patterns
- FastAPI for REST endpoints with OpenTelemetry middleware
- Pydantic for data validation
- pytest for testing
- asyncio for concurrent operations
- Type hints throughout
- Dataclasses/Pydantic models for data structures
- OpenTelemetry for logs, metrics, traces
- Structured logging with correlation IDs
```

## Observability Requirements
- **OpenTelemetry Integration**: Instrument all components
- **Telemetry Destination**: Send to Elastic cluster for self-monitoring
- **Trace Everything**: AI interactions, web scraping, content generation
- **Metrics Collection**: Performance, success rates, generation times
- **Structured Logging**: JSON format with correlation IDs
- **Error Tracking**: Detailed error context and stack traces

## Context Management
- Use specialized agents for different components
- Keep conversation focused on single tasks
- Reference existing files rather than re-explaining
- Use tools for external data access

## AI Tool Integration
- **Elastic MCP**: Documentation lookup, feature validation
- **Web Search**: Competitive research, additional context
- **Claude**: Content generation, storytelling
- **File System**: Template management, output generation

## Project Constraints
- Must work across Search/Observability/Security domains individually
- Must support "All Domains" unified presentations
- Configurable for different audiences (business/technical)
- Generate both presentations and hands-on labs
- Integrate with Instruqt platform
- Maintain brand consistency and technical accuracy
- Full observability with OpenTelemetry → Elastic
- Cross-domain storytelling and workshop scenarios

## Testing Strategy
- Unit tests for all business logic
- Integration tests for Elasticsearch interactions
- Mock external APIs during testing
- Test data generation for realistic scenarios
- Validation tests for generated content quality

## Output Requirements
- Markdown slides following presentation framework
- Instruqt lab instructions with step-by-step guidance
- Sample data sets for hands-on exercises
- Configuration files for easy customization