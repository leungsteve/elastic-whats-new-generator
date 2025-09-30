"""
Unified LLM client supporting multiple providers (OpenAI, Gemini, Claude).

This module provides a unified interface for content extraction and generation
across different LLM providers, with automatic provider selection based on
available API keys.
"""

import os
import json
import logging
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from enum import Enum

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.core.models import LLMExtractedContent, Feature

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    GEMINI = "gemini"
    CLAUDE = "claude"


class UnifiedLLMClient:
    """
    Unified client for multiple LLM providers.

    Automatically selects the best available provider based on API keys
    and provides a consistent interface for content extraction and generation.
    """

    # Class-level cache for prompts
    _prompts_cache: Optional[Dict[str, Any]] = None

    def __init__(
        self,
        provider: Optional[LLMProvider] = None,
        openai_api_key: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        openai_base_url: Optional[str] = None,
        usage_storage: Optional['LLMUsageStorage'] = None
    ):
        """
        Initialize unified LLM client.

        Args:
            provider: Specific provider to use (auto-selects if None)
            openai_api_key: OpenAI API key
            gemini_api_key: Google Gemini API key
            anthropic_api_key: Anthropic API key
            model: Specific model to use (provider-specific defaults if None)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            openai_base_url: Custom base URL for OpenAI API (for proxies)
            usage_storage: Optional LLMUsageStorage for tracking usage
        """
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.usage_storage = usage_storage

        # Get API keys from environment if not provided
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        self.anthropic_api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")

        # Get OpenAI proxy settings from environment
        self.openai_base_url = openai_base_url or os.getenv("OPENAI_BASE_URL")

        # Select provider
        if provider:
            self.provider = provider
        else:
            self.provider = self._auto_select_provider()

        if not self.provider:
            raise ValueError("No LLM provider available. Set OPENAI_API_KEY, GEMINI_API_KEY, or ANTHROPIC_API_KEY")

        # Select model based on provider
        self.model = model or self._get_default_model()

        # Initialize provider-specific client
        self.client = self._initialize_client()

        logger.info(f"Initialized UnifiedLLMClient with provider: {self.provider.value}, model: {self.model}")

    @classmethod
    def _load_prompts_config(cls) -> Dict[str, Any]:
        """Load prompts from config file (cached)."""
        if cls._prompts_cache is not None:
            return cls._prompts_cache

        config_path = Path(__file__).parent.parent.parent / "config" / "llm_prompts.yaml"

        try:
            with open(config_path, 'r') as f:
                cls._prompts_cache = yaml.safe_load(f)
                logger.info(f"Loaded LLM prompts from {config_path}")
                return cls._prompts_cache
        except FileNotFoundError:
            logger.warning(f"Prompts config not found at {config_path}, using defaults")
            return {}
        except Exception as e:
            logger.error(f"Failed to load prompts config: {e}")
            return {}

    def _auto_select_provider(self) -> Optional[LLMProvider]:
        """Auto-select provider based on available API keys."""
        # Priority: OpenAI > Gemini > Claude (based on cost and availability)
        if self.openai_api_key:
            return LLMProvider.OPENAI
        elif self.gemini_api_key:
            return LLMProvider.GEMINI
        elif self.anthropic_api_key:
            return LLMProvider.CLAUDE
        return None

    def _get_default_model(self) -> str:
        """Get default model for selected provider."""
        defaults = {
            LLMProvider.OPENAI: "gpt-4o-mini",  # Cost-effective GPT-4 class model
            LLMProvider.GEMINI: "gemini-1.5-flash",  # Fast and cost-effective
            LLMProvider.CLAUDE: "claude-3-sonnet-20240229"
        }
        return defaults[self.provider]

    def _initialize_client(self):
        """Initialize provider-specific client."""
        if self.provider == LLMProvider.OPENAI:
            from openai import OpenAI
            # Support custom base URL for proxies
            if self.openai_base_url:
                logger.info(f"Using custom OpenAI base URL: {self.openai_base_url}")
                return OpenAI(api_key=self.openai_api_key, base_url=self.openai_base_url)
            else:
                return OpenAI(api_key=self.openai_api_key)
        elif self.provider == LLMProvider.GEMINI:
            import google.generativeai as genai
            genai.configure(api_key=self.gemini_api_key)
            return genai.GenerativeModel(self.model)
        elif self.provider == LLMProvider.CLAUDE:
            from anthropic import Anthropic
            return Anthropic(api_key=self.anthropic_api_key)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def _call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        operation_type: str = "unknown",
        feature_ids: Optional[List[str]] = None,
        domain: Optional[str] = None
    ) -> str:
        """
        Make LLM API call with provider-specific handling and usage tracking.

        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            operation_type: Type of operation (extract, generate_presentation, generate_lab)
            feature_ids: Optional list of feature IDs involved
            domain: Optional domain context

        Returns:
            Response text
        """
        import time
        start_time = time.time()
        success = False
        error_message = None
        response_text = ""
        token_usage = None

        try:
            if self.provider == LLMProvider.OPENAI:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
                response_text = response.choices[0].message.content
                # Extract token usage if available
                if hasattr(response, 'usage'):
                    token_usage = {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    }
                success = True
                return response_text

            elif self.provider == LLMProvider.GEMINI:
                # Gemini combines system and user prompts
                full_prompt = f"{system_prompt}\n\n{user_prompt}"
                response = self.client.generate_content(
                    full_prompt,
                    generation_config={
                        "max_output_tokens": self.max_tokens,
                        "temperature": self.temperature
                    }
                )
                response_text = response.text
                success = True
                return response_text

            elif self.provider == LLMProvider.CLAUDE:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}]
                )
                response_text = response.content[0].text
                # Extract token usage if available
                if hasattr(response, 'usage'):
                    token_usage = {
                        "prompt_tokens": response.usage.input_tokens,
                        "completion_tokens": response.usage.output_tokens,
                        "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                    }
                success = True
                return response_text

        except Exception as e:
            error_message = str(e)
            logger.error(f"{self.provider.value} API error: {e}")
            raise
        finally:
            # Log usage if storage is available
            response_time = time.time() - start_time
            if self.usage_storage:
                try:
                    self._log_usage(
                        system_prompt=system_prompt,
                        user_prompt=user_prompt,
                        response_text=response_text,
                        operation_type=operation_type,
                        feature_ids=feature_ids or [],
                        domain=domain,
                        token_usage=token_usage,
                        response_time_seconds=response_time,
                        success=success,
                        error_message=error_message
                    )
                except Exception as log_error:
                    logger.warning(f"Failed to log LLM usage: {log_error}")

    def _log_usage(
        self,
        system_prompt: str,
        user_prompt: str,
        response_text: str,
        operation_type: str,
        feature_ids: List[str],
        domain: Optional[str],
        token_usage: Optional[Dict[str, int]],
        response_time_seconds: float,
        success: bool,
        error_message: Optional[str]
    ):
        """Log LLM usage to Elasticsearch."""
        from src.core.models import LLMUsageLog

        # Estimate cost based on provider and tokens
        estimated_cost = self._estimate_cost(token_usage)

        log_entry = LLMUsageLog(
            provider=self.provider.value,
            model=self.model,
            operation_type=operation_type,
            feature_ids=feature_ids,
            domain=domain,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_text=response_text,
            token_usage=token_usage,
            response_time_seconds=response_time_seconds,
            success=success,
            error_message=error_message,
            estimated_cost_usd=estimated_cost
        )

        self.usage_storage.log(log_entry)
        logger.info(f"Logged LLM usage: {log_entry.id} ({operation_type})")

    def _estimate_cost(self, token_usage: Optional[Dict[str, int]]) -> Optional[float]:
        """Estimate cost in USD based on provider and token usage."""
        if not token_usage:
            return None

        # Cost per 1K tokens (approximate as of 2025)
        costs = {
            LLMProvider.OPENAI: {
                "gpt-4o": {"prompt": 0.0025, "completion": 0.01},
                "gpt-4o-mini": {"prompt": 0.00015, "completion": 0.0006}
            },
            LLMProvider.GEMINI: {
                "gemini-1.5-flash": {"prompt": 0.000075, "completion": 0.0003}
            },
            LLMProvider.CLAUDE: {
                "claude-3-sonnet-20240229": {"prompt": 0.003, "completion": 0.015}
            }
        }

        provider_costs = costs.get(self.provider, {})
        model_costs = provider_costs.get(self.model, {"prompt": 0, "completion": 0})

        prompt_cost = (token_usage.get("prompt_tokens", 0) / 1000.0) * model_costs.get("prompt", 0)
        completion_cost = (token_usage.get("completion_tokens", 0) / 1000.0) * model_costs.get("completion", 0)

        return prompt_cost + completion_cost

    def extract_content(
        self,
        feature_name: str,
        scraped_content: str,
        documentation_url: str
    ) -> LLMExtractedContent:
        """
        Stage 1: Extract structured content from scraped documentation.

        Args:
            feature_name: Name of the feature
            scraped_content: Raw scraped text
            documentation_url: Source URL

        Returns:
            LLMExtractedContent with structured information
        """
        logger.info(f"Extracting content for {feature_name} using {self.provider.value}")

        system_prompt = """You are an expert technical writer analyzing Elastic product documentation.
Your task is to extract key structured information from raw documentation text WITH SPECIFIC TECHNICAL DETAILS.

Output MUST be valid JSON with this exact structure:
{
  "summary": "2-3 sentence concise summary of the feature",
  "use_cases": ["use case 1", "use case 2", ...],
  "key_capabilities": ["capability 1", "capability 2", ...],
  "benefits": ["benefit 1", "benefit 2", ...],
  "technical_requirements": ["requirement 1", "requirement 2", ...],
  "configuration_examples": ["complete config block 1", "complete config block 2", ...],
  "metrics_examples": ["before/after metric 1", "benchmark 2", ...],
  "api_commands": ["complete API command 1", "complete API command 2", ...],
  "implementation_steps": ["step 1", "step 2", ...],
  "limitations": ["limitation 1", "caveat 2", ...],
  "prerequisites": ["prerequisite 1", "dependency 2", ...],
  "version_info": "9.1.0+, Serverless Preview, AWS us-east-1",
  "comparisons": ["comparison 1", "comparison 2", ...],
  "hands_on_exercise_ideas": ["exercise 1", "exercise 2", ...],
  "sample_data_suggestions": ["data idea 1", "data idea 2", ...],
  "validation_checkpoints": ["checkpoint 1", "checkpoint 2", ...],
  "common_pitfalls": ["pitfall 1", "pitfall 2", ...],
  "demo_scenario": "compelling demo scenario for presentations",
  "business_impact_metrics": ["ROI metric 1", "efficiency gain 2", ...],
  "competitive_advantages": ["advantage 1", "advantage 2", ...],
  "visual_aids_suggestions": ["diagram suggestion 1", "chart suggestion 2", ...],
  "target_audience": "developers|devops|architects|data-engineers|security-analysts",
  "complexity_level": "beginner|intermediate|advanced"
}

CRITICAL EXTRACTION GUIDELINES:

1. **Configuration Examples** - Extract COMPLETE code blocks:
   - Include full PUT/POST request body with all parameters
   - Show complete mapping definitions, not snippets
   - Example: "PUT /my-index\\n{\\n  \\"mappings\\": {\\n    \\"properties\\": {\\n      \\"embedding\\": {\\n        \\"type\\": \\"dense_vector\\",\\n        \\"dims\\": 768,\\n        \\"index_options\\": { \\"type\\": \\"int8_hnsw\\" }\\n      }\\n    }\\n  }\\n}"

2. **Metrics Examples** - Extract CONCRETE numbers with context:
   - Include exact before/after values (e.g., "192GB → 9GB memory usage")
   - Include percentage improvements (e.g., "95% reduction in memory")
   - Include benchmark results (e.g., "NDCG@10: 0.1998 → 0.2059")
   - Include throughput/latency data (e.g., "5x faster filtered search")

3. **API Commands** - Extract COMPLETE working examples:
   - Full curl commands with headers if shown
   - Complete request/response bodies
   - Include all required parameters
   - Example: "POST /_search\\n{\\n  \\"query\\": {\\n    \\"knn\\": {\\n      \\"field\\": \\"embedding\\",\\n      \\"query_vector\\": [0.1, 0.2],\\n      \\"num_candidates\\": 30\\n    }\\n  }\\n}"

4. **Implementation Steps** - Extract step-by-step guide:
   - Order steps logically (1, 2, 3...)
   - Include action verbs ("Create", "Configure", "Execute")
   - Example: "1. Define dense_vector mapping with quantization", "2. Ingest documents", "3. Execute kNN search"

5. **Limitations** - Extract ALL constraints and caveats:
   - Regional restrictions (e.g., "Only available in AWS us-east-1")
   - Performance constraints (e.g., "Rate limit: 500 req/min")
   - Compatibility issues (e.g., "Not supported in GovCloud")
   - Technical constraints (e.g., "Max batch size: 16 documents")
   - Conditions (e.g., "Only beneficial when 40%+ vectors filtered")

6. **Prerequisites** - Extract dependencies and requirements:
   - Software versions (e.g., "Elasticsearch 9.1+")
   - Infrastructure requirements (e.g., "HNSW graph-based kNN")
   - Configuration needs (e.g., "float32 vectors with 384+ dimensions")

7. **Version Info** - Extract availability information:
   - Format: "MinVersion, Tier, Region/Cloud"
   - Example: "9.1.0+, Serverless Preview, AWS us-east-1"
   - Include status: "Technical Preview", "GA", "Beta"

8. **Comparisons** - Extract performance/feature comparisons:
   - Before/after comparisons (e.g., "ACORN vs naive: 5x speedup")
   - Method comparisons (e.g., "BBQ better ranking in 9/10 datasets vs float32")
   - Include specific numbers/datasets when available

9. **Hands-On Exercise Ideas** - Design engaging lab activities:
   - Specific, achievable tasks users can complete
   - Progressive difficulty (beginner → advanced)
   - Example: "Configure BBQ quantization on e-commerce product vectors", "Compare query performance with/without ACORN filtering"

10. **Sample Data Suggestions** - Recommend realistic datasets:
    - Specific data types and scales
    - Example: "1M e-commerce product descriptions with 768-dim embeddings", "Apache access logs (100GB) for observability testing"
    - Include data generation hints if applicable

11. **Validation Checkpoints** - Define success criteria:
    - Observable outcomes at each implementation step
    - Example: "Verify index size reduced by ~90%", "Confirm search latency < 50ms", "Check NDCG@10 score > 0.85"

12. **Common Pitfalls** - Identify troubleshooting tips:
    - Typical misconfigurations or errors
    - Example: "Forgetting to set num_candidates causes poor recall", "Using BBQ on <384 dims reduces quality"

13. **Demo Scenario** - Create compelling narrative:
    - Real-world relatable scenario (1-2 sentences)
    - Example: "E-commerce site with 10M products needs sub-50ms semantic search while reducing infrastructure costs by 80%"

14. **Business Impact Metrics** - Quantify business value:
    - Cost savings, revenue impact, efficiency gains
    - Example: "$50K/year cloud cost savings", "2x faster time-to-resolution", "30% increase in search conversion"

15. **Competitive Advantages** - Highlight differentiators:
    - How Elastic stands out vs alternatives
    - Example: "Only solution with both BBQ and ACORN in single platform", "5x faster than Pinecone filtered search"

16. **Visual Aids Suggestions** - Recommend presentation visuals:
    - Specific diagram/chart types
    - Example: "Before/after memory comparison bar chart", "Query latency vs filter selectivity line graph", "HNSW graph traversal animation"

QUALITY STANDARDS:
- Prefer specific over generic ("Uses int8_hnsw index_options" > "Supports quantization")
- Include units and context with numbers ("192GB → 6GB" not "32x reduction")
- Extract 3-5 items per field (more for complex features)
- Prioritize actionable, technical details over marketing language
- For lab hints: Be specific and testable
- For presentation hints: Be compelling and business-focused"""

        user_prompt = f"""Analyze this Elastic feature documentation and extract structured information.

FEATURE: {feature_name}
SOURCE URL: {documentation_url}

DOCUMENTATION CONTENT:
{scraped_content[:8000]}

Extract the key information in the required JSON format."""

        try:
            response_text = self._call_llm(
                system_prompt,
                user_prompt,
                operation_type="extract",
                feature_ids=[feature_name],
                domain=None
            )
            response_data = self._parse_json_response(response_text)

            # Validate required fields
            required_fields = ["summary", "use_cases", "key_capabilities", "benefits", "technical_requirements"]
            for field in required_fields:
                if field not in response_data:
                    raise ValueError(f"Missing required field: {field}")

            extracted = LLMExtractedContent(
                summary=response_data["summary"],
                use_cases=response_data.get("use_cases", []),
                key_capabilities=response_data.get("key_capabilities", []),
                benefits=response_data.get("benefits", []),
                technical_requirements=response_data.get("technical_requirements", []),
                configuration_examples=response_data.get("configuration_examples", []),
                metrics_examples=response_data.get("metrics_examples", []),
                api_commands=response_data.get("api_commands", []),
                # Enhanced fields
                implementation_steps=response_data.get("implementation_steps", []),
                limitations=response_data.get("limitations", []),
                prerequisites=response_data.get("prerequisites", []),
                version_info=response_data.get("version_info"),
                comparisons=response_data.get("comparisons", []),
                # Lab generation hints
                hands_on_exercise_ideas=response_data.get("hands_on_exercise_ideas", []),
                sample_data_suggestions=response_data.get("sample_data_suggestions", []),
                validation_checkpoints=response_data.get("validation_checkpoints", []),
                common_pitfalls=response_data.get("common_pitfalls", []),
                # Presentation generation hints
                demo_scenario=response_data.get("demo_scenario"),
                business_impact_metrics=response_data.get("business_impact_metrics", []),
                competitive_advantages=response_data.get("competitive_advantages", []),
                visual_aids_suggestions=response_data.get("visual_aids_suggestions", []),
                target_audience=response_data.get("target_audience", "developers"),
                complexity_level=response_data.get("complexity_level", "intermediate"),
                extracted_at=datetime.now(timezone.utc),
                model_used=f"{self.provider.value}/{self.model}"
            )

            logger.info(f"Successfully extracted content: {len(extracted.use_cases)} use cases, "
                       f"{len(extracted.key_capabilities)} capabilities, "
                       f"{len(extracted.configuration_examples)} config examples, "
                       f"{len(extracted.metrics_examples)} metrics, "
                       f"{len(extracted.api_commands)} commands, "
                       f"{len(extracted.implementation_steps)} steps, "
                       f"{len(extracted.limitations)} limitations, "
                       f"{len(extracted.comparisons)} comparisons, "
                       f"{len(extracted.hands_on_exercise_ideas)} lab exercises, "
                       f"{len(extracted.validation_checkpoints)} checkpoints")

            return extracted

        except Exception as e:
            logger.error(f"Content extraction failed: {e}")
            raise ValueError(f"Failed to extract content: {e}")

    def generate_presentation_slides(
        self,
        features: List[Feature],
        domain: str,
        audience: str,
        narrative_style: str,
        technical_depth: str,
        slide_count: int = 7
    ) -> Dict[str, Any]:
        """
        Stage 2: Generate comprehensive presentation with storytelling.

        Args:
            features: List of features with llm_extracted content
            domain: Target domain
            audience: Target audience
            narrative_style: Narrative approach
            technical_depth: Technical depth level
            slide_count: Number of slides

        Returns:
            Dict with presentation data
        """
        logger.info(f"Generating presentation using {self.provider.value}")

        # Build feature context
        feature_contexts = []
        for feature in features:
            if not (feature.content_research and feature.content_research.llm_extracted):
                continue

            extracted = feature.content_research.llm_extracted
            context = f"""
Feature: {feature.name}
Summary: {extracted.summary}
Use Cases:
{chr(10).join(f'  - {uc}' for uc in extracted.use_cases[:3])}
Key Capabilities:
{chr(10).join(f'  - {cap}' for cap in extracted.key_capabilities[:4])}
Benefits:
{chr(10).join(f'  - {ben}' for ben in extracted.benefits[:3])}
"""

            # Add PRESENTATION-SPECIFIC HINTS (NEW)
            if hasattr(extracted, 'demo_scenario') and extracted.demo_scenario:
                context += f"\n📺 Demo Scenario: {extracted.demo_scenario}\n"

            if hasattr(extracted, 'business_impact_metrics') and extracted.business_impact_metrics:
                context += "\n💰 Business Impact Metrics:\n"
                context += chr(10).join(f'  - {metric}' for metric in extracted.business_impact_metrics[:4])
                context += "\n"

            if hasattr(extracted, 'competitive_advantages') and extracted.competitive_advantages:
                context += "\n🏆 Competitive Advantages:\n"
                context += chr(10).join(f'  - {adv}' for adv in extracted.competitive_advantages[:3])
                context += "\n"

            if hasattr(extracted, 'visual_aids_suggestions') and extracted.visual_aids_suggestions:
                context += "\n📊 Visual Aid Suggestions:\n"
                context += chr(10).join(f'  - {vis}' for vis in extracted.visual_aids_suggestions[:3])
                context += "\n"

            if hasattr(extracted, 'comparisons') and extracted.comparisons:
                context += "\n⚖️  Comparisons:\n"
                context += chr(10).join(f'  - {comp}' for comp in extracted.comparisons[:3])
                context += "\n"

            feature_contexts.append(context)

        # Load prompts from config (with fallback to defaults)
        prompts_config = self._load_prompts_config()
        presentation_prompts = prompts_config.get('presentation_generator', {})

        # Get system prompt template (with fallback)
        system_prompt_template = presentation_prompts.get('system_prompt', """You are an expert presentation designer for Elastic technical content.
Create a compelling {slide_count}-slide presentation following Elastic's REQUIRED storytelling framework.

REQUIRED PRESENTATION FLOW (7 slides):
1. Opening Hook - Infrastructure challenge that resonates with audience
2. Innovation Overview - "Three Game-Changing Innovations" overview
3. Theme 1: Simplify - "Do more with less" features
4. Theme 2: Optimize - "Do it faster" features
5. Theme 3: AI Innovation - "Do it with AI" features
6. Business Case/ROI - Quantified benefits and competitive differentiation
7. Call to Action - Clear next steps

THREE UNIVERSAL THEMES (classify ALL features):
- **Simplify**: Reduce complexity, automate operations, ease of use
- **Optimize**: Performance improvements, efficiency gains, cost reduction
- **AI Innovation**: AI/ML capabilities, intelligent features, GenAI integration

Output MUST be valid JSON with this structure:
{{
  "title": "Presentation title",
  "slides": [
    {{
      "title": "Slide title",
      "subtitle": "Optional subtitle or null",
      "content": "Markdown formatted slide content with bullets",
      "business_value": "Business value statement",
      "theme": "simplify|optimize|ai_innovation",
      "speaker_notes": "COMPREHENSIVE talk track (3-5 paragraphs): What to say, key points to emphasize, transitions, timing notes"
    }}
  ],
  "story_arc": {{
    "opening_hook": "Compelling opening challenge",
    "central_theme": "Unifying theme across all three innovations",
    "resolution_message": "How these innovations solve the challenge",
    "call_to_action": "Next steps for prospects"
  }}
}}

Guidelines:
- Audience: {audience}
- Narrative: {narrative_style}
- Technical depth: {technical_depth}
- Follow the 7-slide structure exactly
- Group features by theme (Simplify/Optimize/AI Innovation)
- Each theme slide should highlight 2-4 features
- Business case slide must show ROI and competitive advantages
- Opening hook should identify a relatable challenge""")

        # Get user prompt template (with fallback)
        user_prompt_template = presentation_prompts.get('user_prompt', """Generate a {slide_count}-slide presentation for Elastic {domain} following the REQUIRED 7-slide structure.

FEATURES TO INCLUDE (classify by theme):
{feature_contexts}

REQUIRED STRUCTURE:
Slide 1: Opening Hook - Start with infrastructure/operational challenge
Slide 2: Innovation Overview - Preview three game-changing themes
Slide 3: Simplify Theme - Features that reduce complexity
Slide 4: Optimize Theme - Features that improve performance
Slide 5: AI Innovation Theme - Features leveraging AI/ML
Slide 6: Business Case - ROI, cost savings, competitive advantages
Slide 7: Call to Action - Next steps (demo, trial, contact)

Classify each feature into one of the three themes and create a cohesive story.""")

        # Format prompts with variables
        system_prompt = system_prompt_template.format(
            slide_count=slide_count,
            audience=audience,
            narrative_style=narrative_style,
            technical_depth=technical_depth
        )

        user_prompt = user_prompt_template.format(
            slide_count=slide_count,
            domain=domain,
            feature_contexts=chr(10).join(feature_contexts)
        )

        try:
            feature_ids = [f.id for f in features]
            response_text = self._call_llm(
                system_prompt,
                user_prompt,
                operation_type="generate_presentation",
                feature_ids=feature_ids,
                domain=domain
            )
            presentation_data = self._parse_json_response(response_text)

            if "slides" not in presentation_data:
                raise ValueError("No slides in response")

            logger.info(f"Generated {len(presentation_data['slides'])} slides")
            return presentation_data

        except Exception as e:
            logger.error(f"Presentation generation failed: {e}")
            raise ValueError(f"Failed to generate presentation: {e}")

    # Temporarily disable retry to see actual error
    # @retry(
    #     stop=stop_after_attempt(3),
    #     wait=wait_exponential(multiplier=1, min=4, max=10),
    #     retry=retry_if_exception_type((Exception,))
    # )
    def generate_lab(
        self,
        features: List[Feature],
        domain: str = "search",
        scenario_type: str = "auto",
        data_size: str = "demo",
        technical_depth: str = "medium"
    ) -> Dict[str, Any]:
        """
        Generate lab instructions using LLM.

        Args:
            features: List of features to include in lab
            domain: Target domain
            scenario_type: Scenario type (auto/ecommerce/observability/security)
            data_size: Data size (demo=50 rows, realistic=500 rows, large=5000 rows)
            technical_depth: Technical depth level

        Returns:
            Lab instruction data as dict
        """
        logger.info(f"Generating lab for {len(features)} feature(s) in {domain} domain")

        # Validate features
        if not features:
            raise ValueError("No features provided for lab generation")

        # Load lab prompts from YAML
        prompts = self._load_prompts_config()
        lab_prompts = prompts.get('lab_generator', {})

        # Build feature list and details
        try:
            feature_list = "\n".join([f"- {f.name}: {f.description}" for f in features])
        except AttributeError as e:
            logger.error(f"Feature object missing attribute: {e}. Features type: {type(features[0])}")
            raise ValueError(f"Invalid feature object: {e}")

        feature_details_parts = []
        for feature in features:
            details = f"\nFeature: {feature.name}\nDescription: {feature.description}"
            if feature.benefits:
                details += f"\nBenefits: {', '.join(feature.benefits[:3])}"
            if feature.documentation_links:
                details += f"\nDocs: {feature.documentation_links[0]}"

            # ENHANCEMENT: Add AI-extracted content if available
            if hasattr(feature, 'content_research') and feature.content_research:
                cr = feature.content_research
                ec = cr.llm_extracted if hasattr(cr, 'llm_extracted') else None

                if ec:
                    # Add use cases
                    if hasattr(ec, 'use_cases') and ec.use_cases:
                        details += f"\n\nUse Cases:"
                        for uc in ec.use_cases[:3]:
                            details += f"\n  - {uc}"

                    # Add key capabilities
                    if hasattr(ec, 'key_capabilities') and ec.key_capabilities:
                        details += f"\n\nKey Capabilities:"
                        for cap in ec.key_capabilities[:5]:
                            details += f"\n  - {cap}"

                    # Add technical requirements
                    if hasattr(ec, 'technical_requirements') and ec.technical_requirements:
                        details += f"\n\nTechnical Requirements:"
                        for req in ec.technical_requirements[:3]:
                            details += f"\n  - {req}"

                    # Add configuration examples (NEW)
                    if hasattr(ec, 'configuration_examples') and ec.configuration_examples:
                        details += f"\n\nConfiguration Examples:"
                        for conf in ec.configuration_examples[:3]:
                            details += f"\n  - {conf}"

                    # Add metrics examples (NEW)
                    if hasattr(ec, 'metrics_examples') and ec.metrics_examples:
                        details += f"\n\nMetrics Examples:"
                        for metric in ec.metrics_examples[:3]:
                            details += f"\n  - {metric}"

                    # Add API commands (NEW)
                    if hasattr(ec, 'api_commands') and ec.api_commands:
                        details += f"\n\nAPI Commands:"
                        for cmd in ec.api_commands[:3]:
                            details += f"\n  - {cmd}"

                    # Add LAB-SPECIFIC HINTS (NEW)
                    if hasattr(ec, 'hands_on_exercise_ideas') and ec.hands_on_exercise_ideas:
                        details += f"\n\n🧪 Hands-On Exercise Ideas:"
                        for ex in ec.hands_on_exercise_ideas:
                            details += f"\n  - {ex}"

                    if hasattr(ec, 'sample_data_suggestions') and ec.sample_data_suggestions:
                        details += f"\n\n📊 Sample Data Suggestions:"
                        for data in ec.sample_data_suggestions:
                            details += f"\n  - {data}"

                    if hasattr(ec, 'validation_checkpoints') and ec.validation_checkpoints:
                        details += f"\n\n✓ Validation Checkpoints:"
                        for check in ec.validation_checkpoints:
                            details += f"\n  - {check}"

                    if hasattr(ec, 'common_pitfalls') and ec.common_pitfalls:
                        details += f"\n\n⚠️  Common Pitfalls to Avoid:"
                        for pit in ec.common_pitfalls:
                            details += f"\n  - {pit}"

                    logger.info(f"Enhanced context for {feature.name} with AI-extracted content including lab hints")
                else:
                    logger.warning(f"No llm_extracted content found for {feature.name}")

            feature_details_parts.append(details)

        feature_details = "\n".join(feature_details_parts)

        # Convert data size to actual number
        data_size_mapping = {
            "demo": "50-100",
            "realistic": "200-500",
            "large": "1000-5000"
        }
        data_size_num = data_size_mapping.get(data_size, "50-100")

        # Get prompts with fallback defaults
        system_prompt_template = lab_prompts.get('system_prompt', """You are an expert at creating story-driven, hands-on Elastic labs.
Create an engaging lab with realistic datasets and copy-paste ready commands.""")

        user_prompt_template = lab_prompts.get('user_prompt', """Create a hands-on lab for Elastic {domain}.

FEATURES TO TEACH:
{feature_list}

{feature_details}

Create an engaging lab with sample data and ES|QL queries.""")

        # Format prompts
        # System prompt doesn't need formatting - it's static
        system_prompt = system_prompt_template

        user_prompt = user_prompt_template.format(
            domain=domain,
            feature_list=feature_list,
            scenario_type=scenario_type,
            data_size=data_size_num,
            technical_depth=technical_depth,
            feature_details=feature_details
        )

        try:
            feature_ids = [f.id for f in features]
            response_text = self._call_llm(
                system_prompt,
                user_prompt,
                operation_type="generate_lab",
                feature_ids=feature_ids,
                domain=domain
            )
            lab_data = self._parse_json_response(response_text)

            logger.info(f"Generated lab: {lab_data.get('title', 'Untitled')}")
            return lab_data

        except Exception as e:
            logger.error(f"Lab generation failed: {e}")
            raise ValueError(f"Failed to generate lab: {e}")

    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON from LLM response, handling markdown code blocks."""
        text = response_text.strip()

        # Remove markdown code block markers
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]

        if text.endswith("```"):
            text = text[:-3]

        text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.error(f"Full response text (first 2000 chars):\n{text[:2000]}")
            logger.error(f"Error location context:\n{text[max(0, 2962-100):min(len(text), 2962+100)]}")
            raise ValueError(f"Invalid JSON in response: {e}")

    def health_check(self) -> bool:
        """Verify API connectivity."""
        try:
            response = self._call_llm(
                "You are a helpful assistant.",
                "Respond with 'ok'",
                operation_type="health_check",
                feature_ids=[],
                domain=None
            )
            return "ok" in response.lower()
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    def get_provider_info(self) -> Dict[str, str]:
        """Get current provider information."""
        return {
            "provider": self.provider.value,
            "model": self.model,
            "available_providers": [
                p.value for p in LLMProvider
                if (p == LLMProvider.OPENAI and self.openai_api_key) or
                   (p == LLMProvider.GEMINI and self.gemini_api_key) or
                   (p == LLMProvider.CLAUDE and self.anthropic_api_key)
            ]
        }