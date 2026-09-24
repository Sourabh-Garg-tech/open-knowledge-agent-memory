# Claude Code Instructions: Open Knowledge Format (OKF)

See [AGENTS.md](./AGENTS.md) for full autonomous operating directives.

## Summary for Claude Code
1. To install OKF on the user's host machine, run `powershell -ExecutionPolicy Bypass -File install.ps1` (Windows) or `bash install.sh` (Linux/macOS).
2. The core knowledge graph resides at `~/.okf_knowledge/index.md`. Always query `index.md` before answering environment or architecture questions.
3. Keep warm memory under 50 nodes. Concepts untouched for >45 days are archived to `archive/concepts/`.
4. Always pass new concepts through `core/sanitize_okf.py` to prevent credential leakage.
