#!/usr/bin/env python3
"""
OKF Security Sanitization Engine (Regex + Shannon Entropy Analysis).
Redacts known token prefixes, high-entropy cryptographic strings, personal user paths, and machine PII.
"""

import sys
import os
import re
import math
from collections import Counter

def calculate_shannon_entropy(text: str) -> float:
    """Calculates the Shannon entropy H(S) of a string."""
    if not text:
        return 0.0
    counts = Counter(text)
    length = len(text)
    return -sum((count / length) * math.log2(count / length) for count in counts.values())

def sanitize_content(content: str) -> str:
    """Applies structural regex and Shannon entropy filters to redact sensitive information."""
    if not content:
        return ""

    sanitized = content

    # 1. Path & Identity Normalization
    home = os.path.expanduser("~")
    sanitized = re.sub(re.escape(home), "~", sanitized)
    userprofile = os.environ.get("USERPROFILE")
    if userprofile:
        sanitized = re.sub(re.escape(userprofile), "~", sanitized)
    sanitized = re.sub(r'(?i)C:\\Users\\[a-zA-Z0-9_\-\.]+', "~", sanitized)

    computer_name = os.environ.get("COMPUTERNAME")
    if computer_name:
        sanitized = re.sub(re.escape(computer_name), "<HOST_ANONYMIZED>", sanitized)

    # 2. Network IP & Private Key Scrubbing
    sanitized = re.sub(r'\b192\.168\.\d{1,3}\.\d{1,3}\b', '192.168.x.x', sanitized)
    sanitized = re.sub(r'\b10\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '10.x.x.x', sanitized)
    sanitized = re.sub(r'-----\s*BEGIN[ A-Z0-9_-]+KEY\s*-----[\s\S]*?-----\s*END[ A-Z0-9_-]+KEY\s*-----', '<PRIVATE_KEY_REDACTED>', sanitized)

    # 3. Structural Regex Pass (Known Prefixes)
    known_patterns = [
        (r'ghp_[a-zA-Z0-9]{36}', '<GITHUB_PAT_REDACTED>'),
        (r'github_pat_[a-zA-Z0-9_]{82}', '<GITHUB_PAT_REDACTED>'),
        (r'hf_[a-zA-Z0-9]{34}', '<HF_TOKEN_REDACTED>'),
        (r'AIza[0-9A-Za-z-_]{35}', '<GCP_KEY_REDACTED>'),
        (r'(?i)bearer\s+[a-zA-Z0-9_\-\.]{20,}', 'Bearer <TOKEN_REDACTED>'),
        (r'([a-zA-Z0-9_]+_key|token|secret|password)\s*[:=]\s*["\']?([a-zA-Z0-9/+=_\-]{20,})["\']?', None)
    ]

    for pattern, replacement in known_patterns:
        if replacement:
            sanitized = re.sub(pattern, replacement, sanitized)
        else:
            # High-entropy extraction pass for generic assignments (H > 4.3)
            matches = list(re.finditer(pattern, sanitized, re.IGNORECASE))
            for m in matches:
                value = m.group(2)
                if calculate_shannon_entropy(value) > 4.3:
                    sanitized = sanitized.replace(value, "<HIGH_ENTROPY_SECRET_REDACTED>")

    # 4. Tokenizer Fallback for Unstructured High-Entropy Strings (H >= 4.5, len >= 24)
    tokens = re.split(r'[\s=\":;\',]+', sanitized)
    for token in tokens:
        clean_token = token.strip()
        if len(clean_token) >= 24 and calculate_shannon_entropy(clean_token) >= 4.5:
            # Exclude standard URLs, hex commit SHAs (40 chars lowercase hex), and markdown links
            if (not clean_token.startswith("http") 
                and not re.match(r'^[0-9a-f]{40}$', clean_token, re.IGNORECASE)
                and not clean_token.endswith(".md")):
                sanitized = sanitized.replace(clean_token, "<HIGH_ENTROPY_TOKEN_REDACTED>")

    return sanitized

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if os.path.isfile(arg):
            with open(arg, "r", encoding="utf-8", errors="ignore") as f:
                print(sanitize_content(f.read()))
        else:
            print(sanitize_content(arg))
    elif not sys.stdin.isatty():
        print(sanitize_content(sys.stdin.read()))
    else:
        print("Usage: sanitize_okf.py <file-path-or-text>")
