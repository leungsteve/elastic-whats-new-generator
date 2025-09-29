# Testing LLM Usage Tracking

This guide explains how to test the new LLM usage tracking and content storage features.

## Prerequisites

1. **Elasticsearch running** (locally or remote)
2. **LLM API key** (OpenAI, Gemini, or Claude)
3. **Python dependencies installed**

## Quick Setup

### 1. Set Environment Variables

```bash
# Elasticsearch connection
export ELASTICSEARCH_HOST=http://localhost:9200
export ELASTICSEARCH_PASSWORD=your_password  # if using authentication

# LLM API key (choose one)
export OPENAI_API_KEY=sk-your-key-here
# OR
export GEMINI_API_KEY=your-gemini-key
# OR
export ANTHROPIC_API_KEY=your-claude-key
```

### 2. Run Quick Connection Test

This verifies Elasticsearch is accessible and creates the indices:

```bash
python test_tracking_quick.py
```

**Expected output:**
```
🧪 Quick Test: Elasticsearch Connection & Index Setup

Connecting to: http://localhost:9200
✅ Connected to Elasticsearch
   Version: 8.x.x
   Cluster: elasticsearch

Creating indices...
✅ llm-usage-logs - created/verified
✅ generated-content - created/verified

Elasticsearch indices:
   - llm-usage-logs (0 docs)
   - generated-content (0 docs)
   - elastic-features (X docs)

✅ Setup Complete!
```

### 3. Run Full Tracking Test

This tests the complete LLM tracking system:

```bash
python test_llm_tracking.py
```

**What it tests:**
1. ✅ Elasticsearch connection
2. ✅ Storage initialization (creates indices)
3. ✅ LLM client with tracking enabled
4. ✅ Makes a test LLM call
5. ✅ Logs usage automatically to Elasticsearch
6. ✅ Queries usage logs
7. ✅ Retrieves usage analytics
8. ✅ Stores generated content
9. ✅ Queries stored content

**Expected output:**
```
============================================================
Testing LLM Usage Tracking
============================================================

1. Connecting to Elasticsearch...
✅ Connected to Elasticsearch at http://localhost:9200

2. Initializing storage...
✅ Storage initialized
   - LLM Usage Index: llm-usage-logs
   - Generated Content Index: generated-content

3. Initializing LLM client with tracking...
✅ LLM client initialized
   - Provider: openai
   - Model: gpt-4o

4. Testing LLM call with usage tracking...
✅ LLM call successful
   Response: Hello! I'm happy to let you know that tracking works! ...

5. Querying usage logs...
✅ Found 1 usage log(s)
   - Operation: test
   - Provider: openai
   - Model: gpt-4o
   - Success: True
   - Total Tokens: 45
   - Estimated Cost: $0.000123
   - Response Time: 1.23s

6. Getting usage analytics...
✅ Analytics retrieved
   - Total Calls: 1
   - By Provider: {'openai': 1}
   - By Operation: {'test': 1}
   - Total Tokens: 45
   - Total Cost: $0.000123
   - Avg Response Time: 1.23s
   - Success Rate: 100.0%

7. Testing generated content storage...
✅ Generated content stored
   - Content ID: 123e4567-e89b-12d3-a456-426614174000
   - Type: presentation
   - Title: Test Presentation - ES|QL Features

8. Querying generated content...
✅ Found 1 presentation(s)
   1. Test Presentation - ES|QL Features
      - Domain: search
      - Features: ES|QL LOOKUP JOINS

============================================================
✅ LLM Tracking Test Complete!
============================================================
```

## Verify in Kibana

After running the tests, you can view the data in Kibana:

### View LLM Usage Logs

1. Open Kibana
2. Go to **Discover**
3. Select index: `llm-usage-logs`
4. You should see:
   - Timestamps
   - Provider (openai/gemini/claude)
   - Model used
   - Operation type
   - System/user prompts
   - Full responses
   - Token usage
   - Estimated costs
   - Response times

### View Generated Content

1. In Kibana Discover
2. Select index: `generated-content`
3. You should see:
   - Content type (presentation/lab)
   - Titles
   - Domains
   - Feature IDs
   - Full markdown content
   - Structured data (JSON)
   - Generation parameters

### Create Visualizations

You can create dashboards to visualize:
- **Cost over time** (line chart)
- **Tokens by provider** (pie chart)
- **Operations by type** (bar chart)
- **Success rate** (gauge)
- **Response time trends** (line chart)

## Troubleshooting

### "Cannot connect to Elasticsearch"

```bash
# Check if Elasticsearch is running
curl http://localhost:9200

# If using authentication
curl -u elastic:your_password http://localhost:9200

# Check your environment variables
echo $ELASTICSEARCH_HOST
echo $ELASTICSEARCH_PASSWORD
```

### "No LLM provider available"

```bash
# Make sure you have at least one API key set
echo $OPENAI_API_KEY
echo $GEMINI_API_KEY
echo $ANTHROPIC_API_KEY

# Set one:
export OPENAI_API_KEY=sk-your-key-here
```

### "No logs found"

- Elasticsearch needs a moment to index documents
- Try waiting 5-10 seconds and query again
- Check indices: `curl http://localhost:9200/_cat/indices`

### Indices Not Created

```bash
# Manually create with curl
curl -X PUT "http://localhost:9200/llm-usage-logs"
curl -X PUT "http://localhost:9200/generated-content"

# Or re-run the quick test
python test_tracking_quick.py
```

## What Data is Tracked?

### LLM Usage Log Entry

```json
{
  "id": "uuid",
  "timestamp": "2025-09-29T12:00:00Z",
  "provider": "openai",
  "model": "gpt-4o",
  "operation_type": "generate_lab",
  "feature_ids": ["feature-1", "feature-2"],
  "domain": "search",
  "system_prompt": "You are an expert...",
  "user_prompt": "Generate a lab for...",
  "response_text": "# Lab Title\n\n...",
  "token_usage": {
    "prompt_tokens": 1500,
    "completion_tokens": 800,
    "total_tokens": 2300
  },
  "response_time_seconds": 3.45,
  "success": true,
  "error_message": null,
  "estimated_cost_usd": 0.0115
}
```

### Generated Content Entry

```json
{
  "id": "uuid",
  "timestamp": "2025-09-29T12:00:00Z",
  "content_type": "lab",
  "title": "Fleet Health Monitoring with ES|QL",
  "domain": "search",
  "feature_ids": ["esql-lookup-joins"],
  "feature_names": ["ES|QL LOOKUP JOINS"],
  "markdown_content": "# Lab Title\n\nFull markdown here...",
  "structured_data": {
    "dataset_tables": [...],
    "challenges": [...]
  },
  "generation_params": {
    "scenario_type": "auto",
    "data_size": "realistic",
    "technical_depth": "medium"
  },
  "llm_usage_log_id": "uuid-of-llm-call",
  "tags": ["esql", "lookup-join"],
  "version": 1
}
```

## Next Steps

Once testing is successful:

1. **Integrate into API** - Wire up storage in `main.py`
2. **Add to Endpoints** - Store content when generated
3. **Create Query APIs** - Endpoints to retrieve logs and content
4. **Build UI** - Dashboard to view analytics and history
5. **Monitor Costs** - Set up alerts for high usage

## Cost Monitoring

The system estimates costs based on:
- **GPT-4o**: $0.0025/1K prompt tokens, $0.01/1K completion tokens
- **GPT-4o-mini**: $0.00015/1K prompt tokens, $0.0006/1K completion tokens
- **Gemini 1.5 Flash**: $0.000075/1K prompt tokens, $0.0003/1K completion tokens
- **Claude 3 Sonnet**: $0.003/1K prompt tokens, $0.015/1K completion tokens

Track your actual costs in the LLM provider dashboard and compare with estimates.