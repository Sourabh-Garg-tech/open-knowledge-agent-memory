#!/usr/bin/env python3
"""
Unit tests for Shannon Entropy calculation and sanitization.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "core")))
from sanitize_okf import calculate_shannon_entropy, sanitize_content

class TestShannonEntropy(unittest.TestCase):
    def test_zero_entropy(self):
        self.assertEqual(calculate_shannon_entropy(""), 0.0)
        self.assertEqual(calculate_shannon_entropy("aaaaaaaaaa"), 0.0)

    def test_prose_entropy_range(self):
        text = "This is a standard English sentence describing the software architecture and system conventions."
        entropy = calculate_shannon_entropy(text)
        self.assertTrue(2.5 <= entropy <= 4.2, f"Prose entropy {entropy} out of expected range")

    def test_random_key_entropy(self):
        high_entropy_key = "dK3#m9!xP7$qR2*vL5^tY8@bN1&jM4~"
        entropy = calculate_shannon_entropy(high_entropy_key)
        self.assertTrue(entropy >= 4.3, f"Expected high entropy, got {entropy}")

    def test_known_token_sanitization(self):
        content = "My token is ghp_123456789012345678901234567890123456 and hf_1234567890123456789012345678901234"
        sanitized = sanitize_content(content)
        self.assertNotIn("ghp_", sanitized)
        self.assertNotIn("hf_", sanitized)
        self.assertIn("<GITHUB_PAT_REDACTED>", sanitized)
        self.assertIn("<HF_TOKEN_REDACTED>", sanitized)

    def test_assignment_entropy_sanitization(self):
        content = 'api_key = "dK3m9xP7qR2vL5tY8bN1jM4wZ0kQ="'
        sanitized = sanitize_content(content)
        self.assertIn("<HIGH_ENTROPY_SECRET_REDACTED>", sanitized)

    def test_url_and_commit_sha_whitelisting(self):
        url = "https://github.com/organization/project-name-example/tree/main"
        commit_sha = "e4d909c290d0fb1ca068ffaddf22cbd0adddef12"
        markdown_link = "docs/api_design_standards.md"

        content = f"See {url} at commit {commit_sha} in {markdown_link}"
        sanitized = sanitize_content(content)

        self.assertIn(url, sanitized, "URL was incorrectly redacted")
        self.assertIn(commit_sha, sanitized, "Commit SHA was incorrectly redacted")
        self.assertIn(markdown_link, sanitized, "Markdown path was incorrectly redacted")

if __name__ == "__main__":
    unittest.main()
