"""
Main FastAPI application for the Elastic What's New Generator.

This module provides REST API endpoints for feature management,
content generation, and presentation creation.
"""

from typing import List, Dict, Any, Optional
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

from src.core.models import Feature, Domain, Theme, SlideContent, LabInstruction
from src.core.classifier import FeatureClassifier
from src.core.generators.content_generator import ContentGenerator
from src.core.generators.presentation_generator import PresentationGenerator
from src.core.generators.unified_presentation_generator import UnifiedPresentationGenerator
from src.integrations.web_scraper import WebScraper
from src.integrations.instruqt_exporter import InstruqtExporter
from src.integrations.markdown_exporter import MarkdownExporter, MarkdownFormat

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

# Dependency for Elasticsearch (in production, configure with settings)
def get_es_client():
    """Get Elasticsearch client (mock for development)."""
    # In production, return actual ES client: Elasticsearch(["localhost:9200"])
    return None

def get_feature_storage(es_client = Depends(get_es_client)):
    """Get FeatureStorage instance."""
    if es_client and ELASTICSEARCH_AVAILABLE:
        return FeatureStorage(es_client)
    return None


# Request/Response models
class FeatureCreateRequest(BaseModel):
    name: str
    description: str
    benefits: List[str] = []
    documentation_links: List[str] = []
    domain: Domain
    scrape_docs: bool = False

class FeatureResponse(BaseModel):
    id: str
    name: str
    description: str
    benefits: List[str]
    theme: Optional[Theme]
    domain: Domain
    created_at: str

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

class UnifiedPresentationRequest(BaseModel):
    feature_ids: List[str]
    quarter: str = "Q1-2024"
    audience: str = "mixed"
    story_theme: str = "platform_transformation"

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

class LabMarkdownExportResponse(BaseModel):
    content: Optional[str] = None
    download_url: Optional[str] = None
    filename: str
    format_type: str
    character_count: int
    lab_count: int


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

    # Scrape documentation if requested
    if request.scrape_docs and request.documentation_links:
        try:
            scraped_content = web_scraper.extract_feature_context(
                request.name,
                request.documentation_links
            )
            feature.scraped_content = scraped_content
        except Exception as e:
            # Log error but don't fail the request
            print(f"Warning: Failed to scrape docs: {e}")

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
        theme=feature.theme,
        domain=feature.domain,
        created_at=feature.created_at.isoformat()
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
                theme=f.theme,
                domain=f.domain,
                created_at=f.created_at.isoformat()
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
            theme=feature.theme,
            domain=feature.domain,
            created_at=feature.created_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve feature: {e}")


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
        # Use unified generator for ALL_DOMAINS or multi-domain scenarios
        if request.domain == Domain.ALL_DOMAINS or len(set(f.domain for f in features)) > 1:
            presentation = unified_presentation_generator.generate_unified_presentation(
                features=features,
                quarter=request.quarter,
                audience=request.audience,
                story_theme="platform_transformation"
            )
        else:
            presentation = presentation_generator.generate_complete_presentation(
                features=features,
                domain=request.domain,
                quarter=request.quarter,
                audience=request.audience
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
                "audience": request.audience,
                "framework": "7-slide Elastic presentation framework"
            }
        }
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


# Development server runner
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)