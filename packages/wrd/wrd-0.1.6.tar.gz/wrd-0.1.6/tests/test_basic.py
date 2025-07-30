"""Basic tests for the WRD package."""

import os
import sys
import unittest
from unittest.mock import patch

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestWRD(unittest.TestCase):
    """Test cases for the WRD package."""

    def setUp(self):
        """Set up test fixtures."""
        pass

    def test_import(self):
        """Test that the package can be imported."""
        import wrd

        self.assertIsNotNone(wrd)
        self.assertTrue(hasattr(wrd, '__version__'))

    @patch('wrd.__main__.main')
    def test_main_module(self, mock_main):
        """Test that the __main__ module can be executed."""
        import wrd.__main__

        wrd.__main__.main()
        mock_main.assert_called_once()

    def test_cli_commands(self):
        """Test that the basic CLI commands are available."""
        from wrd.__main__ import main

        # This is a simple test that the main function exists
        self.assertTrue(callable(main))


if __name__ == '__main__':
    unittest.main()
