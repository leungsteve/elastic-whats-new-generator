import pytest
from src.core.classifier import FeatureClassifier
from src.core.models import Feature, Theme

class TestFeatureClassifier:
    
    def test_classify_optimization_feature(self, sample_feature):
        """Test classification of optimization features"""
        # BBQ with performance benefits should be OPTIMIZE
        classifier = FeatureClassifier()
        theme = classifier.classify(sample_feature)
        assert theme == Theme.OPTIMIZE
    
    def test_classify_simplification_feature(self):
        """Test classification of simplification features"""
        feature = Feature(
            id="autoops-001",
            name="AutoOps",
            description="Automated monitoring and alerting",
            benefits=["Reduces operational overhead", "Simplifies monitoring"],
            domain="search"
        )
        
        classifier = FeatureClassifier()
        theme = classifier.classify(feature)
        assert theme == Theme.SIMPLIFY
    
    def test_classify_ai_feature(self):
        """Test classification of AI features"""
        feature = Feature(
            id="agent-builder-001",
            name="Agent Builder",
            description="Framework for building AI agents",
            benefits=["AI-powered workflows", "Intelligent automation"],
            domain="search"
        )
        
        classifier = FeatureClassifier()
        theme = classifier.classify(feature)
        assert theme == Theme.AI_INNOVATION
    
    def test_classification_rules(self):
        """Test classification rules and keywords"""
        classifier = FeatureClassifier()
        
        # Test optimization keywords
        optimize_keywords = classifier.get_optimization_keywords()
        assert "performance" in optimize_keywords
        assert "faster" in optimize_keywords
        assert "memory" in optimize_keywords
        
        # Test simplification keywords
        simplify_keywords = classifier.get_simplification_keywords()
        assert "automated" in simplify_keywords
        assert "reduce complexity" in simplify_keywords
        assert "single interface" in simplify_keywords