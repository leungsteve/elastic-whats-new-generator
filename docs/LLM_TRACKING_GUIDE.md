# LLM Usage Tracking & Content Storage - User Guide

## Quick Start

### Accessing Analytics
1. Open the web UI at `http://localhost:8000`
2. Click the **Analytics** tab in the sidebar
3. View real-time metrics, charts, and content history

### What Gets Tracked?
Every time the system uses an LLM (OpenAI, Gemini, or Claude), it automatically logs:
- ✅ The exact prompt sent to the LLM
- ✅ The complete response received
- ✅ Token usage (prompt + completion tokens)
- ✅ Estimated cost in USD
- ✅ Response time
- ✅ Success or failure status

Every presentation or lab you generate is automatically saved with:
- ✅ Full markdown content
- ✅ All slides/challenges/datasets
- ✅ Generation parameters
- ✅ Feature associations

## Analytics Dashboard

### Summary Cards
At the top of the Analytics tab, you'll see four key metrics:

**Total LLM Calls**
- Number of times the system called an LLM API
- Includes all operations: extraction, presentation generation, lab generation

**Total Cost (USD)**
- Sum of all estimated costs
- Based on provider pricing per 1K tokens
- Updated in real-time

**Avg Response Time**
- Average time for LLM to respond
- Helps identify performance issues

**Success Rate**
- Percentage of successful LLM calls
- Helps track API reliability

### Usage Charts

**By Provider**
- Visual breakdown showing OpenAI vs. Gemini vs. Claude usage
- Bar width represents proportion of total calls

**By Operation**
- Shows distribution across operation types:
  - `extract` - Content extraction from documentation
  - `generate_presentation` - Presentation generation
  - `generate_lab` - Lab generation
  - `test` - Test operations

### Content History Browser
Browse all presentations and labs ever generated:

**Filters**
- **Content Type**: Filter by presentation or lab
- **Domain**: Filter by search, observability, security, or all_domains

**Content Cards** show:
- Title and content type (with icon)
- Domain
- Number of features included
- Timestamp when generated

**Actions**
- **Click card** - View details in a modal
- **Download button** - Download markdown file immediately

### Activity Log
See recent LLM calls with:
- ✅ Green border - Successful call
- ❌ Red border - Failed call
- Provider and model used
- Token count and cost
- Response time

## REST API Usage

### Get Analytics Summary
```bash
curl http://localhost:8000/api/llm-usage/analytics | jq .
```

Response:
```json
{
  "analytics": {
    "total_calls": 42,
    "by_provider": {"openai": 30, "gemini": 12},
    "by_operation": {"generate_presentation": 15, "generate_lab": 20, "extract": 7},
    "total_tokens": 125430.0,
    "total_cost_usd": 0.5421,
    "avg_response_time_seconds": 2.34,
    "success_rate": 0.976
  }
}
```

### Query LLM Logs
```bash
# Get recent logs
curl "http://localhost:8000/api/llm-usage/logs?size=10" | jq .

# Filter by operation
curl "http://localhost:8000/api/llm-usage/logs?operation_type=generate_presentation&size=20" | jq .

# Filter by provider
curl "http://localhost:8000/api/llm-usage/logs?provider=openai&size=20" | jq .

# Get only successful calls
curl "http://localhost:8000/api/llm-usage/logs?success_only=true" | jq .
```

### Query Generated Content
```bash
# Get all content
curl "http://localhost:8000/api/generated-content?size=20" | jq .

# Filter by type
curl "http://localhost:8000/api/generated-content?content_type=presentation" | jq .

# Filter by domain
curl "http://localhost:8000/api/generated-content?domain=search" | jq .

# Get specific content
curl "http://localhost:8000/api/generated-content/{content_id}" | jq .

# Get markdown for download
curl "http://localhost:8000/api/generated-content/{content_id}/markdown" | jq -r .markdown > output.md
```

### Query Specific Log
```bash
curl "http://localhost:8000/api/llm-usage/{log_id}" | jq .
```

## Cost Tracking

### Current Pricing (per 1,000 tokens)

**OpenAI**
- gpt-4o: $0.0025 (prompt) / $0.01 (completion)
- gpt-4o-mini: $0.00015 (prompt) / $0.0006 (completion)

**Google Gemini**
- gemini-1.5-flash: $0.000075 (prompt) / $0.0003 (completion)

**Anthropic Claude**
- claude-3-sonnet: $0.003 (prompt) / $0.015 (completion)

### Estimating Costs
The system automatically calculates costs based on:
1. Token usage (prompt + completion tokens)
2. Provider-specific pricing
3. Model used

**Example**:
- Operation: Generate presentation
- Provider: OpenAI (gpt-4o)
- Tokens: 2,000 prompt + 1,500 completion
- Cost: (2,000/1000 × $0.0025) + (1,500/1000 × $0.01) = $0.005 + $0.015 = **$0.020**

### Monitoring Spend
1. Check **Total Cost** card for current spend
2. Review **By Provider** chart to see which provider costs most
3. Use `/api/llm-usage/analytics?start_date=2025-01-01` for date-range analysis
4. Export logs to CSV for detailed analysis (coming soon)

## Elasticsearch Queries

### Direct Kibana Queries

**View all LLM logs:**
```json
GET llm-usage-logs/_search
{
  "size": 10,
  "sort": [{"timestamp": "desc"}]
}
```

**Calculate total cost:**
```json
GET llm-usage-logs/_search
{
  "size": 0,
  "aggs": {
    "total_cost": {"sum": {"field": "estimated_cost_usd"}}
  }
}
```

**Find expensive calls:**
```json
GET llm-usage-logs/_search
{
  "query": {
    "range": {"estimated_cost_usd": {"gte": 0.01}}
  },
  "sort": [{"estimated_cost_usd": "desc"}]
}
```

**View all generated content:**
```json
GET generated-content/_search
{
  "size": 10,
  "sort": [{"timestamp": "desc"}]
}
```

## Troubleshooting

### No Data in Analytics Tab
**Check:**
1. Is Elasticsearch configured in `.env`?
2. Are indices created? Run: `curl http://localhost:9200/_cat/indices?v`
3. Have you generated any content yet?

### Costs Seem Wrong
**Notes:**
- Costs are **estimates** based on public pricing
- Actual costs may vary based on your billing agreement
- Always verify with your provider's billing dashboard
- Token counts from Claude may be estimates if not provided in response

### Content Not Appearing
**Check:**
1. Wait 2-3 seconds after generation (Elasticsearch needs time to index)
2. Refresh the Analytics tab
3. Check browser console for errors (F12)
4. Verify `/api/generated-content` endpoint returns data

### Downloads Not Working
**Browser settings:**
- Check if browser is blocking downloads
- Some browsers require "Allow downloads" permission
- Try different browser if issue persists

## Best Practices

### Cost Optimization
1. **Use appropriate models**: gpt-4o-mini for simple tasks, gpt-4o for complex
2. **Cache extractions**: Stage 1 caching reduces redundant calls
3. **Monitor regularly**: Check Analytics tab weekly
4. **Set budgets**: Define monthly spend limits
5. **Analyze patterns**: Use `/api/llm-usage/analytics` to find optimization opportunities

### Content Management
1. **Review history**: Check Content History Browser before regenerating
2. **Reuse content**: Download and edit existing content instead of regenerating
3. **Tag effectively**: Use consistent tags for easier searching
4. **Version control**: Keep track of content versions for iterations

### Performance
1. **Monitor response times**: Identify slow operations
2. **Check success rates**: Investigate failures
3. **Review error logs**: Use Activity Log to find issues
4. **Optimize prompts**: Shorter prompts = faster responses = lower costs

## Advanced Usage

### Custom Analytics Queries
Build your own dashboards using the Elasticsearch data:

```python
from elasticsearch import Elasticsearch

es = Elasticsearch(['http://localhost:9200'])

# Get cost by day
result = es.search(index='llm-usage-logs', body={
    "size": 0,
    "aggs": {
        "costs_by_day": {
            "date_histogram": {
                "field": "timestamp",
                "calendar_interval": "day"
            },
            "aggs": {
                "total_cost": {"sum": {"field": "estimated_cost_usd"}}
            }
        }
    }
})
```

### Exporting Data
```bash
# Export all logs to JSON
curl "http://localhost:8000/api/llm-usage/logs?size=1000" > llm_logs.json

# Export all content to JSON
curl "http://localhost:8000/api/generated-content?size=1000" > generated_content.json
```

## FAQ

**Q: Does tracking slow down the system?**
A: No, logging is asynchronous and adds <50ms overhead.

**Q: Can I disable tracking?**
A: Tracking is automatically disabled if Elasticsearch is not configured.

**Q: How long is data retained?**
A: Data is retained indefinitely unless you manually delete indices.

**Q: Can I see prompts sent to LLMs?**
A: Yes, full prompts are stored in `llm-usage-logs` index (not shown in UI for brevity).

**Q: Are API keys logged?**
A: No, API keys are never logged or stored.

**Q: Can I export analytics to Excel?**
A: Use the REST API to get JSON data, then import to Excel (CSV export coming soon).

## Support

For issues or questions:
1. Check this guide
2. Review `LLM_TRACKING_SUMMARY.md`
3. Check server logs: `tail -f server.log`
4. Open an issue on GitHub