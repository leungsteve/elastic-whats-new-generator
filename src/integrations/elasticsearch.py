"""
Elasticsearch integration for feature storage and retrieval.

This module provides the FeatureStorage class for persisting and querying
feature data in Elasticsearch.
"""

import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from elasticsearch import Elasticsearch
from src.core.models import Feature, Theme, Domain


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
            "scraped_content": feature.scraped_content,
            "created_at": feature.created_at.isoformat(),
            "updated_at": feature.updated_at.isoformat()
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
                    "fields": ["name", "description", "benefits", "scraped_content"]
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
                        "scraped_content": {"type": "text", "analyzer": "standard"},
                        "created_at": {"type": "date"},
                        "updated_at": {"type": "date"}
                    }
                }
            }

            self.es.indices.create(index=self.index_name, body=mapping)

    def _doc_to_feature(self, doc: Dict[str, Any]) -> Feature:
        """Convert Elasticsearch document to Feature object."""
        return Feature(
            id=doc["id"],
            name=doc["name"],
            description=doc["description"],
            benefits=doc.get("benefits", []),
            documentation_links=doc.get("documentation_links", []),
            theme=Theme(doc["theme"]) if doc.get("theme") else None,
            domain=Domain(doc["domain"]),
            scraped_content=doc.get("scraped_content"),
            created_at=datetime.fromisoformat(doc["created_at"]),
            updated_at=datetime.fromisoformat(doc["updated_at"])
        )