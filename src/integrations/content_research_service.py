"""
Content Research Service for enhanced feature content discovery and extraction.

This service orchestrates web scraping, AI content extraction, and ELSER embedding
generation to create comprehensive feature content research.
"""

import asyncio
import time
import re
from typing import List, Dict, Any, Optional, Set
from urllib.parse import urljoin, urlparse
from datetime import datetime, timezone
import logging

import requests
from bs4 import BeautifulSoup

from ..core.models import (
    Feature, SourceContent, SourceMetadata, ContentResearch,
    ContentResearchStatus, ExtractedContent, AIInsights,
    CodeExample, UseCase, PresentationAngle, LabScenario,
    ELSEREmbedding, ContentEmbeddings
)

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter to ensure respectful scraping."""

    def __init__(self, requests_per_second: float = 2.0):
        self.min_interval = 1.0 / requests_per_second
        self.last_request = {}

    async def wait_if_needed(self, domain: str):
        """Wait if necessary to respect rate limits."""
        now = time.time()
        if domain in self.last_request:
            elapsed = now - self.last_request[domain]
            if elapsed < self.min_interval:
                await asyncio.sleep(self.min_interval - elapsed)
        self.last_request[domain] = time.time()


class ContentResearchConfig:
    """Configuration for content research behavior."""

    def __init__(self):
        self.enabled = True
        self.max_sources_per_feature = 10
        self.max_follow_depth = 2
        self.timeout_seconds = 30
        self.rate_limit_per_domain = 2.0
        self.max_content_length = 50000
        self.extract_code_examples = True
        self.follow_external_links = False
        self.ai_insights_enabled = True
        self.generate_embeddings = True
        self.embedding_model = ".elser_model_2"

        # Allowed domains for scraping
        self.allowed_domains = [
            "elastic.co",
            "github.com/elastic",
            "discuss.elastic.co"
        ]

        # Domain-specific rules
        self.domain_rules = {
            "elastic.co": {
                "priority": 1.0,
                "rate_limit": 2.0,
                "content_selectors": [".content", ".main", "#main-content"],
                "exclude_selectors": [".navigation", ".footer", ".sidebar"]
            },
            "github.com": {
                "priority": 0.8,
                "rate_limit": 1.0,
                "content_selectors": [".readme", ".md-content"],
                "file_types": [".md", ".rst", ".txt"]
            }
        }


class ContentResearchService:
    """Service for comprehensive feature content research."""

    def __init__(self, config: Optional[ContentResearchConfig] = None, ai_client = None, elasticsearch_client = None):
        self.config = config or ContentResearchConfig()
        self.ai_client = ai_client
        self.elasticsearch_client = elasticsearch_client
        self.rate_limiter = RateLimiter(self.config.rate_limit_per_domain)

        # HTTP session setup
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Elastic What\'s New Generator Research Bot 1.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })

    async def research_feature_content(self, feature: Feature) -> ContentResearch:
        """
        Main research pipeline for a feature.

        Args:
            feature: Feature to research

        Returns:
            Complete ContentResearch object
        """
        logger.info(f"Starting content research for feature: {feature.id}")

        try:
            # Update status to in progress
            content_research = feature.content_research
            content_research.status = ContentResearchStatus.IN_PROGRESS
            content_research.last_updated = datetime.now(timezone.utc)

            # Step 1: Validate and scrape primary sources
            primary_sources = await self._scrape_primary_sources(feature.documentation_links)
            content_research.primary_sources = primary_sources

            # Step 2: Discover and scrape related sources
            related_sources = await self._discover_related_sources(primary_sources, feature)
            content_research.related_sources = related_sources

            # Step 3: Extract structured content using AI
            if self.config.ai_insights_enabled and self.ai_client:
                extracted_content = await self._extract_structured_content(
                    primary_sources + related_sources, feature
                )
                content_research.extracted_content = extracted_content

                # Step 4: Generate AI insights
                ai_insights = await self._generate_ai_insights(
                    extracted_content, primary_sources + related_sources, feature
                )
                content_research.ai_insights = ai_insights

            # Step 5: Generate ELSER embeddings
            if self.config.generate_embeddings and self.elasticsearch_client:
                embeddings = await self._generate_embeddings(content_research, feature)
                content_research.embeddings = embeddings

            # Mark as completed
            content_research.status = ContentResearchStatus.COMPLETED
            content_research.last_updated = datetime.now(timezone.utc)

            logger.info(f"Content research completed for feature: {feature.id}")
            return content_research

        except Exception as e:
            logger.error(f"Content research failed for feature {feature.id}: {e}")
            content_research.status = ContentResearchStatus.FAILED
            content_research.last_updated = datetime.now(timezone.utc)
            return content_research

    async def _scrape_primary_sources(self, urls: List[str]) -> List[SourceContent]:
        """Scrape primary documentation sources."""
        sources = []

        for url in urls:
            if not self._is_url_allowed(url):
                logger.warning(f"URL not in allowed domains: {url}")
                continue

            try:
                domain = urlparse(url).netloc
                await self.rate_limiter.wait_if_needed(domain)

                source_content = await self._scrape_url(url, "manual", "documentation")
                if source_content:
                    sources.append(source_content)

            except Exception as e:
                logger.error(f"Failed to scrape primary source {url}: {e}")

        return sources

    async def _discover_related_sources(self, primary_sources: List[SourceContent], feature: Feature) -> List[SourceContent]:
        """Discover and scrape related sources from embedded links."""
        if not self.config.follow_external_links:
            return []

        related_sources = []
        discovered_urls: Set[str] = set()

        # Extract links from primary sources
        for source in primary_sources:
            links = self._extract_links_from_content(source.content, source.url)

            for link in links:
                if len(discovered_urls) >= self.config.max_sources_per_feature:
                    break

                if link in discovered_urls or not self._is_url_allowed(link):
                    continue

                relevance_score = self._calculate_relevance_score(link, source.content, feature)
                if relevance_score > 0.3:  # Minimum relevance threshold
                    discovered_urls.add(link)

        # Scrape discovered URLs
        for url in list(discovered_urls)[:self.config.max_sources_per_feature // 2]:
            try:
                domain = urlparse(url).netloc
                await self.rate_limiter.wait_if_needed(domain)

                source_content = await self._scrape_url(url, "link_following", "related")
                if source_content:
                    # Calculate final relevance score
                    relevance_score = self._calculate_relevance_score(url, source_content.content, feature)
                    source_content.relevance_score = relevance_score
                    related_sources.append(source_content)

            except Exception as e:
                logger.error(f"Failed to scrape related source {url}: {e}")

        return related_sources

    async def _scrape_url(self, url: str, discovery_method: str, content_type: str) -> Optional[SourceContent]:
        """Scrape a single URL and return SourceContent."""
        try:
            response = self.session.get(url, timeout=self.config.timeout_seconds)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract content
            title = self._extract_title(soup)
            content = self._extract_content(soup, url)
            word_count = len(content.split())

            # Extract metadata
            metadata = self._extract_metadata(soup, response)

            # Find embedded links
            links_found = self._extract_links_from_content(content, url)

            return SourceContent(
                url=url,
                title=title,
                content=content,
                word_count=word_count,
                content_type=content_type,
                discovery_method=discovery_method,
                metadata=metadata,
                links_found=links_found[:20]  # Limit to prevent bloat
            )

        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")
            return SourceContent(
                url=url,
                title="Error",
                content="",
                status="failed",
                discovery_method=discovery_method,
                content_type=content_type
            )

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        title_selectors = ['h1', 'title', '.page-title', '.title', '.entry-title']

        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text().strip()
                if title:
                    return title[:200]  # Limit length

        return "Unknown Title"

    def _extract_content(self, soup: BeautifulSoup, url: str) -> str:
        """Extract main content from the page."""
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            element.decompose()

        # Get domain-specific selectors
        domain = urlparse(url).netloc
        domain_rules = self.config.domain_rules.get(domain, {})
        content_selectors = domain_rules.get('content_selectors', ['.content', '.main', 'main', 'article'])

        # Try domain-specific selectors first
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                text = content_element.get_text()
                text = re.sub(r'\s+', ' ', text).strip()
                if len(text) > 100:  # Ensure we got meaningful content
                    return text[:self.config.max_content_length]

        # Fallback to body content
        body = soup.find('body')
        if body:
            text = body.get_text()
            text = re.sub(r'\s+', ' ', text).strip()
            return text[:self.config.max_content_length]

        return ""

    def _extract_metadata(self, soup: BeautifulSoup, response) -> SourceMetadata:
        """Extract metadata from the page."""
        metadata = SourceMetadata()

        # Extract sections (h1, h2, h3 tags)
        sections = []
        for heading in soup.find_all(['h1', 'h2', 'h3']):
            section_text = heading.get_text().strip()
            if section_text:
                sections.append(section_text)
        metadata.page_sections = sections[:10]  # Limit to 10 sections

        # Count code examples
        code_elements = soup.find_all(['pre', 'code', '.highlight', '.code-block'])
        metadata.code_examples = len([el for el in code_elements if len(el.get_text().strip()) > 20])

        # Count images
        metadata.images = len(soup.find_all('img'))

        # Extract meta tags
        meta_author = soup.find('meta', attrs={'name': 'author'})
        if meta_author:
            metadata.author = meta_author.get('content', '')

        # Try to get last modified from headers or meta tags
        last_modified = response.headers.get('last-modified')
        if last_modified:
            metadata.last_modified = last_modified

        return metadata

    def _extract_links_from_content(self, content: str, base_url: str) -> List[str]:
        """Extract links from content."""
        soup = BeautifulSoup(content, 'html.parser')
        links = []

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            # Convert relative URLs to absolute
            absolute_url = urljoin(base_url, href)

            # Filter out common non-content links
            if not any(skip in absolute_url.lower() for skip in ['#', 'javascript:', 'mailto:', 'tel:']):
                links.append(absolute_url)

        return list(set(links))  # Remove duplicates

    def _calculate_relevance_score(self, url: str, context: str, feature: Feature) -> float:
        """Calculate relevance score for a discovered link."""
        score = 0.0

        # Domain authority scoring
        domain = urlparse(url).netloc
        if 'elastic.co' in domain:
            score += 0.4
        elif 'github.com' in domain and 'elastic' in domain:
            score += 0.3
        elif any(allowed in domain for allowed in self.config.allowed_domains):
            score += 0.2

        # Content type scoring
        if '/guide/' in url or '/docs/' in url:
            score += 0.3
        elif '/blog/' in url:
            score += 0.2
        elif '/discuss/' in url:
            score += 0.1

        # Feature name relevance
        feature_terms = feature.name.lower().split()
        url_lower = url.lower()
        context_lower = context.lower()

        for term in feature_terms:
            if term in url_lower:
                score += 0.2
            if term in context_lower[:500]:  # Check context around the link
                score += 0.1

        # Domain alignment
        domain_keywords = {
            'search': ['search', 'query', 'index', 'elasticsearch'],
            'observability': ['observability', 'monitoring', 'logs', 'metrics', 'apm'],
            'security': ['security', 'siem', 'threat', 'detection']
        }

        domain_terms = domain_keywords.get(feature.domain.value, [])
        for term in domain_terms:
            if term in url_lower or term in context_lower:
                score += 0.1

        return min(score, 1.0)

    def _is_url_allowed(self, url: str) -> bool:
        """Check if URL is in allowed domains."""
        domain = urlparse(url).netloc
        return any(allowed in domain for allowed in self.config.allowed_domains)

    async def _extract_structured_content(self, sources: List[SourceContent], feature: Feature) -> ExtractedContent:
        """Use AI to extract structured content from sources."""
        if not self.ai_client:
            return ExtractedContent()

        # Combine content from all sources
        combined_content = self._combine_source_content(sources)

        try:
            # Extract key concepts
            key_concepts = await self._extract_key_concepts(combined_content, feature)

            # Extract configuration examples
            config_examples = await self._extract_configuration_examples(combined_content, feature)

            # Generate use cases
            use_cases = await self._generate_use_cases(combined_content, feature)

            # Extract prerequisites
            prerequisites = await self._extract_prerequisites(combined_content, feature)

            # Find related features
            related_features = await self._find_related_features(combined_content, feature)

            return ExtractedContent(
                key_concepts=key_concepts,
                configuration_examples=config_examples,
                use_cases=use_cases,
                prerequisites=prerequisites,
                related_features=related_features
            )

        except Exception as e:
            logger.error(f"Failed to extract structured content: {e}")
            return ExtractedContent()

    def _combine_source_content(self, sources: List[SourceContent]) -> str:
        """Combine content from multiple sources."""
        combined = []

        for source in sources:
            if source.content and source.status == "success":
                # Add source header
                combined.append(f"=== {source.title} ({source.url}) ===")
                combined.append(source.content[:2000])  # Limit per source
                combined.append("")

        return "\n".join(combined)

    async def _extract_key_concepts(self, content: str, feature: Feature) -> List[str]:
        """Extract key technical concepts using AI."""
        prompt = f"""
        Analyze this technical documentation for {feature.name} and extract the key concepts.
        Focus on:
        - Technical terms and technologies
        - Configuration parameters
        - API endpoints and methods
        - Related Elasticsearch features

        Return a simple list of key concepts, one per line.

        Content: {content[:4000]}
        """

        try:
            response = await self.ai_client.generate_response(prompt)
            concepts = [line.strip() for line in response.split('\n') if line.strip()]
            return concepts[:15]  # Limit to 15 concepts
        except Exception as e:
            logger.error(f"Failed to extract key concepts: {e}")
            return []

    async def _extract_configuration_examples(self, content: str, feature: Feature) -> List[CodeExample]:
        """Extract configuration examples using AI."""
        prompt = f"""
        Extract configuration examples for {feature.name} from this documentation.
        For each example, provide:
        - A clear title
        - The configuration code
        - A brief description

        Format as JSON:
        [
          {{
            "title": "Example title",
            "code": "configuration code here",
            "description": "what this example does",
            "language": "json"
          }}
        ]

        Content: {content[:4000]}
        """

        try:
            response = await self.ai_client.generate_response(prompt)
            # Parse JSON response and convert to CodeExample objects
            import json
            examples_data = json.loads(response)

            examples = []
            for ex in examples_data[:5]:  # Limit to 5 examples
                examples.append(CodeExample(
                    title=ex.get('title', ''),
                    code=ex.get('code', ''),
                    description=ex.get('description', ''),
                    language=ex.get('language', 'json')
                ))

            return examples
        except Exception as e:
            logger.error(f"Failed to extract configuration examples: {e}")
            return []

    async def _generate_use_cases(self, content: str, feature: Feature) -> List[UseCase]:
        """Generate practical use cases using AI."""
        prompt = f"""
        Based on this documentation for {feature.name}, generate 3-5 practical use cases.
        Each use case should include:
        - Title and description
        - Complexity level (beginner/intermediate/advanced)
        - Estimated implementation time

        Format as JSON:
        [
          {{
            "title": "Use case title",
            "description": "Use case description",
            "complexity": "intermediate",
            "estimated_time": "30 minutes"
          }}
        ]

        Content: {content[:4000]}
        """

        try:
            response = await self.ai_client.generate_response(prompt)
            import json
            use_cases_data = json.loads(response)

            use_cases = []
            for uc in use_cases_data[:5]:  # Limit to 5 use cases
                use_cases.append(UseCase(
                    title=uc.get('title', ''),
                    description=uc.get('description', ''),
                    complexity=uc.get('complexity', 'intermediate'),
                    estimated_time=uc.get('estimated_time', '30 minutes')
                ))

            return use_cases
        except Exception as e:
            logger.error(f"Failed to generate use cases: {e}")
            return []

    async def _extract_prerequisites(self, content: str, feature: Feature) -> List[str]:
        """Extract prerequisites using AI."""
        prompt = f"""
        Extract the prerequisites for implementing {feature.name} based on this documentation.
        Focus on:
        - Required Elasticsearch version
        - Required indices or mappings
        - Dependencies
        - Basic knowledge requirements

        Return a simple list, one prerequisite per line.

        Content: {content[:3000]}
        """

        try:
            response = await self.ai_client.generate_response(prompt)
            prerequisites = [line.strip() for line in response.split('\n') if line.strip()]
            return prerequisites[:10]  # Limit to 10 prerequisites
        except Exception as e:
            logger.error(f"Failed to extract prerequisites: {e}")
            return []

    async def _find_related_features(self, content: str, feature: Feature) -> List[str]:
        """Find related features using AI."""
        prompt = f"""
        Identify related Elasticsearch features mentioned in this documentation for {feature.name}.
        Look for features that work together or are commonly used with this feature.

        Return a simple list of feature names, one per line.

        Content: {content[:3000]}
        """

        try:
            response = await self.ai_client.generate_response(prompt)
            related = [line.strip() for line in response.split('\n') if line.strip()]
            return related[:10]  # Limit to 10 related features
        except Exception as e:
            logger.error(f"Failed to find related features: {e}")
            return []

    async def _generate_ai_insights(self, extracted_content: ExtractedContent, sources: List[SourceContent], feature: Feature) -> AIInsights:
        """Generate AI insights about the feature."""
        if not self.ai_client:
            return AIInsights()

        combined_content = self._combine_source_content(sources)

        try:
            # Generate technical summary
            technical_summary = await self._generate_technical_summary(combined_content, feature)

            # Generate business value
            business_value = await self._generate_business_value(combined_content, feature)

            # Generate presentation angles
            presentation_angles = await self._suggest_presentation_angles(extracted_content, feature)

            # Generate lab scenarios
            lab_scenarios = await self._suggest_lab_scenarios(extracted_content, feature)

            return AIInsights(
                technical_summary=technical_summary,
                business_value=business_value,
                implementation_complexity="medium",  # Could be AI-generated too
                learning_curve="moderate",
                recommended_audience=["developers", "data engineers"],
                presentation_angles=presentation_angles,
                lab_scenarios=lab_scenarios,
                content_themes=["technical", "implementation"]
            )

        except Exception as e:
            logger.error(f"Failed to generate AI insights: {e}")
            return AIInsights()

    async def _generate_technical_summary(self, content: str, feature: Feature) -> str:
        """Generate technical summary using AI."""
        prompt = f"""
        Create a technical summary for {feature.name} in 2-3 sentences.
        Focus on:
        - What it does technically
        - Key implementation details
        - Performance or architectural benefits

        Content: {content[:3000]}
        """

        try:
            return await self.ai_client.generate_response(prompt)
        except Exception as e:
            logger.error(f"Failed to generate technical summary: {e}")
            return ""

    async def _generate_business_value(self, content: str, feature: Feature) -> str:
        """Generate business value proposition using AI."""
        prompt = f"""
        Analyze the business value of {feature.name} based on this documentation.
        Focus on:
        - Cost reduction opportunities
        - Efficiency improvements
        - User experience benefits
        - Competitive advantages

        Provide a concise business value statement in 2-3 sentences.

        Content: {content[:3000]}
        """

        try:
            return await self.ai_client.generate_response(prompt)
        except Exception as e:
            logger.error(f"Failed to generate business value: {e}")
            return ""

    async def _suggest_presentation_angles(self, extracted_content: ExtractedContent, feature: Feature) -> List[PresentationAngle]:
        """Suggest presentation angles based on content."""
        angles = []

        # Technical angle if we have code examples
        if extracted_content.configuration_examples:
            angles.append(PresentationAngle(
                angle="Technical Deep Dive",
                description="Focus on implementation details and configuration",
                target_audience="technical",
                estimated_slides=8
            ))

        # Business angle if we have use cases
        if extracted_content.use_cases:
            angles.append(PresentationAngle(
                angle="Business Value Focus",
                description="Emphasize ROI and business outcomes",
                target_audience="business",
                estimated_slides=5
            ))

        return angles

    async def _suggest_lab_scenarios(self, extracted_content: ExtractedContent, feature: Feature) -> List[LabScenario]:
        """Suggest lab scenarios based on content."""
        scenarios = []

        for i, use_case in enumerate(extracted_content.use_cases[:3]):
            scenarios.append(LabScenario(
                title=f"{feature.name}: {use_case.title}",
                description=use_case.description,
                difficulty=use_case.complexity,
                duration=use_case.estimated_time,
                technologies=["Elasticsearch", "Kibana"]
            ))

        return scenarios

    async def _generate_embeddings(self, content_research: ContentResearch, feature: Feature) -> ContentEmbeddings:
        """Generate ELSER embeddings for semantic search."""
        if not self.elasticsearch_client:
            return ContentEmbeddings()

        try:
            # Prepare texts for embedding
            texts = self._prepare_embedding_texts(content_research, feature)

            embeddings = ContentEmbeddings()

            # Generate feature summary embedding
            if texts.get('feature_summary'):
                embeddings.feature_summary = await self._generate_single_embedding(
                    texts['feature_summary'], 'feature_summary'
                )

            # Generate technical content embedding
            if texts.get('technical_content'):
                embeddings.technical_content = await self._generate_single_embedding(
                    texts['technical_content'], 'technical_content'
                )

            # Generate full documentation embedding
            if texts.get('full_documentation'):
                embeddings.full_documentation = await self._generate_single_embedding(
                    texts['full_documentation'], 'full_documentation'
                )

            return embeddings

        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            return ContentEmbeddings()

    def _prepare_embedding_texts(self, content_research: ContentResearch, feature: Feature) -> Dict[str, str]:
        """Prepare optimized text for ELSER embedding."""
        texts = {}

        # Feature summary embedding text
        feature_summary = f"""
        {feature.name} - {feature.description}
        Benefits: {', '.join(feature.benefits)}
        Business value: {content_research.ai_insights.business_value}
        Target audience: {', '.join(content_research.ai_insights.recommended_audience)}
        """
        texts['feature_summary'] = feature_summary.strip()

        # Technical content embedding text
        key_concepts = ', '.join(content_research.extracted_content.key_concepts)
        use_case_titles = '; '.join([uc.title for uc in content_research.extracted_content.use_cases])
        prerequisites = ', '.join(content_research.extracted_content.prerequisites)

        technical_content = f"""
        Key concepts: {key_concepts}
        Use cases: {use_case_titles}
        Prerequisites: {prerequisites}
        Related features: {', '.join(content_research.extracted_content.related_features)}
        """
        texts['technical_content'] = technical_content.strip()

        # Full documentation embedding (truncated to model limits)
        all_content = []
        for source in content_research.primary_sources + content_research.related_sources:
            if source.content:
                all_content.append(source.content[:1000])  # Limit per source

        full_documentation = ' '.join(all_content)[:8000]  # ELSER token limit
        texts['full_documentation'] = full_documentation

        return texts

    async def _generate_single_embedding(self, text: str, field_name: str) -> ELSEREmbedding:
        """Generate a single ELSER embedding."""
        try:
            response = await self.elasticsearch_client.ml.infer_trained_model(
                model_id=self.config.embedding_model,
                docs=[{"text_field": text}]
            )

            return ELSEREmbedding(
                text=text,
                elser_embedding=response["inference_results"][0]["predicted_value"],
                model_version=self.config.embedding_model
            )

        except Exception as e:
            logger.error(f"Failed to generate embedding for {field_name}: {e}")
            return ELSEREmbedding(text=text, elser_embedding={})