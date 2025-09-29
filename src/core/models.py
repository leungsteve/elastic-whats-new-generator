"""
Core data models for the Elastic What's New Generator.

This module defines the fundamental data structures used throughout the application,
including features, themes, domains, and generated content models.
"""

from enum import Enum
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator, ConfigDict


class Theme(str, Enum):
    """Three universal innovation themes for feature classification."""
    SIMPLIFY = "simplify"
    OPTIMIZE = "optimize"
    AI_INNOVATION = "ai_innovation"

    @property
    def title(self) -> str:
        """Human-readable title for the theme."""
        titles = {
            self.SIMPLIFY: "Simplify",
            self.OPTIMIZE: "Optimize",
            self.AI_INNOVATION: "AI Innovation"
        }
        return titles[self]

    @property
    def tagline(self) -> str:
        """Marketing tagline for the theme."""
        taglines = {
            self.SIMPLIFY: "Do more with less",
            self.OPTIMIZE: "Do it faster",
            self.AI_INNOVATION: "Do it with AI"
        }
        return taglines[self]


class Domain(str, Enum):
    """Elastic product domains."""
    SEARCH = "search"
    OBSERVABILITY = "observability"
    SECURITY = "security"
    ALL_DOMAINS = "all_domains"

    @property
    def display_name(self) -> str:
        """Human-readable display name."""
        names = {
            self.SEARCH: "Search",
            self.OBSERVABILITY: "Observability",
            self.SECURITY: "Security",
            self.ALL_DOMAINS: "All Domains"
        }
        return names[self]


# Content Research Models

class ContentResearchStatus(str, Enum):
    """Status of content research operations."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ResearchDepth(str, Enum):
    """Depth level for content research."""
    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"


class SourceMetadata(BaseModel):
    """Metadata for scraped content sources."""

    page_sections: List[str] = Field(default_factory=list, description="Page sections found")
    code_examples: int = Field(default=0, description="Number of code examples")
    images: int = Field(default=0, description="Number of images")
    last_modified: Optional[str] = Field(None, description="Last modification date")
    language: str = Field(default="en", description="Content language")
    author: Optional[str] = Field(None, description="Content author")
    publish_date: Optional[str] = Field(None, description="Publication date")
    tags: List[str] = Field(default_factory=list, description="Content tags")


class SourceContent(BaseModel):
    """Scraped content from a documentation source."""

    url: str = Field(..., description="Source URL")
    title: str = Field(..., description="Page title")
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    content_type: str = Field(default="documentation", description="Type of content")
    status: str = Field(default="success", description="Scraping status")
    word_count: int = Field(default=0, description="Word count of content")
    content: str = Field(default="", description="Full scraped text content")
    metadata: SourceMetadata = Field(default_factory=SourceMetadata)
    links_found: List[str] = Field(default_factory=list, description="Links discovered in content")
    source_url: Optional[str] = Field(None, description="URL where this link was found")
    discovery_method: str = Field(default="manual", description="How this source was discovered")
    relevance_score: float = Field(default=1.0, description="Relevance score (0-1)")


class CodeExample(BaseModel):
    """Extracted code example with context."""

    title: str = Field(..., description="Example title")
    code: str = Field(..., description="Code content")
    description: str = Field(..., description="Example description")
    language: str = Field(default="json", description="Programming language")


class UseCase(BaseModel):
    """Practical use case for a feature."""

    title: str = Field(..., description="Use case title")
    description: str = Field(..., description="Use case description")
    complexity: str = Field(default="intermediate", description="Complexity level")
    estimated_time: str = Field(default="30 minutes", description="Estimated time")


class ExtractedContent(BaseModel):
    """AI-extracted structured content from documentation."""

    key_concepts: List[str] = Field(default_factory=list, description="Key technical concepts")
    configuration_examples: List[CodeExample] = Field(default_factory=list, description="Configuration examples")
    use_cases: List[UseCase] = Field(default_factory=list, description="Practical use cases")
    prerequisites: List[str] = Field(default_factory=list, description="Prerequisites")
    related_features: List[str] = Field(default_factory=list, description="Related feature names")
    performance_considerations: List[str] = Field(default_factory=list, description="Performance notes")


class PresentationAngle(BaseModel):
    """Suggested presentation angle for a feature."""

    angle: str = Field(..., description="Presentation angle name")
    description: str = Field(..., description="Angle description")
    target_audience: str = Field(..., description="Target audience")
    estimated_slides: int = Field(default=5, description="Estimated slide count")


class LabScenario(BaseModel):
    """Suggested lab scenario for hands-on learning."""

    title: str = Field(..., description="Lab title")
    description: str = Field(..., description="Lab description")
    difficulty: str = Field(default="intermediate", description="Difficulty level")
    duration: str = Field(default="60 minutes", description="Estimated duration")
    technologies: List[str] = Field(default_factory=list, description="Technologies used")


class AIInsights(BaseModel):
    """AI-generated insights about a feature."""

    technical_summary: str = Field(default="", description="Technical summary")
    business_value: str = Field(default="", description="Business value proposition")
    implementation_complexity: str = Field(default="medium", description="Implementation complexity")
    learning_curve: str = Field(default="moderate", description="Learning curve assessment")
    recommended_audience: List[str] = Field(default_factory=list, description="Recommended audience")
    presentation_angles: List[PresentationAngle] = Field(default_factory=list, description="Presentation suggestions")
    lab_scenarios: List[LabScenario] = Field(default_factory=list, description="Lab scenario suggestions")
    content_themes: List[str] = Field(default_factory=list, description="Content themes")


class ELSEREmbedding(BaseModel):
    """ELSER embedding for semantic search."""

    text: str = Field(..., description="Text that was embedded")
    elser_embedding: Dict[str, Any] = Field(default_factory=dict, description="ELSER sparse vector")
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    model_version: str = Field(default=".elser_model_2", description="ELSER model version")


class ContentEmbeddings(BaseModel):
    """Collection of ELSER embeddings for different content types."""

    feature_summary: Optional[ELSEREmbedding] = Field(None, description="Feature summary embedding")
    technical_content: Optional[ELSEREmbedding] = Field(None, description="Technical content embedding")
    full_documentation: Optional[ELSEREmbedding] = Field(None, description="Full documentation embedding")


class LLMExtractedContent(BaseModel):
    """Structured content extracted by LLM from scraped documentation.

    This model represents the output of Stage 1 (Extraction Phase) where Claude
    analyzes raw scraped content and extracts key structured information that will
    be cached in Elasticsearch and used for presentation generation.
    """

    summary: str = Field(..., description="Concise feature summary (2-3 sentences)")
    use_cases: List[str] = Field(default_factory=list, description="Common use cases and applications")
    key_capabilities: List[str] = Field(default_factory=list, description="Core technical capabilities")
    benefits: List[str] = Field(default_factory=list, description="Business and technical benefits")
    technical_requirements: List[str] = Field(default_factory=list, description="Prerequisites and requirements")
    target_audience: str = Field(default="developers", description="Primary target audience")
    complexity_level: str = Field(default="intermediate", description="Technical complexity (beginner/intermediate/advanced)")
    extracted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Extraction timestamp")
    model_used: str = Field(default="claude-3-sonnet-20240229", description="LLM model used for extraction")

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class ContentResearch(BaseModel):
    """Comprehensive content research data for a feature."""

    status: ContentResearchStatus = Field(default=ContentResearchStatus.PENDING)
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    scraping_enabled: bool = Field(default=True, description="Whether scraping is enabled")
    research_depth: ResearchDepth = Field(default=ResearchDepth.STANDARD)

    # Source content
    primary_sources: List[SourceContent] = Field(default_factory=list, description="Primary documentation sources")
    related_sources: List[SourceContent] = Field(default_factory=list, description="Related discovered sources")

    # LLM-extracted structured content (Stage 1: Extraction Phase)
    llm_extracted: Optional[LLMExtractedContent] = Field(None, description="LLM-extracted structured content for presentation generation")

    # Processed content (legacy fields - may be deprecated in favor of llm_extracted)
    extracted_content: ExtractedContent = Field(default_factory=ExtractedContent)
    ai_insights: AIInsights = Field(default_factory=AIInsights)

    # Semantic embeddings
    embeddings: ContentEmbeddings = Field(default_factory=ContentEmbeddings)


class Feature(BaseModel):
    """Core feature model representing an Elastic capability."""

    id: str = Field(..., description="Unique identifier for the feature")
    name: str = Field(..., description="Feature name")
    description: str = Field(..., description="Brief description of the feature")
    benefits: List[str] = Field(default_factory=list, description="List of feature benefits")
    documentation_links: List[str] = Field(default_factory=list, description="Links to documentation")
    theme: Optional[Theme] = Field(None, description="Classified innovation theme")
    domain: Domain = Field(..., description="Product domain")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Enhanced content research
    content_research: ContentResearch = Field(default_factory=ContentResearch, description="Comprehensive content research data")

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Feature name cannot be empty')
        return v.strip()

    @field_validator('description')
    @classmethod
    def description_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Feature description cannot be empty')
        return v.strip()

    def update_timestamp(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(timezone.utc)

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class StoryPosition(str, Enum):
    """Position in the story arc for narrative structure."""
    OPENING_HOOK = "opening_hook"
    SETUP = "setup"
    RISING_ACTION = "rising_action"
    CLIMAX = "climax"
    RESOLUTION = "resolution"
    CALL_TO_ACTION = "call_to_action"


class TalkTrack(BaseModel):
    """Comprehensive talk track for a slide with timing and engagement."""

    opening_statement: str = Field(..., description="30-45 second opening hook")
    key_points: List[str] = Field(..., description="2-3 main talking points (2-3 minutes total)")
    transition_to_next: str = Field(..., description="Bridge to next slide")
    engagement_prompts: List[str] = Field(default_factory=list, description="Audience engagement questions")
    technical_depth_notes: Dict[str, str] = Field(
        default_factory=dict,
        description="Audience-specific variations (business vs technical)"
    )
    demo_callouts: List[str] = Field(default_factory=list, description="Suggested demo points")
    timing_minutes: float = Field(default=3.0, description="Estimated speaking time in minutes")
    confidence_level: str = Field(default="medium", description="Speaker confidence requirement (low/medium/high)")
    backup_explanations: List[str] = Field(default_factory=list, description="Alternative explanations for complex topics")


class CustomerStory(BaseModel):
    """Customer success story for business value demonstration."""

    company_name: Optional[str] = Field(None, description="Customer company name (anonymized if needed)")
    industry: str = Field(..., description="Customer industry")
    challenge: str = Field(..., description="Business challenge addressed")
    solution: str = Field(..., description="How the feature solved the challenge")
    outcome: str = Field(..., description="Quantified business outcome")
    quote: Optional[str] = Field(None, description="Customer testimonial quote")
    metrics: Dict[str, str] = Field(default_factory=dict, description="Success metrics (e.g., '50% reduction in time')")


class BusinessImpact(BaseModel):
    """Quantified business impact and ROI data."""

    roi_percentage: Optional[float] = Field(None, description="Return on investment percentage")
    cost_savings: Optional[str] = Field(None, description="Cost savings description")
    time_savings: Optional[str] = Field(None, description="Time savings description")
    productivity_gains: Optional[str] = Field(None, description="Productivity improvement description")
    risk_reduction: Optional[str] = Field(None, description="Risk mitigation benefits")
    competitive_advantage: Optional[str] = Field(None, description="Market differentiation")


class SlideContent(BaseModel):
    """Generated slide content for presentations with comprehensive storytelling."""

    title: str = Field(..., description="Slide title")
    subtitle: Optional[str] = Field(None, description="Optional subtitle")
    content: str = Field(..., description="Main slide content")
    business_value: str = Field(..., description="Business value proposition")
    theme: Theme = Field(..., description="Associated innovation theme")
    story_position: Optional[StoryPosition] = Field(None, description="Position in narrative arc")

    # Enhanced talk track system
    talk_track: Optional[TalkTrack] = Field(None, description="Comprehensive speaker guidance")

    # Supporting content
    customer_stories: List[CustomerStory] = Field(default_factory=list, description="Relevant customer success stories")
    business_impact: Optional[BusinessImpact] = Field(None, description="Quantified business impact data")
    competitive_context: Optional[str] = Field(None, description="Market positioning and competitive advantage")

    # Narrative flow
    narrative_thread: Optional[str] = Field(None, description="How this slide connects to overall story")
    emotional_hook: Optional[str] = Field(None, description="Emotional engagement element")

    # Speaker notes (legacy field, now enhanced by talk_track)
    speaker_notes: Optional[str] = Field(None, description="Additional speaker notes")

    @field_validator('title', 'content', 'business_value')
    @classmethod
    def content_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Content fields cannot be empty')
        return v.strip()


class DatasetTable(BaseModel):
    """Dataset table schema for lab exercises."""

    name: str = Field(..., description="Table/index name")
    description: str = Field(..., description="Table purpose")
    fields: Dict[str, str] = Field(..., description="Field name → Elasticsearch field type mapping")
    sample_count: int = Field(..., description="Number of sample records")
    relationships: List[str] = Field(default_factory=list, description="Foreign key relationships (e.g., 'orders.customer_id')")


class LabChallenge(BaseModel):
    """Individual challenge/exercise in a lab."""

    number: int = Field(..., description="Challenge number (1-7)")
    title: str = Field(..., description="Challenge title")
    description: str = Field(..., description="What to accomplish")
    hint: Optional[str] = Field(None, description="Hint for solving")
    solution: str = Field(..., description="Complete solution command")
    expected_output: str = Field(..., description="Description of expected result")
    feature_used: Optional[str] = Field(None, description="Primary feature demonstrated")


class LabInstruction(BaseModel):
    """Lab instruction content for hands-on exercises with multi-feature support."""

    title: str = Field(..., description="Lab title")
    story_context: str = Field(..., description="2-3 paragraph narrative setting up the scenario")
    objective: str = Field(..., description="Learning objective")
    scenario: str = Field(..., description="Real-world scenario description (legacy field)")

    # Multi-feature support
    feature_ids: List[str] = Field(default_factory=list, description="Feature IDs covered in this lab")

    # Enhanced dataset structure
    dataset_tables: List[DatasetTable] = Field(default_factory=list, description="Multi-table dataset schema")
    setup_commands: List[str] = Field(default_factory=list, description="Copy-paste ready setup commands (index creation, bulk data)")

    # Challenge-based structure
    challenges: List[LabChallenge] = Field(default_factory=list, description="Progressive challenges")

    # Legacy fields (kept for backwards compatibility)
    setup_instructions: str = Field(default="", description="Setup and preparation steps (legacy)")
    steps: List[str] = Field(default_factory=list, description="Step-by-step instructions (legacy)")
    validation: str = Field(default="", description="How to validate completion (legacy)")
    sample_data: Optional[Dict[str, Any]] = Field(None, description="Sample data configuration (legacy)")

    # Metadata
    estimated_time: Optional[int] = Field(None, description="Estimated completion time in minutes")
    estimated_time_minutes: Optional[int] = Field(None, description="Alias for estimated_time")
    difficulty: Optional[str] = Field("intermediate", description="Difficulty level")

    @field_validator('challenges', 'steps')
    @classmethod
    def must_have_content(cls, v, info):
        # Either challenges or steps must be provided
        if info.field_name == 'challenges' and len(v) == 0:
            # Check if steps exist (legacy mode)
            return v
        return v


class StoryArc(BaseModel):
    """Complete story arc plan for a presentation."""

    opening_hook: str = Field(..., description="Industry challenge or compelling opener")
    central_theme: str = Field(..., description="Unifying theme connecting all features")
    narrative_thread: str = Field(..., description="Main storyline weaving features together")
    climax_feature: Optional[str] = Field(None, description="Most impactful feature ID for climax")
    resolution_message: str = Field(..., description="How features solve the opening challenge")
    call_to_action: str = Field(..., description="Next steps for audience")
    customer_journey_stages: List[str] = Field(default_factory=list, description="Customer journey mapped to features")
    competitive_positioning: Optional[str] = Field(None, description="How story positions against competition")


class NarrativeFlow(BaseModel):
    """Analysis of narrative flow between slides."""

    overall_coherence_score: float = Field(..., description="How well the story flows (0-1)")
    transition_quality: Dict[str, float] = Field(default_factory=dict, description="Slide-to-slide transition scores")
    pacing_analysis: str = Field(..., description="Analysis of presentation pacing")
    momentum_curve: List[float] = Field(default_factory=list, description="Energy/engagement curve across slides")
    suggested_improvements: List[str] = Field(default_factory=list, description="Narrative improvement suggestions")


class AudienceAdaptation(BaseModel):
    """Audience-specific content adaptations."""

    audience_type: str = Field(..., description="Target audience (business/technical/mixed)")
    technical_depth_level: str = Field(..., description="Appropriate technical depth (high/medium/low)")
    business_focus_areas: List[str] = Field(default_factory=list, description="Key business topics to emphasize")
    jargon_adjustments: Dict[str, str] = Field(default_factory=dict, description="Technical term simplifications")
    engagement_strategies: List[str] = Field(default_factory=list, description="Audience-specific engagement tactics")


class Presentation(BaseModel):
    """Complete presentation model with enhanced storytelling."""

    id: str = Field(..., description="Unique presentation identifier")
    domain: Domain = Field(..., description="Target domain")
    quarter: str = Field(..., description="Quarter identifier (e.g., 'Q1-2024')")
    title: str = Field(..., description="Presentation title")
    slides: List[SlideContent] = Field(..., description="Ordered list of slides")
    featured_themes: List[Theme] = Field(..., description="Themes covered in presentation")
    feature_ids: List[str] = Field(..., description="Source feature IDs")
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Enhanced storytelling components
    story_arc: Optional[StoryArc] = Field(None, description="Complete story arc plan")
    narrative_flow: Optional[NarrativeFlow] = Field(None, description="Narrative flow analysis")
    audience_adaptation: Optional[AudienceAdaptation] = Field(None, description="Audience-specific adaptations")
    total_talk_time_minutes: float = Field(default=30.0, description="Total estimated presentation time")
    confidence_requirements: Dict[str, str] = Field(default_factory=dict, description="Speaker skill requirements per section")

    @field_validator('slides')
    @classmethod
    def slides_must_not_be_empty(cls, v):
        if not v or len(v) == 0:
            raise ValueError('Presentation must have at least one slide')
        return v

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class Lab(BaseModel):
    """Complete lab exercise model."""

    id: str = Field(..., description="Unique lab identifier")
    feature_ids: List[str] = Field(..., description="Associated feature IDs")
    domain: Domain = Field(..., description="Target domain")
    instruction: LabInstruction = Field(..., description="Lab instructions")
    cross_domain_integration: Optional[List[Domain]] = Field(None, description="Cross-domain integrations")
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class ClassificationResult(BaseModel):
    """Result of feature classification."""

    feature_id: str = Field(..., description="Feature being classified")
    theme: Theme = Field(..., description="Classified theme")
    confidence: float = Field(..., description="Classification confidence (0-1)")
    reasoning: Optional[str] = Field(None, description="Classification reasoning")
    model_used: str = Field(..., description="LLM model used for classification")

    @field_validator('confidence')
    @classmethod
    def confidence_must_be_valid(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('Confidence must be between 0 and 1')
        return v


class ContentGenerationRequest(BaseModel):
    """Request for content generation with enhanced storytelling."""

    features: List[Feature] = Field(..., description="Features to include")
    domain: Domain = Field(..., description="Target domain")
    content_type: str = Field(..., description="Type of content to generate")
    audience: Optional[str] = Field("mixed", description="Target audience (business/technical/mixed)")

    # Storytelling configuration
    storytelling_enabled: bool = Field(default=True, description="Enable advanced storytelling features")
    narrative_style: str = Field(default="customer_journey", description="Narrative approach (customer_journey/problem_solution/innovation_showcase)")
    talk_track_detail_level: str = Field(default="comprehensive", description="Talk track detail (basic/standard/comprehensive)")
    include_customer_stories: bool = Field(default=True, description="Include customer success stories")
    competitive_positioning: bool = Field(default=False, description="Include competitive positioning")

    # Audience-specific customization
    technical_depth: str = Field(default="medium", description="Technical depth level (low/medium/high)")
    business_focus: List[str] = Field(default_factory=list, description="Key business areas to emphasize")

    custom_parameters: Optional[Dict[str, Any]] = Field(None, description="Custom generation parameters")

    @field_validator('features')
    @classmethod
    def features_must_not_be_empty(cls, v):
        if not v or len(v) == 0:
            raise ValueError('Must provide at least one feature')
        return v


class GenerationMetrics(BaseModel):
    """Metrics for content generation operations."""

    operation_id: str = Field(..., description="Unique operation identifier")
    content_type: str = Field(..., description="Type of content generated")
    features_processed: int = Field(..., description="Number of features processed")
    generation_time_seconds: float = Field(..., description="Total generation time")
    tokens_used: Optional[int] = Field(None, description="LLM tokens consumed")
    model_used: str = Field(..., description="LLM model used")
    success: bool = Field(..., description="Whether operation succeeded")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )