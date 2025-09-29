# Elastic What's New Generator

**Amplify Elastic's Innovation Story** - Automated presentation and Instruqt lab generation for quarterly Elastic feature releases across Search, Observability, Security, and the unified Elastic platform.

## 🎯 Purpose

**Drive Elastic Sales and Adoption** - Transform quarterly Elastic feature releases into compelling, sales-ready presentations and hands-on labs that showcase Elastic's competitive advantages and drive pipeline generation. Generate domain-specific content highlighting Elastic Search, Elastic Observability, Elastic Security, or unified Elastic platform capabilities that demonstrate clear business value and technical differentiation.

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

**Benefits for Elastic Enablement:**
- ✅ **Showcase Elastic Innovation**: Extract once, generate unlimited Elastic-focused presentations and labs
- ✅ **Efficient Content Creation**: 90%+ reduction in effort through intelligent caching of Elastic documentation
- ✅ **Rapid Elastic Enablement**: Generate sales-ready Elastic content in seconds vs. minutes
- ✅ **Consistent Elastic Messaging**: Ensure quality and accuracy across all Elastic platform outputs
- ✅ **Real-World Elastic Use Cases**: Story-driven labs demonstrating Elastic's business value
- ✅ **Hands-On Elastic Training**: Progressive challenges showcasing Elastic capabilities

### Multi-Provider LLM Support
- **OpenAI** (gpt-4o, gpt-4o-mini) - Default, cost-effective
- **Google Gemini** (gemini-1.5-flash) - Fast alternative
- **Anthropic Claude** (claude-3-sonnet) - High-quality fallback
- **Proxy Support** - Custom API gateways and Claude Code Max
- **Auto-Fallback** - Automatic provider selection based on availability

### Elastic Multi-Domain Support
- **Elastic Search**: Showcase Elastic's search and AI capabilities
- **Elastic Observability**: Highlight Elastic's monitoring and APM solutions
- **Elastic Security**: Demonstrate Elastic's SIEM and threat detection
- **Unified Elastic Platform**: Cross-domain storytelling showing Elastic's complete value proposition
- **Customizable Messaging**: Configure content generation for different Elastic audiences

## 🚀 Features

### Core Capabilities
- **AI-Powered Elastic Feature Classification** into three compelling value themes:
  - **Simplify**: Position Elastic as the solution to "Do more with less"
  - **Optimize**: Showcase how Elastic helps customers "Do it faster"
  - **AI Innovation**: Highlight Elastic's AI capabilities - "Do it with AI"

- **Advanced Storytelling Framework for Elastic** 🎭:
  - **Story Arc Planning**: Craft compelling narratives that position Elastic as the hero
  - **Talk Track Generation**: Sales-ready speaker notes that emphasize Elastic's unique value
  - **Customer Story Integration**: Real-world Elastic success stories with quantified ROI
  - **Business Value Calculation**: ROI projections demonstrating Elastic's financial impact
  - **Competitive Positioning**: Clear differentiation showing why prospects should choose Elastic

- **Enhanced User Interface**:
  - **Test Feature Filtering**: Automatic hiding of test features from production UI
  - **Advanced Storytelling Controls**: Narrative style, talk track detail, technical depth
  - **Enhanced Previews**: Story arc overview, talk track previews, customer story summaries
  - **Cross-Tab Functionality**: Consistent filtering across Features, Presentations, and Labs tabs
  - **Analytics Dashboard**: Real-time LLM usage tracking, cost monitoring, and content history browser

- **Hands-On Elastic Lab Generation** 🧪:
  - **Real-World Elastic Use Cases**: Demonstrate Elastic's value through compelling business scenarios
  - **Elastic-Powered Datasets**: Multi-table datasets showcasing Elastic's data relationships and indexing
  - **Copy-Paste Ready Elastic Commands**: Kibana Dev Tools commands demonstrating Elastic Query Language (ES|QL)
  - **Progressive Elastic Challenges**: 5-7 exercises showcasing Elastic capabilities from basics to advanced
  - **Complete Elastic Solutions**: Full ES|QL demonstrations with Elastic best practices
  - **Flexible Elastic Scenarios**: E-commerce, observability, or security use cases highlighting Elastic's versatility

- **Elastic Multi-Domain Content Generation**:
  - **Elastic Search Presentations**: Showcase search, vector search, and AI-powered relevance
  - **Elastic Observability Presentations**: Highlight logs, metrics, APM, and unified observability
  - **Elastic Security Presentations**: Demonstrate SIEM, threat detection, and endpoint protection
  - **Unified Elastic Platform**: Cross-domain storytelling showing the power of Elastic's integrated platform
  - **Instruqt-Compatible Labs**: Hands-on Elastic training with narrative-driven learning experiences

- **Flexible LLM Integration**:
  - Primary: Claude for high-quality content generation
  - Fallback: OpenAI GPT-4 for reliability
  - Extensible architecture for additional providers

### Elastic-Focused Output Formats
- **Elastic Sales Presentations**: Markdown slides positioning Elastic with:
  - Advanced storytelling that makes Elastic the hero
  - Comprehensive talk tracks emphasizing Elastic's competitive advantages
  - Business value calculations showing Elastic's ROI

- **Elastic Hands-On Labs**: Story-driven Instruqt workshops featuring:
  - Real-world Elastic implementations and use cases
  - Copy-paste ready Elastic commands (create indices, bulk load data)
  - Progressive Elastic challenges (5-7 exercises)
  - Complete ES|QL solutions demonstrating Elastic's query power

- **Elastic Customer Success Stories**: Real-world examples with:
  - Quantified business impact from Elastic deployments
  - ROI metrics and competitive win reasons

- **Elastic Speaker Notes**: Sales-ready talk tracks with:
  - Timing guidance for Elastic demos
  - Transition scripts emphasizing Elastic differentiation
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