# 🔒 AI Safety, Grounding & Adversarial Defense Architecture

**Document Version**: 1.1.0  
**Scope**: LLM Prompt-Injection Defense, Telemetry Data Isolation, Zero-Hallucination Grounding  
**Target Compliance**: INSA Critical Infrastructure AI Security Directives, OWASP Top 10 for LLM Applications  

---

## 1. Core AI Security Invariants

In a high-security national defense SOC, language models analyze untrusted, attacker-controlled inputs:
- Malicious command lines containing obfuscated script code.
- Phishing email bodies containing social engineering lures and attempted meta-prompt overrides.
- HTTP User-Agent strings, domain names, and file paths crafted to subvert system prompts.

To prevent adversarial compromise of the SOC decision loop, ETHIO-CYBERGUARD enforces four foundational invariants:

1. **Strict Data-Plane / Control-Plane Separation**: Raw telemetry data, email text, and process arguments are always packaged inside structured JSON data blocks. They are never concatenated directly into conversational instruction templates.
2. **Zero Autonomous Containment Execution**: No AI agent has direct programmatic access to shell execution or firewall configuration tools. Agents generate recommendations; only certified human analysts can execute them via the Dual-Custody Approval gate.
3. **Retrieval Grounding with Mandatory Citations**: The SOC Assistant and Investigation agents are explicitly constrained to synthesize conclusions from verified telemetry. Every assertion must cite an exact `event_id`, process PID, or threat indicator hash.
4. **Deterministic Schema Gatekeeper**: Multi-agent outputs are strictly validated against Pydantic v2 schemas. Responses violating schema boundaries are immediately dropped and routed to deterministic heuristic handlers.

---

## 2. Multi-Layer Prompt Injection Defense

```text
[Untrusted Telemetry / Phishing Content]
                   │
                   ▼
┌────────────────────────────────────────────────────────┐
│             Layer 1: Sanitization & Parsing            │
│  • Strip meta-instruction delimiters (---, ```, <sys>) │
│  • Escape quote breaks and control characters          │
│  • Token length bounding (max 4,096 tokens per slice)  │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│             Layer 2: Adversarial Tactic Tagging        │
│  • Detects strings: "ignore previous instructions",    │
│    "system prompt override", "you are now a helpful"   │
│  • Flags input as adversary technique MITRE T1059      │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│             Layer 3: Isolated Context Injection        │
│  System Prompt (Immutable)                             │
│  <untrusted_evidence_data> { JSON Payload } </data>    │
│  Evaluation Prompt: "Analyze strictly the evidence."   │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│             Layer 4: Schema & Citation Validation      │
│  • Pydantic v2 JSON Schema Verification                │
│  • Citation Cross-Referencing against Active Incident  │
└────────────────────────────────────────────────────────┘
```

---

## 3. Defense Against Amharic Language Exploitation

Adversaries targeting Ethiopian banking and telecom infrastructure often utilize Ge'ez script lures (Amharic, Tigrinya, Oromo) to bypass standard English-only safety filters.

ETHIO-CYBERGUARD incorporates native Amharic NLP tokenizer rules that:
- Detect semantic evasion tactics embedded in Ge'ez text (e.g., hidden instructions instructing the model to misclassify a Telebirr phishing URL as safe).
- Treat Amharic and Latin scripts symmetrically under strict data isolation rules.
- Identify urgent financial pressure phrases (`አስቸኳይ`, `የ10,000 ብር ቦነስ`, `የይለፍ ቃልዎን ያረጋግጡ`) as phishing signals regardless of token layout.

---

## 4. Hallucination Mitigation & Verification Matrix

| Vulnerability | Threat Vector | ETHIO-CYBERGUARD Mitigation |
| :--- | :--- | :--- |
| **Hallucinated IP / Hash** | AI invents an IP address not present in evidence | Output validation filters all cited entities against the incident's normalized event store. Unmatched entities trigger immediate rejection. |
| **False Positive Escalation** | AI inflates risk score without telemetry justification | Risk Assessment Agent requires explainable mathematical justification breakdown ($w_1 \cdot \text{Crit} + w_2 \cdot \text{Threat} \dots$). |
| **Denial of Service via Prompt Bloat** | Attacker floods telemetry with 1MB log messages | Gateway rate limiter and payload truncator enforce maximum 64KB per single log event. |
| **Indirect Injection via Threat Feed** | Attacker poisons public MISP feed with malicious markdown | Intelligence ingest normalizer sanitizes indicator descriptions and forces plain text representation. |
