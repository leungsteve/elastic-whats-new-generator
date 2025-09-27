"""
Content generation system for Elastic What's New Generator.

This module generates presentation slides and lab instructions based on
classified features and their themes.
"""

from typing import List, Optional
from src.core.models import Feature, Theme, SlideContent, LabInstruction


class ContentGenerator:
    """Generates presentation and lab content from classified features."""

    def __init__(self):
        """Initialize the content generator."""
        self._theme_taglines = {
            Theme.SIMPLIFY: "Do more with less",
            Theme.OPTIMIZE: "Do it faster",
            Theme.AI_INNOVATION: "Do it with AI"
        }

    def generate_slide_content(self, feature: Feature) -> SlideContent:
        """
        Generate slide content for a feature.

        Args:
            feature: The feature to generate content for

        Returns:
            Generated slide content
        """
        theme = feature.theme or Theme.SIMPLIFY

        # Generate title
        title = f"{feature.name}: {theme.title} Your {feature.domain.display_name}"

        # Generate business value based on benefits
        if feature.benefits:
            business_value = self._generate_business_value(feature.benefits, theme)
        else:
            business_value = f"Transform your {feature.domain.display_name} capabilities with {theme.title.lower()} innovations"

        # Generate main content with AI assistance
        content = self._generate_slide_content_text(feature, theme)

        # Enhance content with AI-generated insights
        from src.integrations.ai_tools import claude_generate
        ai_prompt = f"Enhance the presentation content for {feature.name}: {feature.description}"
        ai_content = claude_generate(ai_prompt, str(feature.benefits))
        content = f"{content}\n\n**AI Insights:** {ai_content}"

        return SlideContent(
            title=title,
            content=content,
            business_value=business_value,
            theme=theme
        )

    def generate_lab_instructions(self, feature: Feature) -> LabInstruction:
        """
        Generate lab instructions for a feature.

        Args:
            feature: The feature to generate lab instructions for

        Returns:
            Generated lab instructions
        """
        theme = feature.theme or Theme.SIMPLIFY
        domain = feature.domain.display_name

        # Generate lab components
        title = f"Hands-on with {feature.name}"

        objective = f"Learn how {feature.name} helps you {theme.tagline.lower()} in {domain}"

        scenario = self._generate_lab_scenario(feature, theme)

        setup_instructions = f"""
# Lab Setup

1. Access your Elasticsearch cluster
2. Open Kibana in your browser
3. Navigate to Dev Tools
4. Ensure sample {feature.domain.value} data is loaded

**Note**: This lab requires Elasticsearch 8.x or later
""".strip()

        steps = self._generate_lab_steps(feature, theme)

        validation = f"Verify that {feature.name} is working by checking the improvements in {theme.value} metrics"

        return LabInstruction(
            title=title,
            objective=objective,
            scenario=scenario,
            setup_instructions=setup_instructions,
            steps=steps,
            validation=validation,
            estimated_time=30,
            difficulty="intermediate"
        )

    def _generate_business_value(self, benefits: List[str], theme: Theme) -> str:
        """Generate business value proposition from feature benefits."""
        if not benefits:
            return f"Deliver {theme.tagline.lower()} results for your organization"

        primary_benefit = benefits[0]
        theme_context = {
            Theme.SIMPLIFY: "reducing operational complexity",
            Theme.OPTIMIZE: "improving performance and efficiency",
            Theme.AI_INNOVATION: "leveraging AI capabilities"
        }

        return f"{primary_benefit} while {theme_context[theme]}"

    def _generate_slide_content_text(self, feature: Feature, theme: Theme) -> str:
        """Generate the main slide content text."""
        tagline = self._theme_taglines[theme]

        content_parts = [
            f"**{tagline}** with {feature.name}",
            "",
            f"**What it is:** {feature.description}",
            ""
        ]

        if feature.benefits:
            content_parts.extend([
                "**Key Benefits:**",
                *[f"• {benefit}" for benefit in feature.benefits[:3]],
                ""
            ])

        content_parts.extend([
            f"**Impact:** Transform your {feature.domain.display_name} operations",
            f"**Theme:** {theme.title} - {tagline}"
        ])

        return "\n".join(content_parts)

    def _generate_lab_scenario(self, feature: Feature, theme: Theme) -> str:
        """Generate a realistic lab scenario based on domain and theme."""
        domain_scenarios = {
            "search": {
                Theme.SIMPLIFY: "You're a developer building an e-commerce search experience and need to simplify the implementation",
                Theme.OPTIMIZE: "Your search application is experiencing performance issues with large datasets",
                Theme.AI_INNOVATION: "You want to add AI-powered search capabilities to improve relevance"
            },
            "observability": {
                Theme.SIMPLIFY: "Your team manages multiple monitoring tools and needs to consolidate operations",
                Theme.OPTIMIZE: "You're experiencing high monitoring costs and need to optimize resource usage",
                Theme.AI_INNOVATION: "You want to leverage AI to reduce mean time to resolution (MTTR)"
            },
            "security": {
                Theme.SIMPLIFY: "Your security team is overwhelmed by multiple security tools and complex workflows",
                Theme.OPTIMIZE: "You need to reduce investigation time and improve threat detection speed",
                Theme.AI_INNOVATION: "You want to enhance threat detection with AI-powered security analytics"
            }
        }

        domain_key = feature.domain.value
        if domain_key in domain_scenarios and theme in domain_scenarios[domain_key]:
            base_scenario = domain_scenarios[domain_key][theme]
            return f"{base_scenario}. In this lab, you'll explore how {feature.name} addresses this challenge."

        return f"In this hands-on lab, you'll explore {feature.name} and learn how it helps you {theme.tagline.lower()}."

    def _generate_lab_steps(self, feature: Feature, theme: Theme) -> List[str]:
        """Generate step-by-step lab instructions."""
        steps = [
            f"**Step 1: Explore Current State**\n   - Examine the current {feature.domain.value} setup\n   - Identify areas for improvement",

            f"**Step 2: Configure {feature.name}**\n   - Enable {feature.name} in your cluster\n   - Review configuration options",

            f"**Step 3: Implement the Feature**\n   - Follow the implementation guide\n   - Apply {feature.name} to sample data",

            f"**Step 4: Measure Impact**\n   - Compare before and after metrics\n   - Analyze the {theme.value} improvements",

            f"**Step 5: Optimize Settings**\n   - Fine-tune configuration based on results\n   - Document best practices for your use case"
        ]

        return steps