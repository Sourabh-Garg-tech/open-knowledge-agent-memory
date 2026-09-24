# Contributing to Open Knowledge Format (OKF)

Thank you for your interest in contributing to OKF! We welcome contributions to core engines, integration skills, documentation, and universal concept templates.

---

## Code of Conduct & Security Invariants

All contributions must strictly adhere to the **Zero Leakage & Deterministic Quality** policy:
1. **Zero Secret Leakage:** Never submit PRs containing API keys, private tokens, passwords, personal machine paths (`C:\Users\...` or `/home/...`), or internal IPs. All concept files must pass `sanitize_okf.py`.
2. **Shannon Entropy Passing:** Any assigned key-value pair must have Shannon Entropy $H(S) \le 4.3$ unless it is an explicitly whitelisted test mock.
3. **Graph Integrity:** All markdown relative links must resolve to real files on disk. Commits are checked via `test_okf_graph.py`.

---

## Development Workflow

### 1. Fork & Clone
```bash
git clone https://github.com/your-username/open-knowledge-agent-memory.git
cd open-knowledge-agent-memory
```

### 2. Run Local Tests
```bash
# Run Shannon Entropy unit tests
python tests/test_entropy.py

# Run Graph Validator tests
python tests/test_validator.py
```

### 3. Adding New Universal Concepts
When contributing new concept nodes to `starter_graph/concepts/`:
* Use `core/new_okf_node.py` to scaffold the file.
* Ensure YAML frontmatter contains valid tags, descriptions, and `anonymized: true`.
* Concepts must describe general, reusable software architecture or development patterns applicable to any engineer in the world.

---

## Submitting Pull Requests
1. Create a feature branch: `git checkout -b feat/my-new-feature`
2. Ensure all tests pass: `python tests/test_entropy.py`
3. Commit with semantic commit messages (`feat: ...`, `fix: ...`, `docs: ...`).
4. Push and open a Pull Request against `main`.
