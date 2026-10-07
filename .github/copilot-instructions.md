# GitHub Copilot Custom Instructions for ETHIO-CYBERGUARD

## Repository Context
You are working on **ETHIO-CYBERGUARD**, a next-generation AI-powered Security Operations Center (SOC) and SIEM platform built specifically for Ethiopian critical national infrastructure defense (Commercial Bank of Ethiopia, INSA, Ethio Telecom).

## Key Principles & Conventions

### Frontend (React 19 + TypeScript + Tailwind CSS v4)
- **Language**: Modern TypeScript with strict typing. Avoid using `any`.
- **Framework**: React 19 functional components with hooks (`useState`, `useEffect`, `useRef`, `useCallback`).
- **Icons**: Always import icons from `lucide-react`. Ensure every imported icon is actually used in JSX to prevent `TS6133` unused declaration errors.
- **Styling**: Tailwind CSS v4 classes with dark theme tactical aesthetic (colors: `#070B12`, `#0D131C`, `#111923`, `#1E2A38`, `#00D9FF`, `#FF1744`, `#22C55E`, `#F59E0B`).
- **Vite Configuration**: Always preserve `base: './'` in `vite.config.ts` to ensure compatibility with GitHub Pages deployments.

### Backend (FastAPI + Python 3.10+)
- **Framework**: FastAPI with Pydantic v2 schemas and models.
- **Routing**: Group endpoints by functional domain (`/api/auth`, `/api/incidents`, `/api/response`, `/api/phishing`, `/api/osint`, `/api/typosquat`, `/api/threat-intelligence`).
- **Testing**: Maintain 100% passing tests with `pytest`. When adding new routes, write corresponding unit tests in `tests/unit/`.

### Security Guardrails
- **Dual-Custody Approvals**: Do not allow automatic execution of containment actions without an approval gate.
- **Role-Based Access Control**: Respect the 7 roles (`SUPER_ADMIN`, `SOC_MANAGER`, `SECURITY_ANALYST`, `INCIDENT_RESPONDER`, `THREAT_HUNTER`, `AUDITOR`, `READ_ONLY`).
- **Input Sanitization**: Always validate and sanitize user input against prompt injection and SSRF.
