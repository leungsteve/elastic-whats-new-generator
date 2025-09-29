import pytest
from unittest.mock import Mock, MagicMock
from src.core.models import Feature, Theme, Domain

# Optional imports - only needed for integration tests
try:
    from elasticsearch import Elasticsearch
    from src.integrations.elasticsearch import FeatureStorage
    ELASTICSEARCH_AVAILABLE = True
except ImportError:
    ELASTICSEARCH_AVAILABLE = False

@pytest.fixture
def sample_feature():
    """Create a sample feature for testing"""
    return Feature(
        id="bbq-001",
        name="Better Binary Quantization",
        description="95% memory reduction with improved ranking quality",
        benefits=[
            "Reduces memory usage by 95%",
            "Improves ranking quality",
            "Faster query performance"
        ],
        documentation_links=[
            "https://elastic.co/blog/bbq",
            "https://elastic.co/docs/bbq"
        ],
        theme=Theme.OPTIMIZE,
        domain=Domain.SEARCH
    )

@pytest.fixture
def mock_elasticsearch():
    """Mock Elasticsearch client for testing"""
    mock_es = Mock()
    mock_es.index.return_value = {"_id": "test-id"}
    mock_es.get.return_value = {
        "_source": {
            "id": "bbq-001",
            "name": "Better Binary Quantization",
            "description": "95% memory reduction with improved ranking quality",
            "benefits": ["Reduces memory usage by 95%", "Improves ranking quality", "Faster query performance"],
            "documentation_links": ["https://elastic.co/blog/bbq"],
            "theme": "optimize",
            "domain": "search",
            "scraped_content": None,
            "created_at": "2024-01-01T00:00:00+00:00",
            "updated_at": "2024-01-01T00:00:00+00:00"
        }
    }
    mock_es.search.return_value = {
        "hits": {
            "hits": [
                {
                    "_source": {
                        "id": "bbq-001",
                        "name": "Better Binary Quantization",
                        "description": "95% memory reduction with improved ranking quality",
                        "benefits": ["Reduces memory usage by 95%", "Improves ranking quality", "Faster query performance"],
                        "documentation_links": ["https://elastic.co/blog/bbq"],
                        "theme": "optimize",
                        "domain": "search",
                        "scraped_content": None,
                        "created_at": "2024-01-01T00:00:00+00:00",
                        "updated_at": "2024-01-01T00:00:00+00:00"
                    }
                }
            ]
        }
    }
    # Mock indices
    mock_indices = Mock()
    mock_indices.exists.return_value = False
    mock_indices.create.return_value = {"acknowledged": True}
    mock_es.indices = mock_indices
    mock_es.delete.return_value = {"_id": "test-id"}
    return mock_es

@pytest.fixture
def feature_storage(mock_elasticsearch):
    """Feature storage with mocked Elasticsearch"""
    if not ELASTICSEARCH_AVAILABLE:
        pytest.skip("Elasticsearch not available")
    return FeatureStorage(mock_elasticsearch)

@pytest.fixture
def mock_web_response():
    """Mock web response for scraping tests"""
    return {
        "title": "Better Binary Quantization",
        "content": "BBQ reduces memory usage significantly...",
        "benefits": ["95% memory reduction", "better ranking"]
    }

@pytest.fixture
def test_config():
    """Test configuration settings"""
    return {
        "elasticsearch_url": "http://localhost:9200",
        "test_index": "test-features",
        "claude_api_key": "test-key"
    }