#!/usr/bin/env bash
# Open Knowledge Format (OKF) 1-Click Turnkey Installer for Linux / macOS.
# Deploys the complete cognitive architecture, core Python engines, starter knowledge graph,
# and Git pre-commit quality gate into $HOME/.okf_knowledge.

set -e

echo "=========================================================="
echo "   Open Knowledge Agent Memory (OKF) Turnkey Installer    "
echo "=========================================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd || pwd)"
TMP_DIR=""

if [ ! -d "$SCRIPT_DIR/core" ]; then
    echo "  + Remote execution detected. Fetching repository components..."
    TMP_DIR=$(mktemp -d 2>/dev/null || mktemp -d -t 'okf_install')
    REPO_URL="${OKF_REPO_URL:-https://github.com/open-knowledge-format/open-knowledge-agent-memory.git}"
    git clone --depth 1 "$REPO_URL" "$TMP_DIR" 2>/dev/null
    SCRIPT_DIR="$TMP_DIR"
    trap 'rm -rf "$TMP_DIR"' EXIT
fi

TARGET_BASE="$HOME/.okf_knowledge"

echo "[1/6] Setting up directory hierarchy at $TARGET_BASE..."
mkdir -p "$TARGET_BASE/concepts" "$TARGET_BASE/archive/concepts" "$TARGET_BASE/staging" "$TARGET_BASE/scripts"

echo "[2/6] Deploying core Python 3 engines..."
if [ -d "$SCRIPT_DIR/core" ]; then
    cp "$SCRIPT_DIR/core/"*.py "$TARGET_BASE/scripts/"
    chmod +x "$TARGET_BASE/scripts/"*.py 2>/dev/null || true
    echo "  + Python engines deployed to $TARGET_BASE/scripts"
fi

echo "[3/6] Deploying starter knowledge graph..."
if [ -d "$SCRIPT_DIR/starter_graph" ]; then
    if [ ! -f "$TARGET_BASE/index.md" ]; then
        cp "$SCRIPT_DIR/starter_graph/index.md" "$TARGET_BASE/index.md"
        echo "  + Created master index.md"
    fi
    cp -n "$SCRIPT_DIR/starter_graph/concepts/"*.md "$TARGET_BASE/concepts/" 2>/dev/null || true
    echo "  + Deployed starter concepts"
fi

echo "[4/6] Initializing Git repository and quality gate..."
if [ ! -d "$TARGET_BASE/.git" ]; then
    git -C "$TARGET_BASE" init -b master
    echo "  + Initialized Git repository on 'master'"
fi

cp "$SCRIPT_DIR/.gitignore" "$TARGET_BASE/.gitignore" 2>/dev/null || true

# Install pre-commit hook
mkdir -p "$TARGET_BASE/.git/hooks"
cat << 'EOF' > "$TARGET_BASE/.git/hooks/pre-commit"
#!/usr/bin/env bash
# OKF Graph Integrity & Security Pre-Commit Guard

echo "=== [Pre-Commit Hook] Running OKF Graph Integrity & Security Verification ==="

python scripts/test_okf_graph.py
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo "ERROR: OKF Graph validation failed! Commit aborted."
    echo "Check for dead links, unsanitized paths, or frontmatter errors before committing."
    exit 1
fi

echo "SUCCESS: OKF Graph verified clean. Proceeding with commit."
exit 0
EOF
chmod +x "$TARGET_BASE/.git/hooks/pre-commit"
echo "  + Installed Git pre-commit quality gate hook"

echo "[5/6] Deploying agent skills and lifecycle hooks (if Gemini/Antigravity present)..."
SKILLS_DIR="$HOME/.gemini/config/skills"
if [ -d "$SCRIPT_DIR/integrations/skills" ]; then
    mkdir -p "$SKILLS_DIR"
    for skill_path in "$SCRIPT_DIR/integrations/skills/"*; do
        if [ -d "$skill_path" ]; then
            skill_name="$(basename "$skill_path")"
            mkdir -p "$SKILLS_DIR/$skill_name"
            cp "$skill_path/SKILL.md" "$SKILLS_DIR/$skill_name/SKILL.md"
            echo "  + Deployed skill: $skill_name"
        fi
    done
fi

GEMINI_CONFIG="$HOME/.gemini/config"
if [ -d "$GEMINI_CONFIG" ] && [ -f "$SCRIPT_DIR/integrations/hooks/hooks.json" ]; then
    cp "$SCRIPT_DIR/integrations/hooks/hooks.json" "$GEMINI_CONFIG/hooks.json"
    echo "  + Deployed Antigravity lifecycle hook to $GEMINI_CONFIG/hooks.json"
fi

echo "[6/6] Verifying graph integrity..."
python3 "$TARGET_BASE/scripts/test_okf_graph.py"

git -C "$TARGET_BASE" add -A
if [ -n "$(git -C "$TARGET_BASE" status --porcelain)" ]; then
    git -C "$TARGET_BASE" commit -m "feat(okf): initialize cognitive memory system"
    echo "  + Initial commit created"
fi

echo "[7/7] Installing Shell CLI shortcuts (okf-status, okf-search, etc.)..."
RC_FILE=""
if [ -f "$HOME/.bashrc" ]; then
    RC_FILE="$HOME/.bashrc"
elif [ -f "$HOME/.zshrc" ]; then
    RC_FILE="$HOME/.zshrc"
fi

if [ -n "$RC_FILE" ] && ! grep -q "okf-status()" "$RC_FILE"; then
    cat << 'RC_EOF' >> "$RC_FILE"

# Open Knowledge Format (OKF) Shell Functions
export OKF_HOME="$HOME/.okf_knowledge"

okf-status() {
    local warm=$(find "$OKF_HOME/concepts" -name "*.md" 2>/dev/null | wc -l)
    local staging=$(find "$OKF_HOME/staging" -name "*.md" 2>/dev/null | wc -l)
    local archive=$(find "$OKF_HOME/archive/concepts" -name "*.md" 2>/dev/null | wc -l)
    echo "=========================================================="
    echo "       Open Knowledge Format (OKF) Memory Graph           "
    echo "=========================================================="
    echo "  Location: $OKF_HOME"
    echo "  Warm Memory:    $warm / 50 nodes"
    echo "  Staging Inbox:  $staging candidate(s)"
    echo "  Cold Archive:   $archive node(s)"
    git -C "$OKF_HOME" status -s
    echo "=========================================================="
}

okf-search() {
    grep -rn "$1" "$OKF_HOME/concepts/"
}

okf-verify() {
    python3 "$OKF_HOME/scripts/test_okf_graph.py"
}

okf-prune() {
    python3 "$OKF_HOME/scripts/prune_okf_memory.py"
}

okf-dream() {
    python3 "$OKF_HOME/scripts/invoke_dream_synthesis.py"
}

okf-new() {
    python3 "$OKF_HOME/scripts/new_okf_node.py" "$1" "${2:-Autonomous learning entry.}"
}

okf-record() {
    python3 "$OKF_HOME/scripts/record_okf_learning.py" "$1" "$2" "$3"
}
RC_EOF
    echo "  + Added CLI functions to $RC_FILE"
fi

echo "[8/8] Registering daily background Dream Synthesis task..."
if command -v crontab >/dev/null 2>&1; then
    if ! crontab -l 2>/dev/null | grep -q "invoke_dream_synthesis.py"; then
        (crontab -l 2>/dev/null; echo "0 23 * * * python3 $TARGET_BASE/scripts/invoke_dream_synthesis.py >/dev/null 2>&1") | crontab - 2>/dev/null || true
        echo "  + Registered daily cron task (23:00)"
    fi
fi

echo "=========================================================="
echo "  SUCCESS: OKF Cognitive Memory System is 100% Deployed!   "
echo "=========================================================="
echo "Next Step: Add the directives block from integrations/directives/AGENTS.md"
echo "to your system prompt or rules file (e.g. AGENTS.md, .cursorrules)."
echo "Available CLI commands: okf-status, okf-search, okf-new, okf-record, okf-verify, okf-prune, okf-dream"
