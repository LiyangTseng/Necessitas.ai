"""
Basic test to verify the test setup is working.
"""

import unittest
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# class TestBasic(unittest.TestCase):
#     """Basic test cases to verify test setup."""

#     def test_imports(self):
#         """Test that we can import basic modules."""
#         try:
#             # Test basic Python imports
#             import os
#             import sys
#             import unittest
#             from datetime import datetime

#             # Test that we can import our modules
#             from backend.app.services.job_recommender import JobRecommender
#             from backend.app.services.resume_parser import ResumeParser

#             self.assertTrue(True, "All imports successful")
#         except ImportError as e:
#             self.fail(f"Import failed: {e}")

#     def test_basic_math(self):
#         """Test basic math operations."""
#         self.assertEqual(2 + 2, 4)
#         self.assertEqual(10 - 5, 5)
#         self.assertEqual(3 * 4, 12)
#         self.assertEqual(8 / 2, 4)

#     def test_string_operations(self):
#         """Test basic string operations."""
#         test_string = "Hello, World!"
#         self.assertEqual(len(test_string), 13)
#         self.assertIn("Hello", test_string)
#         self.assertIn("World", test_string)

#     def test_list_operations(self):
#         """Test basic list operations."""
#         test_list = [1, 2, 3, 4, 5]
#         self.assertEqual(len(test_list), 5)
#         self.assertEqual(test_list[0], 1)
#         self.assertEqual(test_list[-1], 5)
#         self.assertIn(3, test_list)

#     def test_dict_operations(self):
#         """Test basic dictionary operations."""
#         test_dict = {"name": "John", "age": 30, "city": "San Francisco"}
#         self.assertEqual(len(test_dict), 3)
#         self.assertEqual(test_dict["name"], "John")
#         self.assertEqual(test_dict["age"], 30)
#         self.assertIn("city", test_dict)

#     def test_datetime_operations(self):
#         """Test datetime operations."""
#         from datetime import datetime, date

#         now = datetime.now()
#         today = date.today()

#         self.assertIsInstance(now, datetime)
#         self.assertIsInstance(today, date)
#         self.assertGreater(now.year, 2020)
#         self.assertGreaterEqual(today.month, 1)
#         self.assertLessEqual(today.month, 12)


# if __name__ == '__main__':
#     unittest.main()
