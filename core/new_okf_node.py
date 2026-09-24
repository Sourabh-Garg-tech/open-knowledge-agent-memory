#!/usr/bin/env python3
"""
OKF Concept Node Generator with automatic sanitization and trust metadata.
"""

import os
import sys
import re
import datetime
import argparse

scripts_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, scripts_dir)
from sanitize_okf import sanitize_content

def create_node(title: str, description: str, tags: list, status: str = "draft"):
    base = os.path.dirname(scripts_dir)
    concepts_dir = os.path.join(base, "concepts")
    os.makedirs(concepts_dir, exist_ok=True)

    slug = re.sub(r'[^a-z0-9]+', '_', title.lower()).strip('_')
    target_file = os.path.join(concepts_dir, f"{slug}.md")

    if os.path.exists(target_file):
        print(f"ERROR: Concept node already exists: {target_file}", file=sys.stderr)
        return 1

    date_str = datetime.date.today().isoformat()
    tags_str = ", ".join(tags) if tags else "general"

    template = f"""---
type: concept
title: {title}
description: {description}
status: {status}
trust_score: 1
tags: [{tags_str}]
created_at: {date_str}
updated_at: {date_str}
anonymized: true
sources: []
---

# {title}

## Summary
{description}

## Verified Guidelines & Code Patterns
<!-- Add actionable code patterns or rules here -->

## Verification & Test Record
* **Status History:** {status} created on {date_str}.
* **Verification Criteria:** <!-- What test confirms this concept? -->

## References & Cross-Links
* [Master Index](../index.md)
"""

    cleaned = sanitize_content(template)
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(cleaned)

    print(f"SUCCESS: Created new OKF node: {target_file}")
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a new OKF concept node.")
    parser.add_argument("title", help="Title of the concept")
    parser.add_argument("description", help="One-line summary")
    parser.add_argument("--tags", nargs="+", default=["general"], help="List of tags")
    parser.add_argument("--status", default="draft", choices=["candidate", "draft", "verified", "stable"])
    args = parser.parse_args()

    sys.exit(create_node(args.title, args.description, args.tags, args.status))
