# Contributing to ETHIO-CYBERGUARD

Thank you for your interest in contributing to **ETHIO-CYBERGUARD**! As an open-source cybersecurity project defending national and enterprise infrastructure, we welcome contributions from security analysts, developers, and researchers.

---

## 1. Development Workflow

1. Fork the repository and create your feature branch:
   ```bash
   git checkout -b feature/my-new-detection-rule
   ```
2. Set up your local environment:
   ```bash
   make install
   ```
3. Run tests before submitting:
   ```bash
   make test
   make security
   ```

---

## 2. Contributing Detection Rules

When submitting new SIGMA rules:
- Place the rule in the appropriate `detection-rules/<category>/` directory.
- Ensure MITRE ATT&CK technique tags (e.g. `attack.t1059.001`) are present.
- Provide false-positive guidance and references.
- Verify that `services.detection.evaluator.SigmaRuleEvaluator` parses your rule without syntax warnings.

---

## 3. Pull Request Guidelines

- Ensure all Pytest unit tests pass (`27+ tests passing`).
- Ensure frontend compiles cleanly (`cd apps/web && npm run build`).
- Do not commit secrets, private keys, or API tokens.
