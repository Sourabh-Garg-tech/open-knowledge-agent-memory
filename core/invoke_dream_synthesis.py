#!/usr/bin/env python3
"""
OKF Unified Dream Synthesis & Autonomous Distillation Engine.
Scans active Git repositories and Antigravity conversation sessions (last 24h),
extracts goals, tool executions, and resolutions, sanitizes with Shannon Entropy,
and autonomously distills project learnings into Warm Memory (concepts/) and staging.
"""

import os
import sys
import json
import re
import subprocess
from datetime import datetime

scripts_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, scripts_dir)
from sanitize_okf import sanitize_content

def harvest_git_commits(scan_root: str, hours: int = 24) -> list:
    """Scans scan_root for git repositories with commits in the last N hours."""
    results = []
    if not os.path.isdir(scan_root):
        return results

    cutoff_str = f"{hours} hours ago"
    for root, dirs, files in os.walk(scan_root):
        dirs[:] = [d for d in dirs if d not in ("node_modules", ".venv", "venv", "__pycache__", ".git")]
        if ".git" in os.listdir(root):
            repo_name = os.path.basename(root)
            try:
                cmd = ["git", "-C", root, "log", f"--since={cutoff_str}", "--format=%h - %s (%cd)", "--date=short"]
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                commits = [c.strip() for c in res.stdout.splitlines() if c.strip()]
                if commits:
                    results.append({"repo": repo_name, "path": root, "commits": commits})
            except Exception:
                continue
    return results

def harvest_antigravity_transcripts(brain_dirs: list, hours: int = 24) -> list:
    """Scans Antigravity brain directories for transcripts modified in the last N hours."""
    results = []
    cutoff_time = datetime.now().timestamp() - (hours * 3600)

    for bdir in brain_dirs:
        if not os.path.isdir(bdir):
            continue
        for root, dirs, files in os.walk(bdir):
            if "transcript.jsonl" in files:
                tpath = os.path.join(root, "transcript.jsonl")
                try:
                    mtime = os.path.getmtime(tpath)
                    if mtime >= cutoff_time:
                        conv_id = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(tpath))))
                        user_requests = []
                        files_touched = set()

                        with open(tpath, "r", encoding="utf-8", errors="ignore") as f:
                            for line in f:
                                try:
                                    item = json.loads(line)
                                    itype = item.get("type", "")
                                    if itype == "USER_INPUT":
                                        content = item.get("content", "")
                                        if content:
                                            clean = content.replace("<USER_REQUEST>", "").replace("</USER_REQUEST>", "").strip()
                                            clean = clean.split("<ADDITIONAL_METADATA>")[0].strip()
                                            if clean and len(clean) > 5:
                                                user_requests.append(clean[:200])
                                    elif itype == "PLANNER_RESPONSE":
                                        for tc in item.get("tool_calls", []):
                                            targs = tc.get("args", {})
                                            target = targs.get("TargetFile") or targs.get("AbsolutePath")
                                            if target:
                                                files_touched.add(os.path.basename(str(target)))
                                except Exception:
                                    continue

                        if user_requests or files_touched:
                            results.append({
                                "conversation_id": conv_id,
                                "source_brain": os.path.basename(os.path.dirname(bdir)),
                                "last_active": datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M"),
                                "requests": user_requests[-4:],
                                "files": sorted(list(files_touched))[:6]
                            })
                except Exception:
                    continue
    return results

def auto_distill_project_concepts(base_dir: str, git_harvest: list) -> list:
    """Autonomously updates or creates project concept nodes in concepts/ from recent commits."""
    concepts_dir = os.path.join(base_dir, "concepts")
    index_file = os.path.join(base_dir, "index.md")
    updated_concepts = []

    for item in git_harvest:
        repo = item["repo"]
        commits = item["commits"]
        if not commits:
            continue

        slug = f"project_{re.sub(r'[^a-z0-9]+', '_', repo.lower()).strip('_')}"
        target_file = os.path.join(concepts_dir, f"{slug}.md")
        today = datetime.now().strftime("%Y-%m-%d")

        commit_bullets = "\n".join([f"- {c}" for c in commits[:8]])

        if os.path.isfile(target_file):
            try:
                with open(target_file, "r", encoding="utf-8", errors="ignore") as f:
                    existing = f.read()

                first_hash = commits[0].split()[0]
                if first_hash not in existing:
                    update_section = f"\n\n### Autonomous Progress Update ({today})\n{commit_bullets}\n"
                    updated_content = sanitize_content(existing + update_section)
                    with open(target_file, "w", encoding="utf-8") as f:
                        f.write(updated_content)
                    updated_concepts.append(slug)
            except Exception:
                pass
        else:
            title = f"Project {repo.replace('_', ' ').replace('-', ' ').title()} Architecture"
            desc = f"Autonomous project tracking and architectural patterns for {repo}."
            template = f"""---
type: concept
title: {title}
description: {desc}
status: draft
trust_score: 2
tags: [project, {repo.lower()}]
created_at: {today}
updated_at: {today}
anonymized: true
sources: [git-history, dream-synthesis]
---

# {title}

## Summary
{desc}

## Key Architecture & Recent Invariants
{commit_bullets}

## Verification & Trust Record
* **Auto-Created:** Synthesized by OKF Dream Engine on {today}.

## References & Cross-Links
* [Master Index](../index.md)
"""
            cleaned = sanitize_content(template)
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(cleaned)

            if os.path.isfile(index_file):
                try:
                    with open(index_file, "r", encoding="utf-8") as f:
                        idx = f.read()
                    rel_link = f"./concepts/{slug}.md"
                    if rel_link not in idx:
                        new_entry = f"* [{title}]({rel_link}) — {desc}\n"
                        pattern = r"(## 1\. Warm Memory Graph \(Active Concepts\)\r?\n)(.*?)((\r?\n## |\Z))"
                        m = re.search(pattern, idx, re.DOTALL)
                        if m:
                            replacement = m.group(1) + m.group(2) + new_entry + m.group(3)
                            with open(index_file, "w", encoding="utf-8") as f:
                                f.write(idx[:m.start()] + replacement + idx[m.end():])
                except Exception:
                    pass
            updated_concepts.append(slug)

    return updated_concepts

def run_dream_synthesis() -> int:
    base = os.path.dirname(scripts_dir)
    staging = os.path.join(base, "staging")
    os.makedirs(staging, exist_ok=True)

    home = os.path.expanduser("~")
    desktop_dir = os.path.join(home, "Desktop")
    brain_dirs = [
        os.path.join(home, ".gemini", "antigravity-cli", "brain"),
        os.path.join(home, ".gemini", "antigravity", "brain")
    ]

    print("=== Running OKF Unified Dream Synthesis ===")

    # 1. Harvest Git commits
    git_harvest = harvest_git_commits(desktop_dir, hours=24)
    print(f"Git Repositories with commits (24h): {len(git_harvest)}")

    # 2. Harvest Antigravity transcripts
    agy_harvest = harvest_antigravity_transcripts(brain_dirs, hours=24)
    print(f"Antigravity Sessions active (24h): {len(agy_harvest)}")

    # 3. Harvest Live Turn Telemetry if present
    live_turns = []
    telemetry_file = os.path.join(staging, "live_turn_harvest.jsonl")
    if os.path.isfile(telemetry_file):
        try:
            with open(telemetry_file, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if line.strip():
                        live_turns.append(json.loads(line.strip()))
        except Exception:
            pass

    if not git_harvest and not agy_harvest and not live_turns:
        print("No recent Git activity or Antigravity sessions detected in the last 24 hours.")
        return 0

    # Build report sections
    sections = []
    now_str = datetime.now().strftime("%Y%m%d_%H%M")
    date_str = datetime.now().strftime("%Y-%m-%d")

    # Section A: Antigravity Sessions
    if agy_harvest:
        sections.append("## 1. Antigravity Session Insights (Active in Last 24 Hours)")
        for sess in agy_harvest:
            sections.append(f"### Session `{sess['conversation_id'][:8]}...` ({sess['source_brain']} - {sess['last_active']})")
            if sess["requests"]:
                sections.append("**User Intents & Goals:**")
                for req in sess["requests"]:
                    sections.append(f"- {req}")
            if sess["files"]:
                sections.append(f"**Key Files Touched:** {', '.join(sess['files'])}")
            sections.append("")

    # Section B: Workspace Git Commits
    if git_harvest:
        sections.append(f"## 2. Workspace Git Activity ({len(git_harvest)} Repositories)")
        for repo in git_harvest:
            sections.append(f"### Repository: {repo['repo']}")
            for c in repo["commits"]:
                sections.append(f"- {c}")
            sections.append("")

    # Section C: Live Turn Signals
    if live_turns:
        sections.append(f"## 3. Live Agent Telemetry ({len(live_turns)} Captured Turns)")
        for lt in live_turns[-5:]:
            sig_str = f" [signals: {', '.join(lt.get('signals', []))}]" if lt.get("signals") else ""
            sections.append(f"- **Intent:** {lt.get('user_intent', '')[:120]}{sig_str}")
        sections.append("")

    sections.append("## 4. Proposed Invariants / Conventions")
    sections.append("<!-- Synthesize verified patterns or promote candidates to ~/.okf_knowledge/concepts/ -->")

    body_text = "\n".join(sections)
    sanitized_body = sanitize_content(body_text)

    candidate_file = os.path.join(staging, f"candidate_synthesis_{now_str}.md")
    template = f"""---
type: concept
title: Unified Dream Synthesis ({now_str})
description: Automated cross-session synthesis of recent Git commits and Antigravity conversation context.
status: candidate
trust_score: 1
tags: [synthesis, candidate, agy-unified]
created_at: {date_str}
updated_at: {date_str}
anonymized: true
sources: [git-history, antigravity-transcripts]
---

# Unified Dream Synthesis ({now_str})

{sanitized_body}
"""

    with open(candidate_file, "w", encoding="utf-8") as f:
        f.write(template)
    print(f"Created candidate synthesis: {candidate_file}")

    # 4. Autonomous Warm Memory Distillation
    distilled = auto_distill_project_concepts(base, git_harvest)
    if distilled:
        print(f"Autonomously distilled project concepts: {', '.join(distilled)}")

    # 5. Prune staging files older than 14 days (TTL)
    cutoff_14d = datetime.now().timestamp() - (14 * 86400)
    for fname in os.listdir(staging):
        if fname.startswith("candidate_") and fname.endswith(".md"):
            fpath = os.path.join(staging, fname)
            try:
                if os.path.getmtime(fpath) < cutoff_14d:
                    os.remove(fpath)
                    print(f"Pruned expired staging candidate: {fname}")
            except Exception:
                pass

    # 6. Reset live telemetry buffer after successful synthesis
    if os.path.isfile(telemetry_file):
        try:
            with open(telemetry_file, "w", encoding="utf-8") as f:
                f.write("")
        except Exception:
            pass

    # 7. Commit to Git repository in .okf_knowledge
    try:
        subprocess.run(["git", "-C", base, "add", "concepts/", "index.md", "staging/"], capture_output=True)
        subprocess.run(["git", "-C", base, "commit", "-m", f"chore(dream): autonomous synthesis & distillation for {now_str}"], capture_output=True)
        print("Committed synthesis and distillation to .okf_knowledge repository.")
    except Exception as e:
        print(f"Warning: git commit failed: {e}", file=sys.stderr)

    return 0

if __name__ == "__main__":
    sys.exit(run_dream_synthesis())
