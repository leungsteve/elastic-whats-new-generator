"""
Main FastAPI application for the Elastic What's New Generator.

This module provides REST API endpoints for feature management,
content generation, and presentation creation.
"""

from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import uvicorn

from src.core.models import Feature, Domain, Theme, SlideContent, LabInstruction
from src.core.classifier import FeatureClassifier
from src.core.generators.content_generator import ContentGenerator
from src.integrations.elasticsearch import FeatureStorage
from src.integrations.web_scraper import WebScraper
from elasticsearch import Elasticsearch

# Initialize FastAPI app
app = FastAPI(
    title="Elastic What's New Generator",
    description="Automated presentation and lab generation for Elastic features",
    version="1.0.0"
)

# Global instances (in production, use dependency injection)
classifier = FeatureClassifier()
content_generator = ContentGenerator()
web_scraper = WebScraper()

# Dependency for Elasticsearch (in production, configure with settings)
def get_es_client():
    """Get Elasticsearch client (mock for development)."""
    # In production, return actual ES client: Elasticsearch(["localhost:9200"])
    return None

def get_feature_storage(es_client = Depends(get_es_client)):
    """Get FeatureStorage instance."""
    if es_client:
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

class PresentationResponse(BaseModel):
    slides: List[Dict[str, Any]]
    domain: str
    generated_at: str


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "elastic-whats-new-generator"}


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


# Development server runner
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)