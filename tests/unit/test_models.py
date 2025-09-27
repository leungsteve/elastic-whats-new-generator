import pytest
from src.core.models import Feature, Theme, SlideContent

def test_feature_creation():
    """Test Feature model creation and validation"""
    feature = Feature(
        id="test-001",
        name="Test Feature",
        description="A test feature",
        domain="search"
    )
    
    assert feature.id == "test-001"
    assert feature.name == "Test Feature"
    assert feature.domain == "search"
    assert feature.theme is None  # Optional field

def test_feature_with_theme():
    """Test Feature with theme assignment"""
    feature = Feature(
        id="test-002",
        name="Performance Feature",
        description="Improves performance",
        domain="search",
        theme=Theme.OPTIMIZE
    )
    
    assert feature.theme == Theme.OPTIMIZE

def test_slide_content_creation():
    """Test SlideContent model"""
    slide = SlideContent(
        title="Optimize Performance",
        content="Detailed content here",
        business_value="Reduces costs by 50%",
        theme=Theme.OPTIMIZE
    )
    
    assert slide.title == "Optimize Performance"
    assert slide.theme == Theme.OPTIMIZE