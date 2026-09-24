#!/usr/bin/env python3
"""
OKF Tiered Memory Pruning & Staging Governance Engine.
1. Moves stale Warm concepts (> 45 days untouched) to Cold Archive.
2. Auto-purges unreviewed candidate notes in staging/ (> 14 days TTL) to eliminate review fatigue.
"""

import os
import sys
import time
import shutil
import argparse

def prune_memory(stale_days=45, staging_ttl_days=14, dry_run=False):
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    base = os.path.dirname(scripts_dir)
    concepts_dir = os.path.join(base, "concepts")
    archive_dir = os.path.join(base, "archive", "concepts")
    staging_dir = os.path.join(base, "staging")

    os.makedirs(archive_dir, exist_ok=True)
    os.makedirs(staging_dir, exist_ok=True)

    now = time.time()
    stale_threshold = now - (stale_days * 86400)
    staging_threshold = now - (staging_ttl_days * 86400)

    # 1. Warm Memory -> Cold Archive (45-Day TTL)
    anchors = {"system_profile.md", "dev_conventions.md"}
    archived_count = 0

    if os.path.isdir(concepts_dir):
        for fname in os.listdir(concepts_dir):
            if not fname.endswith(".md") or fname in anchors:
                continue
            fpath = os.path.join(concepts_dir, fname)
            mtime = os.path.getmtime(fpath)
            if mtime < stale_threshold:
                days_old = int((now - mtime) / 86400)
                print(f"[Cold Tiering] Stale concept detected: {fname} ({days_old} days old)")
                if not dry_run:
                    dest = os.path.join(archive_dir, fname)
                    shutil.move(fpath, dest)
                    archived_count += 1

    # 2. Staging Inbox Auto-TTL Purge (14-Day TTL to prevent review fatigue)
    purged_staging_count = 0
    if os.path.isdir(staging_dir):
        for fname in os.listdir(staging_dir):
            if not fname.endswith(".md"):
                continue
            fpath = os.path.join(staging_dir, fname)
            mtime = os.path.getmtime(fpath)
            if mtime < staging_threshold:
                days_old = int((now - mtime) / 86400)
                print(f"[Staging Purge] Candidate expired (> {staging_ttl_days}d TTL): {fname}")
                if not dry_run:
                    os.remove(fpath)
                    purged_staging_count += 1

    print(f"\nPruning Summary:")
    print(f"  • Warm -> Cold Archived: {archived_count} node(s)")
    print(f"  • Staging Candidates Purged: {purged_staging_count} node(s)")
    if dry_run:
        print("  • (Dry Run Mode: No files were actually moved or deleted)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prune stale OKF memory nodes and expired staging candidates.")
    parser.add_argument("--stale-days", type=int, default=45, help="Days before concept is moved to Cold Archive (default: 45)")
    parser.add_argument("--staging-ttl", type=int, default=14, help="Days before unreviewed candidate in staging is purged (default: 14)")
    parser.add_argument("--dry-run", action="store_true", help="Simulate pruning without modifying files")
    args = parser.parse_args()

    prune_memory(stale_days=args.stale_days, staging_ttl_days=args.staging_ttl, dry_run=args.dry_run)
