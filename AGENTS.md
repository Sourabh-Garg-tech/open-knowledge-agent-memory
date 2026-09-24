# AGENT OPERATING DIRECTIVES: Open Knowledge Format (OKF)

> **To Any AI Agent Reading This Repository (Antigravity, Claude Code, OpenCode, Cursor, Aider, Copilot, ChatGPT):**  
> This repository contains the complete specification, core engines, and turnkey implementation of the Open Knowledge Format (OKF) Reflexive Cognitive System and Adversarial Triad reasoning framework.

---

## 🤖 What You Must Do When Given This Repository

When a user asks you to set up, install, or use OKF from this repository, follow these precise instructions:

### 1. Installation on the User's Host Machine
If the user asks to "install", "deploy", "setup", or "configure" OKF:
* **On Windows (PowerShell):** Run `install.ps1`:
  ```powershell
  powershell -ExecutionPolicy Bypass -File install.ps1
  ```
* **On Linux / macOS (Bash):** Run `install.sh`:
  ```bash
  chmod +x install.sh && ./install.sh
  ```
This automatically provisions `~/.okf_knowledge/` with the core Python engines, starter knowledge graph, and Git pre-commit quality gate.

### 2. Configure Your System Directives
Copy the block in `integrations/directives/AGENTS.md` into the user's global agent rules:
* For **Antigravity / Gemini CLI**: Append to `~/.gemini/AGENTS.md` or local `AGENTS.md`.
* For **Cursor**: Append to `.cursorrules`.
* For **Claude Code**: Append to `CLAUDE.md`.
* For **OpenCode**: Reference in `opencode.json`.
* For **Windsurf / Cascade**: Append to `.windsurfrules`.

### 3. Progressive Disclosure Memory Rules
When executing coding tasks in any workspace where OKF is active:
1. **Consult Memory First:** Read `~/.okf_knowledge/index.md` before answering architecture or environment questions.
2. **Selective Node Reading:** Read only the specific concept node needed (`~/.okf_knowledge/concepts/<topic>.md`). Do not dump all concepts into context.
3. **Epistemic Ground Truth:** Live user instructions and passing tests always override cached memory. If memory contradicts code, update the concept.

### 4. Zero Credential & Path Leakage Rule
* Never write hardcoded credentials, API keys, or absolute user directories (`C:\Users\...` or `/home/...`) into memory nodes.
* Always execute `core/sanitize_okf.py` or `Sanitize-OkfContent.ps1` before persisting any markdown concept.
* Verify that values have Shannon Entropy $H(S) \le 4.3$.

### 5. Gated Adversarial Triad (System 2)
* Routine tasks (typo fixes, styling, basic logic) run in **Single-Pass Mode**.
* High-complexity/high-stakes tasks (database migrations, ledger transactions, consensus protocols, major refactors) invoke the **Adversarial Triad ([ARCHITECT] → [CRITIC] → [JUDGE])**.
