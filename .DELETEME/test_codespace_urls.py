#!/usr/bin/env python
"""
Test runner for verifying GitHub Codespaces URL behavior.

This script runs tests to verify that the API status endpoints
work correctly without port doubling in GitHub Codespaces.
"""
import os
import sys
import unittest
import json
from tests.integration.api.test_status_url import TestCodespacesUrls

if __name__ == "__main__":
    print("===============================================")
    print("🧪 Running Codespaces URL Tests")
    print("===============================================")

    # Check if running in Codespaces
    codespace_name = os.environ.get("CODESPACE_NAME")
    if codespace_name:
        print(f"✅ Running in GitHub Codespaces: {codespace_name}")
        print(f"Test URL: https://{codespace_name}-8080.app.github.dev/api/v1/status")
    else:
        print("⚠️  Not running in GitHub Codespaces - some tests will be skipped")
    print("===============================================\n")

    # Run the tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestCodespacesUrls)
    result = unittest.TextTestRunner(verbosity=2).run(suite)

    # Print summary
    print("\n===============================================")
    print(f"Tests run: {result.testsRun}")
    print(f"Errors: {len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Skipped: {len(result.skipped)}")
    print("===============================================")

    # Exit with appropriate code
    sys.exit(not result.wasSuccessful())
