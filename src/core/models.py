"""
Core data models for the Elastic What's New Generator.

This module defines the fundamental data structures used throughout the application,
including features, themes, domains, and generated content models.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
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


class Feature(BaseModel):
    """Core feature model representing an Elastic capability."""

    id: str = Field(..., description="Unique identifier for the feature")
    name: str = Field(..., description="Feature name")
    description: str = Field(..., description="Brief description of the feature")
    benefits: List[str] = Field(default_factory=list, description="List of feature benefits")
    documentation_links: List[str] = Field(default_factory=list, description="Links to documentation")
    theme: Optional[Theme] = Field(None, description="Classified innovation theme")
    domain: Domain = Field(..., description="Product domain")
    scraped_content: Optional[str] = Field(None, description="Additional scraped content")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

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


class SlideContent(BaseModel):
    """Generated slide content for presentations."""

    title: str = Field(..., description="Slide title")
    subtitle: Optional[str] = Field(None, description="Optional subtitle")
    content: str = Field(..., description="Main slide content")
    business_value: str = Field(..., description="Business value proposition")
    theme: Theme = Field(..., description="Associated innovation theme")
    speaker_notes: Optional[str] = Field(None, description="Optional speaker notes")

    @field_validator('title', 'content', 'business_value')
    @classmethod
    def content_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Content fields cannot be empty')
        return v.strip()


class LabInstruction(BaseModel):
    """Lab instruction content for hands-on exercises."""

    title: str = Field(..., description="Lab title")
    objective: str = Field(..., description="Learning objective")
    scenario: str = Field(..., description="Real-world scenario description")
    setup_instructions: str = Field(..., description="Setup and preparation steps")
    steps: List[str] = Field(..., description="Step-by-step instructions")
    validation: str = Field(..., description="How to validate completion")
    sample_data: Optional[Dict[str, Any]] = Field(None, description="Sample data configuration")
    estimated_time: Optional[int] = Field(None, description="Estimated completion time in minutes")
    difficulty: Optional[str] = Field("intermediate", description="Difficulty level")

    @field_validator('steps')
    @classmethod
    def steps_must_not_be_empty(cls, v):
        if not v or len(v) == 0:
            raise ValueError('Lab must have at least one step')
        return v


class Presentation(BaseModel):
    """Complete presentation model."""

    id: str = Field(..., description="Unique presentation identifier")
    domain: Domain = Field(..., description="Target domain")
    quarter: str = Field(..., description="Quarter identifier (e.g., 'Q1-2024')")
    title: str = Field(..., description="Presentation title")
    slides: List[SlideContent] = Field(..., description="Ordered list of slides")
    featured_themes: List[Theme] = Field(..., description="Themes covered in presentation")
    feature_ids: List[str] = Field(..., description="Source feature IDs")
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

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
    """Request for content generation."""

    features: List[Feature] = Field(..., description="Features to include")
    domain: Domain = Field(..., description="Target domain")
    content_type: str = Field(..., description="Type of content to generate")
    audience: Optional[str] = Field("mixed", description="Target audience")
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