# LLM Architecture

## Overview

The Elastic What's New Generator uses a **two-stage LLM architecture** to efficiently generate high-quality presentations and labs from feature documentation.

## Architecture Principles

1. **Cache-First**: Extract once, generate many times
2. **Provider-Agnostic**: Support multiple LLM providers with automatic fallback
3. **Cost-Efficient**: Minimize LLM API calls through intelligent caching
4. **Customizable**: User-configurable prompts for different presentation styles
5. **Observable**: Full instrumentation and error tracking

## Two-Stage Architecture

### Stage 1: Content Extraction and Caching

```
┌─────────────────┐
│ Feature Created │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Scrape Docs     │  ← Web scraping from elastic.co
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ LLM Extraction  │  ← OpenAI/Gemini/Claude
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Cache in ES     │  ← Elasticsearch storage
└─────────────────┘

Result: LLMExtractedContent cached in Elasticsearch
```

**Purpose:**
- Extract structured information from scraped documentation
- Cache extractions to avoid repeated LLM calls
- Normalize data format across different documentation sources

**Output:**
```json
{
  "llm_extracted": {
    "summary": "2-3 sentence feature summary",
    "use_cases": ["Use case 1", "Use case 2"],
    "key_capabilities": ["Cap 1", "Cap 2"],
    "benefits": ["Benefit 1", "Benefit 2"],
    "technical_requirements": ["Req 1", "Req 2"],
    "target_audience": "developers|devops|security-analysts",
    "complexity_level": "beginner|intermediate|advanced",
    "model_used": "openai/gpt-4o"
  }
}
```

### Stage 2: Presentation and Lab Generation

```
┌──────────────────┐
│ User Requests    │
│ Presentation     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Load Cached      │  ← Read from Elasticsearch
│ Extractions      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ LLM Generate     │  ← OpenAI/Gemini/Claude
│ Presentation     │     with customizable prompts
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 7-Slide          │  ← Structured presentation
│ Presentation     │     with talk tracks
└──────────────────┘
```

**Purpose:**
- Generate cohesive presentations from multiple cached feature extractions
- Apply Elastic's storytelling framework (3 themes, 7-slide structure)
- Create comprehensive talk tracks for each slide
- Support different audiences and narrative styles

**Output:**
```json
{
  "title": "Q1-2025 Observability Innovations",
  "slides": [
    {
      "title": "Opening Hook",
      "content": "Slide content in markdown",
      "business_value": "Value proposition",
      "theme": "simplify|optimize|ai_innovation",
      "speaker_notes": "3-5 paragraph talk track"
    }
  ],
  "story_arc": {
    "opening_hook": "Infrastructure challenge",
    "central_theme": "Unifying theme",
    "resolution_message": "How innovations solve challenge",
    "call_to_action": "Next steps"
  }
}
```

## Multi-Provider LLM Support

### Unified LLM Client

**Architecture:**
```python
class UnifiedLLMClient:
    """Single interface for multiple LLM providers"""

    def __init__(
        self,
        provider: Optional[LLMProvider] = None,  # Auto-select if None
        openai_api_key: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        model: Optional[str] = None,  # Provider-specific models
        openai_base_url: Optional[str] = None  # Proxy support
    ):
        # Auto-select: OpenAI > Gemini > Claude
        self.provider = provider or self._auto_select_provider()
```

### Provider Configuration

**Environment Variables:**
```bash
# OpenAI Configuration (Recommended)
OPENAI_API_KEY=sk-your-key-here
OPENAI_BASE_URL=https://your-proxy-url  # Optional proxy
LLM_MODEL=gpt-4o  # Override default model

# Google Gemini Configuration (Alternative)
GEMINI_API_KEY=your-gemini-key
LLM_MODEL=gemini-1.5-flash

# Anthropic Claude Configuration (Alternative)
ANTHROPIC_API_KEY=your-claude-key
LLM_MODEL=claude-3-sonnet-20240229
```

**Auto-Selection Priority:**
1. OpenAI (if `OPENAI_API_KEY` is set)
2. Gemini (if `GEMINI_API_KEY` is set)
3. Claude (if `ANTHROPIC_API_KEY` is set)

**Default Models:**
- OpenAI: `gpt-4o-mini` (cost-effective)
- Gemini: `gemini-1.5-flash` (fast and cheap)
- Claude: `claude-3-sonnet-20240229` (high quality)

### Proxy Support

**Use Case:** Claude Code Max, custom API gateways, rate limiting proxies

**Configuration:**
```bash
OPENAI_API_KEY=your-proxy-api-key
OPENAI_BASE_URL=https://litellm-proxy-service.example.com
```

**Note:** Do NOT include `/chat/completions` in the base URL - the client adds it automatically.

## Customizable Prompts

### Configuration File

**Location:** `config/llm_prompts.yaml`

**Structure:**
```yaml
presentation_generator:
  system_prompt: |
    Instructions for LLM on how to generate presentations
    Variables: {slide_count}, {audience}, {narrative_style}, {technical_depth}

  user_prompt: |
    Specific request with feature information
    Variables: {domain}, {feature_contexts}

content_extractor:
  system_prompt: |
    Instructions for extracting structured content

  user_prompt: |
    Specific extraction request
    Variables: {feature_name}, {documentation_url}, {scraped_content}

lab_generator:
  system_prompt: |
    Instructions for creating hands-on labs

  user_prompt: |
    Lab generation request
    Variables: {feature_name}, {feature_info}, {format_type}
```

### Customization Examples

**Business-Focused Presentations:**
```yaml
presentation_generator:
  system_prompt: |
    Create executive-level presentations.
    Focus on ROI, business outcomes, and competitive advantages.
    Minimize technical jargon.
    Emphasize cost savings and efficiency gains.
```

**Deep Technical Presentations:**
```yaml
presentation_generator:
  system_prompt: |
    Create detailed technical presentations.
    Include architecture diagrams and code examples.
    Focus on implementation details and best practices.
    Assume advanced technical audience.
```

**5-Slide Structure (vs. default 7-slide):**
```yaml
presentation_generator:
  system_prompt: |
    REQUIRED PRESENTATION FLOW (5 slides):
    1. Opening Hook
    2. Solution Overview
    3. Technical Deep Dive (combined themes)
    4. Business Case
    5. Call to Action
```

### Reloading Configuration

Changes to `config/llm_prompts.yaml` require restarting the server:

```bash
# Stop the server (Ctrl+C or)
pkill -f "uvicorn"

# Restart
./run.sh
```

Prompts are cached on first load for performance.

## Required Presentation Structure

### 7-Slide Framework

The system enforces Elastic's required presentation structure:

1. **Opening Hook** - Infrastructure/operational challenge
2. **Innovation Overview** - Preview of three game-changing themes
3. **Simplify Theme** - "Do more with less" features
4. **Optimize Theme** - "Do it faster" features
5. **AI Innovation Theme** - "Do it with AI" features
6. **Business Case/ROI** - Quantified benefits and competitive advantages
7. **Call to Action** - Clear next steps (demo, trial, contact)

### Three Universal Themes

All features must be classified into one of three themes:

- **Simplify**: Reduce complexity, automate operations, ease of use
- **Optimize**: Performance improvements, efficiency gains, cost reduction
- **AI Innovation**: AI/ML capabilities, intelligent features, GenAI integration

### Talk Tracks

Each slide includes comprehensive speaker notes (3-5 paragraphs) covering:
- What to say during the slide
- Key points to emphasize
- Transition to next slide
- Timing guidance
- Audience engagement tips

## Error Handling

### LLM Provider Failures

**Automatic Fallback:**
```python
# If OpenAI fails, automatically tries Gemini, then Claude
llm_client = UnifiedLLMClient()  # Auto-selects available provider
```

**Retry Logic:**
- Exponential backoff for transient failures
- 3 retry attempts by default
- Detailed error logging

**Graceful Degradation:**
- If all LLM providers fail, return cached content
- Generate basic presentations from feature metadata
- Log warnings for manual review

### Prompt Validation

**JSON Output Validation:**
```python
def _parse_json_response(response_text: str) -> Dict[str, Any]:
    """Parse and validate LLM JSON response"""
    # Remove markdown code blocks
    # Validate JSON structure
    # Check required fields
    # Raise detailed errors
```

**Fallback to Defaults:**
- If custom prompts fail, use built-in defaults
- Log warnings about configuration issues
- Continue with degraded functionality

## Performance Optimization

### Caching Strategy

**LLM Extractions:**
- Cached in Elasticsearch indefinitely
- Invalidated only on explicit research refresh
- Reduces LLM API calls by 90%+

**Prompt Configuration:**
- Loaded once on startup
- Cached in memory
- Minimal reload overhead

### Token Optimization

**Extraction Phase:**
- Truncate scraped content to ~8000 tokens
- Focus on main content sections
- Remove boilerplate and navigation

**Generation Phase:**
- Send only essential extracted data
- Limit to 3-5 use cases, 4-5 capabilities
- Structured format reduces token count

### Concurrent Processing

**Multiple Features:**
```python
# Parallel content extraction
extraction_tasks = [
    extract_content(feature, llm_client)
    for feature in features
]
results = await asyncio.gather(*extraction_tasks)
```

## Monitoring and Observability

### Key Metrics

**LLM Usage:**
- API calls per provider
- Token consumption
- Response times
- Error rates

**Content Quality:**
- Extraction completeness
- Presentation generation success
- User satisfaction ratings

**Cost Tracking:**
- API costs by provider
- Cost per feature extraction
- Cost per presentation generated

### Logging

**LLM Interactions:**
```python
logger.info(f"Using LLM provider: {provider}")
logger.info(f"Extracting content for: {feature_name}")
logger.info(f"Generated {len(slides)} slides")
logger.error(f"LLM extraction failed: {error}")
```

**Configuration:**
```python
logger.info(f"Loaded LLM prompts from {config_path}")
logger.warning(f"Using default prompts - config not found")
```

## Best Practices

### API Key Management

✅ **DO:**
- Use environment variables for API keys
- Use separate keys for dev/staging/prod
- Rotate keys regularly
- Monitor usage and set limits

❌ **DON'T:**
- Commit API keys to git
- Share keys across teams
- Use personal keys in production
- Hardcode keys in configuration

### Prompt Engineering

✅ **DO:**
- Test prompts with multiple features
- Version control prompt changes
- Document why prompts work
- Start with small changes

❌ **DON'T:**
- Make multiple changes at once
- Remove required JSON fields
- Test only in production
- Ignore error messages

### Cost Management

✅ **DO:**
- Use gpt-4o-mini for development
- Cache aggressively
- Monitor token usage
- Set API usage alerts

❌ **DON'T:**
- Re-extract unnecessarily
- Use expensive models by default
- Ignore cost metrics
- Process test data in production

## Troubleshooting

### Common Issues

**"No LLM provider available"**
- Ensure at least one API key is set
- Check environment variables
- Verify key format

**"Prompts config not found"**
- Check file location: `config/llm_prompts.yaml`
- Verify YAML syntax
- Falls back to defaults automatically

**"Invalid JSON in response"**
- LLM may not be following format
- Check prompt clarity
- Try different model
- Review LLM provider status

**"Rate limit exceeded"**
- Reduce concurrent requests
- Add delays between calls
- Upgrade API plan
- Use different provider

### Debug Mode

Enable detailed logging:
```bash
export LOG_LEVEL=DEBUG
export DEBUG=true
./run.sh
```

Check logs for:
- LLM provider selection
- Prompt being sent
- Raw LLM responses
- Parsing errors

## Future Enhancements

- **Streaming Responses**: Generate slides progressively
- **Multi-Modal**: Include image generation for diagrams
- **Fine-Tuned Models**: Custom models for Elastic content
- **A/B Testing**: Compare different prompts automatically
- **Cost Optimization**: Dynamic provider selection based on cost
- **Prompt Analytics**: Track which prompts perform best