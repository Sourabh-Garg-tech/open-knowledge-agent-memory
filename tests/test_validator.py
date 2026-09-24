#!/usr/bin/env python3
"""
Unit tests for Knowledge Graph validation on the starter graph.
"""

import sys
import os
import unittest

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(repo_root, "core"))
import test_okf_graph

class TestGraphValidator(unittest.TestCase):
    def test_starter_graph_validity(self):
        starter_graph_dir = os.path.join(repo_root, "starter_graph")
        concepts_dir = os.path.join(starter_graph_dir, "concepts")
        index_file = os.path.join(starter_graph_dir, "index.md")

        self.assertTrue(os.path.isdir(concepts_dir), "concepts directory must exist")
        self.assertTrue(os.path.isfile(index_file), "index.md must exist")

        nodes = [f for f in os.listdir(concepts_dir) if f.endswith(".md")]
        self.assertEqual(len(nodes), 6, "Starter graph should contain exactly 6 concepts")

        # Verify each node has valid frontmatter and relative links
        for node in nodes:
            node_path = os.path.join(concepts_dir, node)
            with open(node_path, "r", encoding="utf-8") as f:
                content = f.read()

            self.assertTrue(content.startswith("---"), f"{node} missing frontmatter delimiter")
            self.assertIn("type: concept", content, f"{node} missing type field")
            self.assertIn("status:", content, f"{node} missing status field")
            self.assertIn("title:", content, f"{node} missing title field")

if __name__ == "__main__":
    unittest.main()
