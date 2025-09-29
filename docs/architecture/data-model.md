# Data Model Architecture

## Overview

The Elastic What's New Generator uses a sophisticated data model that combines basic feature metadata with enriched content research and ELSER semantic embeddings to enable intelligent content generation and discovery.

## Core Data Structure

### Base Feature Document
```json
{
  "id": "search-001",
  "name": "Advanced Search Filters",
  "description": "Sophisticated filtering capabilities for Elasticsearch queries",
  "domain": "search|observability|security",
  "theme": "optimize|innovate|scale|secure",
  "benefits": ["Improved performance", "Better UX", "Cost reduction"],
  "documentation_links": ["https://elastic.co/guide/..."],
  "created_at": "2025-09-28T17:45:00Z",

  // Enhanced content research structure
  "content_research": { /* see below */ }
}
```

## Content Research Structure

### Research Status and Metadata
```json
"content_research": {
  "status": "completed|in_progress|failed|pending",
  "last_updated": "2025-09-28T17:45:00Z",
  "scraping_enabled": true,
  "research_depth": "basic|standard|comprehensive",

  // Source content structure
  "primary_sources": [ /* see Primary Sources */ ],
  "related_sources": [ /* see Related Sources */ ],
  "extracted_content": { /* see Extracted Content */ },
  "ai_insights": { /* see AI Insights */ },
  "embeddings": { /* see ELSER Embeddings */ }
}
```

### Primary Sources
```json
"primary_sources": [
  {
    "url": "https://elastic.co/guide/en/elasticsearch/reference/current/search-request-body.html",
    "title": "Search Request Body",
    "scraped_at": "2025-09-28T17:30:00Z",
    "content_type": "documentation",
    "status": "success|failed|skipped",
    "word_count": 2500,
    "content": "Full scraped text content...",
    "metadata": {
      "page_sections": ["Overview", "Query DSL", "Filters", "Examples"],
      "code_examples": 8,
      "images": 3,
      "last_modified": "2025-09-15",
      "language": "en"
    },
    "links_found": [
      "https://elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html",
      "https://elastic.co/blog/elasticsearch-query-performance"
    ]
  }
]
```

### Related Sources
```json
"related_sources": [
  {
    "url": "https://elastic.co/blog/elasticsearch-query-performance",
    "title": "Optimizing Elasticsearch Query Performance",
    "source_url": "https://elastic.co/guide/.../search-request-body.html",
    "discovery_method": "link_following|semantic_search|manual",
    "relevance_score": 0.85,
    "content": "Scraped blog content...",
    "scraped_at": "2025-09-28T17:35:00Z",
    "content_type": "blog|tutorial|video|forum",
    "metadata": {
      "author": "Elastic Team",
      "publish_date": "2025-08-15",
      "tags": ["performance", "queries", "optimization"]
    }
  }
]
```

### Extracted Content
```json
"extracted_content": {
  "key_concepts": [
    "query DSL",
    "bool queries",
    "filter context",
    "aggregations",
    "performance optimization"
  ],
  "configuration_examples": [
    {
      "title": "Basic Bool Query with Filters",
      "code": "{\n  \"query\": {\n    \"bool\": {\n      \"filter\": [\n        {\"term\": {\"status\": \"published\"}},\n        {\"range\": {\"publish_date\": {\"gte\": \"2024-01-01\"}}}\n      ]\n    }\n  }\n}",
      "description": "Demonstrates basic filtering without scoring",
      "language": "json"
    }
  ],
  "use_cases": [
    {
      "title": "E-commerce Product Filtering",
      "description": "Filter products by category, price range, and availability",
      "complexity": "beginner",
      "estimated_time": "30 minutes"
    },
    {
      "title": "Log Analysis with Time Ranges",
      "description": "Analyze application logs within specific time windows",
      "complexity": "intermediate",
      "estimated_time": "45 minutes"
    }
  ],
  "prerequisites": [
    "Elasticsearch 8.x installed",
    "Index with appropriate mapping",
    "Basic understanding of JSON"
  ],
  "related_features": [
    "aggregations",
    "query-dsl",
    "mapping",
    "index-templates"
  ],
  "performance_considerations": [
    "Use filter context for exact matches",
    "Avoid script queries in filters",
    "Consider index sorting for range queries"
  ]
}
```

### AI Insights
```json
"ai_insights": {
  "technical_summary": "Advanced search filters provide sophisticated querying capabilities through Elasticsearch's bool query structure, enabling efficient data retrieval with minimal performance impact.",
  "business_value": "Improves user experience by enabling precise data discovery, reduces server load through optimized query execution, and provides foundation for advanced analytics workflows.",
  "implementation_complexity": "medium",
  "learning_curve": "moderate",
  "recommended_audience": ["developers", "data engineers", "solution architects"],
  "presentation_angles": [
    {
      "angle": "Performance Optimization",
      "description": "Focus on query efficiency and resource usage",
      "target_audience": "technical"
    },
    {
      "angle": "User Experience Enhancement",
      "description": "Emphasize improved search relevance and speed",
      "target_audience": "business"
    }
  ],
  "lab_scenarios": [
    {
      "title": "E-commerce Search Implementation",
      "description": "Build a product search with multiple filter criteria",
      "difficulty": "intermediate",
      "duration": "60 minutes",
      "technologies": ["Elasticsearch", "Kibana", "sample data"]
    },
    {
      "title": "Log Filtering Workshop",
      "description": "Analyze application logs using bool queries and filters",
      "difficulty": "beginner",
      "duration": "45 minutes",
      "technologies": ["Elasticsearch", "Filebeat", "sample logs"]
    }
  ],
  "content_themes": [
    "query-optimization",
    "search-relevance",
    "performance-tuning",
    "data-discovery"
  ]
}
```

## ELSER Embeddings Strategy

### Embedding Fields Structure
```json
"embeddings": {
  "feature_summary": {
    "text": "Advanced Search Filters - Sophisticated filtering capabilities for Elasticsearch queries. Benefits: Improved query performance, Better user experience, Reduced server load. Business value: Improves user experience by enabling precise data discovery and reduces infrastructure costs through optimized queries.",
    "elser_embedding": {
      /* ELSER sparse vector representation */
    },
    "generated_at": "2025-09-28T17:45:00Z",
    "model_version": ".elser_model_2"
  },
  "technical_content": {
    "text": "Key concepts: query DSL, bool queries, filter context, aggregations, performance optimization. Use cases: E-commerce product filtering, Log analysis with time ranges, Real-time search applications. Configuration: {\"query\": {\"bool\": {\"filter\": [...]}}}. Prerequisites: Elasticsearch 8.x, Index mapping configured.",
    "elser_embedding": {
      /* ELSER sparse vector representation */
    },
    "generated_at": "2025-09-28T17:45:00Z",
    "model_version": ".elser_model_2"
  },
  "full_documentation": {
    "text": "Combined content from all primary and related sources...",
    "elser_embedding": {
      /* ELSER sparse vector representation */
    },
    "generated_at": "2025-09-28T17:45:00Z",
    "model_version": ".elser_model_2"
  }
}
```

### Embedding Text Composition

**Feature Summary Embedding:**
- Feature name + description
- Key benefits
- Business value summary
- Target audience indicators

**Technical Content Embedding:**
- Key technical concepts
- Configuration examples (code)
- Use cases and scenarios
- Prerequisites and dependencies
- Related features

**Full Documentation Embedding:**
- Complete scraped content from all sources
- Processed and cleaned text
- Code examples with context
- Related discussions and insights

## Elasticsearch Mapping

### Index Template
```json
{
  "index_patterns": ["elastic-whats-new-features*"],
  "template": {
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 1,
      "analysis": {
        "analyzer": {
          "technical_content": {
            "type": "standard",
            "stopwords": ["_english_"]
          }
        }
      }
    },
    "mappings": {
      "properties": {
        "id": {"type": "keyword"},
        "name": {"type": "text", "analyzer": "standard"},
        "description": {"type": "text", "analyzer": "standard"},
        "domain": {"type": "keyword"},
        "theme": {"type": "keyword"},
        "benefits": {"type": "text", "analyzer": "standard"},
        "documentation_links": {"type": "keyword"},
        "created_at": {"type": "date"},

        "content_research": {
          "properties": {
            "status": {"type": "keyword"},
            "last_updated": {"type": "date"},
            "scraping_enabled": {"type": "boolean"},
            "research_depth": {"type": "keyword"},

            "primary_sources": {
              "type": "nested",
              "properties": {
                "url": {"type": "keyword"},
                "title": {"type": "text", "analyzer": "standard"},
                "content": {"type": "text", "analyzer": "technical_content"},
                "scraped_at": {"type": "date"},
                "word_count": {"type": "integer"},
                "metadata": {
                  "properties": {
                    "page_sections": {"type": "keyword"},
                    "code_examples": {"type": "integer"},
                    "language": {"type": "keyword"}
                  }
                }
              }
            },

            "related_sources": {
              "type": "nested",
              "properties": {
                "url": {"type": "keyword"},
                "title": {"type": "text", "analyzer": "standard"},
                "content": {"type": "text", "analyzer": "technical_content"},
                "relevance_score": {"type": "float"},
                "content_type": {"type": "keyword"}
              }
            },

            "extracted_content": {
              "properties": {
                "key_concepts": {"type": "keyword"},
                "use_cases": {
                  "type": "nested",
                  "properties": {
                    "title": {"type": "text"},
                    "description": {"type": "text"},
                    "complexity": {"type": "keyword"},
                    "estimated_time": {"type": "keyword"}
                  }
                },
                "related_features": {"type": "keyword"},
                "prerequisites": {"type": "text"}
              }
            },

            "ai_insights": {
              "properties": {
                "technical_summary": {"type": "text", "analyzer": "standard"},
                "business_value": {"type": "text", "analyzer": "standard"},
                "implementation_complexity": {"type": "keyword"},
                "recommended_audience": {"type": "keyword"},
                "content_themes": {"type": "keyword"}
              }
            },

            "embeddings": {
              "properties": {
                "feature_summary": {
                  "properties": {
                    "text": {"type": "text", "analyzer": "standard"},
                    "elser_embedding": {"type": "sparse_vector"},
                    "generated_at": {"type": "date"},
                    "model_version": {"type": "keyword"}
                  }
                },
                "technical_content": {
                  "properties": {
                    "text": {"type": "text", "analyzer": "technical_content"},
                    "elser_embedding": {"type": "sparse_vector"},
                    "generated_at": {"type": "date"},
                    "model_version": {"type": "keyword"}
                  }
                },
                "full_documentation": {
                  "properties": {
                    "text": {"type": "text", "analyzer": "technical_content"},
                    "elser_embedding": {"type": "sparse_vector"},
                    "generated_at": {"type": "date"},
                    "model_version": {"type": "keyword"}
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

## Search and Query Patterns

### Semantic Search Examples

**Find related features:**
```json
{
  "query": {
    "text_expansion": {
      "content_research.embeddings.feature_summary.elser_embedding": {
        "model_id": ".elser_model_2",
        "model_text": "features that improve query performance and reduce latency"
      }
    }
  }
}
```

**Technical content discovery:**
```json
{
  "query": {
    "text_expansion": {
      "content_research.embeddings.technical_content.elser_embedding": {
        "model_id": ".elser_model_2",
        "model_text": "machine learning anomaly detection configuration"
      }
    }
  }
}
```

**Hybrid search (semantic + keyword):**
```json
{
  "query": {
    "bool": {
      "should": [
        {
          "text_expansion": {
            "content_research.embeddings.feature_summary.elser_embedding": {
              "model_id": ".elser_model_2",
              "model_text": "security threat detection"
            }
          }
        },
        {
          "multi_match": {
            "query": "SIEM security analytics",
            "fields": ["name^2", "description", "content_research.extracted_content.key_concepts"]
          }
        }
      ]
    }
  }
}
```

## Data Lifecycle Management

### Content Research Workflow
1. **Feature Creation**: Basic metadata stored immediately
2. **Content Research Trigger**: Initiated automatically or manually
3. **Primary Source Scraping**: Fetch content from provided documentation links
4. **Related Source Discovery**: Follow embedded links, search for related content
5. **Content Extraction**: Use AI to extract structured information
6. **AI Insights Generation**: Generate summaries and recommendations
7. **ELSER Embedding**: Create semantic embeddings for search
8. **Storage**: Update feature document with enriched content

### Update Strategy
- **Incremental Updates**: Update only `content_research` object without affecting core feature data
- **Versioning**: Track timestamps for cache invalidation and freshness
- **Status Tracking**: Monitor scraping progress and handle failures gracefully
- **Refresh Policy**: Re-scrape content based on configurable intervals or manual triggers

### Performance Considerations
- **Document Size**: Monitor document size growth with rich content
- **Search Performance**: Use appropriate analyzers and mapping configurations
- **Embedding Generation**: Batch process ELSER embeddings for efficiency
- **Storage Optimization**: Consider archiving old content research data

This data model provides the foundation for intelligent content discovery, rich presentation generation, and advanced lab creation while showcasing Elastic's semantic search capabilities through ELSER integration.