"""
Elasticsearch integration for feature storage and retrieval.

This module provides the FeatureStorage class for persisting and querying
feature data in Elasticsearch.
"""

import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from elasticsearch import Elasticsearch
from src.core.models import Feature, Theme, Domain, ContentResearch


class FeatureStorage:
    """Elasticsearch-based storage for features."""

    def __init__(self, es_client: Elasticsearch, index_name: str = "elastic-features"):
        """
        Initialize the feature storage.

        Args:
            es_client: Elasticsearch client instance
            index_name: Name of the index to store features
        """
        self.es = es_client
        self.index_name = index_name
        self._ensure_index_exists()

    def store(self, feature: Feature) -> Dict[str, Any]:
        """
        Store a feature in Elasticsearch.

        Args:
            feature: The feature to store

        Returns:
            Elasticsearch response with document ID
        """
        doc = {
            "id": feature.id,
            "name": feature.name,
            "description": feature.description,
            "benefits": feature.benefits,
            "documentation_links": feature.documentation_links,
            "theme": feature.theme.value if feature.theme else None,
            "domain": feature.domain.value,
            "created_at": feature.created_at.isoformat(),
            "updated_at": feature.updated_at.isoformat(),
            "content_research": feature.content_research.dict() if feature.content_research else None
        }

        return self.es.index(
            index=self.index_name,
            id=feature.id,
            document=doc
        )

    def get_by_id(self, feature_id: str) -> Optional[Feature]:
        """
        Retrieve a feature by ID.

        Args:
            feature_id: The feature ID to retrieve

        Returns:
            Feature object if found, None otherwise
        """
        try:
            response = self.es.get(index=self.index_name, id=feature_id)
            return self._doc_to_feature(response["_source"])
        except Exception:
            return None

    def search_by_theme(self, theme: Theme, size: int = 50) -> List[Feature]:
        """
        Search features by theme.

        Args:
            theme: The theme to search for
            size: Maximum number of results

        Returns:
            List of features matching the theme
        """
        query = {
            "query": {
                "term": {
                    "theme": theme.value
                }
            },
            "size": size
        }

        response = self.es.search(index=self.index_name, body=query)
        return [self._doc_to_feature(hit["_source"]) for hit in response["hits"]["hits"]]

    def get_by_domain(self, domain: str, size: int = 50) -> List[Feature]:
        """
        Get features by domain (alias for search_by_domain with string input).

        Args:
            domain: The domain string to search for
            size: Maximum number of results

        Returns:
            List of features matching the domain
        """
        domain_enum = Domain(domain)
        return self.search_by_domain(domain_enum, size)

    def search_by_domain(self, domain: Domain, size: int = 50) -> List[Feature]:
        """
        Search features by domain.

        Args:
            domain: The domain to search for
            size: Maximum number of results

        Returns:
            List of features matching the domain
        """
        query = {
            "query": {
                "term": {
                    "domain": domain.value
                }
            },
            "size": size
        }

        response = self.es.search(index=self.index_name, body=query)
        return [self._doc_to_feature(hit["_source"]) for hit in response["hits"]["hits"]]

    def search_features(self, query_text: str, size: int = 50) -> List[Feature]:
        """
        Full-text search across features.

        Args:
            query_text: Text to search for
            size: Maximum number of results

        Returns:
            List of features matching the search
        """
        query = {
            "query": {
                "multi_match": {
                    "query": query_text,
                    "fields": [
                        "name", "description", "benefits",
                        "content_research.extracted_content.key_concepts",
                        "content_research.ai_insights.technical_summary",
                        "content_research.primary_sources.content"
                    ]
                }
            },
            "size": size
        }

        response = self.es.search(index=self.index_name, body=query)
        return [self._doc_to_feature(hit["_source"]) for hit in response["hits"]["hits"]]

    def get_all_features(self, size: int = 1000) -> List[Feature]:
        """
        Get all features from the index.

        Args:
            size: Maximum number of results

        Returns:
            List of all features
        """
        query = {
            "query": {
                "match_all": {}
            },
            "size": size
        }

        response = self.es.search(index=self.index_name, body=query)
        return [self._doc_to_feature(hit["_source"]) for hit in response["hits"]["hits"]]

    def delete_feature(self, feature_id: str) -> bool:
        """
        Delete a feature by ID.

        Args:
            feature_id: The feature ID to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            self.es.delete(index=self.index_name, id=feature_id)
            return True
        except Exception:
            return False

    def _ensure_index_exists(self):
        """Ensure the features index exists with proper mapping."""
        if not self.es.indices.exists(index=self.index_name):
            mapping = {
                "mappings": {
                    "properties": {
                        "id": {"type": "keyword"},
                        "name": {"type": "text", "analyzer": "standard"},
                        "description": {"type": "text", "analyzer": "standard"},
                        "benefits": {"type": "text", "analyzer": "standard"},
                        "documentation_links": {"type": "keyword"},
                        "theme": {"type": "keyword"},
                        "domain": {"type": "keyword"},
                        "created_at": {"type": "date"},
                        "updated_at": {"type": "date"},

                        # Content research structure
                        "content_research": {
                            "properties": {
                                "status": {"type": "keyword"},
                                "last_updated": {"type": "date"},
                                "scraping_enabled": {"type": "boolean"},
                                "research_depth": {"type": "keyword"},

                                # Primary sources
                                "primary_sources": {
                                    "type": "nested",
                                    "properties": {
                                        "url": {"type": "keyword"},
                                        "title": {"type": "text", "analyzer": "standard"},
                                        "content": {"type": "text", "analyzer": "standard"},
                                        "scraped_at": {"type": "date"},
                                        "content_type": {"type": "keyword"},
                                        "word_count": {"type": "integer"},
                                        "status": {"type": "keyword"},
                                        "metadata": {
                                            "properties": {
                                                "page_sections": {"type": "keyword"},
                                                "code_examples": {"type": "integer"},
                                                "images": {"type": "integer"},
                                                "language": {"type": "keyword"}
                                            }
                                        }
                                    }
                                },

                                # Related sources
                                "related_sources": {
                                    "type": "nested",
                                    "properties": {
                                        "url": {"type": "keyword"},
                                        "title": {"type": "text", "analyzer": "standard"},
                                        "content": {"type": "text", "analyzer": "standard"},
                                        "relevance_score": {"type": "float"},
                                        "content_type": {"type": "keyword"}
                                    }
                                },

                                # Extracted content
                                "extracted_content": {
                                    "properties": {
                                        "key_concepts": {"type": "keyword"},
                                        "configuration_examples": {
                                            "type": "nested",
                                            "properties": {
                                                "title": {"type": "text"},
                                                "code": {"type": "text"},
                                                "description": {"type": "text"},
                                                "language": {"type": "keyword"}
                                            }
                                        },
                                        "use_cases": {
                                            "type": "nested",
                                            "properties": {
                                                "title": {"type": "text"},
                                                "description": {"type": "text"},
                                                "complexity": {"type": "keyword"},
                                                "estimated_time": {"type": "keyword"}
                                            }
                                        },
                                        "prerequisites": {"type": "text"},
                                        "related_features": {"type": "keyword"},
                                        "performance_considerations": {"type": "text"}
                                    }
                                },

                                # AI insights
                                "ai_insights": {
                                    "properties": {
                                        "technical_summary": {"type": "text", "analyzer": "standard"},
                                        "business_value": {"type": "text", "analyzer": "standard"},
                                        "implementation_complexity": {"type": "keyword"},
                                        "learning_curve": {"type": "keyword"},
                                        "recommended_audience": {"type": "keyword"},
                                        "content_themes": {"type": "keyword"}
                                    }
                                },

                                # ELSER embeddings
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
                                                "text": {"type": "text", "analyzer": "standard"},
                                                "elser_embedding": {"type": "sparse_vector"},
                                                "generated_at": {"type": "date"},
                                                "model_version": {"type": "keyword"}
                                            }
                                        },
                                        "full_documentation": {
                                            "properties": {
                                                "text": {"type": "text", "analyzer": "standard"},
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

            self.es.indices.create(index=self.index_name, body=mapping)

    def _doc_to_feature(self, doc: Dict[str, Any]) -> Feature:
        """Convert Elasticsearch document to Feature object."""
        # Handle content research data
        content_research = None
        if doc.get("content_research"):
            try:
                content_research = ContentResearch.parse_obj(doc["content_research"])
            except Exception:
                # If parsing fails, create empty ContentResearch
                content_research = ContentResearch()
        else:
            content_research = ContentResearch()

        return Feature(
            id=doc["id"],
            name=doc["name"],
            description=doc["description"],
            benefits=doc.get("benefits", []),
            documentation_links=doc.get("documentation_links") or [],
            theme=Theme(doc["theme"]) if doc.get("theme") else None,
            domain=Domain(doc["domain"]),
            created_at=datetime.fromisoformat(doc["created_at"]),
            updated_at=datetime.fromisoformat(doc["updated_at"]),
            content_research=content_research
        )

class LLMUsageStorage:
    """Elasticsearch-based storage for LLM usage logs."""

    def __init__(self, es_client: Elasticsearch, index_name: str = "llm-usage-logs"):
        """
        Initialize the LLM usage log storage.

        Args:
            es_client: Elasticsearch client instance
            index_name: Name of the index to store logs
        """
        self.es = es_client
        self.index_name = index_name
        self._ensure_index_exists()

    def _ensure_index_exists(self):
        """Create the index with appropriate mappings if it doesn't exist."""
        if not self.es.indices.exists(index=self.index_name):
            mappings = {
                "mappings": {
                    "properties": {
                        "id": {"type": "keyword"},
                        "timestamp": {"type": "date"},
                        "provider": {"type": "keyword"},
                        "model": {"type": "keyword"},
                        "operation_type": {"type": "keyword"},
                        "feature_ids": {"type": "keyword"},
                        "domain": {"type": "keyword"},
                        "system_prompt": {"type": "text"},
                        "user_prompt": {"type": "text"},
                        "response_text": {"type": "text"},
                        "token_usage": {
                            "type": "object",
                            "properties": {
                                "prompt_tokens": {"type": "integer"},
                                "completion_tokens": {"type": "integer"},
                                "total_tokens": {"type": "integer"}
                            }
                        },
                        "response_time_seconds": {"type": "float"},
                        "success": {"type": "boolean"},
                        "error_message": {"type": "text"},
                        "estimated_cost_usd": {"type": "float"}
                    }
                }
            }
            self.es.indices.create(index=self.index_name, body=mappings)

    def log(self, log_entry: 'LLMUsageLog') -> Dict[str, Any]:
        """
        Store an LLM usage log entry.

        Args:
            log_entry: The LLM usage log to store

        Returns:
            Elasticsearch response with document ID
        """
        from src.core.models import LLMUsageLog
        
        doc = log_entry.dict()
        
        return self.es.index(
            index=self.index_name,
            id=log_entry.id,
            document=doc
        )

    def get_by_id(self, log_id: str) -> Optional['LLMUsageLog']:
        """
        Retrieve a log entry by ID.

        Args:
            log_id: The log ID to retrieve

        Returns:
            LLMUsageLog object if found, None otherwise
        """
        from src.core.models import LLMUsageLog
        
        try:
            response = self.es.get(index=self.index_name, id=log_id)
            return LLMUsageLog(**response["_source"])
        except Exception:
            return None

    def search_by_operation(self, operation_type: str, size: int = 100) -> List[Dict[str, Any]]:
        """
        Search logs by operation type.

        Args:
            operation_type: The operation type to search for
            size: Maximum number of results

        Returns:
            List of log entries matching the operation type
        """
        query = {
            "query": {
                "term": {
                    "operation_type": operation_type
                }
            },
            "size": size,
            "sort": [{"timestamp": {"order": "desc"}}]
        }

        response = self.es.search(index=self.index_name, body=query)
        return [hit["_source"] for hit in response["hits"]["hits"]]

    def get_usage_analytics(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get usage analytics for a date range.

        Args:
            start_date: Start date for analytics
            end_date: End date for analytics

        Returns:
            Dictionary with usage statistics
        """
        date_filter = {}
        if start_date or end_date:
            date_filter = {"range": {"timestamp": {}}}
            if start_date:
                date_filter["range"]["timestamp"]["gte"] = start_date.isoformat()
            if end_date:
                date_filter["range"]["timestamp"]["lte"] = end_date.isoformat()

        query = {
            "size": 0,
            "query": {"bool": {"filter": [date_filter]}} if date_filter else {"match_all": {}},
            "aggs": {
                "by_provider": {
                    "terms": {"field": "provider"}
                },
                "by_operation": {
                    "terms": {"field": "operation_type"}
                },
                "total_tokens": {
                    "sum": {"field": "token_usage.total_tokens"}
                },
                "total_cost": {
                    "sum": {"field": "estimated_cost_usd"}
                },
                "avg_response_time": {
                    "avg": {"field": "response_time_seconds"}
                },
                "success_rate": {
                    "avg": {"field": "success"}
                }
            }
        }

        response = self.es.search(index=self.index_name, body=query)
        aggs = response["aggregations"]

        return {
            "total_calls": response["hits"]["total"]["value"],
            "by_provider": {bucket["key"]: bucket["doc_count"] for bucket in aggs["by_provider"]["buckets"]},
            "by_operation": {bucket["key"]: bucket["doc_count"] for bucket in aggs["by_operation"]["buckets"]},
            "total_tokens": aggs["total_tokens"]["value"],
            "total_cost_usd": aggs["total_cost"]["value"],
            "avg_response_time_seconds": aggs["avg_response_time"]["value"],
            "success_rate": aggs["success_rate"]["value"]
        }

    def search_by_provider(self, provider: str, size: int = 50) -> List[Dict[str, Any]]:
        """
        Search for LLM usage logs by provider.

        Args:
            provider: LLM provider (openai, gemini, claude)
            size: Maximum number of results

        Returns:
            List of matching log entries
        """
        query = {
            "size": size,
            "query": {
                "term": {"provider": provider}
            },
            "sort": [{"timestamp": {"order": "desc"}}]
        }

        response = self.es.search(index=self.index_name, body=query)
        return [hit["_source"] for hit in response["hits"]["hits"]]

    def get_recent_logs(self, start_date: Optional[datetime] = None, size: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent LLM usage logs.

        Args:
            start_date: Optional start date filter
            size: Maximum number of results

        Returns:
            List of recent log entries
        """
        query = {
            "size": size,
            "sort": [{"timestamp": {"order": "desc"}}]
        }

        if start_date:
            query["query"] = {
                "range": {
                    "timestamp": {
                        "gte": start_date.isoformat()
                    }
                }
            }
        else:
            query["query"] = {"match_all": {}}

        response = self.es.search(index=self.index_name, body=query)
        return [hit["_source"] for hit in response["hits"]["hits"]]


class GeneratedContentStorage:
    """Elasticsearch-based storage for generated presentations and labs."""

    def __init__(self, es_client: Elasticsearch, index_name: str = "generated-content"):
        """
        Initialize the generated content storage.

        Args:
            es_client: Elasticsearch client instance
            index_name: Name of the index to store content
        """
        self.es = es_client
        self.index_name = index_name
        self._ensure_index_exists()

    def _ensure_index_exists(self):
        """Create the index with appropriate mappings if it doesn't exist."""
        if not self.es.indices.exists(index=self.index_name):
            mappings = {
                "mappings": {
                    "properties": {
                        "id": {"type": "keyword"},
                        "timestamp": {"type": "date"},
                        "content_type": {"type": "keyword"},
                        "title": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                        "domain": {"type": "keyword"},
                        "feature_ids": {"type": "keyword"},
                        "feature_names": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                        "markdown_content": {"type": "text"},
                        "structured_data": {"type": "object", "enabled": False},
                        "generation_params": {"type": "object", "enabled": False},
                        "llm_usage_log_id": {"type": "keyword"},
                        "user_id": {"type": "keyword"},
                        "tags": {"type": "keyword"},
                        "version": {"type": "integer"}
                    }
                }
            }
            self.es.indices.create(index=self.index_name, body=mappings)

    def store(self, content: 'GeneratedContent') -> Dict[str, Any]:
        """
        Store generated content.

        Args:
            content: The generated content to store

        Returns:
            Elasticsearch response with document ID
        """
        from src.core.models import GeneratedContent
        
        doc = content.dict()
        
        return self.es.index(
            index=self.index_name,
            id=content.id,
            document=doc
        )

    def get_by_id(self, content_id: str) -> Optional['GeneratedContent']:
        """
        Retrieve generated content by ID.

        Args:
            content_id: The content ID to retrieve

        Returns:
            GeneratedContent object if found, None otherwise
        """
        from src.core.models import GeneratedContent
        
        try:
            response = self.es.get(index=self.index_name, id=content_id)
            return GeneratedContent(**response["_source"])
        except Exception:
            return None

    def search_by_type(self, content_type: str, size: int = 50) -> List[Dict[str, Any]]:
        """
        Search content by type (presentation, lab).

        Args:
            content_type: The content type to search for
            size: Maximum number of results

        Returns:
            List of content entries matching the type
        """
        query = {
            "query": {
                "term": {
                    "content_type": content_type
                }
            },
            "size": size,
            "sort": [{"timestamp": {"order": "desc"}}]
        }

        response = self.es.search(index=self.index_name, body=query)
        return [hit["_source"] for hit in response["hits"]["hits"]]

    def search_by_features(self, feature_ids: List[str], size: int = 50) -> List[Dict[str, Any]]:
        """
        Search content by feature IDs.

        Args:
            feature_ids: List of feature IDs to search for
            size: Maximum number of results

        Returns:
            List of content entries containing these features
        """
        query = {
            "query": {
                "terms": {
                    "feature_ids": feature_ids
                }
            },
            "size": size,
            "sort": [{"timestamp": {"order": "desc"}}]
        }

        response = self.es.search(index=self.index_name, body=query)
        return [hit["_source"] for hit in response["hits"]["hits"]]

    def get_recent_content(self, content_type: Optional[str] = None, size: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent generated content, optionally filtered by type.

        Args:
            content_type: Optional content type filter
            size: Maximum number of results

        Returns:
            List of recent content entries
        """
        query = {
            "size": size,
            "sort": [{"timestamp": {"order": "desc"}}]
        }

        if content_type:
            query["query"] = {
                "term": {
                    "content_type": content_type
                }
            }
        else:
            query["query"] = {"match_all": {}}

        response = self.es.search(index=self.index_name, body=query)
        return [hit["_source"] for hit in response["hits"]["hits"]]

    def search_by_domain(self, domain: str, size: int = 50) -> List[Dict[str, Any]]:
        """
        Search for generated content by domain.

        Args:
            domain: Domain to search for (search, observability, security, all_domains)
            size: Maximum number of results

        Returns:
            List of matching content entries
        """
        query = {
            "size": size,
            "query": {
                "term": {"domain": domain}
            },
            "sort": [{"timestamp": {"order": "desc"}}]
        }

        response = self.es.search(index=self.index_name, body=query)
        return [hit["_source"] for hit in response["hits"]["hits"]]

    def search_by_tags(self, tags: List[str], size: int = 50) -> List[Dict[str, Any]]:
        """
        Search for generated content by tags.

        Args:
            tags: List of tags to search for
            size: Maximum number of results

        Returns:
            List of matching content entries
        """
        query = {
            "size": size,
            "query": {
                "terms": {"tags": tags}
            },
            "sort": [{"timestamp": {"order": "desc"}}]
        }

        response = self.es.search(index=self.index_name, body=query)
        return [hit["_source"] for hit in response["hits"]["hits"]]
