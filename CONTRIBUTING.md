# 🤝 Contributing to ETHIO-CYBERGUARD

Thank you for your interest in contributing to **ETHIO-CYBERGUARD**! We welcome contributions from cybersecurity researchers, software engineers, and community analysts dedicated to strengthening defensive resilience.

---

## 🛠️ Development Setup

### 1. Prerequisites
- **Python 3.10+**
- **Node.js 18+ & npm**
- **Docker & Docker Compose** (optional for local full-stack run)

### 2. Setting Up the Local Environment
```bash
# Clone the repository
git clone https://github.com/AbeniYirgalem/ETHIO-CYBERGUARD.git
cd ETHIO-CYBERGUARD

# Backend setup
cd apps/api
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
pip install -r requirements.txt

# Frontend setup
cd ../../apps/web
npm install
```

### 3. Running the Test Suite
```bash
# Run complete Python unit, integration, and security tests
python -m pytest

# Run frontend build verification
cd apps/web
npm run build
```

---

## 🌿 Contribution Guidelines

1. **Branching Model**:
   - Create focused feature branches from `main`:
     ```bash
     git checkout -b feature/amharic-fraud-heuristic
     ```
2. **Commit Conventions**:
   - Follow [Conventional Commits](https://www.conventionalcommits.org/):
     - `feat:` new feature or detection capability.
     - `fix:` bug fix or false-positive adjustment.
     - `docs:` updates to documentation or diagrams.
     - `test:` test suite additions or fixture updates.
3. **Detection Rules Standards**:
   - Every SIGMA rule added to `detection-rules/` must include test fixtures and a defined MITRE ATT&CK tactic/technique mapping.
4. **Pull Requests**:
   - Ensure all CI tests pass.
   - Describe the security context and threat motivation in the PR description.
