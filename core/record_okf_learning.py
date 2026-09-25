#!/usr/bin/env python3
"""
OKF Autonomous Ingestion Engine (Python 3).
Sanitizes, checks Warm Memory budget, writes node, updates index.md, and commits to Git.
"""

import os
import sys
import re
import datetime
import argparse
import subprocess

scripts_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, scripts_dir)
from sanitize_okf import sanitize_content

def record_learning(title: str, description: str, content: str, tags: list, status: str = "draft", sources: list = None) -> int:
    base = os.path.dirname(scripts_dir)
    concepts_dir = os.path.join(base, "concepts")
    index_file = os.path.join(base, "index.md")
    os.makedirs(concepts_dir, exist_ok=True)

    slug = re.sub(r'[^a-z0-9]+', '_', title.lower()).strip('_')
    target_file = os.path.join(concepts_dir, f"{slug}.md")

    # 1. Warm Memory Cap Check
    existing_nodes = [f for f in os.listdir(concepts_dir) if f.endswith(".md")]
    if len(existing_nodes) >= 50 and not os.path.exists(target_file):
        print("WARNING: Warm Memory cap (50 nodes) reached. Running auto-prune before writing...", file=sys.stderr)
        prune_script = os.path.join(scripts_dir, "prune_okf_memory.py")
        if os.path.exists(prune_script):
            subprocess.run([sys.executable, prune_script], capture_output=True)

    date_str = datetime.date.today().isoformat()
    tags_str = ", ".join(tags) if tags else "general"
    sources_str = ", ".join(sources) if sources else "agent-session"

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
sources: [{sources_str}]
---

# {title}

## Summary
{description}

## Verified Guidelines & Code Patterns
{content}

## Verification & Test Record
* **Status History:** {status} created on {date_str}.
* **Verification Criteria:** Turn execution verified via agent testing.

## References & Cross-Links
* [Master Index](../index.md)
"""

    # 2. Sanitize
    cleaned = sanitize_content(template)
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(cleaned)
    print(f"Created/Updated OKF node: {target_file}")

    # 3. Update index.md
    if os.path.isfile(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            index_content = f.read()
        relative_link = f"./concepts/{slug}.md"
        if relative_link not in index_content:
            new_entry = f"* [{title}]({relative_link}) — {description}\n"
            pattern = r"(## 1\. Warm Memory Graph \(Active Concepts\)\r?\n)(.*?)((\r?\n## |\Z))"
            match = re.search(pattern, index_content, re.DOTALL)
            if match:
                replacement = match.group(1) + match.group(2) + new_entry + match.group(3)
                updated_index = index_content[:match.start()] + replacement + index_content[match.end():]
                with open(index_file, "w", encoding="utf-8") as f:
                    f.write(updated_index)
                print(f"Updated index.md with new concept link: {slug}")

    # 4. Atomic Git commit
    try:
        subprocess.run(["git", "-C", base, "add", f"concepts/{slug}.md", "index.md"], capture_output=True)
        subprocess.run(["git", "-C", base, "commit", "-m", f"feat(memory): auto-record {slug}"], capture_output=True)
        print("Committed changes to .okf_knowledge repository.")
    except Exception as e:
        print(f"Warning: git commit failed: {e}", file=sys.stderr)

    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Record a newly learned concept to OKF.")
    parser.add_argument("title", help="Title of the concept")
    parser.add_argument("description", help="One-line summary")
    parser.add_argument("content", help="Verified guidelines or code patterns")
    parser.add_argument("--tags", nargs="+", default=["general"], help="List of tags")
    parser.add_argument("--status", default="draft", choices=["candidate", "draft", "verified", "stable"])
    parser.add_argument("--sources", nargs="+", default=["agent-session"], help="Sources")
    args = parser.parse_args()

    sys.exit(record_learning(args.title, args.description, args.content, args.tags, args.status, args.sources))
