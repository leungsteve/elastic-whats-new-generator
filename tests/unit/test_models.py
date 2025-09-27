import pytest
from datetime import datetime
from pydantic import ValidationError
from src.core.models import (
    Feature, Theme, Domain, SlideContent, LabInstruction,
    Presentation, Lab, ClassificationResult, ContentGenerationRequest,
    GenerationMetrics
)


class TestTheme:
    """Test Theme enum functionality."""

    def test_theme_values(self):
        """Test theme enum values and properties."""
        assert Theme.SIMPLIFY == "simplify"
        assert Theme.OPTIMIZE == "optimize"
        assert Theme.AI_INNOVATION == "ai_innovation"

    def test_theme_titles(self):
        """Test theme display titles."""
        assert Theme.SIMPLIFY.title == "Simplify"
        assert Theme.OPTIMIZE.title == "Optimize"
        assert Theme.AI_INNOVATION.title == "AI Innovation"

    def test_theme_taglines(self):
        """Test theme marketing taglines."""
        assert Theme.SIMPLIFY.tagline == "Do more with less"
        assert Theme.OPTIMIZE.tagline == "Do it faster"
        assert Theme.AI_INNOVATION.tagline == "Do it with AI"


class TestDomain:
    """Test Domain enum functionality."""

    def test_domain_values(self):
        """Test domain enum values."""
        assert Domain.SEARCH == "search"
        assert Domain.OBSERVABILITY == "observability"
        assert Domain.SECURITY == "security"
        assert Domain.ALL_DOMAINS == "all_domains"

    def test_domain_display_names(self):
        """Test domain display names."""
        assert Domain.SEARCH.display_name == "Search"
        assert Domain.OBSERVABILITY.display_name == "Observability"
        assert Domain.SECURITY.display_name == "Security"
        assert Domain.ALL_DOMAINS.display_name == "All Domains"


class TestFeature:
    """Test Feature model functionality."""

    def test_feature_creation(self):
        """Test basic feature creation."""
        feature = Feature(
            id="test-001",
            name="Test Feature",
            description="A test feature",
            domain=Domain.SEARCH
        )

        assert feature.id == "test-001"
        assert feature.name == "Test Feature"
        assert feature.domain == Domain.SEARCH
        assert feature.theme is None
        assert isinstance(feature.created_at, datetime)

    def test_feature_with_theme(self):
        """Test feature with theme assignment."""
        feature = Feature(
            id="test-002",
            name="Performance Feature",
            description="Improves performance",
            domain=Domain.SEARCH,
            theme=Theme.OPTIMIZE
        )

        assert feature.theme == Theme.OPTIMIZE

    def test_feature_with_benefits(self):
        """Test feature with benefits list."""
        benefits = ["Faster queries", "Lower costs", "Better UX"]
        feature = Feature(
            id="test-003",
            name="BBQ Feature",
            description="Binary quantization",
            domain=Domain.SEARCH,
            benefits=benefits
        )

        assert feature.benefits == benefits

    def test_feature_validation_empty_name(self):
        """Test validation fails for empty name."""
        with pytest.raises(ValidationError):
            Feature(
                id="test-004",
                name="",
                description="Valid description",
                domain=Domain.SEARCH
            )

    def test_feature_validation_empty_description(self):
        """Test validation fails for empty description."""
        with pytest.raises(ValidationError):
            Feature(
                id="test-005",
                name="Valid Name",
                description="",
                domain=Domain.SEARCH
            )

    def test_feature_timestamp_update(self):
        """Test timestamp update functionality."""
        feature = Feature(
            id="test-006",
            name="Test Feature",
            description="Test description",
            domain=Domain.SEARCH
        )

        original_time = feature.updated_at
        feature.update_timestamp()
        assert feature.updated_at > original_time


class TestSlideContent:
    """Test SlideContent model functionality."""

    def test_slide_content_creation(self):
        """Test basic slide content creation."""
        slide = SlideContent(
            title="Optimize Performance",
            content="Detailed content here",
            business_value="Reduces costs by 50%",
            theme=Theme.OPTIMIZE
        )

        assert slide.title == "Optimize Performance"
        assert slide.theme == Theme.OPTIMIZE
        assert slide.subtitle is None

    def test_slide_content_with_subtitle(self):
        """Test slide content with subtitle."""
        slide = SlideContent(
            title="Main Title",
            subtitle="Supporting subtitle",
            content="Content",
            business_value="Value prop",
            theme=Theme.SIMPLIFY
        )

        assert slide.subtitle == "Supporting subtitle"

    def test_slide_content_validation(self):
        """Test slide content validation."""
        with pytest.raises(ValidationError):
            SlideContent(
                title="",  # Empty title
                content="Content",
                business_value="Value",
                theme=Theme.OPTIMIZE
            )


class TestLabInstruction:
    """Test LabInstruction model functionality."""

    def test_lab_instruction_creation(self):
        """Test basic lab instruction creation."""
        lab = LabInstruction(
            title="Search Lab",
            objective="Learn search optimization",
            scenario="E-commerce search scenario",
            setup_instructions="Set up Elasticsearch",
            steps=["Step 1", "Step 2", "Step 3"],
            validation="Check query performance"
        )

        assert lab.title == "Search Lab"
        assert len(lab.steps) == 3
        assert lab.difficulty == "intermediate"  # Default value

    def test_lab_instruction_validation_empty_steps(self):
        """Test validation fails for empty steps."""
        with pytest.raises(ValidationError):
            LabInstruction(
                title="Bad Lab",
                objective="Learn something",
                scenario="Some scenario",
                setup_instructions="Setup",
                steps=[],  # Empty steps
                validation="Validate somehow"
            )


class TestPresentation:
    """Test Presentation model functionality."""

    def test_presentation_creation(self):
        """Test basic presentation creation."""
        slide = SlideContent(
            title="Test Slide",
            content="Content",
            business_value="Value",
            theme=Theme.OPTIMIZE
        )

        presentation = Presentation(
            id="pres-001",
            domain=Domain.SEARCH,
            quarter="Q1-2024",
            title="Search Innovations",
            slides=[slide],
            featured_themes=[Theme.OPTIMIZE],
            feature_ids=["feat-001"]
        )

        assert presentation.domain == Domain.SEARCH
        assert len(presentation.slides) == 1
        assert Theme.OPTIMIZE in presentation.featured_themes

    def test_presentation_validation_empty_slides(self):
        """Test validation fails for empty slides."""
        with pytest.raises(ValidationError):
            Presentation(
                id="pres-002",
                domain=Domain.SEARCH,
                quarter="Q1-2024",
                title="Bad Presentation",
                slides=[],  # Empty slides
                featured_themes=[],
                feature_ids=[]
            )


class TestClassificationResult:
    """Test ClassificationResult model functionality."""

    def test_classification_result_creation(self):
        """Test classification result creation."""
        result = ClassificationResult(
            feature_id="feat-001",
            theme=Theme.AI_INNOVATION,
            confidence=0.85,
            reasoning="AI-related keywords detected",
            model_used="claude-3-sonnet"
        )

        assert result.confidence == 0.85
        assert result.theme == Theme.AI_INNOVATION

    def test_classification_result_validation_confidence(self):
        """Test confidence validation."""
        with pytest.raises(ValidationError):
            ClassificationResult(
                feature_id="feat-001",
                theme=Theme.OPTIMIZE,
                confidence=1.5,  # Invalid confidence > 1
                model_used="test-model"
            )

        with pytest.raises(ValidationError):
            ClassificationResult(
                feature_id="feat-001",
                theme=Theme.OPTIMIZE,
                confidence=-0.1,  # Invalid confidence < 0
                model_used="test-model"
            )


class TestContentGenerationRequest:
    """Test ContentGenerationRequest model functionality."""

    def test_content_generation_request(self):
        """Test content generation request creation."""
        feature = Feature(
            id="feat-001",
            name="Test Feature",
            description="Test description",
            domain=Domain.SEARCH
        )

        request = ContentGenerationRequest(
            features=[feature],
            domain=Domain.SEARCH,
            content_type="presentation",
            audience="technical"
        )

        assert len(request.features) == 1
        assert request.audience == "technical"

    def test_content_generation_request_validation(self):
        """Test request validation."""
        with pytest.raises(ValidationError):
            ContentGenerationRequest(
                features=[],  # Empty features
                domain=Domain.SEARCH,
                content_type="presentation"
            )


class TestGenerationMetrics:
    """Test GenerationMetrics model functionality."""

    def test_generation_metrics_creation(self):
        """Test metrics creation."""
        metrics = GenerationMetrics(
            operation_id="op-001",
            content_type="presentation",
            features_processed=5,
            generation_time_seconds=45.2,
            tokens_used=1500,
            model_used="claude-3-sonnet",
            success=True
        )

        assert metrics.features_processed == 5
        assert metrics.success is True
        assert isinstance(metrics.timestamp, datetime)