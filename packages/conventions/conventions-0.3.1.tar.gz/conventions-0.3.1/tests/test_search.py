"""
Tests for the search functionality.
"""
import unittest
from unittest.mock import patch, MagicMock
from conventions.search import search_conference


class TestSearch(unittest.TestCase):
    """Test cases for the search functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_conference_data = {
            "id": "TESTCONF",
            "title": "Test Conference",
            "url": "https://example.com/conference",
            "sessions": [
                {
                    "code": "session1",
                    "title": "SLAM Research",
                    "time": "10:00-12:00",
                    "location": "Room A",
                    "talks": [
                        {
                            "title": "Advanced SLAM Techniques",
                            "authors": "John Doe, Jane Smith",
                            "abstract": "This talk is about SLAM."
                        }
                    ]
                },
                {
                    "code": "session2",
                    "title": "Computer Vision",
                    "time": "13:00-15:00",
                    "location": "Room B",
                    "talks": [
                        {
                            "title": "Image Recognition",
                            "authors": "Alice Johnson",
                            "abstract": "This talk is about image recognition."
                        }
                    ]
                }
            ]
        }

    def test_search_matches_session_title(self):
        """Test searching for sessions by title."""
        results = search_conference(self.mock_conference_data, "slam")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "SLAM Research")
        self.assertEqual(results[0]["type"], "session")

    def test_search_matches_talk_title(self):
        """Test searching for talks by title."""
        results = search_conference(self.mock_conference_data, "advanced")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Advanced SLAM Techniques")
        self.assertEqual(results[0]["type"], "talk")

    def test_search_matches_authors(self):
        """Test searching for talks by author."""
        results = search_conference(self.mock_conference_data, "alice")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Image Recognition")
        self.assertEqual(results[0]["authors"], "Alice Johnson")

    def test_search_no_matches(self):
        """Test searching with no matches."""
        results = search_conference(self.mock_conference_data, "robotics")
        self.assertEqual(len(results), 0)


if __name__ == "__main__":
    unittest.main() 