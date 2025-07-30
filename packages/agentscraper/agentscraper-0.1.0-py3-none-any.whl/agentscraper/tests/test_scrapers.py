"""Tests for scrapers."""

import unittest
from unittest.mock import patch, MagicMock
from agentscraper.scrapers.GoogleScraper import GoogleScraper

class TestGoogleScraper(unittest.TestCase):
    """Test cases for GoogleScraper."""
    
    def setUp(self):
        """Set up test environment."""
        self.scraper = GoogleScraper(user_agent="AgentScraper/Test", timeout=10)
        
    @patch('agentscraper.scrapers.GoogleScraper.requests.get')
    def test_search(self, mock_get):
        """Test search method."""
        # Mock response
        mock_response = MagicMock()
        mock_response.text = "<html>Test HTML</html>"
        mock_get.return_value = mock_response
        
        # Test
        result = self.scraper.search("test query")
        
        # Assert
        self.assertEqual(result, "<html>Test HTML</html>")
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertTrue("test+query" in args[0])
        self.assertEqual(kwargs["timeout"], 10)

if __name__ == '__main__':
    unittest.main()