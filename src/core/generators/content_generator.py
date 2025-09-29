"""
Content generation system for Elastic What's New Generator.

This module generates presentation slides and lab instructions based on
classified features and their themes.
"""

from typing import List, Optional
from src.core.models import (
    Feature, Theme, SlideContent, LabInstruction, StoryPosition,
    TalkTrack, CustomerStory, BusinessImpact, StoryArc,
    AudienceAdaptation, ContentGenerationRequest
)
from src.core.config import config_loader
from src.core.storytelling import StoryArcPlanner, TalkTrackGenerator, NarrativeFlowAnalyzer


class ContentGenerator:
    """Generates presentation and lab content with advanced storytelling capabilities."""

    def __init__(self):
        """Initialize the content generator with storytelling components."""
        self.config_loader = config_loader
        self._theme_taglines = {
            Theme.SIMPLIFY: "Do more with less",
            Theme.OPTIMIZE: "Do it faster",
            Theme.AI_INNOVATION: "Do it with AI"
        }

        # Initialize storytelling components
        self.story_planner = StoryArcPlanner()
        self.talk_track_generator = TalkTrackGenerator()
        self.flow_analyzer = NarrativeFlowAnalyzer()

    def generate_slide_content(
        self,
        feature: Feature,
        story_position: StoryPosition = StoryPosition.RISING_ACTION,
        request: Optional[ContentGenerationRequest] = None,
        slide_number: int = 1,
        total_slides: int = 5
    ) -> SlideContent:
        """
        Generate enhanced slide content with comprehensive storytelling.

        Args:
            feature: The feature to generate content for
            story_position: Position in the story arc
            request: Content generation request with audience preferences
            slide_number: Current slide number in presentation
            total_slides: Total number of slides

        Returns:
            Generated slide content with comprehensive talk track
        """
        # Use defaults if no request provided
        if not request:
            request = ContentGenerationRequest(
                features=[feature],
                domain=feature.domain,
                content_type="presentation"
            )

        theme = feature.theme or Theme.SIMPLIFY

        # Generate title based on story position
        title = self._generate_contextual_title(feature, theme, story_position)

        # Generate business value based on benefits and audience
        business_value = self._generate_enhanced_business_value(feature, theme, request.audience)

        # Generate main content with storytelling context
        content = self._generate_enhanced_slide_content(feature, theme, story_position, request)

        # Generate comprehensive talk track
        talk_track = self.talk_track_generator.generate_talk_track(
            feature=feature,
            story_position=story_position,
            audience_type=request.audience,
            technical_depth=request.technical_depth,
            slide_number=slide_number,
            total_slides=total_slides
        )

        # Generate customer stories if enabled
        customer_stories = []
        if request.include_customer_stories:
            customer_stories = self._generate_customer_stories(feature, request.audience)

        # Generate business impact data
        business_impact = self._generate_business_impact(feature, theme)

        # Generate competitive context if enabled
        competitive_context = None
        if request.competitive_positioning:
            competitive_context = self._generate_competitive_context(feature, theme)

        # Generate narrative thread
        narrative_thread = self._generate_narrative_thread(feature, story_position)

        return SlideContent(
            title=title,
            content=content,
            business_value=business_value,
            theme=theme,
            story_position=story_position,
            talk_track=talk_track,
            customer_stories=customer_stories,
            business_impact=business_impact,
            competitive_context=competitive_context,
            narrative_thread=narrative_thread
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

        # Get lab template configuration for difficulty determination
        try:
            # Determine difficulty based on feature complexity
            difficulty = self._determine_lab_difficulty(feature, theme)
            lab_template = self.config_loader.get_lab_template(difficulty)
            estimated_time = lab_template.estimated_time
        except:
            # Fallback to default values
            difficulty = "intermediate"
            estimated_time = 30

        return LabInstruction(
            title=title,
            objective=objective,
            scenario=scenario,
            setup_instructions=setup_instructions,
            steps=steps,
            validation=validation,
            estimated_time=estimated_time,
            difficulty=difficulty
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

    def _determine_lab_difficulty(self, feature: Feature, theme: Theme) -> str:
        """Determine lab difficulty based on feature and theme complexity."""
        # AI features are typically more advanced
        if theme == Theme.AI_INNOVATION:
            return "advanced"

        # Features with many benefits are more complex
        if feature.benefits and len(feature.benefits) > 3:
            return "intermediate"

        # Simple features or optimization-focused are beginner-friendly
        if theme == Theme.SIMPLIFY or len(feature.description) < 100:
            return "beginner"

        # Default to intermediate
        return "intermediate"

    def generate_complete_presentation(
        self,
        features: List[Feature],
        request: ContentGenerationRequest
    ) -> dict:
        """
        Generate a complete presentation with story arc and comprehensive talk tracks.

        Args:
            features: List of features to include
            request: Content generation request

        Returns:
            Complete presentation with story arc, slides, and narrative analysis
        """
        # Create story arc
        story_arc = self.story_planner.create_story_arc(features, request.domain, request)

        # Create audience adaptation
        audience_adaptation = self._create_audience_adaptation(request)

        # Assign story positions to features
        positioned_features = self._assign_story_positions(features, story_arc)

        # Generate slides with storytelling
        slides = []
        total_slides = len(positioned_features)

        for i, (feature, position) in enumerate(positioned_features):
            slide = self.generate_slide_content(
                feature=feature,
                story_position=position,
                request=request,
                slide_number=i + 1,
                total_slides=total_slides
            )
            slides.append(slide)

        # Analyze narrative flow
        slide_dicts = [self._slide_to_dict(slide) for slide in slides]
        narrative_flow = self.flow_analyzer.analyze_narrative_flow(slide_dicts, story_arc)

        # Calculate total talk time
        total_talk_time = sum(slide.talk_track.timing_minutes for slide in slides)

        # Generate confidence requirements
        confidence_requirements = {
            f"slide_{i+1}": slide.talk_track.confidence_level
            for i, slide in enumerate(slides)
        }

        return {
            "story_arc": story_arc,
            "slides": slides,
            "narrative_flow": narrative_flow,
            "audience_adaptation": audience_adaptation,
            "total_talk_time_minutes": total_talk_time,
            "confidence_requirements": confidence_requirements,
            "featured_themes": list(set(slide.theme for slide in slides)),
            "feature_ids": [feature.id for feature in features]
        }

    # New storytelling helper methods
    def _generate_contextual_title(self, feature: Feature, theme: Theme, story_position: StoryPosition) -> str:
        """Generate title based on story context."""
        if story_position == StoryPosition.OPENING_HOOK:
            return f"The Challenge: {feature.domain.display_name} Transformation"
        elif story_position == StoryPosition.CLIMAX:
            return f"Game Changer: {feature.name}"
        elif story_position == StoryPosition.CALL_TO_ACTION:
            return f"Your Next Step: {feature.name}"
        else:
            return f"{feature.name}: {theme.title} Your {feature.domain.display_name}"

    def _generate_enhanced_business_value(self, feature: Feature, theme: Theme, audience: str) -> str:
        """Generate audience-specific business value."""
        if not feature.benefits:
            base_value = f"Transform your {feature.domain.display_name} capabilities"
        else:
            base_value = feature.benefits[0]

        if audience == "business":
            return f"{base_value} - driving measurable ROI and competitive advantage"
        elif audience == "technical":
            return f"{base_value} - through advanced technical capabilities and streamlined operations"
        else:  # mixed
            return f"{base_value} - delivering both technical excellence and business results"

    def _generate_enhanced_slide_content(self, feature: Feature, theme: Theme, story_position: StoryPosition, request: ContentGenerationRequest) -> str:
        """Generate enhanced slide content with storytelling."""
        content_parts = []

        # Story-specific opening
        if story_position == StoryPosition.OPENING_HOOK:
            content_parts.extend([
                "**The Challenge:**",
                f"Organizations struggle with {feature.domain.display_name.lower()} complexity",
                ""
            ])
        elif story_position == StoryPosition.CLIMAX:
            content_parts.extend([
                "**The Breakthrough:**",
                f"{feature.name} changes everything",
                ""
            ])

        # Core content
        tagline = self._theme_taglines[theme]
        content_parts.extend([
            f"**{tagline}** with {feature.name}",
            "",
            f"**What it is:** {feature.description}",
            ""
        ])

        # Benefits with storytelling context
        if feature.benefits:
            content_parts.extend([
                "**Key Benefits:**",
                *[f"• {benefit}" for benefit in feature.benefits[:3]],
                ""
            ])

        # Technical insights if appropriate
        if request.technical_depth in ["medium", "high"] and feature.content_research.extracted_content.key_concepts:
            concepts = ", ".join(feature.content_research.extracted_content.key_concepts[:3])
            content_parts.extend([
                f"**Technical Foundation:** {concepts}",
                ""
            ])

        # Closing with story context
        content_parts.extend([
            f"**Impact:** {self._get_story_impact(story_position, feature, theme)}"
        ])

        return "\n".join(content_parts)

    def _generate_customer_stories(self, feature: Feature, audience: str) -> List[CustomerStory]:
        """Generate customer success stories."""
        # For now, generate a sample customer story
        # In a real implementation, this would query a customer story database
        return [
            CustomerStory(
                company_name="TechCorp (anonymized)",
                industry="E-commerce",
                challenge=f"Struggling with {feature.domain.display_name.lower()} inefficiencies",
                solution=f"Implemented {feature.name} to streamline operations",
                outcome="50% reduction in operational overhead",
                metrics={"efficiency_gain": "50%", "time_savings": "20 hours/week"}
            )
        ]

    def _generate_business_impact(self, feature: Feature, theme: Theme) -> BusinessImpact:
        """Generate quantified business impact."""
        # Sample business impact - in real implementation, this would use actual data
        impact_map = {
            Theme.SIMPLIFY: BusinessImpact(
                productivity_gains="30-50% operational efficiency improvement",
                time_savings="Reduce manual work by 40%",
                cost_savings="Lower operational costs by 25%"
            ),
            Theme.OPTIMIZE: BusinessImpact(
                roi_percentage=150.0,
                productivity_gains="2x performance improvement",
                cost_savings="Reduce infrastructure costs by 30%"
            ),
            Theme.AI_INNOVATION: BusinessImpact(
                competitive_advantage="First-mover advantage with AI capabilities",
                productivity_gains="Unlock new insights and automation",
                risk_reduction="Proactive issue detection and resolution"
            )
        }
        return impact_map.get(theme, BusinessImpact())

    def _generate_competitive_context(self, feature: Feature, theme: Theme) -> str:
        """Generate competitive positioning context."""
        return f"While competitors offer point solutions, {feature.name} provides integrated {theme.title.lower()} capabilities that scale across your entire {feature.domain.display_name.lower()} ecosystem."

    def _generate_narrative_thread(self, feature: Feature, story_position: StoryPosition) -> str:
        """Generate narrative connection to overall story."""
        thread_map = {
            StoryPosition.OPENING_HOOK: "This sets the stage for our innovation journey",
            StoryPosition.SETUP: "Building the foundation for transformation",
            StoryPosition.RISING_ACTION: "Each capability builds momentum toward our goal",
            StoryPosition.CLIMAX: "This is where everything comes together",
            StoryPosition.RESOLUTION: "Bringing all innovations into a unified solution",
            StoryPosition.CALL_TO_ACTION: "Your path forward starts here"
        }
        return thread_map.get(story_position, "Part of our comprehensive innovation story")

    def _get_story_impact(self, story_position: StoryPosition, feature: Feature, theme: Theme) -> str:
        """Get story-appropriate impact statement."""
        if story_position == StoryPosition.CLIMAX:
            return f"Revolutionary {theme.title.lower()} transformation for {feature.domain.display_name}"
        elif story_position == StoryPosition.CALL_TO_ACTION:
            return "Ready to get started? Let's make it happen"
        else:
            return f"Transform your {feature.domain.display_name} operations with {theme.title.lower()} innovation"

    def _create_audience_adaptation(self, request: ContentGenerationRequest) -> AudienceAdaptation:
        """Create audience-specific adaptations."""
        return AudienceAdaptation(
            audience_type=request.audience,
            technical_depth_level=request.technical_depth,
            business_focus_areas=request.business_focus,
            jargon_adjustments={
                "implementation": "setup" if request.audience == "business" else "implementation",
                "optimization": "improvement" if request.audience == "business" else "optimization"
            },
            engagement_strategies=[
                "Use business metrics and ROI focus" if request.audience == "business" else "Include technical deep-dives",
                "Interactive demos and hands-on examples"
            ]
        )

    def _assign_story_positions(self, features: List[Feature], story_arc: StoryArc) -> List[tuple]:
        """Assign story positions to features."""
        positioned = []
        total_features = len(features)

        for i, feature in enumerate(features):
            if i == 0:
                position = StoryPosition.OPENING_HOOK
            elif i == total_features - 1:
                position = StoryPosition.CALL_TO_ACTION
            elif story_arc.climax_feature and feature.id == story_arc.climax_feature:
                position = StoryPosition.CLIMAX
            elif i == 1:
                position = StoryPosition.SETUP
            elif i == total_features - 2:
                position = StoryPosition.RESOLUTION
            else:
                position = StoryPosition.RISING_ACTION

            positioned.append((feature, position))

        return positioned

    def _slide_to_dict(self, slide: SlideContent) -> dict:
        """Convert slide to dictionary for analysis."""
        return {
            "title": slide.title,
            "theme": slide.theme.value,
            "story_position": slide.story_position.value,
            "timing_minutes": slide.talk_track.timing_minutes
        }