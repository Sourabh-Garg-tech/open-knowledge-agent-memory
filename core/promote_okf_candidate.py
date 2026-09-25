#!/usr/bin/env python3
"""
OKF Candidate Promotion Engine.
Lists, reviews, and promotes candidate proposals from staging/ into verified Warm Memory (concepts/).
Updates index.md, removes staging candidate, and executes an atomic Git commit.
"""

import os
import sys
import re
import argparse
import subprocess
from datetime import datetime

scripts_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, scripts_dir)
from sanitize_okf import sanitize_content

def list_candidates() -> int:
    base = os.path.dirname(scripts_dir)
    staging = os.path.join(base, "staging")
    if not os.path.isdir(staging):
        print("No staging directory found.")
        return 0

    candidates = [f for f in os.listdir(staging) if f.startswith("candidate_") and f.endswith(".md")]
    if not candidates:
        print("Staging inbox is empty (0 candidates).")
        return 0

    print(f"=== OKF Staging Candidates ({len(candidates)} Pending) ===")
    for i, c in enumerate(sorted(candidates, reverse=True), 1):
        fpath = os.path.join(staging, c)
        size = os.path.getsize(fpath)
        mtime = datetime.fromtimestamp(os.path.getmtime(fpath)).strftime("%Y-%m-%d %H:%M")
        
        # Read title from frontmatter
        title = c
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(500)
                m = re.search(r"^title:\s*(.+)$", content, re.MULTILINE)
                if m:
                    title = m.group(1).strip()
        except Exception:
            pass

        print(f"  [{i}] {c}")
        print(f"      Title: {title} | Size: {size} bytes | Created: {mtime}")
    return 0

def promote_candidate(candidate_name: str, title: str, description: str, tags: list, content: str = "", status: str = "verified", keep: bool = False) -> int:
    base = os.path.dirname(scripts_dir)
    staging = os.path.join(base, "staging")
    concepts = os.path.join(base, "concepts")
    index_file = os.path.join(base, "index.md")

    # Locate candidate file
    candidate_path = candidate_name
    if not os.path.isfile(candidate_path):
        candidate_path = os.path.join(staging, candidate_name)
    if not os.path.isfile(candidate_path):
        # Try matching partial filename
        matches = [f for f in os.listdir(staging) if candidate_name in f and f.endswith(".md")]
        if matches:
            candidate_path = os.path.join(staging, matches[0])
        else:
            print(f"ERROR: Candidate file not found: {candidate_name}", file=sys.stderr)
            return 1

    # Read candidate file content if custom content not provided
    if not content:
        with open(candidate_path, "r", encoding="utf-8", errors="ignore") as f:
            raw_body = f.read()
            # Strip frontmatter if present
            body_match = re.search(r"^---\s*[\r\n]+.*?[\r\n]+---\s*[\r\n]+(.*)$", raw_body, re.DOTALL)
            content = body_match.group(1).strip() if body_match else raw_body.strip()

    slug = re.sub(r'[^a-z0-9]+', '_', title.lower()).strip('_')
    target_node = os.path.join(concepts, f"{slug}.md")

    # Warm Memory cap check
    warm_nodes = [f for f in os.listdir(concepts) if f.endswith(".md")]
    if len(warm_nodes) >= 50 and not os.path.exists(target_node):
        print("WARNING: Warm Memory cap (50 nodes) reached. Running auto-prune before promotion...", file=sys.stderr)
        prune_script = os.path.join(scripts_dir, "prune_okf_memory.py")
        if os.path.exists(prune_script):
            subprocess.run([sys.executable, prune_script], capture_output=True)

    date_str = datetime.now().strftime("%Y-%m-%d")
    tag_str = ", ".join(tags) if tags else "promoted, concept"
    trust_score = 3 if status == "verified" else (5 if status == "stable" else 2)

    template = f"""---
type: concept
title: {title}
description: {description}
status: {status}
trust_score: {trust_score}
tags: [{tag_str}]
created_at: {date_str}
updated_at: {date_str}
anonymized: true
sources: [dream-synthesis, candidate-promotion]
---

# {title}

## Summary
{description}

## Verified Architecture & Implementation Guidelines
{content}

## Verification & Trust Record
* **Promotion Date:** Promoted from `{os.path.basename(candidate_path)}` on {date_str}.
* **Status:** `{status}` (Trust Score: {trust_score}).

## References & Cross-Links
* [Master Index](../index.md)
"""

    cleaned = sanitize_content(template)
    with open(target_node, "w", encoding="utf-8") as f:
        f.write(cleaned)
    print(f"Promoted concept node created: {target_node}")

    # Update index.md
    if os.path.isfile(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            idx = f.read()
        rel_link = f"./concepts/{slug}.md"
        if rel_link not in idx:
            new_entry = f"* [{title}]({rel_link}) — {description}\n"
            pattern = r"(## 1\. Warm Memory Graph \(Active Concepts\)\r?\n)(.*?)((\r?\n## |\Z))"
            match = re.search(pattern, idx, re.DOTALL)
            if match:
                replacement = match.group(1) + match.group(2) + new_entry + match.group(3)
                updated_idx = idx[:match.start()] + replacement + idx[match.end():]
                with open(index_file, "w", encoding="utf-8") as f:
                    f.write(updated_idx)
                print(f"Updated index.md with link: {slug}")

    # Delete or keep candidate file
    if not keep:
        try:
            os.remove(candidate_path)
            print(f"Removed staging candidate: {candidate_path}")
        except Exception:
            pass

    # Atomic Git commit
    try:
        subprocess.run(["git", "-C", base, "add", f"concepts/{slug}.md", "index.md", "staging/"], capture_output=True)
        subprocess.run(["git", "-C", base, "commit", "-m", f"feat(promotion): promote candidate to {slug}"], capture_output=True)
        print("Committed promotion to .okf_knowledge repository.")
    except Exception as e:
        print(f"Warning: git commit failed: {e}", file=sys.stderr)

    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Review and promote OKF staging candidates.")
    parser.add_argument("--list", action="store_true", help="List all pending candidates in staging/")
    parser.add_argument("--candidate", help="Candidate filename or pattern to promote")
    parser.add_argument("--title", help="Title for the promoted concept")
    parser.add_argument("--description", default="Promoted architectural concept.", help="Summary description")
    parser.add_argument("--content", default="", help="Detailed markdown content or distilled guidelines")
    parser.add_argument("--tags", nargs="+", default=["promoted"], help="Tags")
    parser.add_argument("--status", default="verified", choices=["draft", "verified", "stable"])
    parser.add_argument("--keep", action="store_true", help="Do not delete candidate from staging/")
    args = parser.parse_args()

    if args.list or not args.candidate:
        sys.exit(list_candidates())
    else:
        title = args.title or "Promoted Concept"
        sys.exit(promote_candidate(args.candidate, title, args.description, args.tags, args.content, args.status, args.keep))
