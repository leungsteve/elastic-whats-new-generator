import pytest
from unittest.mock import patch, Mock
from src.integrations.web_scraper import WebScraper

class TestWebScraper:
    
    @patch('requests.get')
    def test_scrape_elastic_documentation(self, mock_get):
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
        mock_get.return_value = mock_response
        
        scraper = WebScraper()
        content = scraper.scrape_documentation("https://elastic.co/docs/bbq")
        
        assert content["title"] == "Better Binary Quantization"
        assert "95%" in content["description"]
        assert content["benefits"]
    
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