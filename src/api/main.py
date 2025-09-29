"""
Main FastAPI application for the Elastic What's New Generator.

This module provides REST API endpoints for feature management,
content generation, and presentation creation.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import tempfile
import shutil
import zipfile
import uvicorn
import logging
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

from src.core.models import Feature, Domain, Theme, SlideContent, LabInstruction, ContentResearch
from src.core.models import ContentGenerationRequest as StorytellingContentGenerationRequest
from src.core.classifier import FeatureClassifier
from src.core.generators.content_generator import ContentGenerator
from src.core.generators.presentation_generator import PresentationGenerator
from src.core.generators.unified_presentation_generator import UnifiedPresentationGenerator
from src.core.generators.llm_presentation_generator import LLMPresentationGenerator
from src.integrations.web_scraper import WebScraper
from src.integrations.instruqt_exporter import InstruqtExporter
from src.integrations.markdown_exporter import MarkdownExporter, MarkdownFormat
from src.integrations.content_research_service import ContentResearchService, ContentResearchConfig
from src.core.storytelling import StoryArcPlanner, TalkTrackGenerator, NarrativeFlowAnalyzer
from src.integrations.customer_story_research import CustomerStoryResearcher, BusinessValueCalculator

# Unified LLM client for multi-provider support (OpenAI, Gemini, Claude)
try:
    from src.integrations.unified_llm_client import UnifiedLLMClient
    import os
    # Initialize unified LLM client (auto-selects provider based on available API keys)
    # Use model from environment or default based on provider
    llm_model = os.getenv("LLM_MODEL")  # Override default model if needed
    llm_client = UnifiedLLMClient(model=llm_model) if llm_model else UnifiedLLMClient()
    print(f"LLM client initialized: {llm_client.get_provider_info()}")
except Exception as e:
    print(f"LLM client not available: {e}")
    llm_client = None

# Optional imports
try:
    from src.integrations.elasticsearch import FeatureStorage
    from elasticsearch import Elasticsearch
    ELASTICSEARCH_AVAILABLE = True
except ImportError:
    ELASTICSEARCH_AVAILABLE = False
    FeatureStorage = None
    Elasticsearch = None

# Initialize FastAPI app
app = FastAPI(
    title="Elastic What's New Generator",
    description="Automated presentation and lab generation for Elastic features",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
web_dir = Path(__file__).parent.parent.parent / "web"
if web_dir.exists():
    app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")

# Global instances (in production, use dependency injection)
classifier = FeatureClassifier()
content_generator = ContentGenerator()
presentation_generator = PresentationGenerator(content_generator)
unified_presentation_generator = UnifiedPresentationGenerator(content_generator)
web_scraper = WebScraper()
instruqt_exporter = InstruqtExporter()
markdown_exporter = MarkdownExporter()

# Storytelling components
story_arc_planner = StoryArcPlanner()
talk_track_generator = TalkTrackGenerator()
narrative_flow_analyzer = NarrativeFlowAnalyzer()
customer_story_researcher = CustomerStoryResearcher()
business_value_calculator = BusinessValueCalculator()

# Content research service with unified LLM client integration
content_research_config = ContentResearchConfig()
content_research_service = ContentResearchService(
    config=content_research_config,
    claude_client=llm_client  # Pass unified LLM client for extraction
)

# LLM presentation generator (Stage 2 of two-stage LLM architecture)
llm_presentation_generator = LLMPresentationGenerator(llm_client) if llm_client else None

# Dependency for Elasticsearch (in production, configure with settings)
def get_es_client():
    """Get Elasticsearch client for Serverless or local development."""
    import os

    # Check for Serverless configuration first
    es_url = os.getenv('ELASTICSEARCH_URL')
    api_key = os.getenv('ELASTICSEARCH_API_KEY')

    if es_url and api_key:
        # Serverless connection
        return Elasticsearch(
            es_url,
            api_key=api_key,
            verify_certs=True
        )
    elif es_url:
        # Local Elasticsearch without API key
        return Elasticsearch([es_url])

    # No configuration - demo mode
    return None

def get_feature_storage(es_client = Depends(get_es_client)):
    """Get FeatureStorage instance."""
    if es_client and ELASTICSEARCH_AVAILABLE:
        return FeatureStorage(es_client, index_name="elastic-whats-new-features")
    return None


# Request/Response models
class FeatureCreateRequest(BaseModel):
    name: str
    description: str
    benefits: List[str] = []
    documentation_links: List[str] = []
    domain: Domain
    scrape_docs: bool = False

class FeatureUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    benefits: Optional[List[str]] = None
    documentation_links: Optional[List[str]] = None
    domain: Optional[Domain] = None
    regenerate_content: bool = False

class ContentResearchRequest(BaseModel):
    feature_id: str
    force_refresh: bool = False

class FeatureResponse(BaseModel):
    id: str
    name: str
    description: str
    benefits: List[str]
    documentation_links: Optional[List[str]] = None
    theme: Optional[Theme]
    domain: Domain
    created_at: str
    updated_at: str
    content_research: Optional[ContentResearch] = None

class ClassificationRequest(BaseModel):
    feature_id: str

class ContentGenerationRequest(BaseModel):
    feature_ids: List[str]
    domain: Domain
    content_type: str  # "presentation" or "lab"
    audience: str = "mixed"

class PresentationGenerationRequest(BaseModel):
    feature_ids: List[str]
    domain: Domain
    quarter: str = "Q1-2024"
    audience: str = "mixed"
    # Advanced Storytelling Features
    narrative_style: str = "customer_journey"  # customer_journey, problem_solution, innovation_showcase
    talk_track_detail: str = "standard"  # comprehensive, standard, basic
    technical_depth: str = "medium"  # high, medium, low
    include_customer_stories: bool = True
    competitive_positioning: bool = False
    storytelling_enabled: bool = True

class UnifiedPresentationRequest(BaseModel):
    feature_ids: List[str]
    quarter: str = "Q1-2024"
    audience: str = "mixed"
    story_theme: str = "platform_transformation"
    # Advanced Storytelling Features
    narrative_style: str = "customer_journey"  # customer_journey, problem_solution, innovation_showcase
    talk_track_detail: str = "standard"  # comprehensive, standard, basic
    technical_depth: str = "medium"  # high, medium, low
    include_customer_stories: bool = True
    competitive_positioning: bool = False
    storytelling_enabled: bool = True

class PresentationResponse(BaseModel):
    slides: List[Dict[str, Any]]
    domain: str
    generated_at: str

class InstruqtExportRequest(BaseModel):
    feature_ids: List[str]
    track_title: str = "Elastic Workshop"
    export_format: str = "zip"  # "zip" or "directory"

class InstruqtExportResponse(BaseModel):
    track_slug: str
    download_url: str
    file_count: int
    track_metadata: Dict[str, Any]

class MarkdownExportRequest(BaseModel):
    presentation_id: Optional[str] = None
    feature_ids: List[str] = []
    domain: Optional[Domain] = None
    quarter: str = "Q1-2024"
    audience: str = "mixed"
    format_type: str = "standard"  # "standard", "github", "reveal_js"
    include_speaker_notes: bool = True
    include_metadata: bool = True
    include_business_value: bool = True
    filename: Optional[str] = None

class MarkdownExportResponse(BaseModel):
    content: Optional[str] = None
    download_url: Optional[str] = None
    filename: str
    format_type: str
    character_count: int

class LabMarkdownExportRequest(BaseModel):
    feature_ids: List[str]
    track_title: str = "Elastic Workshop"
    format_type: str = "standard"  # "standard", "github", "instruqt"
    include_metadata: bool = True
    export_format: str = "inline"  # "inline", "file", "multiple"
    filename: Optional[str] = None
    # Storytelling features for enhanced lab experience
    narrative_style: str = "customer_journey"
    include_customer_stories: bool = True
    technical_depth: str = "high"  # Labs are typically technical
    storytelling_enabled: bool = True

class LabMarkdownExportResponse(BaseModel):
    content: Optional[str] = None
    download_url: Optional[str] = None
    filename: str
    format_type: str
    character_count: int
    lab_count: int


class CustomerStoryRequest(BaseModel):
    """Request model for customer story research."""
    feature_id: str
    research_depth: str = "standard"  # basic, standard, comprehensive
    include_metrics: bool = True
    industry_focus: Optional[str] = None


class CustomerStoryResponse(BaseModel):
    """Response model for customer story research."""
    feature_id: str
    customer_stories: List[Dict[str, Any]]
    business_impact: Dict[str, Any]
    generated_at: datetime
    research_depth: str


class BusinessValueRequest(BaseModel):
    """Request model for business value calculation."""
    feature_ids: List[str]
    organization_size: str = "medium"  # small, medium, large, enterprise
    industry: Optional[str] = None
    current_spend: Optional[float] = None


class BusinessValueResponse(BaseModel):
    """Response model for business value calculation."""
    feature_ids: List[str]
    roi_projection: Dict[str, Any]
    value_drivers: List[Dict[str, str]]
    total_annual_savings: str
    payback_period: str
    calculated_at: datetime


class CompetitivePositioningRequest(BaseModel):
    """Request model for competitive positioning analysis."""
    feature_id: str
    competitors: Optional[List[str]] = None
    analysis_depth: str = "standard"  # basic, standard, comprehensive


class CompetitivePositioningResponse(BaseModel):
    """Response model for competitive positioning analysis."""
    feature_id: str
    competitive_analysis: Dict[str, Any]
    differentiators: List[str]
    market_position: str
    competitor_comparison: Dict[str, str]
    analyzed_at: datetime


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "elastic-whats-new-generator"}


# Serve web UI
@app.get("/")
async def serve_ui():
    """Serve the web UI."""
    web_file = web_dir / "index.html"
    if web_file.exists():
        return FileResponse(web_file)
    return {"message": "Web UI not available", "api_docs": "/docs"}


# Feature endpoints
@app.post("/features", response_model=FeatureResponse)
async def create_feature(
    request: FeatureCreateRequest,
    feature_storage: Optional[FeatureStorage] = Depends(get_feature_storage)
):
    """Create a new feature."""
    # Generate unique ID
    feature_id = f"{request.domain.value}-{hash(request.name) % 10000:04d}"

    # Create feature
    feature = Feature(
        id=feature_id,
        name=request.name,
        description=request.description,
        benefits=request.benefits,
        documentation_links=request.documentation_links,
        domain=request.domain
    )

    # Trigger content research if requested
    if request.scrape_docs and request.documentation_links:
        try:
            # The content research will be triggered asynchronously after feature creation
            # For now, just mark that research should be performed
            feature.content_research.scraping_enabled = True
        except Exception as e:
            # Log error but don't fail the request
            print(f"Warning: Failed to enable content research: {e}")

    # Classify feature
    try:
        theme = classifier.classify(feature)
        feature.theme = theme
    except Exception as e:
        print(f"Warning: Failed to classify feature: {e}")

    # Store feature if storage available
    if feature_storage:
        try:
            feature_storage.store(feature)
        except Exception as e:
            print(f"Warning: Failed to store feature: {e}")

    return FeatureResponse(
        id=feature.id,
        name=feature.name,
        description=feature.description,
        benefits=feature.benefits,
        documentation_links=feature.documentation_links,
        theme=feature.theme,
        domain=feature.domain,
        created_at=feature.created_at.isoformat(),
        updated_at=feature.updated_at.isoformat(),
        content_research=feature.content_research
    )


@app.get("/features", response_model=List[FeatureResponse])
async def list_features(
    domain: Optional[Domain] = None,
    theme: Optional[Theme] = None,
    limit: int = 50,
    feature_storage: Optional[FeatureStorage] = Depends(get_feature_storage)
):
    """List features with optional filtering."""
    if not feature_storage:
        raise HTTPException(status_code=503, detail="Feature storage not available")

    try:
        if domain:
            features = feature_storage.search_by_domain(domain, limit)
        elif theme:
            features = feature_storage.search_by_theme(theme, limit)
        else:
            features = feature_storage.get_all_features(limit)

        return [
            FeatureResponse(
                id=f.id,
                name=f.name,
                description=f.description,
                benefits=f.benefits,
                documentation_links=f.documentation_links,
                theme=f.theme,
                domain=f.domain,
                created_at=f.created_at.isoformat(),
                updated_at=f.updated_at.isoformat(),
                content_research=f.content_research
            )
            for f in features
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve features: {e}")


@app.get("/features/{feature_id}", response_model=FeatureResponse)
async def get_feature(
    feature_id: str,
    feature_storage: Optional[FeatureStorage] = Depends(get_feature_storage)
):
    """Get a specific feature by ID."""
    if not feature_storage:
        raise HTTPException(status_code=503, detail="Feature storage not available")

    try:
        feature = feature_storage.get_by_id(feature_id)
        if not feature:
            raise HTTPException(status_code=404, detail="Feature not found")

        return FeatureResponse(
            id=feature.id,
            name=feature.name,
            description=feature.description,
            benefits=feature.benefits,
            documentation_links=feature.documentation_links,
            theme=feature.theme,
            domain=feature.domain,
            created_at=feature.created_at.isoformat(),
            updated_at=feature.updated_at.isoformat(),
            content_research=feature.content_research
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve feature: {e}")


@app.put("/features/{feature_id}", response_model=FeatureResponse)
async def update_feature(
    feature_id: str,
    request: FeatureUpdateRequest,
    feature_storage: Optional[FeatureStorage] = Depends(get_feature_storage),
    es_client = Depends(get_es_client)
):
    """Update an existing feature."""
    if not feature_storage:
        raise HTTPException(status_code=503, detail="Feature storage not available")

    try:
        # Get the existing feature
        feature = feature_storage.get_by_id(feature_id)
        if not feature:
            raise HTTPException(status_code=404, detail="Feature not found")

        # Update fields that were provided
        if request.name is not None:
            feature.name = request.name
        if request.description is not None:
            feature.description = request.description
        if request.benefits is not None:
            feature.benefits = request.benefits
        if request.documentation_links is not None:
            feature.documentation_links = request.documentation_links
        if request.domain is not None:
            feature.domain = request.domain

        # Update timestamp
        feature.updated_at = datetime.now(timezone.utc)

        # Store the updated feature
        feature_storage.store(feature)

        # Trigger content research regeneration if requested
        if request.regenerate_content and es_client:
            from src.integrations.content_research_service import ContentResearchService
            content_service = ContentResearchService(es_client)
            try:
                # Trigger content research in background (don't wait for completion)
                import asyncio
                asyncio.create_task(content_service.research_feature_content(feature))
            except Exception as e:
                # Log error but don't fail the update
                print(f"Warning: Failed to trigger content research: {e}")

        return FeatureResponse(
            id=feature.id,
            name=feature.name,
            description=feature.description,
            benefits=feature.benefits,
            documentation_links=feature.documentation_links,
            theme=feature.theme,
            domain=feature.domain,
            created_at=feature.created_at.isoformat(),
            updated_at=feature.updated_at.isoformat(),
            content_research=feature.content_research
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update feature: {e}")


@app.delete("/features/{feature_id}")
async def delete_feature(
    feature_id: str,
    feature_storage: Optional[FeatureStorage] = Depends(get_feature_storage)
):
    """Delete a feature by ID."""
    if not feature_storage:
        raise HTTPException(status_code=503, detail="Feature storage not available")

    try:
        # Check if feature exists before deletion
        feature = feature_storage.get_by_id(feature_id)
        if not feature:
            raise HTTPException(status_code=404, detail="Feature not found")

        # Delete the feature
        success = feature_storage.delete_feature(feature_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete feature")

        return {"message": "Feature deleted successfully", "feature_id": feature_id}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete feature: {e}")


# Classification endpoint
@app.post("/features/{feature_id}/classify")
async def classify_feature(
    feature_id: str,
    feature_storage: Optional[FeatureStorage] = Depends(get_feature_storage)
):
    """Classify a feature into innovation themes."""
    if not feature_storage:
        raise HTTPException(status_code=503, detail="Feature storage not available")

    try:
        feature = feature_storage.get_by_id(feature_id)
        if not feature:
            raise HTTPException(status_code=404, detail="Feature not found")

        classification_result = classifier.classify_with_confidence(feature)

        # Update feature with classification
        feature.theme = classification_result.theme
        feature_storage.store(feature)

        return {
            "feature_id": feature_id,
            "theme": classification_result.theme,
            "confidence": classification_result.confidence,
            "reasoning": classification_result.reasoning
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {e}")


# Content generation endpoints
@app.post("/content/slides")
async def generate_slides(
    request: ContentGenerationRequest,
    feature_storage: Optional[FeatureStorage] = Depends(get_feature_storage)
):
    """Generate presentation slides for features."""
    if not feature_storage:
        # Use sample features for demo
        from tests.fixtures.sample_data import get_sample_search_features
        sample_features = get_sample_search_features()
        features = [f for f in sample_features if f.id in request.feature_ids]
    else:
        try:
            features = [feature_storage.get_by_id(fid) for fid in request.feature_ids]
            features = [f for f in features if f is not None]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve features: {e}")

    if not features:
        raise HTTPException(status_code=404, detail="No features found")

    try:
        slides = []
        for feature in features:
            slide_content = content_generator.generate_slide_content(feature)
            slides.append({
                "title": slide_content.title,
                "subtitle": slide_content.subtitle,
                "content": slide_content.content,
                "business_value": slide_content.business_value,
                "theme": slide_content.theme.value,
                "feature_id": feature.id
            })

        return {
            "slides": slides,
            "domain": request.domain.value,
            "audience": request.audience,
            "generated_at": "2024-01-01T00:00:00Z"  # Use actual timestamp in production
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content generation failed: {e}")


@app.post("/content/labs")
async def generate_labs(
    request: ContentGenerationRequest,
    feature_storage: Optional[FeatureStorage] = Depends(get_feature_storage)
):
    """Generate lab instructions for features."""
    if not feature_storage:
        # Use sample features for demo
        from tests.fixtures.sample_data import get_sample_search_features
        sample_features = get_sample_search_features()
        features = [f for f in sample_features if f.id in request.feature_ids]
    else:
        try:
            features = [feature_storage.get_by_id(fid) for fid in request.feature_ids]
            features = [f for f in features if f is not None]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve features: {e}")

    if not features:
        raise HTTPException(status_code=404, detail="No features found")

    try:
        labs = []
        for feature in features:
            lab_instruction = content_generator.generate_lab_instructions(feature)
            labs.append({
                "title": lab_instruction.title,
                "objective": lab_instruction.objective,
                "scenario": lab_instruction.scenario,
                "setup_instructions": lab_instruction.setup_instructions,
                "steps": lab_instruction.steps,
                "validation": lab_instruction.validation,
                "estimated_time": lab_instruction.estimated_time,
                "difficulty": lab_instruction.difficulty,
                "feature_id": feature.id
            })

        return {
            "labs": labs,
            "domain": request.domain.value,
            "generated_at": "2024-01-01T00:00:00Z"  # Use actual timestamp in production
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lab generation failed: {e}")


@app.post("/presentations/complete")
async def generate_complete_presentation(
    request: PresentationGenerationRequest,
    feature_storage: Optional[FeatureStorage] = Depends(get_feature_storage)
):
    """Generate a complete presentation following the 7-slide framework."""
    if not feature_storage:
        # Use sample features for demo
        from tests.fixtures.sample_data import get_all_sample_features
        all_features = get_all_sample_features()

        if request.domain == Domain.ALL_DOMAINS:
            features = all_features
        else:
            features = [f for f in all_features if f.domain == request.domain]

        # Filter by requested feature IDs if specified
        if request.feature_ids:
            features = [f for f in features if f.id in request.feature_ids]
    else:
        try:
            if request.feature_ids:
                features = [feature_storage.get_by_id(fid) for fid in request.feature_ids]
                features = [f for f in features if f is not None]
            else:
                # Get all features for domain
                if request.domain == Domain.ALL_DOMAINS:
                    features = feature_storage.get_all_features()
                else:
                    features = feature_storage.search_by_domain(request.domain)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve features: {e}")

    if not features:
        raise HTTPException(status_code=404, detail="No features found")

    try:
        # Check if we should use LLM presentation generation
        use_llm_generation = (
            llm_presentation_generator is not None and
            llm_presentation_generator.can_generate_presentation(features)
        )

        if use_llm_generation:
            # NEW: Use LLM-powered presentation generation (Stage 2)
            logger.info("Using LLM-powered presentation generation with cached extracted content")

            presentation_dict = llm_presentation_generator.generate_presentation(
                features=features,
                domain=request.domain,
                audience=request.audience,
                narrative_style=request.narrative_style,
                technical_depth=request.technical_depth,
                slide_count=7,
                quarter=request.quarter or "Q1-2025"
            )

            # Extract story arc from presentation
            story_arc = presentation_dict.get("story_arc")
            customer_stories = []  # LLM may include these inline

        else:
            # LEGACY: Use existing content generator (regex-based extraction)
            logger.info("Using legacy content generation (features lack LLM-extracted content)")

            # Generate storytelling components if enabled
            story_arc = None
            talk_tracks = []
            customer_stories = []

            # Create ContentGenerationRequest (always needed for content generation)
            content_request = StorytellingContentGenerationRequest(
                features=features,
                domain=request.domain,
                content_type="presentation",
                audience=request.audience,
                storytelling_enabled=request.storytelling_enabled,
                narrative_style=request.narrative_style,
                talk_track_detail_level=request.talk_track_detail,
                technical_depth=request.technical_depth,
                include_customer_stories=request.include_customer_stories,
                competitive_positioning=request.competitive_positioning
            )

            if request.storytelling_enabled:
                # Generate story arc
                story_arc = story_arc_planner.create_story_arc(
                    features=features,
                    domain=request.domain,
                    request=content_request
                )

                # Generate customer stories if requested
                if request.include_customer_stories:
                    for feature in features[:3]:  # Limit to 3 features for performance
                        feature_stories = await customer_story_researcher.research_customer_stories(
                            feature=feature,
                            max_stories=1
                        )
                        customer_stories.extend(feature_stories)

            # Use enhanced content generator with storytelling
            presentation_dict = content_generator.generate_complete_presentation(
                features=features,
                request=content_request
            )

        # Convert to API response format
        slides_data = []
        for slide in presentation_dict["slides"]:
            # Handle both dict (from LLM) and object (from legacy generator)
            if isinstance(slide, dict):
                slides_data.append({
                    "title": slide.get("title", ""),
                    "subtitle": slide.get("subtitle"),
                    "content": slide.get("content", ""),
                    "business_value": slide.get("business_value", ""),
                    "theme": slide.get("theme", "ai_innovation"),
                    "speaker_notes": slide.get("speaker_notes")
                })
            else:
                slides_data.append({
                    "title": slide.title,
                    "subtitle": slide.subtitle,
                    "content": slide.content,
                    "business_value": slide.business_value,
                    "theme": slide.theme.value,
                    "speaker_notes": slide.speaker_notes if hasattr(slide, 'speaker_notes') else None
                })

        # Build response with storytelling components
        # Handle featured_themes - can be strings (from LLM) or enum objects (from legacy)
        featured_themes = presentation_dict.get("featured_themes", [])
        if featured_themes and hasattr(featured_themes[0], 'value'):
            # Legacy format - enum objects
            featured_themes = [theme.value for theme in featured_themes]
        # else: already strings from LLM

        response_data = {
            "presentation": {
                "id": f"{request.domain.value}-presentation-{request.quarter}",
                "title": f"{request.domain.value.title()} Innovation - {request.quarter}",
                "domain": request.domain.value,
                "quarter": request.quarter,
                "slides": slides_data,
                "featured_themes": featured_themes,
                "feature_ids": presentation_dict.get("feature_ids", []),
                "generated_at": datetime.now(timezone.utc).isoformat()
            },
            "metadata": {
                "slide_count": len(slides_data),
                "feature_count": len(features),
                "audience": request.audience,
                "framework": "7-slide Elastic presentation framework with storytelling"
            }
        }

        # Add storytelling components if enabled
        if request.storytelling_enabled:
            if story_arc:
                # Handle both dict (from LLM) and object (from legacy)
                if isinstance(story_arc, dict):
                    response_data["story_arc"] = {
                        "narrative_style": request.narrative_style,
                        "opening_hook": story_arc.get('opening_hook', ''),
                        "central_theme": story_arc.get('central_theme', ''),
                        "narrative_thread": story_arc.get('narrative_thread', ''),
                        "resolution_message": story_arc.get('resolution_message', ''),
                        "call_to_action": story_arc.get('call_to_action', '')
                    }
                else:
                    response_data["story_arc"] = {
                        "narrative_style": request.narrative_style,
                        "opening_hook": getattr(story_arc, 'opening_hook', ''),
                        "central_theme": getattr(story_arc, 'central_theme', ''),
                        "narrative_thread": getattr(story_arc, 'narrative_thread', ''),
                        "resolution_message": getattr(story_arc, 'resolution_message', ''),
                        "call_to_action": getattr(story_arc, 'call_to_action', '')
                    }

            if customer_stories:
                response_data["customer_stories"] = [
                    {
                        "company_name": story.company_name,
                        "industry": story.industry,
                        "challenge": story.challenge,
                        "solution": story.solution,
                        "outcome": story.outcome,
                        "quote": story.quote,
                        "metrics": story.metrics
                    } for story in customer_stories
                ]

            # Add talk tracks from the presentation if available
            # Talk tracks are embedded in slides now via talk_track field
            # No separate talk_tracks list in presentation_dict format
            pass

        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Presentation generation failed: {e}")


@app.post("/presentations/unified")
async def generate_unified_presentation(
    request: UnifiedPresentationRequest,
    feature_storage: Optional[FeatureStorage] = Depends(get_feature_storage)
):
    """Generate an enhanced unified presentation with cross-domain storytelling."""
    # Get features
    if not feature_storage:
        # Use sample features for demo
        from tests.fixtures.sample_data import get_all_sample_features
        all_features = get_all_sample_features()

        # Filter by requested feature IDs if specified
        if request.feature_ids:
            features = [f for f in all_features if f.id in request.feature_ids]
        else:
            features = all_features
    else:
        try:
            if request.feature_ids:
                features = [feature_storage.get_by_id(fid) for fid in request.feature_ids]
                features = [f for f in features if f is not None]
            else:
                # Get all features across domains
                features = feature_storage.get_all_features()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve features: {e}")

    if not features:
        raise HTTPException(status_code=404, detail="No features found")

    try:
        # Generate unified presentation
        presentation = unified_presentation_generator.generate_unified_presentation(
            features=features,
            quarter=request.quarter,
            audience=request.audience,
            story_theme=request.story_theme
        )

        # Convert to API response format
        slides_data = []
        for slide in presentation.slides:
            slides_data.append({
                "title": slide.title,
                "subtitle": slide.subtitle,
                "content": slide.content,
                "business_value": slide.business_value,
                "theme": slide.theme.value,
                "speaker_notes": slide.speaker_notes
            })

        # Analyze domain distribution for metadata
        domain_counts = {}
        for feature in features:
            domain_counts[feature.domain.value] = domain_counts.get(feature.domain.value, 0) + 1

        return {
            "presentation": {
                "id": presentation.id,
                "title": presentation.title,
                "domain": presentation.domain.value,
                "quarter": presentation.quarter,
                "slides": slides_data,
                "featured_themes": [theme.value for theme in presentation.featured_themes],
                "feature_ids": presentation.feature_ids,
                "generated_at": presentation.generated_at.isoformat()
            },
            "metadata": {
                "slide_count": len(slides_data),
                "feature_count": len(features),
                "domain_distribution": domain_counts,
                "audience": request.audience,
                "story_theme": request.story_theme,
                "framework": "Enhanced 10-slide unified presentation framework",
                "cross_domain_synergies": len(domain_counts) > 1,
                "is_truly_unified": len([d for d in domain_counts.keys() if d != "all_domains"]) >= 3
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unified presentation generation failed: {e}")


@app.post("/presentations/markdown/export", response_model=MarkdownExportResponse)
async def export_presentation_markdown(
    request: MarkdownExportRequest,
    feature_storage: Optional[FeatureStorage] = Depends(get_feature_storage)
):
    """Export presentation to markdown format."""
    try:
        # Determine format type
        format_mapping = {
            "standard": MarkdownFormat.STANDARD,
            "github": MarkdownFormat.GITHUB,
            "reveal_js": MarkdownFormat.REVEAL_JS
        }
        format_type = format_mapping.get(request.format_type, MarkdownFormat.STANDARD)

        # If presentation_id is provided, try to retrieve existing presentation
        presentation = None
        if request.presentation_id:
            # In a real implementation, you'd retrieve the presentation from storage
            # For now, we'll generate a new one based on the request parameters
            pass

        # Generate presentation from features
        if not presentation:
            # Get features
            if not feature_storage:
                # Use sample features for demo
                from tests.fixtures.sample_data import get_all_sample_features
                all_features = get_all_sample_features()

                if request.domain:
                    if request.domain == Domain.ALL_DOMAINS:
                        features = all_features
                    else:
                        features = [f for f in all_features if f.domain == request.domain]
                else:
                    features = all_features

                # Filter by requested feature IDs if specified
                if request.feature_ids:
                    features = [f for f in features if f.id in request.feature_ids]
            else:
                try:
                    if request.feature_ids:
                        features = [feature_storage.get_by_id(fid) for fid in request.feature_ids]
                        features = [f for f in features if f is not None]
                    else:
                        # Get all features for domain
                        if request.domain == Domain.ALL_DOMAINS:
                            features = feature_storage.get_all_features()
                        else:
                            features = feature_storage.search_by_domain(request.domain)
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Failed to retrieve features: {e}")

            if not features:
                raise HTTPException(status_code=404, detail="No features found")

            # Generate presentation based on domain
            if request.domain == Domain.ALL_DOMAINS or (features and len(set(f.domain for f in features)) > 1):
                presentation = unified_presentation_generator.generate_unified_presentation(
                    features,
                    request.quarter,
                    request.audience
                )
            else:
                presentation = presentation_generator.generate_complete_presentation(
                    features,
                    request.domain or features[0].domain,
                    request.quarter,
                    request.audience
                )

        # Export to markdown
        markdown_content = markdown_exporter.export_presentation(
            presentation,
            format_type=format_type,
            include_speaker_notes=request.include_speaker_notes,
            include_metadata=request.include_metadata,
            include_business_value=request.include_business_value
        )

        # Generate filename
        if request.filename:
            filename = request.filename
            if not filename.endswith('.md'):
                filename += '.md'
        else:
            domain_slug = presentation.domain.value if hasattr(presentation.domain, 'value') else str(presentation.domain)
            filename = f"{domain_slug}-presentation-{request.quarter}-{request.format_type}.md"

        # Save file for download (in production, use proper file storage)
        temp_path = Path("/tmp") / filename
        temp_path.parent.mkdir(parents=True, exist_ok=True)

        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        download_url = f"/downloads/{filename}"

        return MarkdownExportResponse(
            download_url=download_url,
            filename=filename,
            format_type=request.format_type,
            character_count=len(markdown_content)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Markdown export failed: {e}")


@app.post("/presentations/markdown/inline", response_model=MarkdownExportResponse)
async def export_presentation_markdown_inline(
    request: MarkdownExportRequest,
    feature_storage: Optional[FeatureStorage] = Depends(get_feature_storage)
):
    """Export presentation to markdown format (returns content inline)."""
    try:
        # Determine format type
        format_mapping = {
            "standard": MarkdownFormat.STANDARD,
            "github": MarkdownFormat.GITHUB,
            "reveal_js": MarkdownFormat.REVEAL_JS
        }
        format_type = format_mapping.get(request.format_type, MarkdownFormat.STANDARD)

        # Generate presentation from features (same logic as above)
        if not feature_storage:
            # Use sample features for demo
            from tests.fixtures.sample_data import get_all_sample_features
            all_features = get_all_sample_features()

            if request.domain:
                if request.domain == Domain.ALL_DOMAINS:
                    features = all_features
                else:
                    features = [f for f in all_features if f.domain == request.domain]
            else:
                features = all_features

            # Filter by requested feature IDs if specified
            if request.feature_ids:
                features = [f for f in features if f.id in request.feature_ids]
        else:
            try:
                if request.feature_ids:
                    features = [feature_storage.get_by_id(fid) for fid in request.feature_ids]
                    features = [f for f in features if f is not None]
                else:
                    # Get all features for domain
                    if request.domain == Domain.ALL_DOMAINS:
                        features = feature_storage.get_all_features()
                    else:
                        features = feature_storage.search_by_domain(request.domain)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to retrieve features: {e}")

        if not features:
            raise HTTPException(status_code=404, detail="No features found")

        # Generate presentation based on domain
        if request.domain == Domain.ALL_DOMAINS or (features and len(set(f.domain for f in features)) > 1):
            presentation = unified_presentation_generator.generate_unified_presentation(
                features,
                request.quarter,
                request.audience
            )
        else:
            presentation = presentation_generator.generate_complete_presentation(
                features,
                request.domain or features[0].domain,
                request.quarter,
                request.audience
            )

        # Export to markdown
        markdown_content = markdown_exporter.export_presentation(
            presentation,
            format_type=format_type,
            include_speaker_notes=request.include_speaker_notes,
            include_metadata=request.include_metadata,
            include_business_value=request.include_business_value
        )

        # Generate filename for reference
        domain_slug = presentation.domain.value if hasattr(presentation.domain, 'value') else str(presentation.domain)
        filename = f"{domain_slug}-presentation-{request.quarter}-{request.format_type}.md"

        return MarkdownExportResponse(
            content=markdown_content,
            filename=filename,
            format_type=request.format_type,
            character_count=len(markdown_content)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Markdown export failed: {e}")


@app.post("/labs/markdown/export", response_model=LabMarkdownExportResponse)
async def export_lab_markdown(
    request: LabMarkdownExportRequest,
    feature_storage: Optional[FeatureStorage] = Depends(get_feature_storage)
):
    """Export lab instructions to markdown format."""
    try:
        # Get features
        if not feature_storage:
            # Use sample features for demo
            from tests.fixtures.sample_data import get_all_sample_features
            all_features = get_all_sample_features()
            features = [f for f in all_features if f.id in request.feature_ids]
        else:
            try:
                features = [feature_storage.get_by_id(fid) for fid in request.feature_ids]
                features = [f for f in features if f is not None]
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to retrieve features: {e}")

        if not features:
            raise HTTPException(status_code=404, detail="No features found")

        # Generate lab instructions for each feature
        lab_instructions = []
        for feature in features:
            lab_instruction = content_generator.generate_lab_instructions(feature)
            lab_instructions.append(lab_instruction)

        # Export to markdown
        if len(lab_instructions) == 1:
            # Single lab export
            markdown_content = instruqt_exporter.export_lab_to_markdown(
                lab_instructions[0],
                format_type=request.format_type,
                include_metadata=request.include_metadata
            )
            filename = f"{features[0].name.lower().replace(' ', '-')}-lab-{request.format_type}.md"
        else:
            # Multiple labs export
            markdown_content = instruqt_exporter.export_multiple_labs_to_markdown(
                lab_instructions,
                track_title=request.track_title,
                format_type=request.format_type,
                include_metadata=request.include_metadata
            )
            filename = f"{request.track_title.lower().replace(' ', '-')}-{request.format_type}.md"

        # Override filename if provided
        if request.filename:
            filename = request.filename
            if not filename.endswith('.md'):
                filename += '.md'

        # Handle export format
        if request.export_format == "file":
            # Save file for download
            temp_path = Path("/tmp") / filename
            temp_path.parent.mkdir(parents=True, exist_ok=True)

            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            download_url = f"/downloads/{filename}"

            return LabMarkdownExportResponse(
                download_url=download_url,
                filename=filename,
                format_type=request.format_type,
                character_count=len(markdown_content),
                lab_count=len(lab_instructions)
            )
        else:
            # Inline export
            return LabMarkdownExportResponse(
                content=markdown_content,
                filename=filename,
                format_type=request.format_type,
                character_count=len(markdown_content),
                lab_count=len(lab_instructions)
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lab markdown export failed: {e}")


@app.post("/labs/markdown/single", response_model=LabMarkdownExportResponse)
async def export_single_lab_markdown(
    request: LabMarkdownExportRequest,
    feature_storage: Optional[FeatureStorage] = Depends(get_feature_storage)
):
    """Export a single lab instruction to markdown format."""
    try:
        if len(request.feature_ids) != 1:
            raise HTTPException(status_code=400, detail="Single lab export requires exactly one feature ID")

        # Get single feature
        if not feature_storage:
            # Use sample features for demo
            from tests.fixtures.sample_data import get_all_sample_features
            all_features = get_all_sample_features()
            features = [f for f in all_features if f.id == request.feature_ids[0]]
        else:
            try:
                feature = feature_storage.get_by_id(request.feature_ids[0])
                features = [feature] if feature else []
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to retrieve feature: {e}")

        if not features:
            raise HTTPException(status_code=404, detail="Feature not found")

        feature = features[0]

        # Generate lab instruction
        lab_instruction = content_generator.generate_lab_instructions(feature)

        # Export to markdown
        markdown_content = instruqt_exporter.export_lab_to_markdown(
            lab_instruction,
            format_type=request.format_type,
            include_metadata=request.include_metadata
        )

        # Generate filename
        filename = f"{feature.name.lower().replace(' ', '-')}-lab-{request.format_type}.md"
        if request.filename:
            filename = request.filename
            if not filename.endswith('.md'):
                filename += '.md'

        # Handle export format
        if request.export_format == "file":
            # Save file for download
            temp_path = Path("/tmp") / filename
            temp_path.parent.mkdir(parents=True, exist_ok=True)

            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            download_url = f"/downloads/{filename}"

            return LabMarkdownExportResponse(
                download_url=download_url,
                filename=filename,
                format_type=request.format_type,
                character_count=len(markdown_content),
                lab_count=1
            )
        else:
            # Inline export
            return LabMarkdownExportResponse(
                content=markdown_content,
                filename=filename,
                format_type=request.format_type,
                character_count=len(markdown_content),
                lab_count=1
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Single lab markdown export failed: {e}")


@app.post("/instruqt/export", response_model=InstruqtExportResponse)
async def export_instruqt_track(
    request: InstruqtExportRequest,
    feature_storage: Optional[FeatureStorage] = Depends(get_feature_storage)
):
    """Export features as Instruqt track for hands-on training."""
    # Get features
    if not feature_storage:
        # Use sample features for demo
        from tests.fixtures.sample_data import get_all_sample_features
        all_features = get_all_sample_features()
        features = [f for f in all_features if f.id in request.feature_ids]
    else:
        try:
            features = [feature_storage.get_by_id(fid) for fid in request.feature_ids]
            features = [f for f in features if f is not None]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve features: {e}")

    if not features:
        raise HTTPException(status_code=404, detail="No features found")

    try:
        # Generate lab instructions for each feature
        lab_instructions = []
        for feature in features:
            lab_instruction = content_generator.generate_lab_instructions(feature)
            lab_instructions.append(lab_instruction)

        # Create temporary directory for export
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Export to Instruqt format
            if len(features) == 1:
                # Single track
                track_dir = instruqt_exporter.export_lab_instruction(
                    lab_instructions[0],
                    features[0],
                    temp_path
                )
            else:
                # Combined track
                track_dir = instruqt_exporter.export_multiple_labs(
                    lab_instructions,
                    features,
                    temp_path,
                    request.track_title
                )

            # Count files
            file_count = sum(1 for _ in track_dir.rglob("*") if _.is_file())

            track_slug = track_dir.name

            if request.export_format == "zip":
                # Create ZIP file
                zip_path = temp_path / f"{track_slug}.zip"
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in track_dir.rglob("*"):
                        if file_path.is_file():
                            # Add file to ZIP with relative path
                            arcname = file_path.relative_to(track_dir)
                            zipf.write(file_path, arcname)

                # Move ZIP to a location accessible for download
                # In production, this would be a proper file storage service
                download_path = Path("/tmp") / f"{track_slug}.zip"
                shutil.copy2(zip_path, download_path)
                download_url = f"/downloads/{track_slug}.zip"
            else:
                # Directory format (for development/testing)
                download_url = f"/tracks/{track_slug}"
                download_path = track_dir

            # Get track metadata
            track_metadata = {
                "feature_count": len(features),
                "total_estimated_time": sum(lab.estimated_time for lab in lab_instructions),
                "domains": list(set(f.domain.value for f in features)),
                "difficulties": list(set(lab.difficulty for lab in lab_instructions))
            }

            return InstruqtExportResponse(
                track_slug=track_slug,
                download_url=download_url,
                file_count=file_count,
                track_metadata=track_metadata
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Instruqt export failed: {e}")


@app.get("/downloads/{filename}")
async def download_file(filename: str):
    """Download exported Instruqt track files."""
    file_path = Path("/tmp") / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/zip"
    )


# Content Research Endpoints

@app.post("/features/{feature_id}/research")
async def trigger_content_research(
    feature_id: str,
    request: ContentResearchRequest,
    feature_storage: Optional[FeatureStorage] = Depends(get_feature_storage),
    es_client = Depends(get_es_client)
):
    """Trigger content research for a specific feature."""
    if not feature_storage:
        raise HTTPException(status_code=503, detail="Feature storage not available")

    try:
        # Get the feature
        feature = feature_storage.get_by_id(feature_id)
        if not feature:
            raise HTTPException(status_code=404, detail="Feature not found")

        # Check if research already exists and force_refresh is not set
        if (feature.content_research.status == "completed" and
            not request.force_refresh):
            return {
                "status": "already_completed",
                "message": "Content research already completed. Use force_refresh=true to regenerate.",
                "feature_id": feature_id,
                "last_updated": feature.content_research.last_updated.isoformat()
            }

        # Initialize content research service with AI, ES, and unified LLM client
        research_service = ContentResearchService(
            config=content_research_config,
            ai_client=content_generator,  # Reuse existing AI client
            elasticsearch_client=es_client,
            claude_client=llm_client  # Add unified LLM client for extraction
        )

        # Trigger research (this would normally be async/background)
        updated_research = await research_service.research_feature_content(feature)

        # Update feature with research results
        feature.content_research = updated_research
        feature_storage.store(feature)

        return {
            "status": "completed",
            "message": "Content research completed successfully",
            "feature_id": feature_id,
            "research_status": updated_research.status.value,
            "primary_sources_count": len(updated_research.primary_sources),
            "related_sources_count": len(updated_research.related_sources),
            "key_concepts_count": len(updated_research.extracted_content.key_concepts),
            "embeddings_generated": bool(updated_research.embeddings.feature_summary)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content research failed: {e}")


@app.get("/features/{feature_id}/research")
async def get_content_research_status(
    feature_id: str,
    feature_storage: Optional[FeatureStorage] = Depends(get_feature_storage)
):
    """Get content research status for a feature."""
    if not feature_storage:
        raise HTTPException(status_code=503, detail="Feature storage not available")

    try:
        feature = feature_storage.get_by_id(feature_id)
        if not feature:
            raise HTTPException(status_code=404, detail="Feature not found")

        research = feature.content_research

        return {
            "feature_id": feature_id,
            "status": research.status.value,
            "last_updated": research.last_updated.isoformat(),
            "scraping_enabled": research.scraping_enabled,
            "research_depth": research.research_depth.value,
            "sources": {
                "primary_count": len(research.primary_sources),
                "related_count": len(research.related_sources),
                "total_word_count": sum(s.word_count for s in research.primary_sources + research.related_sources)
            },
            "extracted_content": {
                "key_concepts_count": len(research.extracted_content.key_concepts),
                "use_cases_count": len(research.extracted_content.use_cases),
                "config_examples_count": len(research.extracted_content.configuration_examples),
                "prerequisites_count": len(research.extracted_content.prerequisites)
            },
            "ai_insights": {
                "has_technical_summary": bool(research.ai_insights.technical_summary),
                "has_business_value": bool(research.ai_insights.business_value),
                "presentation_angles_count": len(research.ai_insights.presentation_angles),
                "lab_scenarios_count": len(research.ai_insights.lab_scenarios)
            },
            "embeddings": {
                "feature_summary": bool(research.embeddings.feature_summary),
                "technical_content": bool(research.embeddings.technical_content),
                "full_documentation": bool(research.embeddings.full_documentation)
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get research status: {e}")


@app.get("/features/{feature_id}/research/detailed")
async def get_detailed_content_research(
    feature_id: str,
    feature_storage: Optional[FeatureStorage] = Depends(get_feature_storage)
):
    """Get detailed content research data for a feature."""
    if not feature_storage:
        raise HTTPException(status_code=503, detail="Feature storage not available")

    try:
        feature = feature_storage.get_by_id(feature_id)
        if not feature:
            raise HTTPException(status_code=404, detail="Feature not found")

        # Return the complete content research structure
        # Note: This could be large, so in production you might want to paginate or limit
        return {
            "feature_id": feature_id,
            "feature_name": feature.name,
            "content_research": feature.content_research.model_dump()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get detailed research: {e}")


@app.post("/features/{feature_id}/research/search")
async def semantic_search_features(
    query: str,
    search_field: str = "feature_summary",  # feature_summary, technical_content, full_documentation
    limit: int = 10,
    es_client = Depends(get_es_client)
):
    """Perform semantic search using ELSER embeddings."""
    if not es_client:
        raise HTTPException(status_code=503, detail="Elasticsearch not available")

    try:
        # Construct ELSER search query
        search_query = {
            "query": {
                "text_expansion": {
                    f"content_research.embeddings.{search_field}.elser_embedding": {
                        "model_id": ".elser_model_2",
                        "model_text": query
                    }
                }
            },
            "size": limit,
            "_source": [
                "id", "name", "description", "domain", "theme",
                f"content_research.embeddings.{search_field}.text"
            ]
        }

        response = await es_client.search(
            index="elastic-whats-new-features",
            body=search_query
        )

        results = []
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            results.append({
                "feature_id": source["id"],
                "name": source["name"],
                "description": source["description"],
                "domain": source["domain"],
                "theme": source.get("theme"),
                "score": hit["_score"],
                "embedding_text": source.get("content_research", {}).get("embeddings", {}).get(search_field, {}).get("text", "")[:200]
            })

        return {
            "query": query,
            "search_field": search_field,
            "total_results": response["hits"]["total"]["value"],
            "results": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Semantic search failed: {e}")


# === Customer Story & Business Value Endpoints ===

@app.post("/features/{feature_id}/customer-stories", response_model=CustomerStoryResponse)
async def research_customer_stories(
    feature_id: str,
    request: CustomerStoryRequest,
    feature_storage: FeatureStorage = Depends(get_feature_storage)
):
    """Generate customer success stories and business impact analysis for a specific feature."""
    if not feature_storage:
        raise HTTPException(status_code=503, detail="Feature storage not available")

    try:
        # Get the feature
        feature = feature_storage.get_by_id(feature_id)
        if not feature:
            raise HTTPException(status_code=404, detail="Feature not found")

        # Initialize customer story researcher
        researcher = CustomerStoryResearcher()

        # Research customer stories
        customer_stories = await researcher.research_customer_stories(
            feature,
            count=3 if request.research_depth == "basic" else 5 if request.research_depth == "standard" else 8,
            industry_focus=request.industry_focus
        )

        # Research business impact if requested
        business_impact = {}
        if request.include_metrics:
            business_impact = await researcher.research_business_impact(feature)
            business_impact = business_impact.model_dump() if hasattr(business_impact, 'model_dump') else business_impact

        return CustomerStoryResponse(
            feature_id=feature_id,
            customer_stories=[story.model_dump() if hasattr(story, 'model_dump') else story for story in customer_stories],
            business_impact=business_impact,
            generated_at=datetime.now(timezone.utc),
            research_depth=request.research_depth
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Customer story research failed: {e}")


@app.post("/features/business-value", response_model=BusinessValueResponse)
async def calculate_business_value(
    request: BusinessValueRequest,
    feature_storage: FeatureStorage = Depends(get_feature_storage)
):
    """Calculate business value and ROI for multiple features."""
    if not feature_storage:
        raise HTTPException(status_code=503, detail="Feature storage not available")

    try:
        # Get all features
        features = []
        for feature_id in request.feature_ids:
            feature = feature_storage.get_by_id(feature_id)
            if feature:
                features.append(feature)

        if not features:
            raise HTTPException(status_code=404, detail="No valid features found")

        # Initialize business value calculator
        calculator = BusinessValueCalculator()

        # Calculate ROI projection for the first feature (or aggregate logic could be added)
        primary_feature = features[0]
        roi_projection = calculator.calculate_roi_projection(primary_feature)

        # Generate value drivers for all features
        all_value_drivers = []
        for feature in features:
            drivers = calculator.generate_value_drivers(feature)
            all_value_drivers.extend(drivers)

        return BusinessValueResponse(
            feature_ids=request.feature_ids,
            roi_projection=roi_projection.model_dump() if hasattr(roi_projection, 'model_dump') else roi_projection,
            value_drivers=all_value_drivers,
            total_annual_savings=getattr(roi_projection, 'total_annual_savings', '$100K - $500K'),
            payback_period=getattr(roi_projection, 'payback_period', '6-12 months'),
            calculated_at=datetime.now(timezone.utc)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Business value calculation failed: {e}")


@app.post("/features/{feature_id}/competitive-analysis", response_model=CompetitivePositioningResponse)
async def analyze_competitive_positioning(
    feature_id: str,
    request: CompetitivePositioningRequest,
    feature_storage: FeatureStorage = Depends(get_feature_storage)
):
    """Generate competitive positioning analysis for a specific feature."""
    if not feature_storage:
        raise HTTPException(status_code=503, detail="Feature storage not available")

    try:
        # Get the feature
        feature = feature_storage.get_by_id(feature_id)
        if not feature:
            raise HTTPException(status_code=404, detail="Feature not found")

        # Initialize customer story researcher (which also handles competitive analysis)
        researcher = CustomerStoryResearcher()

        # Research competitive positioning
        competitive_analysis = await researcher.research_competitive_positioning(
            feature,
            competitors=request.competitors
        )

        return CompetitivePositioningResponse(
            feature_id=feature_id,
            competitive_analysis=competitive_analysis.model_dump() if hasattr(competitive_analysis, 'model_dump') else competitive_analysis,
            differentiators=getattr(competitive_analysis, 'differentiators', []),
            market_position=getattr(competitive_analysis, 'market_position', 'Leading'),
            competitor_comparison=getattr(competitive_analysis, 'competitor_comparison', {}),
            analyzed_at=datetime.now(timezone.utc)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Competitive analysis failed: {e}")


# === End-to-End Presentation Generation ===

@app.post("/presentations/complete-storytelling")
async def generate_complete_storytelling_presentation(
    request: PresentationGenerationRequest,
    feature_storage: FeatureStorage = Depends(get_feature_storage)
):
    """
    Generate a complete presentation with full story arcs, talk tracks, customer stories, and business value.
    This endpoint provides end-to-end storytelling presentation generation.
    """
    if not feature_storage:
        raise HTTPException(status_code=503, detail="Feature storage not available")

    try:
        # Get all features
        features = []
        for feature_id in request.feature_ids:
            feature = feature_storage.get_by_id(feature_id)
            if feature:
                features.append(feature)

        if not features:
            raise HTTPException(status_code=404, detail="No valid features found")

        # Initialize all storytelling components
        story_arc_planner = StoryArcPlanner()
        talk_track_generator = TalkTrackGenerator()
        narrative_flow_analyzer = NarrativeFlowAnalyzer()
        customer_story_researcher = CustomerStoryResearcher()
        business_value_calculator = BusinessValueCalculator()

        # Create comprehensive storytelling presentation
        presentation_data = {
            "metadata": {
                "title": f"{request.domain.value.title()} Innovation Showcase",
                "subtitle": f"Q{request.quarter.split('-')[0][1:]} {request.quarter.split('-')[1]} Release Highlights",
                "domain": request.domain.value,
                "audience": request.audience,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "storytelling_enabled": request.storytelling_enabled,
                "feature_count": len(features)
            },
            "story_arc": {},
            "customer_stories": [],
            "business_value": {},
            "competitive_analysis": {},
            "talk_tracks": [],
            "slides": []
        }

        if request.storytelling_enabled:
            # 1. Create Story Arc
            from src.core.models import ContentGenerationRequest as StorytellingContentRequest
            content_request = StorytellingContentRequest(
                features=features,
                domain=request.domain,
                content_type="presentation",
                audience=request.audience,
                narrative_style=request.narrative_style,
                technical_depth=request.technical_depth,
                storytelling_enabled=True,
                include_customer_stories=request.include_customer_stories,
                competitive_positioning=request.competitive_positioning
            )

            story_arc = story_arc_planner.create_story_arc(features, request.domain, content_request)
            presentation_data["story_arc"] = {
                "narrative_style": request.narrative_style,
                "positions": [pos.value for pos in story_arc.positions] if hasattr(story_arc, 'positions') else [],
                "themes": [theme.value for theme in story_arc.themes] if hasattr(story_arc, 'themes') else [],
                "total_duration": getattr(story_arc, 'estimated_duration', 25)
            }

            # 2. Generate Customer Stories (if requested)
            if request.include_customer_stories:
                for feature in features[:3]:  # Limit to first 3 features for performance
                    try:
                        customer_stories = await customer_story_researcher.research_customer_stories(feature, max_stories=2)
                        business_impact = await customer_story_researcher.research_business_impact(feature)

                        presentation_data["customer_stories"].append({
                            "feature_id": feature.id,
                            "feature_name": feature.name,
                            "stories": [story.model_dump() if hasattr(story, 'model_dump') else story for story in customer_stories],
                            "business_impact": business_impact.model_dump() if hasattr(business_impact, 'model_dump') else business_impact
                        })
                    except Exception as e:
                        print(f"Warning: Could not generate customer stories for {feature.name}: {e}")

            # 3. Calculate Business Value
            try:
                primary_feature = features[0]
                roi_projection = business_value_calculator.calculate_roi_projection(primary_feature)
                value_drivers = []
                for feature in features:
                    drivers = business_value_calculator.generate_value_drivers(feature)
                    value_drivers.extend(drivers)

                presentation_data["business_value"] = {
                    "roi_projection": roi_projection.model_dump() if hasattr(roi_projection, 'model_dump') else roi_projection,
                    "value_drivers": value_drivers,
                    "total_annual_savings": getattr(roi_projection, 'total_annual_savings', '$500K - $2M'),
                    "payback_period": getattr(roi_projection, 'payback_period', '6-12 months')
                }
            except Exception as e:
                print(f"Warning: Could not calculate business value: {e}")

            # 4. Competitive Analysis (if requested)
            if request.competitive_positioning:
                try:
                    primary_feature = features[0]
                    competitive_analysis = await customer_story_researcher.research_competitive_positioning(primary_feature)
                    presentation_data["competitive_analysis"] = {
                        "feature_id": primary_feature.id,
                        "analysis": competitive_analysis.model_dump() if hasattr(competitive_analysis, 'model_dump') else competitive_analysis,
                        "generated_for": primary_feature.name
                    }
                except Exception as e:
                    print(f"Warning: Could not generate competitive analysis: {e}")

        # 5. Generate Enhanced Slides with Storytelling
        unified_generator = UnifiedPresentationGenerator()

        # Generate the main content
        slides_content = unified_generator.generate_unified_presentation(
            features,
            quarter=request.quarter,
            audience=request.audience
        )

        # Enhance slides with storytelling elements
        enhanced_slides = []
        slides_list = slides_content.slides if hasattr(slides_content, 'slides') else []
        for i, slide in enumerate(slides_list):
            enhanced_slide = {
                "slide_number": i + 1,
                "title": getattr(slide, 'title', f"Slide {i + 1}"),
                "content": getattr(slide, 'content', ""),
                "business_value": getattr(slide, 'business_value', ""),
                "theme": getattr(slide, 'theme', None),
                "story_position": presentation_data["story_arc"].get("positions", ["introduction"])[min(i, len(presentation_data["story_arc"].get("positions", [])) - 1)] if presentation_data["story_arc"] else "introduction",
                "estimated_duration": 2.5
            }

            # Add storytelling enhancements if enabled
            if request.storytelling_enabled and i < len(features):
                feature = features[i]
                try:
                    from src.core.storytelling import StoryPosition
                    story_position = StoryPosition.OPENING_HOOK if i == 0 else StoryPosition.PROBLEM_BUILD

                    talk_track = talk_track_generator.generate_talk_track(
                        feature,
                        story_position,
                        detail_level=request.talk_track_detail,
                        technical_depth=request.technical_depth
                    )

                    enhanced_slide["talk_track"] = {
                        "opening_statement": getattr(talk_track, 'opening_statement', ''),
                        "key_points": getattr(talk_track, 'key_points', []),
                        "transitions": getattr(talk_track, 'transitions', []),
                        "estimated_duration": getattr(talk_track, 'estimated_duration', 2.5)
                    }
                except Exception as e:
                    print(f"Warning: Could not generate talk track for slide {i + 1}: {e}")

            enhanced_slides.append(enhanced_slide)

        presentation_data["slides"] = enhanced_slides

        # 6. Generate Summary and Analytics
        presentation_data["summary"] = {
            "total_slides": len(enhanced_slides),
            "estimated_duration": sum(slide.get("estimated_duration", 2.5) for slide in enhanced_slides),
            "storytelling_features": {
                "story_arc": bool(presentation_data["story_arc"]),
                "customer_stories": len(presentation_data["customer_stories"]) > 0,
                "business_value": bool(presentation_data["business_value"]),
                "competitive_analysis": bool(presentation_data["competitive_analysis"]),
                "talk_tracks": any("talk_track" in slide for slide in enhanced_slides)
            },
            "feature_distribution": {
                feature.domain.value: len([f for f in features if f.domain == feature.domain])
                for feature in features
            }
        }

        return {
            "success": True,
            "presentation_id": f"storytelling-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}",
            "presentation": presentation_data,
            "generation_metadata": {
                "request_parameters": request.model_dump(),
                "processing_time": "Generated in real-time",
                "api_version": "v1.0-storytelling"
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Complete storytelling presentation generation failed: {e}")


# Development server runner
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)