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

## Architecture Documentation
- **Data Model**: See `docs/architecture/data-model.md` for Elasticsearch schema, ELSER embeddings, and content research structure
- **Content Research**: See `docs/architecture/content-research.md` for web scraping and AI enhancement workflow
- **Storytelling Framework**: Advanced narrative arcs, talk tracks, and customer story integration in `src/core/storytelling.py`
- **Customer Research**: Business impact and competitive positioning in `src/integrations/customer_story_research.py`

## Development Scope Constraints
**Current Phase**: Advanced Storytelling & UI Enhancement Implementation
**Future Enhancements**: Documented in docs/future-enhancements.md
**Do NOT implement**: Feedback loops, content governance, multi-modal generation until explicitly requested

## Current Sprint Focus
- Core feature classification and content generation
- Advanced storytelling framework with narrative arcs and talk tracks
- Customer story research and business impact integration
- Enhanced UI with comprehensive storytelling controls
- Test feature filtering and improved user experience
- OpenTelemetry instrumentation
- Multi-domain support

## Code Preferences
```python
# Preferred patterns
- FastAPI for REST endpoints
- Pydantic for data validation
- pytest for testing
- asyncio for concurrent operations
- Type hints throughout
- Dataclasses/Pydantic models for data structures
- Structured logging for debugging
```

## Quality Requirements
- **Error Handling**: Graceful degradation and detailed error messages
- **Testing**: Comprehensive unit and integration test coverage
- **Documentation**: Clear API documentation and usage examples
- **Performance**: Efficient content generation and storage operations

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
- Markdown slides following presentation framework with advanced storytelling
- Comprehensive talk tracks and speaker notes for presentations
- Customer success stories and business impact metrics
- Instruqt lab instructions with step-by-step guidance and narrative flow
- Sample data sets for hands-on exercises
- Configuration files for easy customization

## Recent Enhancements

### Storytelling Framework (Latest)
- **Story Arc Planning**: Multi-position narrative structure (Hook, Build, Climax, Resolution)
- **Talk Track Generation**: Comprehensive speaker notes with timing and transitions
- **Customer Story Integration**: Real-world success stories with quantified business impact
- **Business Value Calculation**: ROI projections and value drivers
- **Competitive Positioning**: Differentiation analysis and market positioning

### UI Improvements (Latest)
- **Test Feature Filtering**: Automatic hiding of test features from production UI
- **Advanced Storytelling Controls**: Narrative style, talk track detail, technical depth
- **Enhanced Previews**: Story arc overview, talk track previews, customer story summaries
- **Cross-Tab Functionality**: Consistent filtering across Features, Presentations, and Labs tabs
- **Cache Management**: Improved JavaScript loading with version control

### Key Files Updated
- `web/index.html`: Added comprehensive storytelling form controls (lines 157-203)
- `web/app.js`: Enhanced presentation/lab generation with storytelling parameters
- `src/core/storytelling.py`: Complete storytelling framework implementation
- `src/integrations/customer_story_research.py`: Customer story and business impact research
- `src/core/models.py`: Extended data models for storytelling components