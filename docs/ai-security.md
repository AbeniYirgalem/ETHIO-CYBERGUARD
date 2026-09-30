# AI Safety, Grounding & Prompt-Injection Protection

ETHIO-CYBERGUARD deploys seven specialized AI agents. Because the platform inspects untrusted external inputs (phishing email bodies, PowerShell script lines, attacker-controlled domain names), rigorous security boundaries are established.

---

## 1. Security Invariants

1. **Untrusted Data Boundary**: Raw log messages, email contents, and command lines are treated strictly as untrusted data inputs, never as instructional prompts.
2. **Anti-Injection Guardrails**: All agent prompts include strict system instructions directing the model to flag attempted command injections (`"Ignore previous instructions"`, `"System prompt override"`) as adversary tactics (MITRE T1566 / Execution attempt) rather than obeying them.
3. **No Autonomous Destruction**: No LLM agent is equipped with destructive tool execution permissions. Agents can only submit containment *recommendations* into the human approval queue.
4. **Verifiable Citations**: AI responses must cite exact log events (`Event Log 4688`, `ScriptBlock PID 4812`), threat feed matches, or risk factors. Hallucinations are penalized and blocked by output schema validation.

---

## 2. Multi-Agent Cluster Roles

- **Event Analysis Agent (Agent 1)**: Deobfuscates arguments, parses base64/AMSI payloads.
- **Threat Intelligence Agent (Agent 2)**: Cross-references IOCs against Ethio-CERT and INSA threat databases.
- **Correlation Agent (Agent 3)**: Synthesizes multi-stage attack chains into unified incident graphs.
- **Investigation Agent (Agent 4)**: Evaluates forensic hypotheses against observed evidence.
- **Risk Assessment Agent (Agent 5)**: Computes explainable numerical risk vectors (0-100).
- **Executive Report Agent (Agent 6)**: Formulates boardroom-ready disclosures and regulatory compliance reports.
- **Security Assistant Agent (Agent 7)**: Grounded SOC copilot answering analyst queries with citations.
