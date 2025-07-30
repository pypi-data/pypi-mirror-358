"""Tests for agents."""

import unittest
from unittest.mock import MagicMock
from agentscraper.agent.TitleAgent import TitleAgent

class TestTitleAgent(unittest.TestCase):
    """Test cases for TitleAgent."""
    
    def test_title_extraction(self):
        """Test title extraction."""
        # Mock LLM provider
        mock_provider = MagicMock()
        mock_provider.get_completion.return_value = '["Title 1", "Title 2", "Title 3"]'
        
        # Create agent
        agent = TitleAgent(mock_provider)
        
        # Test
        result = agent.process("<html>Test content</html>")
        
        # Assert
        self.assertEqual(len(result["titles"]), 3)
        self.assertEqual(result["count"], 3)
        self.assertEqual(result["titles"][0], "Title 1")
        
        # Verify LLM was called
        mock_provider.get_completion.assert_called_once()

if __name__ == '__main__':
    unittest.main()