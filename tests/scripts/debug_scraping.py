#!/usr/bin/env python3
"""
Debug script to test web scraping functionality.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def test_manual_scraping():
    """Test manual scraping to understand the issue."""
    url = "https://www.elastic.co/guide/en/elasticsearch/reference/current/knn-search.html"
    print(f"🔍 Testing manual scraping of: {url}")
    print("=" * 80)

    try:
        # Test basic request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }

        print("1. Making HTTP request...")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        print(f"✅ Response status: {response.status_code}")
        print(f"✅ Content length: {len(response.text)} characters")

        # Test HTML parsing
        print("\n2. Parsing HTML with BeautifulSoup...")
        soup = BeautifulSoup(response.text, 'html.parser')

        # Check title
        title_element = soup.find('title')
        if title_element:
            title = title_element.get_text().strip()
            print(f"✅ Page title: {title}")
        else:
            print("❌ No title found")

        # Test different selectors for elastic.co
        selectors_to_test = [
            ".content",
            ".main",
            "#main-content",
            "main",
            "article",
            ".guide-content",
            ".guide-section",
            ".section"
        ]

        print("\n3. Testing content selectors...")
        for selector in selectors_to_test:
            content_element = soup.select_one(selector)
            if content_element:
                text = content_element.get_text()
                text_length = len(text.strip())
                print(f"✅ Selector '{selector}': {text_length} chars")
                if text_length > 100:
                    print(f"   Preview: {text.strip()[:200]}...")
            else:
                print(f"❌ Selector '{selector}': No content found")

        # Test fallback to body
        print("\n4. Testing fallback to body...")
        body = soup.find('body')
        if body:
            body_text = body.get_text()
            body_length = len(body_text.strip())
            print(f"✅ Body content: {body_length} chars")
            if body_length > 100:
                print(f"   Preview: {body_text.strip()[:200]}...")
        else:
            print("❌ No body element found")

        return True

    except Exception as e:
        print(f"❌ Scraping failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_service_scraping():
    """Test using the actual content research service."""
    print("\n🔬 Testing with ContentResearchService")
    print("=" * 80)

    try:
        from src.integrations.content_research_service import ContentResearchService, ContentResearchConfig

        # Create service with debug config
        config = ContentResearchConfig()
        service = ContentResearchService(config)

        url = "https://www.elastic.co/guide/en/elasticsearch/reference/current/knn-search.html"
        print(f"Testing URL: {url}")

        # Test URL validation
        is_allowed = service._is_url_allowed(url)
        print(f"✅ URL allowed: {is_allowed}")

        # Test domain extraction
        domain = urlparse(url).netloc
        print(f"✅ Domain: {domain}")

        # Check domain rules
        domain_rules = getattr(service.config, 'domain_rules', service.domain_rules if hasattr(service, 'domain_rules') else {})
        print(f"✅ Domain rules available: {list(domain_rules.keys())}")

        if domain in domain_rules:
            content_selectors = domain_rules[domain].get('content_selectors', [])
            print(f"✅ Content selectors for {domain}: {content_selectors}")

        # Test the actual scraping method
        print("\nTesting _scrape_url method...")
        source_content = await service._scrape_url(url, "manual_test", "documentation")

        if source_content:
            print(f"✅ Scraped successfully!")
            print(f"   Title: {source_content.title}")
            print(f"   Content length: {source_content.word_count} words")
            print(f"   Preview: {source_content.content[:200]}...")
        else:
            print("❌ Scraping returned None")

        return source_content is not None

    except Exception as e:
        print(f"❌ Service scraping failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Web Scraping Debug Tool")
    print("==========================\n")

    success1 = test_manual_scraping()
    success2 = asyncio.run(test_service_scraping())

    if success1 and success2:
        print("\n🎉 All scraping tests passed!")
    else:
        print("\n❌ Some scraping tests failed.")