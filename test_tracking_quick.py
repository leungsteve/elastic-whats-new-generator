#!/usr/bin/env python3
"""Quick test to verify Elasticsearch connection and index creation."""

import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from elasticsearch import Elasticsearch
from src.integrations.elasticsearch import LLMUsageStorage, GeneratedContentStorage

print("\n🧪 Quick Test: Elasticsearch Connection & Index Setup\n")

# Get Elasticsearch credentials (support both local and cloud)
es_url = os.getenv("ELASTICSEARCH_URL") or os.getenv("ELASTICSEARCH_HOST", "http://localhost:9200")
es_api_key = os.getenv("ELASTICSEARCH_API_KEY")
es_password = os.getenv("ELASTICSEARCH_PASSWORD", "")

print(f"Connecting to: {es_url}")

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

    if not es.ping():
        print("❌ Cannot connect to Elasticsearch")
        print("\nTroubleshooting:")
        print("  1. Is Elasticsearch running?")
        print("  2. Check ELASTICSEARCH_HOST: export ELASTICSEARCH_HOST=http://localhost:9200")
        print("  3. Check ELASTICSEARCH_PASSWORD if using authentication")
        sys.exit(1)

    print("✅ Connected to Elasticsearch")

    # Get cluster info
    info = es.info()
    print(f"   Version: {info['version']['number']}")
    print(f"   Cluster: {info['cluster_name']}")

    # Initialize storage (this creates indices if they don't exist)
    print("\nCreating indices...")
    usage_storage = LLMUsageStorage(es)
    content_storage = GeneratedContentStorage(es)

    print(f"✅ {usage_storage.index_name} - created/verified")
    print(f"✅ {content_storage.index_name} - created/verified")

    # List all indices
    print("\nElasticsearch indices:")
    indices = es.cat.indices(format="json")
    for idx in sorted(indices, key=lambda x: x['index']):
        if not idx['index'].startswith('.'):
            print(f"   - {idx['index']} ({idx['docs.count']} docs)")

    print("\n✅ Setup Complete!")
    print("\nYou can now run: python test_llm_tracking.py")

except Exception as e:
    print(f"❌ Error: {e}")
    print("\nMake sure:")
    print("  - Elasticsearch is running")
    print("  - Credentials are correct")
    print("  - You can access the host")
    sys.exit(1)