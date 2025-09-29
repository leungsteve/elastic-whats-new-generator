"""
Storytelling and narrative components for Elastic What's New Generator.

This module provides advanced storytelling capabilities including story arc planning,
comprehensive talk track generation, and narrative flow analysis.
"""

from typing import List, Dict, Optional, Tuple
from src.core.models import (
    Feature, Theme, Domain, StoryArc, StoryPosition,
    TalkTrack, CustomerStory, BusinessImpact, NarrativeFlow,
    AudienceAdaptation, ContentGenerationRequest
)


class StoryArcPlanner:
    """Plans compelling story arcs for presentations based on features and themes."""

    def __init__(self):
        """Initialize the story arc planner."""
        self._industry_hooks = {
            Domain.SEARCH: "In today's data-driven world, organizations are drowning in information but starving for insights.",
            Domain.OBSERVABILITY: "Modern applications are more complex than ever, with distributed systems creating unprecedented visibility challenges.",
            Domain.SECURITY: "Cyber threats are evolving faster than traditional security measures can adapt.",
            Domain.ALL_DOMAINS: "Organizations face an unprecedented convergence of data challenges across search, observability, and security."
        }

        self._theme_narratives = {
            Theme.SIMPLIFY: "streamlining complex workflows into intuitive experiences",
            Theme.OPTIMIZE: "accelerating performance while reducing operational overhead",
            Theme.AI_INNOVATION: "leveraging artificial intelligence to unlock new possibilities"
        }

    def create_story_arc(
        self,
        features: List[Feature],
        domain: Domain,
        request: ContentGenerationRequest
    ) -> StoryArc:
        """
        Create a comprehensive story arc for the given features.

        Args:
            features: List of features to include in the story
            domain: Target domain for the presentation
            request: Content generation request with audience and style preferences

        Returns:
            Complete story arc plan
        """
        # Analyze feature themes and select climax
        theme_distribution = self._analyze_theme_distribution(features)
        climax_feature = self._select_climax_feature(features, theme_distribution)

        # Generate opening hook based on domain and features
        opening_hook = self._generate_opening_hook(domain, features, request.narrative_style)

        # Create central theme that unifies all features
        central_theme = self._generate_central_theme(features, domain, theme_distribution)

        # Build narrative thread connecting features
        narrative_thread = self._build_narrative_thread(features, climax_feature, request.narrative_style)

        # Generate resolution and call to action
        resolution_message = self._generate_resolution(features, domain, central_theme)
        call_to_action = self._generate_call_to_action(request.audience, domain)

        # Map customer journey stages if applicable
        customer_journey_stages = self._map_customer_journey(features, request.narrative_style)

        # Add competitive positioning if requested
        competitive_positioning = None
        if request.competitive_positioning:
            competitive_positioning = self._generate_competitive_positioning(features, domain)

        return StoryArc(
            opening_hook=opening_hook,
            central_theme=central_theme,
            narrative_thread=narrative_thread,
            climax_feature=climax_feature.id if climax_feature else None,
            resolution_message=resolution_message,
            call_to_action=call_to_action,
            customer_journey_stages=customer_journey_stages,
            competitive_positioning=competitive_positioning
        )

    def _analyze_theme_distribution(self, features: List[Feature]) -> Dict[Theme, int]:
        """Analyze the distribution of themes across features."""
        distribution = {Theme.SIMPLIFY: 0, Theme.OPTIMIZE: 0, Theme.AI_INNOVATION: 0}
        for feature in features:
            if feature.theme:
                distribution[feature.theme] += 1
        return distribution

    def _select_climax_feature(self, features: List[Feature], theme_distribution: Dict[Theme, int]) -> Optional[Feature]:
        """Select the most impactful feature for the story climax."""
        # Prioritize AI Innovation features as they're often most strategic
        ai_features = [f for f in features if f.theme == Theme.AI_INNOVATION]
        if ai_features:
            # Select AI feature with most comprehensive research
            return max(ai_features, key=lambda f: len(f.content_research.primary_sources))

        # Fall back to feature with most benefits or research
        if features:
            return max(features, key=lambda f: len(f.benefits) + len(f.content_research.primary_sources))

        return None

    def _generate_opening_hook(self, domain: Domain, features: List[Feature], narrative_style: str) -> str:
        """Generate a compelling opening hook."""
        base_hook = self._industry_hooks.get(domain, self._industry_hooks[Domain.ALL_DOMAINS])

        if narrative_style == "customer_journey":
            return f"{base_hook} Today, we'll explore how leading organizations are transforming their {domain.display_name.lower()} capabilities through strategic innovation."
        elif narrative_style == "problem_solution":
            return f"{base_hook} Let's examine how these {len(features)} breakthrough innovations directly address these critical challenges."
        else:  # innovation_showcase
            return f"{base_hook} Today, we're excited to showcase {len(features)} game-changing innovations that are redefining what's possible."

    def _generate_central_theme(self, features: List[Feature], domain: Domain, theme_distribution: Dict[Theme, int]) -> str:
        """Generate the central unifying theme."""
        dominant_theme = max(theme_distribution, key=theme_distribution.get)
        theme_narrative = self._theme_narratives[dominant_theme]

        return f"Our Q1 2024 innovations focus on {theme_narrative} across {domain.display_name.lower()}, enabling organizations to achieve unprecedented efficiency and effectiveness."

    def _build_narrative_thread(self, features: List[Feature], climax_feature: Optional[Feature], narrative_style: str) -> str:
        """Build the main narrative thread connecting all features."""
        if narrative_style == "customer_journey":
            return "We'll follow a customer's journey from initial challenges through implementation and ultimate success, showing how each innovation builds upon the last."
        elif narrative_style == "problem_solution":
            return "Each feature we'll explore directly solves a specific pain point, creating a comprehensive solution ecosystem."
        else:  # innovation_showcase
            climax_name = climax_feature.name if climax_feature else "our flagship innovation"
            return f"We'll build momentum through foundational improvements, culminating with {climax_name} - our most transformative advancement."

    def _generate_resolution(self, features: List[Feature], domain: Domain, central_theme: str) -> str:
        """Generate the story resolution."""
        return f"Together, these {len(features)} innovations create a unified platform that transforms {domain.display_name.lower()} from a technical challenge into a strategic advantage."

    def _generate_call_to_action(self, audience: str, domain: Domain) -> str:
        """Generate audience-appropriate call to action."""
        if audience == "business":
            return "Let's discuss how these innovations can accelerate your business objectives and drive measurable ROI."
        elif audience == "technical":
            return "Ready to dive deeper? Let's explore implementation strategies and technical specifications."
        else:  # mixed
            return "Whether you're focused on business outcomes or technical implementation, we're here to help you get started with these powerful new capabilities."

    def _map_customer_journey(self, features: List[Feature], narrative_style: str) -> List[str]:
        """Map features to customer journey stages."""
        if narrative_style != "customer_journey":
            return []

        stages = []
        for i, feature in enumerate(features):
            if i == 0:
                stages.append("Initial Challenge Recognition")
            elif i == len(features) - 1:
                stages.append("Success Realization")
            else:
                stages.append(f"Solution Implementation Phase {i}")

        return stages

    def _generate_competitive_positioning(self, features: List[Feature], domain: Domain) -> str:
        """Generate competitive positioning statement."""
        return f"While competitors focus on point solutions, Elastic delivers integrated {domain.display_name.lower()} capabilities that work seamlessly together, providing unmatched flexibility and performance."


class TalkTrackGenerator:
    """Generates comprehensive talk tracks for presentation slides."""

    def __init__(self):
        """Initialize the talk track generator."""
        self._engagement_prompts = {
            "business": [
                "How many of you have experienced this challenge?",
                "What would a 50% improvement mean for your organization?",
                "Think about your current quarterly priorities..."
            ],
            "technical": [
                "Who's worked with similar architectures?",
                "What's been your experience with scaling these systems?",
                "Let's dive into the technical details..."
            ],
            "mixed": [
                "I'd love to hear your perspectives on this...",
                "This applies whether you're on the business or technical side...",
                "Let's look at this from both angles..."
            ]
        }

    def generate_talk_track(
        self,
        feature: Feature,
        story_position: StoryPosition,
        audience_type: str,
        technical_depth: str,
        slide_number: int,
        total_slides: int
    ) -> TalkTrack:
        """
        Generate a comprehensive talk track for a feature slide.

        Args:
            feature: The feature being presented
            story_position: Position in the story arc
            audience_type: Target audience (business/technical/mixed)
            technical_depth: Technical detail level (low/medium/high)
            slide_number: Current slide number
            total_slides: Total number of slides

        Returns:
            Complete talk track with timing and engagement elements
        """
        # Generate opening statement based on story position
        opening_statement = self._generate_opening_statement(feature, story_position, audience_type)

        # Create key talking points
        key_points = self._generate_key_points(feature, technical_depth, audience_type)

        # Generate transition to next slide
        transition_to_next = self._generate_transition(story_position, slide_number, total_slides)

        # Select appropriate engagement prompts
        engagement_prompts = self._select_engagement_prompts(audience_type, feature)

        # Create technical depth variations
        technical_depth_notes = self._generate_technical_variations(feature, audience_type)

        # Generate demo callouts
        demo_callouts = self._generate_demo_callouts(feature, technical_depth)

        # Calculate timing
        timing_minutes = self._calculate_timing(story_position, len(key_points))

        # Determine confidence level required
        confidence_level = self._assess_confidence_requirement(feature, technical_depth)

        # Generate backup explanations
        backup_explanations = self._generate_backup_explanations(feature, technical_depth)

        return TalkTrack(
            opening_statement=opening_statement,
            key_points=key_points,
            transition_to_next=transition_to_next,
            engagement_prompts=engagement_prompts,
            technical_depth_notes=technical_depth_notes,
            demo_callouts=demo_callouts,
            timing_minutes=timing_minutes,
            confidence_level=confidence_level,
            backup_explanations=backup_explanations
        )

    def _generate_opening_statement(self, feature: Feature, story_position: StoryPosition, audience_type: str) -> str:
        """Generate the opening statement for the slide."""
        if story_position == StoryPosition.OPENING_HOOK:
            return f"Let's start with a question: What if you could {feature.description.lower()}? Today, that's exactly what we're making possible."
        elif story_position == StoryPosition.CLIMAX:
            return f"Now we come to what I believe is our most significant advancement: {feature.name}. This changes everything."
        elif story_position == StoryPosition.CALL_TO_ACTION:
            return f"So where do we go from here? {feature.name} gives us the foundation to take the next step forward."
        else:
            return f"Building on what we've seen, let's explore {feature.name} - another key piece of our innovation story."

    def _generate_key_points(self, feature: Feature, technical_depth: str, audience_type: str) -> List[str]:
        """Generate 2-3 key talking points."""
        points = []

        # Always include core capability
        points.append(f"Core capability: {feature.description}")

        # Add technical or business focus based on audience
        if audience_type == "technical" and technical_depth in ["medium", "high"]:
            if feature.content_research.extracted_content.key_concepts:
                concepts = ", ".join(feature.content_research.extracted_content.key_concepts[:3])
                points.append(f"Technical foundation: Built on {concepts}")

        # Add business value
        if feature.benefits:
            benefits = ", ".join(feature.benefits[:2])
            points.append(f"Business impact: {benefits}")

        # Add implementation insight if available
        if feature.content_research.ai_insights.implementation_complexity:
            complexity = feature.content_research.ai_insights.implementation_complexity
            points.append(f"Implementation: {complexity} complexity with clear migration path")

        return points[:3]  # Limit to 3 points

    def _generate_transition(self, story_position: StoryPosition, slide_number: int, total_slides: int) -> str:
        """Generate transition to next slide."""
        if slide_number == total_slides:
            return "This brings us to our conclusion and next steps."
        elif story_position == StoryPosition.CLIMAX:
            return "Now let's see how this all comes together in practice."
        else:
            return "With this foundation in place, let's see how we build on it."

    def _select_engagement_prompts(self, audience_type: str, feature: Feature) -> List[str]:
        """Select appropriate engagement prompts."""
        base_prompts = self._engagement_prompts.get(audience_type, self._engagement_prompts["mixed"])

        # Customize for the specific feature
        customized = []
        for prompt in base_prompts[:2]:  # Limit to 2 prompts
            if "experience" in prompt.lower():
                customized.append(f"What's been your experience with {feature.domain.display_name.lower()} challenges like this?")
            else:
                customized.append(prompt)

        return customized

    def _generate_technical_variations(self, feature: Feature, audience_type: str) -> Dict[str, str]:
        """Generate audience-specific explanations."""
        variations = {}

        if audience_type == "mixed":
            variations["business_explanation"] = f"In business terms: {feature.description} to drive operational efficiency"
            variations["technical_explanation"] = f"Technically speaking: {feature.description} through advanced architecture"

        return variations

    def _generate_demo_callouts(self, feature: Feature, technical_depth: str) -> List[str]:
        """Generate suggested demo points."""
        callouts = []

        if feature.content_research.extracted_content.configuration_examples:
            callouts.append("Demo: Live configuration example")

        if feature.benefits:
            callouts.append("Demo: Before/after performance comparison")

        if technical_depth == "high":
            callouts.append("Demo: Deep dive into technical implementation")

        return callouts

    def _calculate_timing(self, story_position: StoryPosition, num_key_points: int) -> float:
        """Calculate estimated speaking time."""
        base_time = 2.0  # Base 2 minutes

        if story_position == StoryPosition.OPENING_HOOK:
            base_time += 1.0  # Extra time for setup
        elif story_position == StoryPosition.CLIMAX:
            base_time += 1.5  # Extra time for emphasis

        # Add time for key points
        base_time += (num_key_points * 0.5)

        return min(base_time, 5.0)  # Cap at 5 minutes

    def _assess_confidence_requirement(self, feature: Feature, technical_depth: str) -> str:
        """Assess required speaker confidence level."""
        if technical_depth == "high":
            return "high"
        elif len(feature.content_research.primary_sources) == 0:
            return "high"  # Less source material = need more confidence
        else:
            return "medium"

    def _generate_backup_explanations(self, feature: Feature, technical_depth: str) -> List[str]:
        """Generate alternative explanations for complex topics."""
        explanations = []

        # Simple analogy
        explanations.append(f"Think of {feature.name} like a smart assistant that handles {feature.domain.display_name.lower()} automatically")

        # Business value reframe
        if feature.benefits:
            explanations.append(f"The bottom line: {feature.benefits[0]} with minimal effort")

        # Technical simplification if high depth
        if technical_depth == "high":
            explanations.append("In simpler terms: it just works better, faster, and more reliably than before")

        return explanations


class NarrativeFlowAnalyzer:
    """Analyzes and optimizes narrative flow across presentation slides."""

    def analyze_narrative_flow(self, slides: List[dict], story_arc: StoryArc) -> NarrativeFlow:
        """
        Analyze the narrative flow of a complete presentation.

        Args:
            slides: List of slide content dictionaries
            story_arc: The planned story arc

        Returns:
            Narrative flow analysis with recommendations
        """
        # Calculate overall coherence
        coherence_score = self._calculate_coherence(slides, story_arc)

        # Analyze slide-to-slide transitions
        transition_quality = self._analyze_transitions(slides)

        # Assess pacing
        pacing_analysis = self._analyze_pacing(slides)

        # Calculate momentum curve
        momentum_curve = self._calculate_momentum_curve(slides)

        # Generate improvement suggestions
        improvements = self._suggest_improvements(coherence_score, transition_quality, momentum_curve)

        return NarrativeFlow(
            overall_coherence_score=coherence_score,
            transition_quality=transition_quality,
            pacing_analysis=pacing_analysis,
            momentum_curve=momentum_curve,
            suggested_improvements=improvements
        )

    def _calculate_coherence(self, slides: List[dict], story_arc: StoryArc) -> float:
        """Calculate overall story coherence score."""
        # Simple heuristic based on slide progression and theme consistency
        score = 0.8  # Base score

        # Check if climax feature is properly positioned
        if story_arc.climax_feature:
            climax_position = None
            for i, slide in enumerate(slides):
                if slide.get('feature_id') == story_arc.climax_feature:
                    climax_position = i / len(slides)
                    break

            # Ideal climax position is around 70-80% through presentation
            if climax_position and 0.6 <= climax_position <= 0.8:
                score += 0.1

        return min(score, 1.0)

    def _analyze_transitions(self, slides: List[dict]) -> Dict[str, float]:
        """Analyze quality of slide-to-slide transitions."""
        transitions = {}

        for i in range(len(slides) - 1):
            current_slide = slides[i]
            next_slide = slides[i + 1]

            # Simple transition quality assessment
            transition_score = 0.7  # Base score

            # Check if themes flow logically
            current_theme = current_slide.get('theme')
            next_theme = next_slide.get('theme')

            if current_theme == next_theme:
                transition_score += 0.2  # Same theme = smooth transition

            transitions[f"slide_{i}_to_{i+1}"] = min(transition_score, 1.0)

        return transitions

    def _analyze_pacing(self, slides: List[dict]) -> str:
        """Analyze presentation pacing."""
        total_slides = len(slides)

        if total_slides <= 5:
            return "Fast-paced presentation with concise coverage of key topics"
        elif total_slides <= 10:
            return "Well-balanced pacing allowing for detailed exploration of each topic"
        else:
            return "Comprehensive deep-dive requiring strong facilitation to maintain engagement"

    def _calculate_momentum_curve(self, slides: List[dict]) -> List[float]:
        """Calculate energy/engagement curve across slides."""
        curve = []

        for i, slide in enumerate(slides):
            # Start with baseline energy
            energy = 0.6

            # Opening gets boost
            if i == 0:
                energy += 0.3

            # Climax position gets major boost
            story_position = slide.get('story_position')
            if story_position == 'climax':
                energy += 0.4
            elif story_position == 'call_to_action':
                energy += 0.2

            # Mid-presentation dip is natural
            if 0.3 <= (i / len(slides)) <= 0.6:
                energy -= 0.1

            curve.append(min(energy, 1.0))

        return curve

    def _suggest_improvements(self, coherence: float, transitions: Dict[str, float], momentum: List[float]) -> List[str]:
        """Generate improvement suggestions."""
        suggestions = []

        if coherence < 0.7:
            suggestions.append("Consider strengthening the central narrative theme to improve story coherence")

        # Check for weak transitions
        weak_transitions = [k for k, v in transitions.items() if v < 0.6]
        if weak_transitions:
            suggestions.append("Strengthen slide transitions with better bridge statements")

        # Check momentum curve for excessive dips
        min_momentum = min(momentum) if momentum else 0
        if min_momentum < 0.4:
            suggestions.append("Add engagement elements to maintain audience energy throughout")

        if not suggestions:
            suggestions.append("Narrative flow is strong - consider adding interactive elements for enhanced engagement")

        return suggestions