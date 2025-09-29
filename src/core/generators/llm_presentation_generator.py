"""
LLM-powered presentation generator using Claude for comprehensive storytelling.

This module implements Stage 2 of the two-stage LLM architecture:
- Load features with cached LLM-extracted content
- Generate cohesive presentations using Claude
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from src.core.models import (
    Feature, Domain, Theme, Presentation, SlideContent,
    StoryArc, StoryPosition
)

logger = logging.getLogger(__name__)


class LLMPresentationGenerator:
    """
    Generate presentations using Claude with cached LLM-extracted content.

    This is Stage 2 of the two-stage architecture where we take structured
    content extracted during the research phase and synthesize it into
    compelling presentations.
    """

    def __init__(self, claude_client):
        """
        Initialize LLM presentation generator.

        Args:
            claude_client: ClaudeClient instance for LLM generation
        """
        self.claude_client = claude_client

    def generate_presentation(
        self,
        features: List[Feature],
        domain: Domain,
        audience: str = "mixed",
        narrative_style: str = "customer_journey",
        technical_depth: str = "medium",
        slide_count: int = 7,
        quarter: str = "Q1-2025"
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive presentation using LLM.

        Args:
            features: List of features with llm_extracted content
            domain: Target domain
            audience: Target audience (business/technical/mixed)
            narrative_style: Narrative approach
            technical_depth: Technical depth level
            slide_count: Number of slides to generate
            quarter: Quarter identifier

        Returns:
            Dictionary with presentation data

        Raises:
            ValueError: If features lack LLM-extracted content
        """
        logger.info(f"Generating LLM presentation for {len(features)} features in {domain.value}")

        # Validate features have LLM-extracted content
        features_with_content = [
            f for f in features
            if f.content_research and f.content_research.llm_extracted
        ]

        if not features_with_content:
            raise ValueError(
                "No features have LLM-extracted content. Run content research first."
            )

        logger.info(f"Using {len(features_with_content)} features with LLM-extracted content")

        # Call Claude to generate presentation
        try:
            presentation_data = self.claude_client.generate_presentation_slides(
                features=features_with_content,
                domain=domain.value,
                audience=audience,
                narrative_style=narrative_style,
                technical_depth=technical_depth,
                slide_count=slide_count
            )

            # Convert to Presentation model
            presentation = self._convert_to_presentation_model(
                presentation_data=presentation_data,
                features=features_with_content,
                domain=domain,
                quarter=quarter
            )

            logger.info(f"Successfully generated presentation with {len(presentation['slides'])} slides")

            return presentation

        except Exception as e:
            logger.error(f"LLM presentation generation failed: {e}")
            raise ValueError(f"Failed to generate presentation: {e}")

    def _convert_to_presentation_model(
        self,
        presentation_data: Dict[str, Any],
        features: List[Feature],
        domain: Domain,
        quarter: str
    ) -> Dict[str, Any]:
        """
        Convert Claude's presentation data to our Presentation model format.

        Args:
            presentation_data: Raw data from Claude
            features: Source features
            domain: Target domain
            quarter: Quarter identifier

        Returns:
            Dict matching Presentation model structure
        """
        # Extract slides
        slides = []
        for idx, slide_data in enumerate(presentation_data.get("slides", [])):
            # Parse theme from slide data
            theme_str = slide_data.get("theme", "ai_innovation")
            try:
                theme = Theme(theme_str)
            except ValueError:
                logger.warning(f"Invalid theme '{theme_str}', defaulting to ai_innovation")
                theme = Theme.AI_INNOVATION

            # Determine story position based on slide index
            story_position = self._determine_story_position(idx, len(presentation_data.get("slides", [])))

            slide = {
                "title": slide_data.get("title", "Untitled Slide"),
                "subtitle": slide_data.get("subtitle"),
                "content": slide_data.get("content", ""),
                "business_value": slide_data.get("business_value", ""),
                "theme": theme.value,
                "story_position": story_position.value if story_position else None,
                "speaker_notes": slide_data.get("speaker_notes"),
                "talk_track": None,  # Could be enhanced later
                "customer_stories": [],
                "business_impact": None,
                "competitive_context": None,
                "narrative_thread": None,
                "emotional_hook": None
            }
            slides.append(slide)

        # Extract story arc
        story_arc_data = presentation_data.get("story_arc", {})
        story_arc = {
            "opening_hook": story_arc_data.get("opening_hook", ""),
            "central_theme": story_arc_data.get("central_theme", ""),
            "narrative_thread": "",
            "climax_feature": None,
            "resolution_message": story_arc_data.get("resolution_message", ""),
            "call_to_action": story_arc_data.get("call_to_action", ""),
            "customer_journey_stages": [],
            "competitive_positioning": None
        }

        # Build presentation dict
        presentation = {
            "id": f"{domain.value}-presentation-{quarter}",
            "title": presentation_data.get("title", f"{domain.display_name} Innovation - {quarter}"),
            "domain": domain.value,
            "quarter": quarter,
            "slides": slides,
            "featured_themes": list(set(s["theme"] for s in slides)),
            "feature_ids": [f.id for f in features],
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "story_arc": story_arc,
            "narrative_flow": None,
            "audience_adaptation": None,
            "total_talk_time_minutes": len(slides) * 3.5,  # Estimate
            "confidence_requirements": {}
        }

        return presentation

    def _determine_story_position(self, slide_index: int, total_slides: int) -> Optional[StoryPosition]:
        """
        Determine story position based on slide index.

        Args:
            slide_index: Index of slide (0-based)
            total_slides: Total number of slides

        Returns:
            StoryPosition enum value
        """
        if slide_index == 0:
            return StoryPosition.OPENING_HOOK
        elif slide_index == 1:
            return StoryPosition.SETUP
        elif slide_index < total_slides - 2:
            return StoryPosition.RISING_ACTION
        elif slide_index == total_slides - 2:
            return StoryPosition.CLIMAX
        elif slide_index == total_slides - 1:
            return StoryPosition.CALL_TO_ACTION
        else:
            return StoryPosition.RESOLUTION

    def can_generate_presentation(self, features: List[Feature]) -> bool:
        """
        Check if features have LLM-extracted content for presentation generation.

        Args:
            features: List of features to check

        Returns:
            True if at least one feature has LLM-extracted content
        """
        return any(
            f.content_research and f.content_research.llm_extracted
            for f in features
        )

    def get_extraction_status(self, features: List[Feature]) -> Dict[str, Any]:
        """
        Get status of LLM extraction for features.

        Args:
            features: List of features to check

        Returns:
            Dict with extraction status details
        """
        total = len(features)
        with_extraction = sum(
            1 for f in features
            if f.content_research and f.content_research.llm_extracted
        )
        without_extraction = total - with_extraction

        return {
            "total_features": total,
            "features_with_extraction": with_extraction,
            "features_without_extraction": without_extraction,
            "ready_for_generation": with_extraction > 0,
            "features_needing_research": [
                f.id for f in features
                if not (f.content_research and f.content_research.llm_extracted)
            ]
        }