import pytest
from unittest.mock import Mock, patch
from src.core.generators.content_generator import ContentGenerator
from src.core.models import Feature, Theme

class TestContentGenerator:
    
    def test_generate_slide_content(self, sample_feature):
        """Test slide content generation"""
        generator = ContentGenerator()
        content = generator.generate_slide_content(sample_feature)
        
        assert content.title
        assert content.business_value
        assert content.theme == Theme.OPTIMIZE
        assert "Do it faster" in content.content  # Theme tagline
    
    @patch('src.integrations.ai_tools.claude_generate')
    def test_generate_with_ai_assistance(self, mock_claude, sample_feature):
        """Test content generation with AI assistance"""
        mock_claude.return_value = "Generated content about BBQ performance benefits"
        
        generator = ContentGenerator()
        content = generator.generate_slide_content(sample_feature)
        
        mock_claude.assert_called_once()
        assert "performance benefits" in content.content.lower()
    
    def test_generate_lab_instructions(self, sample_feature):
        """Test lab instruction generation"""
        generator = ContentGenerator()
        lab = generator.generate_lab_instructions(sample_feature)
        
        assert lab.title
        assert lab.objective
        assert lab.steps
        assert len(lab.steps) > 0
        assert lab.validation