# Tool Configuration Files

## config/elasticsearch.yaml
```yaml
# Elasticsearch Configuration
elasticsearch:
  url: ${ELASTICSEARCH_URL:http://localhost:9200}
  index_prefix: "elastic-whats-new"
  indices:
    features: "elastic-whats-new-features"
    presentations: "elastic-whats-new-presentations"
    labs: "elastic-whats-new-labs"
  
  # Index mappings
  mappings:
    features:
      properties:
        id:
          type: keyword
        name:
          type: text
          analyzer: standard
        description:
          type: text
          analyzer: standard
        benefits:
          type: text
          analyzer: standard
        theme:
          type: keyword
        domain:
          type: keyword
        documentation_links:
          type: keyword
        scraped_content:
          type: text
          analyzer: standard
        created_at:
          type: date
        updated_at:
          type: date
        
    presentations:
      properties:
        id:
          type: keyword
        domain:
          type: keyword
        quarter:
          type: keyword
        slides:
          type: nested
          properties:
            theme:
              type: keyword
            title:
              type: text
            content:
              type: text
            business_value:
              type: text
        generated_at:
          type: date
        
    labs:
      properties:
        id:
          type: keyword
        feature_ids:
          type: keyword
        domain:
          type: keyword
        title:
          type: text
        objective:
          type: text
        instructions:
          type: text
        sample_data:
          type: object
        difficulty:
          type: keyword
        estimated_time:
          type: integer
        generated_at:
          type: date

  # Search settings
  search:
    default_size: 50
    max_result_window: 10000
    timeout: "30s"
```

## config/ai_tools.yaml
```yaml
# AI Tools Configuration
ai_tools:
  claude:
    api_key: ${CLAUDE_API_KEY}
    model: "claude-3-5-sonnet-20241022"
    max_tokens: 4000
    temperature: 0.7
    
  elastic_mcp:
    endpoint: ${ELASTIC_MCP_ENDPOINT}
    timeout: 30
    max_retries: 3
    
  web_search:
    provider: "brave"  # or "google", "bing"
    api_key: ${WEB_SEARCH_API_KEY}
    max_results: 10
    timeout: 15

# Content generation prompts
prompts:
  slide_content:
    system: |
      You are an expert technical writer creating sales-focused presentation content for Elastic.
      Your audience includes both business and technical stakeholders.
      Focus on business value, ROI, and competitive advantages.
      
  lab_instructions:
    system: |
      You are creating hands-on lab instructions for Elastic features.
      Use storytelling to create realistic scenarios that practitioners face.
      Start with a relatable challenge, create urgency, then show how Elastic solves it.
      
  business_value:
    templates:
      simplify: "Reduce operational complexity and infrastructure costs"
      optimize: "Improve performance and resource efficiency"
      ai_innovation: "Enable AI-powered capabilities with minimal setup"
```

## config/web_scraping.yaml
```yaml
# Web Scraping Configuration
web_scraping:
  settings:
    timeout: 30
    retries: 3
    delay: 1  # seconds between requests
    user_agent: "Elastic-WhatsNew-Generator/1.0"
    
  # Site-specific configurations
  sites:
    elastic_co:
      base_url: "https://www.elastic.co"
      selectors:
        title: "h1, .page-title, .blog-title"
        description: ".lead, .summary, .excerpt, p:first-of-type"
        benefits: "ul li, .benefits li, .features li"
        content: ".content, .post-content, .documentation"
      rate_limit: 2  # requests per second
      
    elastic_docs:
      base_url: "https://www.elastic.co/guide"
      selectors:
        title: "h1.title, .titlepage h1"
        description: ".abstract, .lead"
        benefits: ".itemizedlist li, .variablelist dd"
        code_examples: "pre code, .code-block"
      rate_limit: 1
      
    github_elastic:
      base_url: "https://github.com/elastic"
      selectors:
        title: "h1"
        description: ".markdown-body p:first-of-type"
        features: ".markdown-body ul li"
      rate_limit: 1
      
  # Content extraction rules
  extraction:
    benefits_keywords:
      - "reduces"
      - "improves"
      - "faster"
      - "better"
      - "simplifies"
      - "automates"
      - "enables"
      - "eliminates"
      
    ignore_elements:
      - "nav"
      - "footer"
      - "aside"
      - ".sidebar"
      - ".advertisement"
      
    min_content_length: 50
    max_content_length: 5000
```

## config/templates.yaml
```yaml
# Template Configuration
templates:
  presentation:
    default_slides:
      - hook
      - innovation_overview
      - simplify_theme
      - optimize_theme
      - ai_innovation_theme
      - cross_platform_benefits
      - competitive_differentiation
      - business_case
      - call_to_action
      
    slide_templates:
      hook:
        title_template: "The {domain} Infrastructure Challenge"
        content_template: |
          - Hidden costs of fragmented solutions
          - Operational complexity at scale
          - Performance bottlenecks
          - AI adoption barriers
          
      theme_deep_dive:
        title_template: "{theme_title} - {tagline}"
        content_template: |
          ## Key Innovations
          {feature_list}
          
          ## Business Value
          {business_value}
          
          ## Technical Benefits
          {technical_benefits}
          
  lab:
    structure:
      - scenario_setup
      - challenge_identification
      - solution_walkthrough
      - hands_on_exercise
      - validation
      - business_value_recap
      
    personas:
      search:
        developer:
          challenges: ["relevance tuning", "performance optimization", "scaling search"]
          scenarios: ["ecommerce search", "enterprise search", "log search"]
        architect:
          challenges: ["infrastructure costs", "data distribution", "AI integration"]
          scenarios: ["multi-cluster setup", "cost optimization", "AI search"]
          
      observability:
        sre:
          challenges: ["MTTR reduction", "alert fatigue", "cost optimization"]
          scenarios: ["incident response", "performance monitoring", "cost analysis"]
        devops:
          challenges: ["deployment visibility", "troubleshooting", "automation"]
          scenarios: ["CI/CD monitoring", "application debugging", "infrastructure automation"]
          
      security:
        analyst:
          challenges: ["threat detection", "investigation time", "false positives"]
          scenarios: ["threat hunting", "incident investigation", "compliance monitoring"]
        ciso:
          challenges: ["security posture", "compliance", "team efficiency"]
          scenarios: ["risk assessment", "compliance reporting", "team productivity"]

# Domain-specific configurations
domains:
  search:
    sample_data_types:
      - ecommerce_products
      - enterprise_documents
      - log_data
      - knowledge_base
    common_challenges:
      - "Search relevance and ranking"
      - "Query performance at scale"
      - "Infrastructure costs"
      - "AI/semantic search adoption"
      
  observability:
    sample_data_types:
      - application_metrics
      - infrastructure_logs
      - distributed_traces
      - performance_data
    common_challenges:
      - "Mean time to resolution (MTTR)"
      - "Monitoring costs and complexity"
      - "Alert fatigue and noise"
      - "Cross-team visibility"
      
  security:
    sample_data_types:
      - security_events
      - threat_intelligence
      - audit_logs
      - network_traffic
    common_challenges:
      - "Threat detection accuracy"
      - "Investigation efficiency"
      - "Compliance requirements"
      - "Team productivity and retention"
```

## config/sample_data.yaml
```yaml
# Sample Data Generation Configuration
sample_data:
  generators:
    ecommerce_products:
      count: 1000
      schema:
        id: "prod-{counter:06d}"
        name: "{product_name}"
        description: "{product_description}"
        category: "{category}"
        price: "{price:float:10.99-999.99}"
        rating: "{rating:float:1.0-5.0}"
        in_stock: "{boolean:0.8}"
        tags: "{tags:list:3-8}"
        
    security_events:
      count: 5000
      schema:
        timestamp: "{timestamp:iso}"
        event_type: "{event_type}"
        source_ip: "{ip_address}"
        destination_ip: "{ip_address}"
        user_agent: "{user_agent}"
        status_code: "{status_code}"
        risk_score: "{risk_score:float:0.0-10.0}"
        
    application_logs:
      count: 10000
      schema:
        timestamp: "{timestamp:iso}"
        level: "{log_level}"
        service: "{service_name}"
        message: "{log_message}"
        duration_ms: "{duration:int:1-5000}"
        status_code: "{http_status}"
        
  # Data relationships for realistic scenarios
  relationships:
    user_sessions:
      - user_id: "user-001"
        events: 15
        pattern: "normal_browsing"
      - user_id: "user-002"
        events: 3
        pattern: "suspicious_activity"
        
    service_dependencies:
      - service: "frontend"
        depends_on: ["auth-service", "product-service"]
      - service: "product-service"
        depends_on: ["database", "cache-service"]
        
  # Scenario-specific data sets
  scenarios:
    ecommerce_search_optimization:
      products: 1000
      search_queries: 500
      user_sessions: 100
      conversion_events: 50
      
    security_threat_investigation:
      security_events: 5000
      threat_indicators: 50
      user_accounts: 200
      network_sessions: 1000
      
    application_performance_monitoring:
      application_logs: 10000
      metrics: 2000
      traces: 500
      alerts: 25
```

## .env.example
```bash
# Elasticsearch Configuration
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=changeme

# AI Tools
CLAUDE_API_KEY=your_claude_api_key_here
ELASTIC_MCP_ENDPOINT=http://localhost:3000
WEB_SEARCH_API_KEY=your_web_search_api_key

# Application Settings
APP_ENV=development
LOG_LEVEL=INFO
DEBUG=true

# Feature Toggle
ENABLE_WEB_SCRAPING=true
ENABLE_AI_GENERATION=true
ENABLE_SAMPLE_DATA_GENERATION=true
```

## requirements.txt
```txt
# Core dependencies
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Elasticsearch
elasticsearch==8.11.0

# Web scraping
requests==2.31.0
beautifulsoup4==4.12.2
scrapy==2.11.0

# AI and ML
anthropic==0.7.7
openai==1.3.8

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.2

# Data processing
pandas==2.1.4
pyyaml==6.0.1
jinja2==3.1.2

# Development tools
black==23.11.0
flake8==6.1.0
mypy==1.7.1
pre-commit==3.6.0

# Security
bandit==1.7.5
```