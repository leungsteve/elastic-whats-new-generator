"""
Sample data fixtures for testing.

This module provides sample features and data for testing the
Elastic What's New Generator components.
"""

from src.core.models import Feature, Theme, Domain


def get_sample_search_features():
    """Get sample Search domain features."""
    return [
        Feature(
            id="bbq-001",
            name="Better Binary Quantization (BBQ)",
            description="95% memory reduction with improved ranking quality",
            benefits=[
                "Reduces memory usage by 95%",
                "Improves ranking quality over scalar quantization",
                "Faster query performance",
                "Lower infrastructure costs"
            ],
            documentation_links=[
                "https://www.elastic.co/guide/en/elasticsearch/reference/current/knn-search.html",
                "https://www.elastic.co/guide/en/elasticsearch/reference/current/dense-vector.html"
            ],
            theme=Theme.OPTIMIZE,
            domain=Domain.SEARCH,
            scraped_content="BBQ (Better Binary Quantization) is a new quantization technique..."
        ),
        Feature(
            id="acorn-001",
            name="ACORN Retrieval",
            description="Efficient retrieval using automatic clustering",
            benefits=[
                "Improves retrieval efficiency",
                "Reduces computational overhead",
                "Better relevance for large datasets"
            ],
            documentation_links=[
                "https://www.elastic.co/guide/en/elasticsearch/reference/current/search-search.html"
            ],
            theme=Theme.OPTIMIZE,
            domain=Domain.SEARCH
        ),
        Feature(
            id="agent-builder-001",
            name="Agent Builder",
            description="Framework for building AI agents with Elasticsearch",
            benefits=[
                "Rapid AI agent development",
                "Built-in search capabilities",
                "Pre-configured AI workflows",
                "Integration with popular LLMs"
            ],
            documentation_links=[
                "https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations.html"
            ],
            theme=Theme.AI_INNOVATION,
            domain=Domain.SEARCH
        ),
        Feature(
            id="cross-cluster-001",
            name="Cross-Cluster Search",
            description="Unified search across multiple Elasticsearch clusters",
            benefits=[
                "Single interface for multiple clusters",
                "Reduced operational complexity",
                "Centralized search experience"
            ],
            documentation_links=[
                "https://www.elastic.co/guide/en/elasticsearch/reference/current/cross-cluster-search.html"
            ],
            theme=Theme.SIMPLIFY,
            domain=Domain.SEARCH
        )
    ]


def get_sample_observability_features():
    """Get sample Observability domain features."""
    return [
        Feature(
            id="autoops-obs-001",
            name="AutoOps for Observability",
            description="Automated monitoring and alerting for observability data",
            benefits=[
                "Reduces operational overhead",
                "Automatic anomaly detection",
                "Self-healing monitoring",
                "Simplified alert management"
            ],
            documentation_links=[
                "https://www.elastic.co/guide/en/observability/current/observability-introduction.html"
            ],
            theme=Theme.SIMPLIFY,
            domain=Domain.OBSERVABILITY
        ),
        Feature(
            id="apm-performance-001",
            name="APM Performance Improvements",
            description="Enhanced performance monitoring with reduced overhead",
            benefits=[
                "50% reduction in monitoring overhead",
                "Faster trace processing",
                "Improved sampling algorithms"
            ],
            documentation_links=[
                "https://www.elastic.co/guide/en/apm/guide/current/performance.html"
            ],
            theme=Theme.OPTIMIZE,
            domain=Domain.OBSERVABILITY
        ),
        Feature(
            id="ai-assistant-obs-001",
            name="AI Assistant for Observability",
            description="AI-powered analysis and recommendations for observability data",
            benefits=[
                "Intelligent root cause analysis",
                "Automated incident response suggestions",
                "Natural language query interface"
            ],
            documentation_links=[
                "https://www.elastic.co/guide/en/observability/current/ai-assistant.html"
            ],
            theme=Theme.AI_INNOVATION,
            domain=Domain.OBSERVABILITY
        )
    ]


def get_sample_security_features():
    """Get sample Security domain features."""
    return [
        Feature(
            id="siem-efficiency-001",
            name="SIEM Query Optimization",
            description="Optimized queries for faster security investigations",
            benefits=[
                "75% faster security queries",
                "Reduced investigation time",
                "Improved analyst productivity"
            ],
            documentation_links=[
                "https://www.elastic.co/guide/en/security/current/siem-optimization.html"
            ],
            theme=Theme.OPTIMIZE,
            domain=Domain.SECURITY
        ),
        Feature(
            id="managed-security-001",
            name="Managed Security Rules",
            description="Automated security rule management and updates",
            benefits=[
                "Automated rule updates",
                "Reduced configuration complexity",
                "Always up-to-date threat detection"
            ],
            documentation_links=[
                "https://www.elastic.co/guide/en/security/current/managed-rules.html"
            ],
            theme=Theme.SIMPLIFY,
            domain=Domain.SECURITY
        ),
        Feature(
            id="ml-security-001",
            name="ML-powered Threat Detection",
            description="Machine learning algorithms for advanced threat detection",
            benefits=[
                "Detect unknown threats",
                "Reduce false positives",
                "Adaptive threat models"
            ],
            documentation_links=[
                "https://www.elastic.co/guide/en/security/current/ml-detection.html"
            ],
            theme=Theme.AI_INNOVATION,
            domain=Domain.SECURITY
        )
    ]


def get_all_sample_features():
    """Get all sample features across domains."""
    return (
        get_sample_search_features() +
        get_sample_observability_features() +
        get_sample_security_features()
    )


# Legacy data for backwards compatibility
SAMPLE_FEATURES = [
    {
        "id": "bbq-001",
        "name": "Better Binary Quantization",
        "description": "95% memory reduction with improved ranking quality",
        "benefits": [
            "Reduces memory usage by 95%",
            "Improves ranking quality",
            "Faster query performance"
        ],
        "documentation_links": [
            "https://elastic.co/blog/bbq"
        ],
        "theme": "optimize",
        "domain": "search"
    },
    {
        "id": "acorn-001",
        "name": "ACORN Filtered Vector Search",
        "description": "Up to 5x faster filtered searches",
        "benefits": [
            "5x faster filtered vector search",
            "No accuracy loss",
            "Flexible filter definition"
        ],
        "theme": "optimize",
        "domain": "search"
    }
]

SAMPLE_PRESENTATION_CONTENT = {
    "title": "Three Game-Changing Innovations",
    "slides": [
        {
            "theme": "simplify",
            "title": "Simplify - Do more with less",
            "features": ["Cross-Cluster Search", "AutoOps", "Managed LLM"]
        },
        {
            "theme": "optimize", 
            "title": "Optimize - Do it faster",
            "features": ["BBQ", "ACORN", "ELSER Token Pruning"]
        },
        {
            "theme": "ai_innovation",
            "title": "AI Innovation - Do it with AI", 
            "features": ["Agent Builder", "Inference Service", "ELSER/E5"]
        }
    ]
}

SAMPLE_LAB_DATA = {
    "ecommerce_products": [
        {
            "id": "prod-001",
            "name": "Wireless Headphones",
            "description": "High-quality wireless headphones with noise cancellation",
            "category": "Electronics",
            "price": 199.99,
            "rating": 4.5
        }
    ],
    "security_events": [
        {
            "timestamp": "2025-01-15T10:30:00Z",
            "event_type": "login_attempt",
            "source_ip": "192.168.1.100",
            "user": "admin",
            "status": "failed",
            "risk_score": 8.5
        }
    ]
}


def get_sample_web_response():
    """Get sample web scraping response for testing."""
    return {
        "title": "Better Binary Quantization",
        "content": "BBQ reduces memory usage significantly while maintaining search quality...",
        "benefits": [
            "95% memory reduction",
            "Better ranking quality",
            "Faster query performance"
        ],
        "code_examples": [
            'PUT /my-index/_settings\n{\n  "index": {\n    "knn": {\n      "bbq": {\n        "enabled": true\n      }\n    }\n  }\n}'
        ],
        "url": "https://elastic.co/blog/bbq",
        "scraped_at": 1640995200.0
    }


def get_sample_presentation_config():
    """Get sample presentation configuration."""
    return {
        "domain": "search",
        "quarter": "Q1-2024",
        "title": "Search Innovations Q1 2024",
        "audience": "technical",
        "themes": ["optimize", "ai_innovation", "simplify"],
        "feature_ids": ["bbq-001", "agent-builder-001", "cross-cluster-001"]
    }


def get_sample_lab_config():
    """Get sample lab configuration."""
    return {
        "domain": "search",
        "feature_id": "bbq-001",
        "difficulty": "intermediate",
        "estimated_time": 45,
        "scenario_type": "ecommerce_search",
        "sample_data": {
            "index_name": "ecommerce_products",
            "document_count": 10000,
            "data_type": "product_catalog"
        }
    }