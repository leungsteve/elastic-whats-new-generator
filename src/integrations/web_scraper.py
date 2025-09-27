"""
Web scraping integration for gathering additional feature context.

This module provides the WebScraper class for extracting information
from Elastic documentation and other web sources.
"""

import re
import time
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup


class WebScraper:
    """Web scraper for gathering feature documentation and context."""

    def __init__(self, delay_seconds: float = 1.0):
        """
        Initialize the web scraper.

        Args:
            delay_seconds: Delay between requests to be respectful
        """
        self.delay_seconds = delay_seconds
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Elastic What\'s New Generator Bot 1.0'
        })

    def scrape_elastic_documentation(self, url: str) -> Dict[str, Any]:
        """
        Scrape Elastic documentation page.

        Args:
            url: URL to scrape

        Returns:
            Dictionary with extracted content
        """
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract title
            title = self._extract_title(soup)

            # Extract main content
            content = self._extract_content(soup)

            # Extract benefits/features
            benefits = self._extract_benefits(soup)

            # Extract code examples
            code_examples = self._extract_code_examples(soup)

            # Sleep to be respectful
            time.sleep(self.delay_seconds)

            return {
                'title': title,
                'content': content,
                'benefits': benefits,
                'code_examples': code_examples,
                'url': url,
                'scraped_at': time.time()
            }

        except Exception as e:
            return {
                'error': str(e),
                'url': url,
                'scraped_at': time.time()
            }

    def scrape_multiple_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Scrape multiple URLs with proper delays.

        Args:
            urls: List of URLs to scrape

        Returns:
            List of scraped content dictionaries
        """
        results = []
        for url in urls:
            result = self.scrape_elastic_documentation(url)
            results.append(result)
            # Additional delay between URLs
            if len(results) < len(urls):
                time.sleep(self.delay_seconds)

        return results

    def extract_feature_context(self, feature_name: str, urls: List[str]) -> str:
        """
        Extract relevant context for a specific feature.

        Args:
            feature_name: Name of the feature to extract context for
            urls: URLs to scrape for context

        Returns:
            Consolidated context string
        """
        scraped_data = self.scrape_multiple_urls(urls)

        context_parts = []

        for data in scraped_data:
            if 'error' in data:
                continue

            # Add title if relevant
            if feature_name.lower() in data.get('title', '').lower():
                context_parts.append(f"Title: {data['title']}")

            # Add content summary
            content = data.get('content', '')
            if content and len(content) > 100:
                # Take first 500 characters as summary
                summary = content[:500] + "..." if len(content) > 500 else content
                context_parts.append(f"Content: {summary}")

            # Add benefits
            benefits = data.get('benefits', [])
            if benefits:
                context_parts.append(f"Benefits: {'; '.join(benefits[:3])}")

        return "\n\n".join(context_parts) if context_parts else ""

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        # Try multiple title selectors
        title_selectors = ['h1', 'title', '.page-title', '.title']

        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()

        return "Unknown Title"

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from the page."""
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()

        # Try to find main content areas
        content_selectors = [
            '.content',
            '.main-content',
            'main',
            'article',
            '.documentation-content',
            '.docs-content'
        ]

        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                text = content_element.get_text()
                # Clean up whitespace
                text = re.sub(r'\s+', ' ', text).strip()
                return text

        # Fallback to body content
        body = soup.find('body')
        if body:
            text = body.get_text()
            text = re.sub(r'\s+', ' ', text).strip()
            return text[:2000]  # Limit length

        return ""

    def _extract_benefits(self, soup: BeautifulSoup) -> List[str]:
        """Extract benefits or key points from the page."""
        benefits = []

        # Look for common benefit patterns
        benefit_patterns = [
            r'reduces?\s+.*?by\s+\d+%',
            r'improves?\s+.*?performance',
            r'increases?\s+.*?efficiency',
            r'saves?\s+.*?time',
            r'enables?\s+.*?scalability'
        ]

        text = soup.get_text()

        for pattern in benefit_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            benefits.extend(matches[:2])  # Limit to 2 per pattern

        # Look for bulleted lists that might contain benefits
        lists = soup.find_all(['ul', 'ol', 'div'])
        for list_element in lists:
            items = list_element.find_all('li')
            for item in items:
                item_text = item.get_text().strip()
                if len(item_text) < 200:
                    benefits.append(item_text)

        return benefits[:5]  # Return top 5 benefits

    def _extract_code_examples(self, soup: BeautifulSoup) -> List[str]:
        """Extract code examples from the page."""
        code_examples = []

        # Find code blocks
        code_selectors = ['pre code', 'code', '.code-block', '.highlight']

        for selector in code_selectors:
            code_elements = soup.select(selector)
            for element in code_elements:
                code_text = element.get_text().strip()
                if len(code_text) > 20 and len(code_text) < 500:  # Reasonable length
                    code_examples.append(code_text)

                if len(code_examples) >= 3:  # Limit to 3 examples
                    break

        return code_examples

    def scrape_documentation(self, url: str) -> Dict[str, Any]:
        """
        Scrape documentation (alias for scrape_elastic_documentation).

        Args:
            url: URL to scrape

        Returns:
            Dictionary with extracted content, with 'description' instead of 'content'
        """
        result = self.scrape_elastic_documentation(url)
        # Convert 'content' to 'description' for compatibility
        if 'content' in result:
            result['description'] = result.pop('content')
        return result

    def extract_benefits(self, html_content: str) -> List[str]:
        """
        Extract benefits from HTML content.

        Args:
            html_content: HTML content to extract benefits from

        Returns:
            List of benefits found in the content
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        return self._extract_benefits(soup)

    def validate_url(self, url: str) -> bool:
        """
        Validate if a URL is accessible.

        Args:
            url: URL to validate

        Returns:
            True if URL is accessible, False otherwise
        """
        try:
            response = self.session.head(url, timeout=10)
            return response.status_code == 200
        except Exception:
            return False