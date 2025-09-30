#!/usr/bin/env python3
"""
Quick test script to check Elasticsearch Serverless connection
"""
import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch

# Load environment variables
load_dotenv()

def test_elasticsearch_connection():
    """Test the Elasticsearch connection with current environment variables"""

    # Check for environment variables
    es_url = os.getenv('ELASTICSEARCH_URL')
    api_key = os.getenv('ELASTICSEARCH_API_KEY')

    print("=== Elasticsearch Serverless Connection Test ===")
    print(f"ELASTICSEARCH_URL: {'✓ Set' if es_url else '✗ Not set'}")
    print(f"ELASTICSEARCH_API_KEY: {'✓ Set' if api_key else '✗ Not set'}")

    if not es_url or not api_key:
        print("\n❌ Missing required environment variables")
        print("Please create a .env file with:")
        print("ELASTICSEARCH_URL=https://your-project.es.region.provider.cloud.es.io:443")
        print("ELASTICSEARCH_API_KEY=your_serverless_api_key_here")
        return False

    # Try to connect
    try:
        print(f"\n🔄 Connecting to: {es_url}")

        es_client = Elasticsearch(
            es_url,
            api_key=api_key,
            verify_certs=True
        )

        # Test the connection
        info = es_client.info()
        print(f"✅ Connection successful!")
        print(f"   Cluster: {info.get('cluster_name', 'Unknown')}")
        print(f"   Version: {info.get('version', {}).get('number', 'Unknown')}")

        # Test index operations
        index_name = "elastic-whats-new-features"
        print(f"\n🔄 Testing index operations on '{index_name}'...")

        # Check if index exists
        if es_client.indices.exists(index=index_name):
            print(f"✅ Index '{index_name}' exists")

            # Get some basic stats
            try:
                stats = es_client.cat.count(index=index_name, format="json")
                if stats:
                    count = stats[0].get('count', '0')
                    print(f"   Document count: {count}")
            except Exception as e:
                print(f"   Could not get count: {e}")
        else:
            print(f"ℹ️  Index '{index_name}' does not exist yet (will be created when first feature is added)")

        return True

    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_elasticsearch_connection()
    exit(0 if success else 1)