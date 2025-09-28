import pytest
from src.core.generators.presentation_generator import PresentationGenerator
from src.core.generators.content_generator import ContentGenerator
from src.core.models import Domain, Theme
from tests.fixtures.sample_data import get_sample_search_features, get_all_sample_features


class TestPresentationGenerator:

    def test_generate_complete_search_presentation(self):
        """Test generating a complete search presentation."""
        content_gen = ContentGenerator()
        pres_gen = PresentationGenerator(content_gen)
        features = get_sample_search_features()

        presentation = pres_gen.generate_complete_presentation(
            features=features,
            domain=Domain.SEARCH,
            quarter="Q1-2024",
            audience="mixed"
        )

        # Verify presentation structure
        assert presentation.title == "Search Innovations - Q1-2024"
        assert presentation.domain == Domain.SEARCH
        assert presentation.quarter == "Q1-2024"
        assert len(presentation.slides) == 9  # 7-slide framework + 2 extra
        assert len(presentation.feature_ids) == len(features)

        # Verify slide titles follow framework
        slide_titles = [slide.title for slide in presentation.slides]
        assert "The Infrastructure Challenge" in slide_titles
        assert "Three Game-Changing Innovations" in slide_titles
        assert "Cross-Platform Benefits" in slide_titles
        assert "Competitive Differentiation" in slide_titles
        assert "Business Case & ROI" in slide_titles
        assert "Ready to Get Started?" in slide_titles

        # Verify theme slides are present
        theme_slides = [slide for slide in presentation.slides if any(theme.title in slide.title for theme in [Theme.SIMPLIFY, Theme.OPTIMIZE, Theme.AI_INNOVATION])]
        assert len(theme_slides) == 3

    def test_generate_unified_presentation(self):
        """Test generating a unified all-domains presentation."""
        content_gen = ContentGenerator()
        pres_gen = PresentationGenerator(content_gen)
        features = get_all_sample_features()

        presentation = pres_gen.generate_complete_presentation(
            features=features,
            domain=Domain.ALL_DOMAINS,
            quarter="Q2-2024",
            audience="technical"
        )

        # Verify unified presentation
        assert presentation.title == "Elastic Platform Innovations - Q2-2024"
        assert presentation.domain == Domain.ALL_DOMAINS
        assert len(presentation.slides) == 9

        # Should include features from multiple domains
        feature_domains = set()
        for feature_id in presentation.feature_ids:
            feature = next(f for f in features if f.id == feature_id)
            feature_domains.add(feature.domain)

        assert len(feature_domains) > 1  # Multiple domains represented

    def test_presentation_with_no_features(self):
        """Test presentation generation with empty feature list."""
        content_gen = ContentGenerator()
        pres_gen = PresentationGenerator(content_gen)

        presentation = pres_gen.generate_complete_presentation(
            features=[],
            domain=Domain.OBSERVABILITY,
            quarter="Q3-2024",
            audience="business"
        )

        # Should still generate presentation structure
        assert presentation.title == "Observability Innovations - Q3-2024"
        assert len(presentation.slides) == 9
        assert len(presentation.feature_ids) == 0

    def test_theme_grouping(self):
        """Test that features are properly grouped by theme."""
        content_gen = ContentGenerator()
        pres_gen = PresentationGenerator(content_gen)
        features = get_sample_search_features()

        grouped = pres_gen._group_features_by_theme(features)

        # Verify grouping
        assert Theme.OPTIMIZE in grouped
        assert Theme.AI_INNOVATION in grouped
        assert Theme.SIMPLIFY in grouped

        # Verify features are in correct groups
        optimize_features = grouped[Theme.OPTIMIZE]
        ai_features = grouped[Theme.AI_INNOVATION]
        simplify_features = grouped[Theme.SIMPLIFY]

        assert any("BBQ" in f.name for f in optimize_features)
        assert any("Agent Builder" in f.name for f in ai_features)
        assert any("Cross-Cluster" in f.name for f in simplify_features)

    def test_domain_specific_hooks(self):
        """Test that domain-specific opening hooks are generated."""
        content_gen = ContentGenerator()
        pres_gen = PresentationGenerator(content_gen)

        # Test different domains
        domain_keywords = {
            Domain.SEARCH: ["search", "relevance", "query"],
            Domain.OBSERVABILITY: ["monitoring", "observability", "mttr", "alert"],
            Domain.SECURITY: ["security", "threat", "incident"]
        }

        for domain in [Domain.SEARCH, Domain.OBSERVABILITY, Domain.SECURITY]:
            hook_slide = pres_gen._generate_opening_hook_slide(domain, "mixed")

            assert hook_slide.title == "The Infrastructure Challenge"
            assert len(hook_slide.content) > 100  # Substantial content

            # Check that domain-relevant keywords are present
            content_lower = hook_slide.content.lower()
            assert any(keyword in content_lower for keyword in domain_keywords[domain])

    def test_cross_platform_benefits_domain_specific(self):
        """Test cross-platform benefits are domain-specific."""
        content_gen = ContentGenerator()
        pres_gen = PresentationGenerator(content_gen)
        features = get_sample_search_features()

        # Test search domain
        search_slide = pres_gen._generate_cross_platform_benefits_slide(features, Domain.SEARCH)
        assert "Search" in search_slide.content
        assert "Observability" in search_slide.content
        assert "Security" in search_slide.content

        # Test all domains
        unified_slide = pres_gen._generate_cross_platform_benefits_slide(features, Domain.ALL_DOMAINS)
        assert "Platform Synergies" in unified_slide.content
        assert "1 + 1 + 1 = 10x" in unified_slide.content