"""Sample data for testing"""

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