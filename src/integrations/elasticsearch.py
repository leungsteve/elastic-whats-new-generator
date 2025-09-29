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