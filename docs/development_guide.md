# Development Guide - TDD & Claude Code Best Practices

## Test-Driven Development Approach

### TDD Cycle for This Project
1. **Red** - Write failing test for new feature
2. **Green** - Write minimal code to pass test
3. **Refactor** - Improve code while keeping tests green
4. **Document** - Update documentation and examples
5. **Observe** - Verify OpenTelemetry instrumentation is working

### Testing Strategy

#### Unit Tests
```python
# Example test structure
def test_feature_classifier():
    """Test feature classification into themes"""
    feature = Feature(
        name="Better Binary Quantization",
        description="95% memory reduction with improved ranking",
        benefits=["cost savings", "performance improvement"],
        domain="search"
    )
    classifier = FeatureClassifier()
    theme = classifier.classify(feature)
    assert theme == Theme.OPTIMIZE

def test_multi_domain_classifier():
    """Test classification for multi-domain features"""
    features = [
        Feature(name="BBQ", domain="search", benefits=["performance"]),
        Feature(name="APM", domain="observability", benefits=["monitoring"]),
        Feature(name="SIEM", domain="security", benefits=["detection"])
    ]
    classifier = MultiDomainClassifier()
    organized = classifier.organize_cross_domain(features)
    
    assert Theme.OPTIMIZE in organized
    assert len(organized[Theme.OPTIMIZE]) >= 2  # Features from multiple domains

def test_content_generator():
    """Test slide content generation"""
    feature = Feature(name="BBQ", theme=Theme.OPTIMIZE, domain="search")
    generator = ContentGenerator()
    content = generator.generate_slide_content(feature)
    assert "Do it faster" in content
    assert "memory reduction" in content
```

#### Integration Tests
```python
def test_elasticsearch_storage():
    """Test feature storage and retrieval"""
    es_client = get_test_elasticsearch_client()
    storage = FeatureStorage(es_client)
    
    feature = create_test_feature()
    storage.store(feature)
    
    retrieved = storage.get_by_id(feature.id)
    assert retrieved.name == feature.name

def test_observability_instrumentation():
    """Test OpenTelemetry instrumentation is working"""
    with patch('opentelemetry.trace.get_tracer') as mock_tracer:
        mock_span = Mock()
        mock_tracer.return_value.start_span.return_value = mock_span
        
        # Test that spans are created for key operations
        classifier = FeatureClassifier()
        classifier.classify(create_test_feature())
        
        mock_tracer.return_value.start_span.assert_called()
        mock_span.set_attribute.assert_called()

def test_web_scraping():
    """Test documentation scraping"""
    scraper = WebScraper()
    with mock_web_response():
        content = scraper.scrape_feature_docs("https://elastic.co/docs/bbq")
        assert content.title
        assert content.description
```

#### Observability Tests
```python
def test_metrics_collection():
    """Test that custom metrics are being collected"""
    from unittest.mock import patch
    
    with patch('prometheus_client.Counter.inc') as mock_counter:
        feature_processor = FeatureProcessor()
        feature_processor.process(create_test_feature())
        
        # Verify metrics were incremented
        mock_counter.assert_called()

def test_structured_logging():
    """Test structured logging with correlation IDs"""
    import structlog
    
    logger = structlog.get_logger()
    with patch.object(logger, 'info') as mock_log:
        # Simulate request with correlation ID
        with correlation_context("test-correlation-id"):
            process_feature(create_test_feature())
            
        # Verify log includes correlation ID
        mock_log.assert_called()
        call_args = mock_log.call_args[1]
        assert 'correlation_id' in call_args

def test_cross_domain_content_generation():
    """Test content generation for all domains"""
    features = [
        Feature(name="BBQ", domain="search"),
        Feature(name="APM Enhancement", domain="observability"),
        Feature(name="ML Security", domain="security")
    ]
    
    generator = MultiDomainContentGenerator()
    presentation = generator.generate_unified_presentation(features)
    
    # Verify cross-domain organization
    assert "Platform Innovation Across All Domains" in presentation.title
    assert len(presentation.themes) == 3  # All three themes represented
    
    # Verify each domain is represented
    domains_mentioned = [f.domain for f in presentation.featured_items]
    assert "search" in domains_mentioned
    assert "observability" in domains_mentioned  
    assert "security" in domains_mentioned
```

#### Content Quality Tests
```python
def test_generated_presentation_quality():
    """Test presentation output meets quality standards"""
    features = [create_test_feature()]
    generator = PresentationGenerator()
    
    slides = generator.generate(features, domain="search")
    
    # Validate structure
    assert len(slides) == 9  # Expected slide count
    assert slides[0].title == "Three Game-Changing Innovations"
    
    # Validate content quality
    for slide in slides:
        assert slide.content  # Not empty
        assert slide.business_value  # Contains value proposition

def test_multi_domain_presentation_quality():
    """Test multi-domain presentation quality"""
    features = create_multi_domain_features()
    generator = PresentationGenerator()
    
    slides = generator.generate(features, domain="all_domains")
    
    # Verify unified messaging
    assert "Platform Innovation Across All Domains" in slides[1].title
    assert any("platform synergies" in slide.content.lower() for slide in slides)
    
def test_lab_instruction_completeness():
    """Test lab instructions are complete and actionable"""
    feature = create_test_feature()
    lab_generator = LabGenerator()
    
    lab = lab_generator.generate(feature)
    
    assert lab.setup_instructions
    assert lab.step_by_step_guide
    assert lab.sample_data
    assert lab.validation_steps

def test_cross_domain_lab_generation():
    """Test cross-domain lab scenario generation"""
    features = [
        Feature(name="Search Feature", domain="search"),
        Feature(name="Security Feature", domain="security")
    ]
    
    lab_generator = CrossDomainLabGenerator()
    lab = lab_generator.generate_unified_lab(features)
    
    assert "threat hunting with search" in lab.title.lower()
    assert lab.cross_domain_integration_steps
    assert len(lab.sample_datasets) >= 2  # Multiple domain datasets
```

## Code Organization Patterns

### Project Structure
```
elastic-whats-new-generator/
├── src/
│   ├── core/                 # Business logic
│   │   ├── models.py        # Data models
│   │   ├── classifier.py    # Feature classification
│   │   └── generators/      # Content generators
│   ├── integrations/        # External service integrations
│   │   ├── elasticsearch.py
│   │   ├── web_scraper.py
│   │   └── ai_tools.py
│   ├── templates/           # Content templates
│   │   ├── presentations/
│   │   └── labs/
│   └── config/              # Configuration management
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── docs/
├── agents/
└── config/
```

### Data Models
```python
from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional

class Theme(Enum):
    SIMPLIFY = "simplify"
    OPTIMIZE = "optimize"
    AI_INNOVATION = "ai_innovation"

class Feature(BaseModel):
    """Core feature model"""
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Feature name")
    description: str = Field(..., description="Brief description")
    benefits: List[str] = Field(default_factory=list)
    documentation_links: List[str] = Field(default_factory=list)
    theme: Optional[Theme] = None
    domain: str = Field(..., description="search|observability|security")
    
class SlideContent(BaseModel):
    """Generated slide content"""
    title: str
    subtitle: Optional[str] = None
    content: str
    business_value: str
    theme: Theme
    
class LabInstruction(BaseModel):
    """Lab instruction content"""
    title: str
    objective: str
    setup_instructions: str
    steps: List[str]
    validation: str
    sample_data: Optional[dict] = None
```

## Claude Code Best Practices

### Efficient Context Management

#### 1. Reference Files Instead of Re-explaining
```markdown
# Good
"Please implement the FeatureClassifier class based on the models defined in src/core/models.py"

# Avoid
"I need a classifier that takes a feature with name, description, and benefits and classifies it into themes..."
```

#### 2. Use Specific Agents for Focused Tasks
```markdown
# Use Content Generator Agent for:
- Slide content creation
- Lab instruction writing
- Storytelling and messaging

# Use Data Processor Agent for:
- Web scraping implementation
- Elasticsearch operations
- Data transformation logic
```

#### 3. Incremental Development
```markdown
# Session 1: Core models and basic classification
# Session 2: Elasticsearch integration
# Session 3: Content generation
# Session 4: Web scraping and AI tools
# Session 5: Quality assurance and testing
```

### Code Quality Guidelines

#### OpenTelemetry Integration Patterns
```python
from opentelemetry import trace, metrics
from opentelemetry.trace import Status, StatusCode
import structlog
from typing import Dict, Any

# Get tracer and meter
tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

# Custom metrics
features_processed = meter.create_counter(
    "features_processed_total",
    description="Total number of features processed",
)

content_generation_duration = meter.create_histogram(
    "content_generation_duration_seconds",
    description="Time taken to generate content",
)

class InstrumentedFeatureClassifier:
    """Feature classifier with OpenTelemetry instrumentation"""
    
    @tracer.start_as_current_span("feature_classification")
    def classify(self, feature: Feature) -> Theme:
        span = trace.get_current_span()
        
        # Add span attributes
        span.set_attribute("feature.id", feature.id)
        span.set_attribute("feature.domain", feature.domain.value)
        span.set_attribute("feature.name", feature.name)
        
        try:
            # Perform classification
            theme = self._classify_internal(feature)
            
            # Record success metrics
            features_processed.add(1, {
                "domain": feature.domain.value,
                "theme": theme.value,
                "status": "success"
            })
            
            span.set_attribute("classification.theme", theme.value)
            span.set_status(Status(StatusCode.OK))
            
            return theme
            
        except Exception as e:
            # Record error metrics
            features_processed.add(1, {
                "domain": feature.domain.value,
                "status": "error"
            })
            
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.record_exception(e)
            raise

class InstrumentedContentGenerator:
    """Content generator with observability"""
    
    @tracer.start_as_current_span("content_generation")
    def generate_slide_content(self, feature: Feature) -> SlideContent:
        span = trace.get_current_span()
        logger = structlog.get_logger()
        
        start_time = time.time()
        
        span.set_attribute("content.type", "slide")
        span.set_attribute("feature.domain", feature.domain.value)
        span.set_attribute("feature.theme", feature.theme.value if feature.theme else "unclassified")
        
        try:
            logger.info("Starting content generation", 
                       feature_id=feature.id, 
                       content_type="slide")
            
            content = self._generate_content_internal(feature)
            
            duration = time.time() - start_time
            content_generation_duration.record(duration, {
                "content_type": "slide",
                "domain": feature.domain.value,
                "ai_tool": "claude"
            })
            
            span.set_attribute("content.length", len(content.content))
            span.set_status(Status(StatusCode.OK))
            
            logger.info("Content generation completed",
                       feature_id=feature.id,
                       duration=duration,
                       content_length=len(content.content))
            
            return content
            
        except Exception as e:
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.record_exception(e)
            
            logger.error("Content generation failed",
                        feature_id=feature.id,
                        error=str(e))
            raise

# Correlation ID context
import contextvars
correlation_id_var = contextvars.ContextVar('correlation_id')

def set_correlation_id(correlation_id: str):
    correlation_id_var.set(correlation_id)

def get_correlation_id() -> str:
    return correlation_id_var.get("")

# Structured logging configuration
def configure_logging():
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            add_correlation_id,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

def add_correlation_id(logger, method_name, event_dict):
    """Add correlation ID to all log messages"""
    correlation_id = get_correlation_id()
    if correlation_id:
        event_dict["correlation_id"] = correlation_id
    return event_dict
```

#### Error Handling Patterns
```python
class ElasticWhatNewError(Exception):
    """Base exception for the application"""
    pass

class FeatureClassificationError(ElasticWhatNewError):
    """Raised when feature cannot be classified"""
    pass

class ContentGenerationError(ElasticWhatNewError):
    """Raised when content generation fails"""
    pass
```

#### Configuration Management
```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    elasticsearch_url: str = "http://localhost:9200"
    elasticsearch_index: str = "elastic-features"
    claude_api_key: str
    elastic_mcp_endpoint: str
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## Development Workflow

### Starting a New Feature
1. **Write test cases** defining expected behavior
2. **Create minimal implementation** to pass tests
3. **Use appropriate agent** for focused development
4. **Iterate with TDD cycle**
5. **Document decisions** in project files

### Claude Code Session Structure
1. **Context setting** - Reference relevant docs/files
2. **Specific task focus** - Single responsibility
3. **Test-first approach** - Write tests before implementation
4. **Incremental progress** - Small, testable changes
5. **Documentation updates** - Keep docs current

### Quality Gates
- All tests passing
- Type checking with mypy
- Code formatting with black
- Linting with flake8
- Security scanning with bandit
- Documentation updates