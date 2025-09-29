# Quick Start: LLM Configuration

## 5-Minute Setup

### 1. Choose Your LLM Provider

**Option A: OpenAI (Recommended)**
```bash
# In .env file:
OPENAI_API_KEY=sk-your-key-here
LLM_MODEL=gpt-4o  # or gpt-4o-mini for lower cost
```

**Option B: Google Gemini**
```bash
# In .env file:
GEMINI_API_KEY=your-gemini-key
LLM_MODEL=gemini-1.5-flash
```

**Option C: Anthropic Claude**
```bash
# In .env file:
ANTHROPIC_API_KEY=your-claude-key
LLM_MODEL=claude-3-sonnet-20240229
```

### 2. Start the Server

```bash
./run.sh
```

### 3. Test It Works

1. Open http://localhost:8000
2. Add a new feature with documentation links
3. Click "Research Content" button
4. Wait for LLM extraction to complete
5. Generate a presentation using the feature

## Using with Proxy (Claude Code Max, LiteLLM, etc.)

```bash
# In .env file:
OPENAI_API_KEY=your-proxy-api-key
OPENAI_BASE_URL=https://your-proxy-url
# Do NOT add /chat/completions - client adds it automatically
```

## How It Works

### Two Stages

**Stage 1: Content Extraction (happens once per feature)**
```
Feature URL → Scrape Docs → LLM Extract → Cache in Elasticsearch
```

**Stage 2: Presentation Generation (happens on-demand)**
```
Select Features → Load Cached Data → LLM Generate → 7-Slide Presentation
```

### Why Two Stages?

- ✅ **Cost Efficient**: Extract once, generate many presentations
- ✅ **Fast**: No re-scraping needed
- ✅ **Consistent**: Same extraction used for all presentations

## Customizing Presentation Style

### Quick Customization

Edit `config/llm_prompts.yaml`:

**For Business Audiences:**
```yaml
presentation_generator:
  system_prompt: |
    Create executive-level presentations.
    Focus on ROI and business outcomes.
    Minimize technical jargon.
    Emphasize cost savings.
```

**For Technical Audiences:**
```yaml
presentation_generator:
  system_prompt: |
    Create detailed technical presentations.
    Include architecture details and code examples.
    Assume advanced technical knowledge.
    Focus on implementation.
```

**Restart server after changes:**
```bash
pkill -f "uvicorn"
./run.sh
```

## Troubleshooting

### "No LLM provider available"
**Problem:** No API key configured
**Solution:** Set at least one API key in `.env` file

### "Rate limit exceeded"
**Problem:** Too many API calls
**Solution:** Wait a few minutes, or upgrade API plan

### "Invalid JSON in response"
**Problem:** LLM not following format
**Solution:** Try different model (gpt-4o is more reliable than gpt-4o-mini)

### "Prompts config not found"
**Problem:** Missing config file
**Solution:** File is optional - system uses defaults. Check `config/llm_prompts.yaml` exists.

### Presentation missing talk tracks
**Problem:** Speaker notes not showing
**Solution:** Refresh browser cache (Cmd+Shift+R or Ctrl+Shift+R)

## Cost Optimization

### Recommended Models by Use Case

**Development/Testing:**
- OpenAI: `gpt-4o-mini` (~$0.15 per 1M input tokens)
- Gemini: `gemini-1.5-flash` (cheapest, fastest)

**Production:**
- OpenAI: `gpt-4o` (~$2.50 per 1M input tokens, best quality)
- Claude: `claude-3-sonnet` (high quality, more expensive)

### Cost Estimation

**Per Feature Extraction:**
- ~8,000 tokens input (scraped docs)
- ~1,000 tokens output (structured JSON)
- Cost: ~$0.02 with gpt-4o-mini, ~$0.25 with gpt-4o

**Per Presentation Generation:**
- ~2,000 tokens input (cached extractions)
- ~3,000 tokens output (7 slides with talk tracks)
- Cost: ~$0.01 with gpt-4o-mini, ~$0.15 with gpt-4o

**Monthly Estimate (100 features, 50 presentations):**
- With gpt-4o-mini: ~$2.50/month
- With gpt-4o: ~$32.50/month

## Advanced Configuration

### Multiple API Keys

You can configure multiple providers for automatic fallback:

```bash
OPENAI_API_KEY=sk-key1
GEMINI_API_KEY=your-gemini-key
ANTHROPIC_API_KEY=your-claude-key
```

System will try OpenAI first, then Gemini, then Claude.

### Per-Provider Model Override

```bash
LLM_MODEL=gpt-4o  # Used for OpenAI
```

Or set model in code:
```python
from src.integrations.unified_llm_client import UnifiedLLMClient

client = UnifiedLLMClient(
    provider=LLMProvider.OPENAI,
    model="gpt-4o-mini"
)
```

### Custom Prompt Variables

In `config/llm_prompts.yaml`, use these variables:

**Presentation Generation:**
- `{slide_count}` - Number of slides (default: 7)
- `{domain}` - Domain (search/observability/security)
- `{audience}` - Target audience (business/technical/mixed)
- `{narrative_style}` - Narrative approach
- `{technical_depth}` - Technical detail level
- `{feature_contexts}` - Auto-generated feature information

**Content Extraction:**
- `{feature_name}` - Name of the feature
- `{documentation_url}` - Documentation URL
- `{scraped_content}` - Scraped documentation text

## Next Steps

- Read [LLM Architecture](architecture/llm-architecture.md) for deep dive
- See [Prompt Customization](../config/README.md) for advanced customization
- Check [Content Research](architecture/content-research.md) for full pipeline details