# Elastic What's New Generator

Automated presentation and Instruqt lab generation for quarterly Elastic feature releases across Search, Observability, Security, and unified platform domains.

## 🎯 Purpose

Transform quarterly Elastic feature releases into compelling presentations and hands-on labs that drive sales pipeline generation. Generate domain-specific or unified platform content that demonstrates clear business value and competitive advantages.

## 🏗️ Architecture

```
Feature Input → LLM Classification → Content Generation → Output
     ↓              ↓                    ↓              ↓
Domain Routing → Theme Organization → Template Rendering → Presentations & Labs
```

### Multi-Domain Support
- **Individual Domains**: Search, Observability, Security
- **Unified Platform**: Cross-domain storytelling and value propositions
- **Flexible LLM Integration**: Claude, OpenAI, with smart fallback

## 🚀 Features

### Core Capabilities
- **AI-Powered Feature Classification** into three universal themes:
  - **Simplify**: "Do more with less"
  - **Optimize**: "Do it faster"
  - **AI Innovation**: "Do it with AI"

- **Multi-Domain Content Generation**:
  - Domain-specific presentations (Search/Observability/Security)
  - Unified platform presentations showing cross-domain synergies
  - Instruqt-compatible lab instructions with sample data

- **Flexible LLM Integration**:
  - Primary: Claude for high-quality content generation
  - Fallback: OpenAI GPT-4 for reliability
  - Extensible architecture for additional providers

### Output Formats
- **Presentations**: Markdown slides following proven framework
- **Lab Instructions**: Step-by-step Instruqt workshops
- **Sample Data**: Realistic datasets for hands-on exercises

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
```

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
│   │   ├── models.py        # Data models
│   │   ├── classifier.py    # Feature classification
│   │   └── generators/      # Content generators
│   ├── integrations/        # External services
│   │   ├── elasticsearch.py # Data storage
│   │   ├── llm_providers.py # LLM abstraction
│   │   └── web_scraper.py   # Documentation scraping
│   └── templates/           # Content templates
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

### Current MVP (Weeks 1-3)
- [x] Project architecture and planning
- [ ] Core data models and LLM integration
- [ ] Feature classification and content generation
- [ ] Multi-domain presentation support
- [ ] FastAPI REST interface

### Future Enhancements
- [ ] OpenTelemetry observability and monitoring
- [ ] Advanced quality validation pipelines
- [ ] Feedback loops and content optimization
- [ ] Multi-modal content generation (images, diagrams)
- [ ] Content governance and version control

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: See [docs/](docs/) directory
- **Issues**: Report bugs and feature requests on GitHub Issues
- **Development Guide**: See [docs/development_guide.md](docs/development_guide.md)

---

**Built with ❤️ for the Elastic community**