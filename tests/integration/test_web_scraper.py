import pytest
from unittest.mock import patch, Mock
from src.integrations.web_scraper import WebScraper

class TestWebScraper:
    
    def test_scrape_elastic_documentation(self):
        """Test scraping Elastic documentation"""
        # Mock response
        mock_response = Mock()
        mock_response.text = """
        <html>
            <head><title>Better Binary Quantization</title></head>
            <body>
                <h1>BBQ Overview</h1>
                <p>BBQ reduces memory usage by 95%...</p>
            </body>
        </html>
        """
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None

        scraper = WebScraper()
        scraper.session.get = Mock(return_value=mock_response)

        content = scraper.scrape_documentation("https://elastic.co/docs/bbq")

        assert content["title"] == "BBQ Overview"  # H1 is extracted as title
        assert "95%" in content["description"]
        assert content["benefits"]
        assert "reduces memory usage by 95%" in content["benefits"]
    
    def test_extract_feature_benefits(self):
        """Test benefit extraction from documentation"""
        html_content = """
        <div class="benefits">
            <li>95% memory reduction</li>
            <li>Improved ranking quality</li>
            <li>Faster query performance</li>
        </div>
        """
        
        scraper = WebScraper()
        benefits = scraper.extract_benefits(html_content)
        
        assert "95% memory reduction" in benefits
        assert "Improved ranking quality" in benefits
        assert len(benefits) == 3