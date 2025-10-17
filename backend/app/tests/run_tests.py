#!/usr/bin/env python3
"""
Test runner for necessitas.ai tests.

This script runs all unit tests and provides detailed output.

Usage:
    # Set PYTHONPATH and run tests
    export PYTHONPATH=/path/to/company_radar/backend/app:$PYTHONPATH
    python tests/run_tests.py

    # Or run from project root
    cd /path/to/company_radar/backend/app
    export PYTHONPATH=.:$PYTHONPATH
    python tests/run_tests.py
"""

import os
import sys
import unittest
import logging


def is_test_module(filename):
    return filename.startswith('test') and filename.endswith('.py')

def load_tests(loader, standard_tests, pattern):
    # Get the tests directory path
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    test_dirs = [
        # 'unit/agents',
        'unit/services',
        'unit/utils'
        # 'integration',
    ]
    suite = unittest.TestSuite()
    for test_dir in test_dirs:
        full_test_dir = os.path.join(tests_dir, test_dir)
        if os.path.exists(full_test_dir):
            for dirpath, dirnames, filenames in os.walk(full_test_dir):
                for filename in filenames:
                    if is_test_module(filename):
                        # Create a module name by removing the base directory and converting the path to a module path
                        module_path = os.path.relpath(os.path.join(dirpath, filename), full_test_dir)
                        module_name = '.'.join(os.path.splitext(module_path)[0].split(os.sep))
                        sys.path.insert(0, full_test_dir)  # Ensure the test directory is in the sys.path
                        module = __import__(module_name, fromlist=[''])
                        suite.addTests(loader.loadTestsFromModule(module))
    return suite

if __name__ == '__main__':
    # Disable all logging during tests
    logging.disable(logging.CRITICAL)
    loader = unittest.TestLoader()
    loader.loadTestsFromNames = load_tests
    unittest.main(testLoader=loader, verbosity=2)
