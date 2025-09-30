# Claude Code Configuration

## Project Overview
**Name**: Elastic What's New Generator
**Purpose**: Drive Elastic sales and adoption by automating compelling presentation and Instruqt lab generation for quarterly Elastic feature releases
**Mission**: Showcase Elastic's competitive advantages and generate pipeline through sales-ready content
**Domains**: Elastic Search, Elastic Observability, Elastic Security, Unified Elastic Platform

## Development Approach
- **Elastic-First**: All content emphasizes Elastic's value proposition and competitive differentiation
- **Sales Enablement**: Generate content that drives Elastic pipeline and adoption
- **Test-Driven Development (TDD)**: Write tests first, then implement
- **Modular Architecture**: Separate concerns into focused Elastic-specific components
- **Configuration-Driven**: YAML/JSON configs for reusability across Elastic domains
- **AI-First**: Leverage Claude and Elastic MCP for Elastic content generation
- **Observable by Design**: Full OpenTelemetry instrumentation tracking Elastic content creation

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
- Elastic feature classification into compelling value themes (Simplify, Optimize, AI Innovation)
- Advanced storytelling positioning Elastic as the hero
- Elastic customer success stories with quantified ROI
- Enhanced UI for generating Elastic sales content
- Test feature filtering for production-ready Elastic content
- Full observability of Elastic content generation
- Multi-domain Elastic platform support (Search, Observability, Security, Unified)

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

## Debugging Protocol - CRITICAL
When the user reports a UI/layout/styling issue:

**STOP. DO NOT make incremental changes. Follow this protocol:**

1. **Gather Diagnostic Evidence FIRST** (before making ANY changes):
   - Ask user to open DevTools (F12)
   - Ask user to inspect the problematic element (right-click → Inspect)
   - Request a screenshot showing DevTools Elements panel with:
     - The highlighted element in the DOM tree
     - The Computed/Styles panel showing box model (margin, padding, width, height)
   - Ask: "Does the issue change when you resize the browser window?"

2. **Analyze Root Cause**:
   - Identify the ACTUAL element causing the issue (not assumptions)
   - Check parent-child relationships and how they fill/expand
   - Verify flex/grid layouts and their fill behavior
   - Look for: width, height, margin, padding, flex, position, display properties

3. **Make ONE Targeted Fix**:
   - Change only the specific property causing the issue
   - Add cache-busting parameter if touching CSS (e.g., `?v=timestamp`)
   - Explain what you're changing and WHY

4. **Verify the Fix**:
   - Ask user: "Did this specific change have ANY effect?"
   - If "no change" after 2 attempts, STOP and request DevTools screenshot
   - Do NOT make more than 2 changes without visual confirmation

**Anti-Patterns to AVOID:**
- ❌ Making 5+ incremental padding/margin adjustments without verification
- ❌ Assuming caching issues without evidence
- ❌ Changing multiple CSS properties at once without knowing which one matters
- ❌ Making changes based on assumptions instead of DevTools evidence
- ❌ Continuing down a path when user says "same" multiple times

**Remember:** One targeted fix based on evidence beats ten guesses.

## AI Tool Integration
- **Elastic MCP**: Elastic documentation lookup, Elastic feature validation
- **Web Search**: Competitive research showing Elastic differentiation
- **Claude**: Generate Elastic-focused content and storytelling
- **File System**: Manage Elastic presentation and lab templates

## Project Constraints - Elastic Focus
- Must work across Elastic Search, Elastic Observability, and Elastic Security domains individually
- Must support "Unified Elastic Platform" presentations showing cross-domain value
- Configurable for different Elastic audiences (business buyers, technical evaluators, developers)
- Generate both Elastic sales presentations and hands-on Elastic labs
- Integrate with Instruqt platform for Elastic training
- Maintain Elastic brand consistency and technical accuracy
- Full observability with OpenTelemetry → Elasticsearch for tracking Elastic content generation
- Cross-domain storytelling showcasing the power of the unified Elastic platform

## Testing Strategy
- Unit tests for all business logic
- Integration tests for Elasticsearch interactions
- Mock external APIs during testing
- Test data generation for realistic scenarios
- Validation tests for generated content quality

## Output Requirements - Elastic Content
- **Elastic Sales Presentations**: Markdown slides positioning Elastic's value with advanced storytelling
- **Elastic Talk Tracks**: Comprehensive speaker notes emphasizing Elastic's competitive advantages
- **Elastic Customer Stories**: Real-world Elastic success stories with quantified ROI and business impact
- **Elastic Hands-On Labs**: Instruqt lab instructions demonstrating Elastic capabilities with narrative flow
- **Elastic Sample Datasets**: Realistic data for hands-on Elastic exercises and ES|QL challenges
- **Flexible Configuration**: Easy customization for different Elastic audiences and use cases

## Recent Enhancements

### Lab Generation Framework (Latest - 2025-09-29)
- **Story-Driven Lab Architecture**: LLM-powered lab generation with realistic business scenarios
- **Multi-Table Datasets**: DatasetTable model with field definitions, relationships, and sample counts
- **Progressive Challenges**: LabChallenge model with hints, solutions, and expected outputs
- **Enhanced Data Models**: Extended LabInstruction with dataset_tables, setup_commands, challenges
- **Copy-Paste Ready Commands**: Generated setup commands work immediately in Kibana Dev Tools
- **Configurable Generation**: Scenario type, data size, technical depth parameters
- **Enhanced Markdown Export**: Updated instruqt_exporter to render new lab structure

### Storytelling Framework (Previous)
- **Story Arc Planning**: Multi-position narrative structure (Hook, Build, Climax, Resolution)
- **Talk Track Generation**: Comprehensive speaker notes with timing and transitions
- **Customer Story Integration**: Real-world success stories with quantified business impact
- **Business Value Calculation**: ROI projections and value drivers
- **Competitive Positioning**: Differentiation analysis and market positioning

### UI Improvements
- **Test Feature Filtering**: Automatic hiding of test features from production UI
- **Advanced Storytelling Controls**: Narrative style, talk track detail, technical depth
- **Lab Generation Controls**: Scenario type, data size, technical depth dropdowns
- **Enhanced Previews**: Story arc overview, talk track previews, customer story summaries
- **Cross-Tab Functionality**: Consistent filtering across Features, Presentations, and Labs tabs
- **Cache Management**: Improved JavaScript loading with version control

### Key Files Updated (Lab Generation)
- `config/llm_prompts.yaml`: Enhanced lab_generator prompts with multi-feature support
- `src/core/models.py`: Added DatasetTable, LabChallenge, extended LabInstruction (lines 357-415)
- `src/integrations/unified_llm_client.py`: Added generate_lab() method (lines 434-524)
- `src/api/main.py`: Updated /labs/markdown/single to use LLM generation (lines 1336-1410)
- `src/integrations/instruqt_exporter.py`: Enhanced _export_standard_markdown for new lab format (lines 614-688)
- `web/index.html`: Added lab scenario options (lines 267-312)
- `web/app.js`: Pass lab generation parameters to API (lines 1311-1325)
- `docs/architecture/llm-architecture.md`: Added Lab Generation Architecture section