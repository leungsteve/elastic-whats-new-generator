# Elastic What's New Generator

Automated presentation and Instruqt lab generation for quarterly Elastic feature releases across Search, Observability, Security, and unified platform domains.

## 🎯 Purpose

Transform quarterly Elastic feature releases into compelling presentations and hands-on labs that drive sales pipeline generation. Generate domain-specific or unified platform content that demonstrates clear business value and competitive advantages.

## 🏗️ Architecture

### Two-Stage LLM Architecture

```
Stage 1: Content Extraction & Caching
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│ Scrape  │ -> │   LLM   │ -> │  Cache  │ -> │  Ready  │
│  Docs   │    │Extract  │    │   in    │    │   for   │
│         │    │Metadata │    │   ES    │    │  Reuse  │
└─────────┘    └─────────┘    └─────────┘    └─────────┘

Stage 2: Content Generation (Presentations & Labs)
┌─────────┐    ┌─────────┐    ┌─────────────────────────┐
│  Load   │ -> │   LLM   │ -> │  7-Slide Presentation   │
│ Cached  │    │Generate │    │  w/ Talk Tracks         │
│ Content │    │         │    │                         │
│         │    │         │    │  OR                     │
│         │    │         │    │                         │
│         │    │         │    │  Story-Driven Lab       │
│         │    │         │    │  w/ Datasets & Challenges│
└─────────┘    └─────────┘    └─────────────────────────┘
```

**Benefits:**
- ✅ Extract once, generate many presentations and labs
- ✅ 90%+ reduction in LLM API calls through caching
- ✅ Fast content generation (seconds vs. minutes)
- ✅ Consistent quality across all outputs
- ✅ Story-driven labs with realistic scenarios and datasets
- ✅ Progressive challenges with complete solutions

### Multi-Provider LLM Support
- **OpenAI** (gpt-4o, gpt-4o-mini) - Default, cost-effective
- **Google Gemini** (gemini-1.5-flash) - Fast alternative
- **Anthropic Claude** (claude-3-sonnet) - High-quality fallback
- **Proxy Support** - Custom API gateways and Claude Code Max
- **Auto-Fallback** - Automatic provider selection based on availability

### Multi-Domain Support
- **Individual Domains**: Search, Observability, Security
- **Unified Platform**: Cross-domain storytelling and value propositions
- **Customizable Prompts**: Configure LLM behavior via YAML

## 🚀 Features

### Core Capabilities
- **AI-Powered Feature Classification** into three universal themes:
  - **Simplify**: "Do more with less"
  - **Optimize**: "Do it faster"
  - **AI Innovation**: "Do it with AI"

- **Advanced Storytelling Framework** 🎭:
  - **Story Arc Planning**: Multi-position narrative structure (Hook, Build, Climax, Resolution)
  - **Talk Track Generation**: Comprehensive speaker notes with timing and transitions
  - **Customer Story Integration**: Real-world success stories with quantified business impact
  - **Business Value Calculation**: ROI projections and value drivers
  - **Competitive Positioning**: Differentiation analysis and market positioning

- **Enhanced User Interface**:
  - **Test Feature Filtering**: Automatic hiding of test features from production UI
  - **Advanced Storytelling Controls**: Narrative style, talk track detail, technical depth
  - **Enhanced Previews**: Story arc overview, talk track previews, customer story summaries
  - **Cross-Tab Functionality**: Consistent filtering across Features, Presentations, and Labs tabs
  - **Analytics Dashboard**: Real-time LLM usage tracking, cost monitoring, and content history browser

- **Story-Driven Lab Generation** 🧪:
  - **Realistic Business Scenarios**: Compelling narratives (e.g., "Black Friday retail analysis")
  - **Multi-Table Datasets**: Related tables with foreign key relationships (customers, orders, products)
  - **Copy-Paste Ready Commands**: Kibana Dev Tools commands that work immediately
  - **Progressive Challenges**: 5-7 exercises building from simple to complex
  - **Complete Solutions**: Full ES|QL commands with explanations and expected outputs
  - **Configurable Parameters**: Scenario type (e-commerce/observability/security), data size (demo/realistic/large), technical depth

- **Multi-Domain Content Generation**:
  - Domain-specific presentations (Search/Observability/Security)
  - Unified platform presentations showing cross-domain synergies
  - Instruqt-compatible lab instructions with narrative flow
  - Customer journey-based lab scenarios

- **Flexible LLM Integration**:
  - Primary: Claude for high-quality content generation
  - Fallback: OpenAI GPT-4 for reliability
  - Extensible architecture for additional providers

### Output Formats
- **Presentations**: Markdown slides with advanced storytelling and comprehensive talk tracks
- **Lab Instructions**: Story-driven Instruqt workshops with:
  - Multi-table dataset schemas with relationships
  - Copy-paste ready setup commands (create indices, bulk load data)
  - Progressive challenges (5-7 exercises)
  - Complete solutions with ES|QL commands and expected outputs
- **Customer Stories**: Real-world success stories with business impact metrics
- **Speaker Notes**: Detailed talk tracks with timing and transition guidance
- **Sample Data**: Realistic datasets (50-5000 records) for hands-on exercises

## 🎯 Advanced Storytelling APIs

### **NEW: Dedicated Storytelling Endpoints**
The system now includes specialized API endpoints for advanced storytelling features:

- **`POST /features/{feature_id}/customer-stories`**
  - Generate customer success stories with quantified business impact
  - Configurable research depth (basic/standard/comprehensive)
  - Industry-focused story generation
  - Real-world metrics and ROI data

- **`POST /features/business-value`**
  - Calculate ROI projections for multiple features
  - Organization size and industry customization
  - Value driver analysis and payback period calculation
  - Annual savings projections with detailed breakdowns

- **`POST /features/{feature_id}/competitive-analysis`**
  - Automated competitive positioning research
  - Market differentiation analysis
  - Competitor comparison matrices
  - Positioning strategy recommendations

- **`POST /presentations/complete-storytelling`** 🌟
  - **End-to-end storytelling presentation generation**
  - Full story arc planning with narrative flow
  - Integrated customer stories and business value
  - Enhanced slides with comprehensive talk tracks
  - Analytics and presentation insights

### **Enhanced Presentation Features**
- **Story Arc Integration**: Multi-position narrative structures (Hook, Build, Climax, Resolution)
- **Talk Track Generation**: Comprehensive speaker notes with timing and transitions
- **Business Impact Integration**: ROI projections and value drivers embedded in presentations
- **Competitive Positioning**: Market analysis and differentiation messaging
- **Customer Story Research**: Real-world success stories with quantified outcomes

## 📊 LLM Usage Tracking & Content Storage

**NEW**: Complete observability for LLM operations and generated content!

### Automatic LLM Usage Tracking
Every LLM API call is automatically logged to Elasticsearch with:
- **Provider & Model**: OpenAI, Gemini, or Claude with specific model version
- **Full Prompts & Responses**: Complete system and user prompts with generated text
- **Token Usage**: Prompt tokens, completion tokens, and total token counts
- **Cost Estimation**: Real-time cost tracking with per-call USD estimates
  - OpenAI gpt-4o: $0.0025/$0.01 per 1K tokens (prompt/completion)
  - OpenAI gpt-4o-mini: $0.00015/$0.0006 per 1K tokens
  - Gemini 1.5 Flash: $0.000075/$0.0003 per 1K tokens
  - Claude 3 Sonnet: $0.003/$0.015 per 1K tokens
- **Performance Metrics**: Response times and success/failure status
- **Context**: Operation type, feature IDs, and domain associations

### Generated Content Storage
All presentations and labs are automatically saved with:
- **Full Markdown Content**: Complete presentation/lab markdown
- **Structured Data**: Slides, challenges, datasets in JSON format
- **Generation Parameters**: Audience, narrative style, technical depth
- **Feature Associations**: Linked feature IDs and names
- **Searchable Tags**: Domain, content type, and custom tags
- **Version Control**: Track content iterations over time

### Analytics Dashboard
Access comprehensive analytics via the web UI's **Analytics** tab:

**Summary Metrics**:
- Total LLM calls and costs
- Average response times
- Success rates

**Visual Breakdowns**:
- Usage by provider (OpenAI vs. Gemini vs. Claude)
- Usage by operation (extract, generate_presentation, generate_lab)

**Content History Browser**:
- Browse all generated presentations and labs
- Filter by type (presentation/lab) and domain
- One-click markdown download
- View generation parameters and metadata

**Activity Log**:
- Real-time LLM call history
- Status indicators (success/error)
- Token usage and cost per call

### REST API Endpoints
Query tracking data programmatically:

```bash
# Get usage analytics
GET /api/llm-usage/analytics
GET /api/llm-usage/logs?operation_type=generate_presentation&size=50

# Query generated content
GET /api/generated-content?content_type=presentation&domain=search
GET /api/generated-content/{content_id}
GET /api/generated-content/{content_id}/markdown

# Get specific LLM log
GET /api/llm-usage/{log_id}
```

### Elasticsearch Indices
- **`llm-usage-logs`**: Complete LLM call history with prompts, responses, and metrics
- **`generated-content`**: All presentations and labs with full metadata

### Benefits
- ✅ **Cost Transparency**: Track spend across all LLM providers
- ✅ **Historical Access**: Never lose generated content
- ✅ **Performance Monitoring**: Identify slow operations
- ✅ **Audit Trail**: Complete record of all LLM usage
- ✅ **Self-Service**: Users can browse and download any previously generated content
- ✅ **Data-Driven Optimization**: Analyze usage patterns to optimize prompts and reduce costs

## 🎨 Customizable LLM Prompts

**NEW**: Customize how presentations and labs are generated!

Edit `config/llm_prompts.yaml` to control:
- Presentation structure and tone
- Talk track detail level
- Technical vs. business focus
- Slide count and narrative style
- Lab difficulty and format

**Example customizations:**
```yaml
presentation_generator:
  system_prompt: |
    Create executive-level presentations
    Focus on ROI and business outcomes
    Minimize technical jargon
```

Changes require server restart. See `config/README.md` for full guide.

**Documentation:**
- [LLM Architecture](docs/architecture/llm-architecture.md) - Complete LLM integration guide
- [Prompt Customization](config/README.md) - How to customize prompts
- [Content Research](docs/architecture/content-research.md) - Two-stage architecture details

## 📋 Requirements

### System Requirements
- Python 3.11+
- Elasticsearch 8.x
- API keys for Claude and/or OpenAI

### External Dependencies
- **Elasticsearch**: Feature and content storage
- **Claude API**: Primary content generation
- **OpenAI API**: Fallback content generation
- **Elastic MCP**: Documentation validation (optional)

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-username/elastic-whats-new-generator.git
cd elastic-whats-new-generator
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your API keys and settings
```

4. **Set up Elasticsearch**
```bash
# Start local Elasticsearch or configure cloud instance
# Update ELASTICSEARCH_URL in .env

# The system will automatically create these indices on first use:
# - elastic-features (feature storage)
# - llm-usage-logs (LLM tracking)
# - generated-content (presentation/lab storage)
```

**Note**: LLM usage tracking and content storage are enabled automatically when Elasticsearch is configured. All LLM calls and generated content will be logged for analytics and historical access.

## 🎮 Usage

### Quick Start
```python
from src.core.generator import PresentationGenerator
from src.core.models import Feature, Domain

# Create a feature
feature = Feature(
    name="Better Binary Quantization",
    description="95% memory reduction with improved ranking quality",
    benefits=["Reduces memory usage by 95%", "Improves ranking quality"],
    domain=Domain.SEARCH
)

# Generate presentation
generator = PresentationGenerator()
presentation = await generator.generate([feature], domain="search")
```

### API Usage
```bash
# Start the FastAPI server
uvicorn src.main:app --reload

# Generate presentation via API
curl -X POST "http://localhost:8000/generate/presentation" \
  -H "Content-Type: application/json" \
  -d '{"features": [...], "domain": "search"}'
```

## 📁 Project Structure

```
elastic-whats-new-generator/
├── src/
│   ├── core/                 # Business logic
│   │   ├── models.py        # Enhanced data models with storytelling
│   │   ├── classifier.py    # Feature classification
│   │   ├── storytelling.py  # Advanced narrative framework (NEW)
│   │   └── generators/      # Content generators
│   ├── integrations/        # External services
│   │   ├── elasticsearch.py # Data storage
│   │   ├── llm_providers.py # LLM abstraction
│   │   ├── web_scraper.py   # Documentation scraping
│   │   └── customer_story_research.py # Customer stories & business impact (NEW)
│   ├── api/                 # FastAPI REST interface
│   └── templates/           # Content templates
├── web/                     # Enhanced UI with storytelling controls (NEW)
│   ├── index.html          # Main interface with advanced storytelling features
│   └── app.js              # Frontend with comprehensive story integration
├── tests/                   # Test suite
├── config/                  # Configuration files
├── agents/                  # Specialized agent docs
└── docs/                    # Documentation
```

## 🧪 Development

### Test-Driven Development
```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test category
pytest tests/unit/
pytest tests/integration/
```

### Code Quality
```bash
# Format code
black src/

# Type checking
mypy src/

# Linting
flake8 src/

# Security scan
bandit -r src/
```

## 🎯 Framework Methodology

### Three Universal Themes
Every feature is classified into one of three innovation themes:
- **Simplify**: Reduce complexity, automate operations, consolidate tools
- **Optimize**: Improve performance, reduce costs, enhance efficiency
- **AI Innovation**: Enable AI capabilities, intelligent automation

### Presentation Structure
1. **Hook**: Domain-specific infrastructure challenge
2. **Innovation Overview**: "Three Game-Changing Innovations"
3. **Theme Deep Dives**: Simplify → Optimize → AI Innovation
4. **Cross-Platform Benefits**: Platform synergies and integration
5. **Competitive Differentiation**: Platform vs. point solutions
6. **Business Case**: Quantified ROI and value propositions
7. **Call to Action**: Next steps and engagement

### Multi-Domain Approach
- **Single Domain**: Focused presentations for Search, Observability, or Security teams
- **All Domains**: Unified platform story showing cross-domain value and synergies
- **Cross-Domain Labs**: Scenarios that demonstrate platform integration (e.g., Search + Security threat hunting)

### Advanced Storytelling Framework 🎭

#### Story Arc Structure
1. **Opening Hook**: Capture attention with relatable challenges
2. **Problem Build**: Escalate urgency and pain points
3. **Solution Introduction**: Present Elastic's innovative approach
4. **Climax**: Demonstrate transformative impact
5. **Resolution**: Quantified outcomes and business value
6. **Call to Action**: Clear next steps for engagement

#### Narrative Styles
- **Customer Journey**: Follow a customer's transformation story
- **Problem → Solution**: Traditional challenge-resolution narrative
- **Innovation Showcase**: Highlight cutting-edge capabilities

#### Talk Track Generation
- **Comprehensive**: Detailed speaker notes with timing (15-20 min presentations)
- **Standard**: Essential talking points and transitions (10-15 min presentations)
- **Basic**: Key messages and bullet points (5-10 min presentations)

#### Customer Story Integration
- **Real-World Scenarios**: Industry-specific use cases
- **Quantified Impact**: ROI, efficiency gains, cost savings
- **Business Value**: Competitive advantages and market positioning

## 🔧 Configuration

### LLM Providers
Configure multiple LLM providers for flexibility and reliability:

```yaml
# config/ai_tools.yaml
ai_tools:
  claude:
    model: "claude-3-5-sonnet-20241022"
    priority: 1
  openai:
    model: "gpt-4-turbo"
    priority: 2
    fallback_for: ["claude"]
```

### Domain Templates
Customize content templates for each domain:

```yaml
# config/templates.yaml
domains:
  search:
    personas: [developer, architect, product_manager]
    challenges: [relevance, performance, cost]
  observability:
    personas: [sre, devops_engineer, platform_engineer]
    challenges: [mttr, monitoring_cost, alert_fatigue]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Implement your feature following TDD principles
5. Ensure all tests pass and code quality checks succeed
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📊 Success Metrics

### Automation Goals
- **Reduce presentation creation time** from days to hours
- **Ensure consistency** across domains and quarters
- **Improve content quality** through AI assistance
- **Enable rapid feature-to-market** communication

### Business Impact
- **Increased sales pipeline** generation
- **Faster prospect education** and engagement
- **Consistent value messaging** across teams
- **Reduced manual content creation** overhead

## 🗺️ Roadmap

### Completed Features ✅
- [x] Project architecture and planning
- [x] Core data models and LLM integration
- [x] Feature classification and content generation
- [x] Multi-domain presentation support
- [x] FastAPI REST interface
- [x] Advanced storytelling framework with narrative arcs
- [x] Customer story research and business impact integration
- [x] Enhanced UI with test feature filtering
- [x] Comprehensive talk track generation
- [x] Story arc planning and narrative flow
- [x] Cross-tab functionality and improved UX

### Current Phase (Advanced Integration) ✅ COMPLETED
- [x] Backend API integration with storytelling parameters
- [x] End-to-end presentation generation with full story arcs
- [x] Customer story API endpoints and data integration
- [x] Business value calculation endpoints
- [x] Competitive positioning research automation

### Future Enhancements
- [ ] OpenTelemetry observability and monitoring
- [ ] Advanced quality validation pipelines
- [ ] Feedback loops and content optimization
- [ ] Multi-modal content generation (images, diagrams)
- [ ] Content governance and version control
- [ ] AI-powered content quality scoring
- [ ] Automated A/B testing for presentation effectiveness

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: See [docs/](docs/) directory
- **Issues**: Report bugs and feature requests on GitHub Issues
- **Development Guide**: See [docs/development_guide.md](docs/development_guide.md)

---

**Built with ❤️ for the Elastic community**