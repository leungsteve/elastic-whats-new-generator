"""
Claude API client for LLM-powered content extraction and generation.

This module provides a unified interface to Claude Sonnet for:
1. Stage 1: Extracting structured content from scraped documentation
2. Stage 2: Generating comprehensive presentations with storytelling
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from anthropic import Anthropic, APIError, APITimeoutError, RateLimitError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.core.models import LLMExtractedContent, Feature

logger = logging.getLogger(__name__)


class ClaudeClient:
    """
    Client for interacting with Claude Sonnet API.

    Handles both content extraction (Stage 1) and presentation generation (Stage 2)
    with proper error handling, retries, and structured output parsing.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-sonnet-20240229",
        max_tokens: int = 4096,
        temperature: float = 0.7
    ):
        """
        Initialize Claude client.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Claude model to use
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        self.client = Anthropic(api_key=self.api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

        logger.info(f"Initialized ClaudeClient with model: {model}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((APITimeoutError, RateLimitError)),
        reraise=True
    )
    def _make_api_call(self, messages: List[Dict[str, str]], system: Optional[str] = None) -> str:
        """
        Make API call to Claude with retry logic.

        Args:
            messages: List of message dicts with 'role' and 'content'
            system: Optional system prompt

        Returns:
            Response text from Claude

        Raises:
            APIError: If API call fails after retries
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system if system else "",
                messages=messages
            )

            # Extract text from response
            content = response.content[0].text

            logger.info(f"Claude API call successful. Tokens: {response.usage.input_tokens} in, {response.usage.output_tokens} out")

            return content

        except RateLimitError as e:
            logger.warning(f"Rate limit hit, will retry: {e}")
            raise
        except APITimeoutError as e:
            logger.warning(f"API timeout, will retry: {e}")
            raise
        except APIError as e:
            logger.error(f"Claude API error: {e}")
            raise

    def extract_content(
        self,
        feature_name: str,
        scraped_content: str,
        documentation_url: str
    ) -> LLMExtractedContent:
        """
        Stage 1: Extract structured content from scraped documentation.

        This method analyzes raw scraped documentation and extracts key information
        that will be cached in Elasticsearch for later presentation generation.

        Args:
            feature_name: Name of the feature being analyzed
            scraped_content: Raw scraped text from documentation
            documentation_url: Source URL for context

        Returns:
            LLMExtractedContent with structured information

        Raises:
            ValueError: If extraction fails or returns invalid data
        """
        logger.info(f"Starting content extraction for feature: {feature_name}")

        # Build extraction prompt
        system_prompt = """You are an expert technical writer analyzing Elastic product documentation.
Your task is to extract key structured information from raw documentation text.

Output MUST be valid JSON with this exact structure:
{
  "summary": "2-3 sentence concise summary of the feature",
  "use_cases": ["use case 1", "use case 2", ...],
  "key_capabilities": ["capability 1", "capability 2", ...],
  "benefits": ["benefit 1", "benefit 2", ...],
  "technical_requirements": ["requirement 1", "requirement 2", ...],
  "target_audience": "developers|devops|architects|data-engineers|security-analysts",
  "complexity_level": "beginner|intermediate|advanced"
}

Guidelines:
- Extract 3-5 use cases
- Extract 4-6 key capabilities
- Extract 3-5 benefits (both technical and business)
- Extract 2-4 technical requirements
- Be concise but informative
- Focus on practical, actionable information
- Maintain Elastic's technical accuracy"""

        user_prompt = f"""Analyze this Elastic feature documentation and extract structured information.

FEATURE: {feature_name}
SOURCE URL: {documentation_url}

DOCUMENTATION CONTENT:
{scraped_content[:8000]}

Extract the key information in the required JSON format."""

        messages = [{"role": "user", "content": user_prompt}]

        try:
            # Call Claude API
            response_text = self._make_api_call(messages, system=system_prompt)

            # Parse JSON response
            response_data = self._parse_json_response(response_text)

            # Validate required fields
            required_fields = ["summary", "use_cases", "key_capabilities", "benefits", "technical_requirements"]
            for field in required_fields:
                if field not in response_data:
                    raise ValueError(f"Missing required field in extraction: {field}")

            # Create LLMExtractedContent
            extracted = LLMExtractedContent(
                summary=response_data["summary"],
                use_cases=response_data.get("use_cases", []),
                key_capabilities=response_data.get("key_capabilities", []),
                benefits=response_data.get("benefits", []),
                technical_requirements=response_data.get("technical_requirements", []),
                target_audience=response_data.get("target_audience", "developers"),
                complexity_level=response_data.get("complexity_level", "intermediate"),
                extracted_at=datetime.utcnow(),
                model_used=self.model
            )

            logger.info(f"Successfully extracted content for {feature_name}")
            logger.debug(f"Extracted: {len(extracted.use_cases)} use cases, {len(extracted.key_capabilities)} capabilities")

            return extracted

        except Exception as e:
            logger.error(f"Content extraction failed for {feature_name}: {e}")
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

        This method takes features with cached LLM-extracted content and generates
        a cohesive presentation with storytelling arc.

        Args:
            features: List of Feature objects with llm_extracted content
            domain: Target domain (search/observability/security/all_domains)
            audience: Target audience (business/technical/mixed)
            narrative_style: Narrative approach (customer_journey/problem_solution/innovation_showcase)
            technical_depth: Technical depth level (low/medium/high)
            slide_count: Number of slides to generate (typically 5-7)

        Returns:
            Dict with slide content, story arc, and metadata

        Raises:
            ValueError: If generation fails or features lack extracted content
        """
        logger.info(f"Starting presentation generation for {len(features)} features")

        # Validate that features have extracted content
        features_with_content = []
        for feature in features:
            if (feature.content_research and
                feature.content_research.llm_extracted):
                features_with_content.append(feature)
            else:
                logger.warning(f"Feature {feature.name} missing llm_extracted content, skipping")

        if not features_with_content:
            raise ValueError("No features have LLM-extracted content for presentation generation")

        # Build feature context from extracted content
        feature_contexts = []
        for feature in features_with_content:
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
Target Audience: {extracted.target_audience}
Complexity: {extracted.complexity_level}
"""
            feature_contexts.append(context)

        # Build presentation generation prompt
        system_prompt = f"""You are an expert presentation designer for Elastic technical content.
Create a compelling {slide_count}-slide presentation following Elastic's storytelling framework.

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
      "speaker_notes": "Comprehensive speaker notes (2-3 paragraphs)"
    }}
  ],
  "story_arc": {{
    "opening_hook": "Compelling opening challenge",
    "central_theme": "Unifying theme",
    "resolution_message": "How features solve the challenge",
    "call_to_action": "Next steps"
  }}
}}

Slide Framework:
1. Opening Hook - Industry challenge
2-{slide_count-2}. Feature Slides - Use cases, capabilities, benefits
{slide_count-1}. Business Impact - ROI and outcomes
{slide_count}. Call to Action - Next steps

Guidelines:
- Use Elastic's three themes: Simplify, Optimize, AI Innovation
- Audience: {audience} - adjust technical depth accordingly
- Narrative: {narrative_style}
- Technical depth: {technical_depth}
- Each slide should tell part of a cohesive story
- Use markdown bullets for content
- Include concrete examples and use cases
- Business value should be quantifiable where possible"""

        user_prompt = f"""Generate a {slide_count}-slide presentation for Elastic {domain}.

FEATURES TO INCLUDE:
{chr(10).join(feature_contexts)}

Create a cohesive, compelling presentation that tells a story and demonstrates value."""

        messages = [{"role": "user", "content": user_prompt}]

        try:
            # Call Claude API
            response_text = self._make_api_call(messages, system=system_prompt)

            # Parse JSON response
            presentation_data = self._parse_json_response(response_text)

            # Validate structure
            if "slides" not in presentation_data or len(presentation_data["slides"]) == 0:
                raise ValueError("No slides generated in presentation")

            logger.info(f"Successfully generated {len(presentation_data['slides'])} slides")

            return presentation_data

        except Exception as e:
            logger.error(f"Presentation generation failed: {e}")
            raise ValueError(f"Failed to generate presentation: {e}")

    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse JSON from Claude response, handling markdown code blocks.

        Args:
            response_text: Raw response text from Claude

        Returns:
            Parsed JSON dict

        Raises:
            ValueError: If JSON parsing fails
        """
        # Claude often wraps JSON in markdown code blocks
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
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response text: {text[:500]}")
            raise ValueError(f"Invalid JSON in Claude response: {e}")

    def health_check(self) -> bool:
        """
        Verify API connectivity and credentials.

        Returns:
            True if API is accessible, False otherwise
        """
        try:
            messages = [{"role": "user", "content": "Respond with 'ok'"}]
            response = self._make_api_call(messages)
            return "ok" in response.lower()
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False