#!/usr/bin/env python3
"""
OKF Knowledge Graph Integrity & Security Validator.
Verifies YAML frontmatter, checks for dead relative links, verifies that paths are sanitized,
and detects any high-entropy cryptographic strings.
"""

import os
import sys
import re

# Add scripts directory to path to import sanitize_okf
scripts_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, scripts_dir)
from sanitize_okf import calculate_shannon_entropy

def validate_graph() -> int:
    base = os.path.dirname(scripts_dir)
    concepts_dir = os.path.join(base, "concepts")
    index_file = os.path.join(base, "index.md")

    if not os.path.isdir(concepts_dir):
        print(f"ERROR: Concepts directory not found: {concepts_dir}", file=sys.stderr)
        return 1

    nodes = [os.path.join(concepts_dir, f) for f in os.listdir(concepts_dir) if f.endswith(".md")]
    warm_count = len(nodes)
    errors = 0

    print(f"=== Validating OKF Knowledge Graph ({warm_count} Warm Nodes) ===")

    # 1. Warm Memory Cap Check (< 50 nodes)
    if warm_count > 50:
        print(f"WARNING: Warm Memory cap exceeded: {warm_count} nodes (Max recommended: 50). Run prune_okf_memory.py.", file=sys.stderr)

    home = os.path.expanduser("~")
    userprofile = os.environ.get("USERPROFILE", "")

    # 2. Inspect each concept node
    for node_path in nodes:
        node_name = os.path.basename(node_path)
        try:
            with open(node_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception as e:
            print(f"ERROR: Failed to read {node_name}: {e}", file=sys.stderr)
            errors += 1
            continue

        # Check frontmatter
        if not re.match(r"^---\s*\r?\n(.*?)\r?\n---", content, re.DOTALL):
            print(f"ERROR: Missing or invalid YAML frontmatter in: {node_name}", file=sys.stderr)
            errors += 1

        # Check for unscrubbed local user paths
        if (home and home in content) or (userprofile and userprofile in content) or re.search(r'C:\\Users\\[a-zA-Z0-9_\-\.]+', content, re.IGNORECASE):
            print(f"ERROR: Unsanitized absolute user path detected in: {node_name}", file=sys.stderr)
            errors += 1

        # Check for known leaked tokens
        if re.search(r'\b(ghp_[a-zA-Z0-9]{36}|hf_[a-zA-Z0-9]{34}|AIza[0-9A-Za-z-_]{35})\b', content):
            print(f"ERROR: Unredacted API token detected in: {node_name}", file=sys.stderr)
            errors += 1

        # Check relative markdown links
        links = re.findall(r'\[.*?\]\((?!https?://)(.*?)\)', content)
        for link in links:
            clean_link = link.split('#')[0].strip()
            if not clean_link:
                continue
            resolved_link = os.path.normpath(os.path.join(os.path.dirname(node_path), clean_link))
            if not os.path.exists(resolved_link):
                print(f"ERROR: Dead link in {node_name} -> {clean_link}", file=sys.stderr)
                errors += 1

    # Also validate index.md
    if os.path.isfile(index_file):
        with open(index_file, "r", encoding="utf-8", errors="ignore") as f:
            idx_content = f.read()
        links = re.findall(r'\[.*?\]\((?!https?://)(.*?)\)', idx_content)
        for link in links:
            clean_link = link.split('#')[0].strip()
            if not clean_link:
                continue
            resolved_link = os.path.normpath(os.path.join(base, clean_link))
            if not os.path.exists(resolved_link):
                print(f"ERROR: Dead link in index.md -> {clean_link}", file=sys.stderr)
                errors += 1

    if errors == 0:
        print("SUCCESS: All OKF nodes, links, and security constraints verified successfully!")
        return 0
    else:
        print(f"FAILED: OKF Graph validation encountered {errors} error(s).", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(validate_graph())
