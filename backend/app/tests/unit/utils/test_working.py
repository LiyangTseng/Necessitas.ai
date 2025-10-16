"""
Working test that demonstrates pyproject.toml configuration usage.
"""

import unittest
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestWorking(unittest.TestCase):
    """Working test cases that demonstrate the setup."""

    def test_basic_math(self):
        """Test basic math operations."""
        self.assertEqual(2 + 2, 4)
        self.assertEqual(10 - 5, 5)
        self.assertEqual(3 * 4, 12)
        self.assertEqual(8 / 2, 4)

    def test_string_operations(self):
        """Test basic string operations."""
        test_string = "Hello, World!"
        self.assertEqual(len(test_string), 13)
        self.assertIn("Hello", test_string)
        self.assertIn("World", test_string)

    def test_list_operations(self):
        """Test basic list operations."""
        test_list = [1, 2, 3, 4, 5]
        self.assertEqual(len(test_list), 5)
        self.assertEqual(test_list[0], 1)
        self.assertEqual(test_list[-1], 5)
        self.assertIn(3, test_list)

    def test_dict_operations(self):
        """Test basic dictionary operations."""
        test_dict = {"name": "John", "age": 30, "city": "San Francisco"}
        self.assertEqual(len(test_dict), 3)
        self.assertEqual(test_dict["name"], "John")
        self.assertEqual(test_dict["age"], 30)
        self.assertIn("city", test_dict)

    def test_datetime_operations(self):
        """Test datetime operations."""
        from datetime import datetime, date

        now = datetime.now()
        today = date.today()

        self.assertIsInstance(now, datetime)
        self.assertIsInstance(today, date)
        self.assertGreater(now.year, 2020)
        self.assertGreaterEqual(today.month, 1)
        self.assertLessEqual(today.month, 12)

    def test_path_operations(self):
        """Test path operations."""
        from pathlib import Path

        current_file = Path(__file__)
        self.assertTrue(current_file.exists())
        self.assertEqual(current_file.suffix, ".py")
        self.assertIn("test_working", current_file.name)

    def test_import_basic_modules(self):
        """Test that we can import basic Python modules."""
        import os
        import sys
        import json
        import re
        import math
        import random

        # Test that modules are available
        self.assertTrue(hasattr(os, "path"))
        self.assertTrue(hasattr(sys, "version"))
        self.assertTrue(hasattr(json, "loads"))
        self.assertTrue(hasattr(re, "search"))
        self.assertTrue(hasattr(math, "pi"))
        self.assertTrue(hasattr(random, "random"))


if __name__ == "__main__":
    unittest.main()
