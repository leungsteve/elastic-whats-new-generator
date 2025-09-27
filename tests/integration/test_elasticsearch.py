import pytest
from src.integrations.elasticsearch import FeatureStorage
from src.core.models import Feature, Theme

class TestElasticsearchIntegration:
    
    def test_store_and_retrieve_feature(self, feature_storage, sample_feature):
        """Test storing and retrieving features"""
        # Store feature
        result = feature_storage.store(sample_feature)
        assert result["_id"]
        
        # Retrieve feature
        retrieved = feature_storage.get_by_id(sample_feature.id)
        assert retrieved.name == sample_feature.name
        assert retrieved.theme == sample_feature.theme
    
    def test_search_features_by_theme(self, feature_storage):
        """Test searching features by theme"""
        # Store features with different themes
        features = [
            Feature(id="f1", name="Feature 1", description="Desc 1", 
                   domain="search", theme=Theme.OPTIMIZE),
            Feature(id="f2", name="Feature 2", description="Desc 2", 
                   domain="search", theme=Theme.SIMPLIFY)
        ]
        
        for feature in features:
            feature_storage.store(feature)
        
        # Search by theme
        optimize_features = feature_storage.search_by_theme(Theme.OPTIMIZE)
        assert len(optimize_features) >= 1
        assert all(f.theme == Theme.OPTIMIZE for f in optimize_features)
    
    def test_get_features_by_domain(self, feature_storage):
        """Test retrieving features by domain"""
        features = feature_storage.get_by_domain("search")
        assert isinstance(features, list)
        # Verify all returned features are from search domain
        for feature in features:
            assert feature.domain == "search"