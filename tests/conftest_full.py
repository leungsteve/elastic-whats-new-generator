import pytest
from unittest.mock import Mock, MagicMock
from elasticsearch import Elasticsearch
from src.core.models import Feature, Theme
from src.integrations.elasticsearch import FeatureStorage

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
        domain="search"
    )

@pytest.fixture
def mock_elasticsearch():
    """Mock Elasticsearch client for testing"""
    mock_es = Mock(spec=Elasticsearch)
    mock_es.index.return_value = {"_id": "test-id"}
    mock_es.get.return_value = {
        "_source": {
            "name": "Test Feature",
            "description": "Test description"
        }
    }
    return mock_es

@pytest.fixture
def feature_storage(mock_elasticsearch):
    """Feature storage with mocked Elasticsearch"""
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