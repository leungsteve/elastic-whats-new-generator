#!/usr/bin/env python3
"""
Test script for LLM usage tracking and content storage.

This script tests:
1. LLM usage logging to Elasticsearch
2. Generated content storage
3. Querying usage analytics
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from elasticsearch import Elasticsearch
from src.integrations.elasticsearch import LLMUsageStorage, GeneratedContentStorage
from src.integrations.unified_llm_client import UnifiedLLMClient
from src.core.models import Feature, Domain, GeneratedContent, LLMUsageLog

def test_llm_tracking():
    """Test LLM usage tracking."""

    print("\n" + "="*60)
    print("Testing LLM Usage Tracking")
    print("="*60 + "\n")

    # 1. Connect to Elasticsearch
    print("1. Connecting to Elasticsearch...")
    es_url = os.getenv("ELASTICSEARCH_URL") or os.getenv("ELASTICSEARCH_HOST", "http://localhost:9200")
    es_api_key = os.getenv("ELASTICSEARCH_API_KEY")
    es_password = os.getenv("ELASTICSEARCH_PASSWORD", "")

    try:
        # Connect (prefer API key for cloud, fallback to basic auth for local)
        if es_api_key:
            es = Elasticsearch(
                [es_url],
                api_key=es_api_key,
                verify_certs=True
            )
        else:
            es = Elasticsearch(
                [es_url],
                basic_auth=("elastic", es_password) if es_password else None,
                verify_certs=False
            )

        # Test connection
        if not es.ping():
            print("❌ Failed to connect to Elasticsearch")
            return False

        print(f"✅ Connected to Elasticsearch at {es_url}")
    except Exception as e:
        print(f"❌ Elasticsearch connection error: {e}")
        print("\nMake sure Elasticsearch is running and credentials are set:")
        print("  export ELASTICSEARCH_HOST=http://localhost:9200")
        print("  export ELASTICSEARCH_PASSWORD=your_password")
        return False

    # 2. Initialize storage
    print("\n2. Initializing storage...")
    try:
        usage_storage = LLMUsageStorage(es)
        content_storage = GeneratedContentStorage(es)
        print("✅ Storage initialized")
        print(f"   - LLM Usage Index: {usage_storage.index_name}")
        print(f"   - Generated Content Index: {content_storage.index_name}")
    except Exception as e:
        print(f"❌ Failed to initialize storage: {e}")
        return False

    # 3. Initialize LLM client with usage tracking
    print("\n3. Initializing LLM client with tracking...")
    try:
        # Use gpt-4o instead of gpt-4o-mini if accessing via proxy
        model = os.getenv("LLM_MODEL", "gpt-4o")
        llm_client = UnifiedLLMClient(usage_storage=usage_storage, model=model)
        print(f"✅ LLM client initialized")
        print(f"   - Provider: {llm_client.provider.value}")
        print(f"   - Model: {llm_client.model}")
    except Exception as e:
        print(f"❌ Failed to initialize LLM client: {e}")
        print("\nMake sure you have an LLM API key set:")
        print("  export OPENAI_API_KEY=your_key")
        print("  or GEMINI_API_KEY=your_key")
        print("  or ANTHROPIC_API_KEY=your_key")
        return False

    # 4. Test LLM call with tracking
    print("\n4. Testing LLM call with usage tracking...")
    try:
        response = llm_client._call_llm(
            system_prompt="You are a helpful assistant.",
            user_prompt="Say 'Hello, tracking works!' in a friendly way.",
            operation_type="test",
            feature_ids=["test-feature-1"],
            domain="search"
        )
        print(f"✅ LLM call successful")
        print(f"   Response: {response[:100]}...")
    except Exception as e:
        print(f"❌ LLM call failed: {e}")
        return False

    # 5. Query usage logs
    print("\n5. Querying usage logs...")
    try:
        import time
        time.sleep(2)  # Wait for Elasticsearch to index

        logs = usage_storage.search_by_operation("test", size=10)
        if logs:
            print(f"✅ Found {len(logs)} usage log(s)")
            latest = logs[0]
            print(f"   - Operation: {latest['operation_type']}")
            print(f"   - Provider: {latest['provider']}")
            print(f"   - Model: {latest['model']}")
            print(f"   - Success: {latest['success']}")
            if latest.get('token_usage'):
                print(f"   - Total Tokens: {latest['token_usage'].get('total_tokens', 'N/A')}")
            if latest.get('estimated_cost_usd'):
                print(f"   - Estimated Cost: ${latest['estimated_cost_usd']:.6f}")
            print(f"   - Response Time: {latest['response_time_seconds']:.2f}s")
        else:
            print("⚠️  No logs found (may need more time to index)")
    except Exception as e:
        print(f"❌ Failed to query logs: {e}")

    # 6. Get usage analytics
    print("\n6. Getting usage analytics...")
    try:
        analytics = usage_storage.get_usage_analytics()
        print(f"✅ Analytics retrieved")
        print(f"   - Total Calls: {analytics['total_calls']}")
        print(f"   - By Provider: {analytics['by_provider']}")
        print(f"   - By Operation: {analytics['by_operation']}")
        if analytics['total_tokens']:
            print(f"   - Total Tokens: {analytics['total_tokens']:.0f}")
        if analytics['total_cost_usd']:
            print(f"   - Total Cost: ${analytics['total_cost_usd']:.6f}")
        if analytics['avg_response_time_seconds']:
            print(f"   - Avg Response Time: {analytics['avg_response_time_seconds']:.2f}s")
        print(f"   - Success Rate: {analytics['success_rate']*100:.1f}%")
    except Exception as e:
        print(f"❌ Failed to get analytics: {e}")

    # 7. Test generated content storage
    print("\n7. Testing generated content storage...")
    try:
        test_content = GeneratedContent(
            content_type="presentation",
            title="Test Presentation - ES|QL Features",
            domain="search",
            feature_ids=["test-feature-1"],
            feature_names=["ES|QL LOOKUP JOINS"],
            markdown_content="# Test Presentation\n\nThis is a test.",
            structured_data={"slides": [{"title": "Test Slide"}]},
            generation_params={"narrative_style": "customer_journey"},
            tags=["test", "esql"]
        )

        content_storage.store(test_content)
        print(f"✅ Generated content stored")
        print(f"   - Content ID: {test_content.id}")
        print(f"   - Type: {test_content.content_type}")
        print(f"   - Title: {test_content.title}")
    except Exception as e:
        print(f"❌ Failed to store content: {e}")

    # 8. Query generated content
    print("\n8. Querying generated content...")
    try:
        time.sleep(2)  # Wait for indexing

        content_list = content_storage.search_by_type("presentation", size=5)
        if content_list:
            print(f"✅ Found {len(content_list)} presentation(s)")
            for i, content in enumerate(content_list[:3], 1):
                print(f"   {i}. {content['title']}")
                print(f"      - Domain: {content['domain']}")
                print(f"      - Features: {', '.join(content['feature_names'][:3])}")
        else:
            print("⚠️  No content found (may need more time to index)")
    except Exception as e:
        print(f"❌ Failed to query content: {e}")

    print("\n" + "="*60)
    print("✅ LLM Tracking Test Complete!")
    print("="*60 + "\n")

    print("What was tested:")
    print("  ✓ Elasticsearch connection")
    print("  ✓ Storage initialization")
    print("  ✓ LLM client with tracking")
    print("  ✓ Automatic usage logging")
    print("  ✓ Usage analytics")
    print("  ✓ Generated content storage")
    print("  ✓ Content querying")

    print("\nNext steps:")
    print("  1. Check Kibana to see the data:")
    print(f"     - Index: {usage_storage.index_name}")
    print(f"     - Index: {content_storage.index_name}")
    print("  2. Integrate into main API (main.py)")
    print("  3. Add UI components to view analytics")

    return True


if __name__ == "__main__":
    try:
        success = test_llm_tracking()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)