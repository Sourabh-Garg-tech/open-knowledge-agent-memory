#!/usr/bin/env python3
"""
Antigravity Lifecycle Hook Handler: OKF Live Session Synchronizer.
Executes on the Antigravity 'Stop' event across all live conversations.
Safely extracts turn context, applies Shannon entropy sanitization, and appends to OKF staging telemetry.
"""

import sys
import os
import json
import re
from datetime import datetime

# Path setup to import OKF sanitizer
scripts_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, scripts_dir)

try:
    from sanitize_okf import sanitize_content
except ImportError:
    def sanitize_content(text: str) -> str:
        return text

def process_hook_payload():
    try:
        if sys.stdin.isatty():
            print("{}")
            return
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            print("{}")
            return
        payload = json.loads(raw_input)
    except Exception:
        print("{}")
        return

    try:
        conv_id = payload.get("conversationId", "unknown")
        transcript_path = payload.get("transcriptPath", "")
        workspaces = payload.get("workspacePaths", [])
        workspace_str = workspaces[0] if workspaces else "default"

        if not transcript_path or not os.path.isfile(transcript_path):
            print("{}")
            return

        # 1. Walk backward through transcript to extract the latest turn
        lines = []
        with open(transcript_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        if not lines:
            print("{}")
            return

        latest_user_prompt = ""
        turn_steps = []
        for line in reversed(lines):
            try:
                item = json.loads(line)
                turn_steps.insert(0, item)
                if item.get("type") == "USER_INPUT":
                    latest_user_prompt = item.get("content", "")
                    break
            except Exception:
                continue

        # 2. Extract tools and modified files from turn
        tools_used = []
        files_modified = []
        planner_summaries = []

        for step in turn_steps:
            stype = step.get("type", "")
            if stype == "PLANNER_RESPONSE":
                tcalls = step.get("tool_calls", [])
                for tc in tcalls:
                    name = tc.get("name", "")
                    args = tc.get("args", {})
                    tools_used.append(name)
                    if name in ("write_to_file", "replace_file_content"):
                        target = args.get("TargetFile", "")
                        if target and target not in files_modified:
                            files_modified.append(target)
            elif stype == "USER_INPUT":
                pass

        # Clean prompt
        clean_prompt = latest_user_prompt.replace("<USER_REQUEST>", "").replace("</USER_REQUEST>", "").strip()
        if len(clean_prompt) > 400:
            clean_prompt = clean_prompt[:400] + "..."

        # 3. Detect signals
        keywords = ["fix", "error", "workaround", "invariant", "rule", "convention", "always", "never", "architect", "triad", "deploy", "config", "okf"]
        matched_signals = [k for k in keywords if k in clean_prompt.lower()]

        # 4. Record turn to staging telemetry
        base_dir = os.path.dirname(scripts_dir)
        staging_dir = os.path.join(base_dir, "staging")
        os.makedirs(staging_dir, exist_ok=True)
        harvest_file = os.path.join(staging_dir, "live_turn_harvest.jsonl")

        turn_record = {
            "timestamp": datetime.now().isoformat(),
            "conversationId": conv_id,
            "workspace": workspace_str,
            "user_intent": clean_prompt,
            "signals": matched_signals,
            "files_modified": files_modified,
            "tools_count": len(tools_used)
        }

        sanitized_json = sanitize_content(json.dumps(turn_record))
        with open(harvest_file, "a", encoding="utf-8") as f:
            f.write(sanitized_json + "\n")

    except Exception:
        # Failsafe: Never break Antigravity execution
        pass

    # Always return empty JSON object to cleanly satisfy the hook contract
    print("{}")

if __name__ == "__main__":
    process_hook_payload()
