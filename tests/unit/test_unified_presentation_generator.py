import pytest
from src.core.generators.unified_presentation_generator import UnifiedPresentationGenerator
from src.core.generators.content_generator import ContentGenerator
from src.core.models import Feature, Domain, Theme
from tests.fixtures.sample_data import get_all_sample_features


class TestUnifiedPresentationGenerator:

    @pytest.fixture
    def unified_generator(self):
        """Create unified presentation generator for testing."""
        content_gen = ContentGenerator()
        return UnifiedPresentationGenerator(content_gen)

    @pytest.fixture
    def multi_domain_features(self):
        """Create features across multiple domains for testing."""
        features = []

        # Search features
        features.append(Feature(
            id="search-001",
            name="Advanced Vector Search",
            description="High-performance vector search capabilities",
            domain=Domain.SEARCH,
            theme=Theme.AI_INNOVATION,
            benefits=["10x faster similarity search", "Better relevance scoring"]
        ))

        # Observability features
        features.append(Feature(
            id="obs-001",
            name="Smart Alerting",
            description="AI-powered alert optimization",
            domain=Domain.OBSERVABILITY,
            theme=Theme.OPTIMIZE,
            benefits=["75% reduction in false alerts", "Faster incident response"]
        ))

        # Security features
        features.append(Feature(
            id="sec-001",
            name="Threat Intelligence Platform",
            description="Unified threat detection and response",
            domain=Domain.SECURITY,
            theme=Theme.AI_INNOVATION,
            benefits=["Real-time threat detection", "Automated response workflows"]
        ))

        return features

    def test_unified_presentation_generation(self, unified_generator, multi_domain_features):
        """Test generating unified presentation with multiple domains."""
        presentation = unified_generator.generate_unified_presentation(
            features=multi_domain_features,
            quarter="Q1-2024",
            audience="mixed"
        )

        # Verify presentation structure
        assert presentation.title == "Elastic Platform Transformation - Q1-2024"
        assert presentation.domain == Domain.ALL_DOMAINS
        assert presentation.quarter == "Q1-2024"
        assert len(presentation.slides) == 10  # Enhanced 10-slide framework

        # Verify slide titles include enhanced content
        slide_titles = [slide.title for slide in presentation.slides]
        assert "The Modern Infrastructure Dilemma" in slide_titles
        assert "The Elastic Platform Advantage" in slide_titles
        assert "Cross-Domain Innovation Matrix" in slide_titles
        assert "Platform Synergies in Action" in slide_titles
        assert "Customer Success Stories" in slide_titles
        assert "Platform Business Case & ROI" in slide_titles
        assert "Your Platform Transformation Journey" in slide_titles

        # Verify cross-domain content
        platform_slide = next(slide for slide in presentation.slides if "Platform Advantage" in slide.title)
        assert "Search" in platform_slide.content
        assert "Observability" in platform_slide.content
        assert "Security" in platform_slide.content

    def test_domain_analysis(self, unified_generator, multi_domain_features):
        """Test domain distribution analysis."""
        analysis = unified_generator._analyze_domain_distribution(multi_domain_features)

        assert analysis["total_features"] == 3
        assert len(analysis["represented_domains"]) == 3
        assert Domain.SEARCH in analysis["represented_domains"]
        assert Domain.OBSERVABILITY in analysis["represented_domains"]
        assert Domain.SECURITY in analysis["represented_domains"]
        assert analysis["is_truly_unified"] is True

        # Check domain counts
        assert analysis["domain_counts"][Domain.SEARCH] == 1
        assert analysis["domain_counts"][Domain.OBSERVABILITY] == 1
        assert analysis["domain_counts"][Domain.SECURITY] == 1

    def test_synergy_narratives(self, unified_generator):
        """Test synergy narrative selection."""
        # Test two-domain synergy
        two_domain_key = ("search", "security")
        assert two_domain_key in unified_generator.synergy_narratives
        narrative = unified_generator.synergy_narratives[two_domain_key]
        assert "title" in narrative
        assert "story" in narrative
        assert "benefits" in narrative

        # Test three-domain synergy
        three_domain_key = ("search", "security", "observability")
        assert three_domain_key in unified_generator.synergy_narratives
        unified_narrative = unified_generator.synergy_narratives[three_domain_key]
        assert "Unified Platform Advantage" in unified_narrative["title"]

    def test_unified_opening_hook(self, unified_generator, multi_domain_features):
        """Test enhanced opening hook generation."""
        analysis = unified_generator._analyze_domain_distribution(multi_domain_features)
        slide = unified_generator._generate_unified_opening_hook(analysis, "mixed")

        assert slide.title == "The Modern Infrastructure Dilemma"
        # Domain order may vary, so check for all domains
        assert "Search" in slide.content
        assert "Observability" in slide.content
        assert "Security" in slide.content
        assert "Data Silos" in slide.content
        assert "Vendor Sprawl" in slide.content
        assert "10x faster" in slide.content
        assert slide.theme == Theme.SIMPLIFY

    def test_platform_opportunity_slide(self, unified_generator, multi_domain_features):
        """Test platform opportunity slide generation."""
        analysis = unified_generator._analyze_domain_distribution(multi_domain_features)
        slide = unified_generator._generate_platform_opportunity_slide(analysis, multi_domain_features)

        assert slide.title == "The Elastic Platform Advantage"
        assert f"{len(multi_domain_features)} breakthrough innovations" in slide.content
        assert "Platform Effect" in slide.content
        assert "Exponential ROI" in slide.content

        # Check domain-specific content
        assert "Search" in slide.content
        assert "Observability" in slide.content
        assert "Security" in slide.content

    def test_cross_domain_innovation_slide(self, unified_generator, multi_domain_features):
        """Test cross-domain innovation matrix slide."""
        features_by_theme = unified_generator._group_features_by_theme(multi_domain_features)
        features_by_domain = unified_generator._group_features_by_domain(multi_domain_features)

        slide = unified_generator._generate_cross_domain_innovation_slide(
            features_by_theme, features_by_domain
        )

        assert slide.title == "Cross-Domain Innovation Matrix"
        assert "Innovation Themes Across All Domains" in slide.content
        assert "Cross-Domain Impact Stories" in slide.content
        assert "10x faster threat hunting" in slide.content
        assert "The Multiplication Effect" in slide.content

    def test_enhanced_theme_slide_with_features(self, unified_generator, multi_domain_features):
        """Test enhanced theme slide with actual features."""
        features_by_domain = unified_generator._group_features_by_domain(multi_domain_features)
        ai_features = [f for f in multi_domain_features if f.theme == Theme.AI_INNOVATION]

        slide = unified_generator._generate_enhanced_theme_slide(
            Theme.AI_INNOVATION, ai_features, features_by_domain
        )

        assert slide.title == f"{Theme.AI_INNOVATION.title}: {Theme.AI_INNOVATION.tagline}"
        assert "Platform-Wide Innovation" in slide.subtitle
        assert "Across All Domains" in slide.content
        assert "Platform Synergies" in slide.content
        assert "Business Impact" in slide.content

    def test_enhanced_theme_slide_without_features(self, unified_generator, multi_domain_features):
        """Test enhanced theme slide without features for that theme."""
        features_by_domain = unified_generator._group_features_by_domain(multi_domain_features)

        slide = unified_generator._generate_enhanced_theme_slide(
            Theme.SIMPLIFY, [], features_by_domain
        )

        assert slide.title == f"{Theme.SIMPLIFY.title}: {Theme.SIMPLIFY.tagline}"
        assert "The Simplify Vision" in slide.content
        assert "Cross-Platform Impact" in slide.content
        assert "Search" in slide.content
        assert "Observability" in slide.content
        assert "Security" in slide.content

    def test_synergy_showcase_slide(self, unified_generator, multi_domain_features):
        """Test synergy showcase slide generation."""
        analysis = unified_generator._analyze_domain_distribution(multi_domain_features)
        slide = unified_generator._generate_synergy_showcase_slide(multi_domain_features, analysis)

        assert slide.title == "Platform Synergies in Action"
        assert "Real-World Integration Scenarios" in slide.content
        assert "The Platform Advantage" in slide.content
        assert "Customer Reality" in slide.content
        assert "Data Correlation" in slide.content

    def test_customer_success_slide(self, unified_generator, multi_domain_features):
        """Test customer success stories slide."""
        analysis = unified_generator._analyze_domain_distribution(multi_domain_features)
        slide = unified_generator._generate_customer_success_slide(analysis)

        assert slide.title == "Customer Success Stories"
        assert "Global Financial Services Company" in slide.content
        assert "Fortune 500 Retailer" in slide.content
        assert "Technology Unicorn" in slide.content
        assert "The Pattern" in slide.content
        assert "300-500% ROI" in slide.content

    def test_platform_business_case_slide(self, unified_generator, multi_domain_features):
        """Test platform business case slide with ROI calculations."""
        analysis = unified_generator._analyze_domain_distribution(multi_domain_features)
        slide = unified_generator._generate_platform_business_case_slide(multi_domain_features, analysis)

        assert slide.title == "Platform Business Case & ROI"
        assert "The Platform Premium" in slide.content
        assert "Quantified Benefits" in slide.content
        assert "Financial Impact" in slide.content
        assert "ROI Calculation" in slide.content
        assert "Implementation Timeline" in slide.content

        # Check ROI calculations include domain multiplier
        assert "domain value PLUS platform multiplier" in slide.content

    def test_implementation_roadmap_slide(self, unified_generator, multi_domain_features):
        """Test implementation roadmap slide."""
        analysis = unified_generator._analyze_domain_distribution(multi_domain_features)
        slide = unified_generator._generate_implementation_roadmap_slide(analysis, "Q1-2024")

        assert slide.title == "Your Platform Transformation Journey"
        assert "Phase 1: Foundation" in slide.content
        assert "Phase 2: Integration" in slide.content
        assert "Phase 3: Optimization" in slide.content
        assert "Success Metrics" in slide.content
        assert "Ready to Begin?" in slide.content

    def test_single_domain_handling(self, unified_generator):
        """Test handling of single domain scenarios."""
        single_domain_features = [
            Feature(
                id="search-001",
                name="Test Feature",
                description="Test description",
                domain=Domain.SEARCH,
                theme=Theme.OPTIMIZE
            )
        ]

        analysis = unified_generator._analyze_domain_distribution(single_domain_features)
        assert analysis["is_truly_unified"] is False
        assert len(analysis["represented_domains"]) == 1

        # Should still generate compelling unified presentation
        presentation = unified_generator.generate_unified_presentation(
            features=single_domain_features,
            quarter="Q1-2024"
        )

        assert len(presentation.slides) == 10
        assert presentation.domain == Domain.ALL_DOMAINS

    def test_theme_synergy_descriptions(self, unified_generator):
        """Test theme-specific synergy descriptions."""
        simplify_desc = unified_generator._get_theme_synergy_description(Theme.SIMPLIFY)
        assert "Unified interfaces" in simplify_desc

        optimize_desc = unified_generator._get_theme_synergy_description(Theme.OPTIMIZE)
        assert "Shared optimization" in optimize_desc

        ai_desc = unified_generator._get_theme_synergy_description(Theme.AI_INNOVATION)
        assert "Platform-wide AI" in ai_desc

    def test_group_features_by_domain(self, unified_generator, multi_domain_features):
        """Test grouping features by domain."""
        grouped = unified_generator._group_features_by_domain(multi_domain_features)

        assert Domain.SEARCH in grouped
        assert Domain.OBSERVABILITY in grouped
        assert Domain.SECURITY in grouped

        assert len(grouped[Domain.SEARCH]) == 1
        assert len(grouped[Domain.OBSERVABILITY]) == 1
        assert len(grouped[Domain.SECURITY]) == 1

    def test_comprehensive_unified_presentation(self, unified_generator):
        """Test with comprehensive sample data."""
        all_features = get_all_sample_features()

        presentation = unified_generator.generate_unified_presentation(
            features=all_features,
            quarter="Q2-2024",
            audience="technical"
        )

        # Should handle multiple features across domains
        assert len(presentation.feature_ids) == len(all_features)
        assert presentation.quarter == "Q2-2024"

        # Verify enhanced storytelling
        synergy_slide = next(
            slide for slide in presentation.slides
            if "Synergies in Action" in slide.title
        )
        assert "Real-World Integration Scenarios" in synergy_slide.content

        business_case_slide = next(
            slide for slide in presentation.slides
            if "Business Case" in slide.title
        )
        assert "Platform Premium" in business_case_slide.content