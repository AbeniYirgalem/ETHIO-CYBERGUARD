# GitHub Copilot Custom Instructions for ETHIO-CYBERGUARD

## Repository Context
You are working on **ETHIO-CYBERGUARD**, a next-generation AI-powered Security Operations Center (SOC) and SIEM platform built specifically for Ethiopian critical national infrastructure defense (Commercial Bank of Ethiopia, INSA, Ethio Telecom).

---

## Key Principles & Conventions

### Frontend (React 19 + TypeScript + Vite 8 + Tailwind CSS v4)
- **Language**: Modern TypeScript with strict typing. Avoid using `any`.
- **Framework**: React 19 functional components with hooks (`useState`, `useEffect`, `useRef`, `useCallback`). Ensure all callbacks passed across effect boundaries are memoized to avoid re-render cascades.
- **Vite & Rolldown Bundling**: Use functional `manualChunks(id)` in `vite.config.ts` (e.g. splitting `vendor` and `lucide`). Never use object dictionary chunks which fail type-checking in Vite 8.
- **Fast Refresh Purity**: Ensure `.tsx` component files only export React components to satisfy Oxlint `react/only-export-components`. Move constants and helper functions to dedicated utility/type files.
- **Icons**: Always import icons from `lucide-react`. Ensure every imported icon is actually used in JSX to prevent `TS6133` unused declaration errors.
- **Styling**: Tailwind CSS v4 classes with dark theme tactical aesthetic (colors: `#070B12`, `#0D131C`, `#111923`, `#1E2A38`, `#00D9FF`, `#FF1744`, `#22C55E`, `#F59E0B`).
- **Base URL**: Always preserve `base: './'` in `vite.config.ts` to ensure compatibility with GitHub Pages deployments.

### Backend (FastAPI + Python 3.10+ + SQLAlchemy 2.0+)
- **Lifecycle Management**: Use ASGI `@asynccontextmanager async def lifespan(app: FastAPI)` context manager. Do not use deprecated `@app.on_event("startup")` or `@app.on_event("shutdown")`.
- **Routing**: Group endpoints by functional domain under `apps/api/routers/` (`auth`, `incidents`, `response`, `phishing`, `osint`, `typosquat`, `threat_intel`, `connectors`, `jobs`, `health`).
- **Resilience**: Implement circuit breakers for external integrations and route malformed telemetry to the Dead-Letter Queue (DLQ).
- **Testing**: Maintain 100% passing tests with `pytest` across all 75 automated unit, integration, and security tests.

### Security Invariants
- **Dual-Custody Approvals**: Do not allow automatic execution of containment actions (`ISOLATE_HOST`, `BLOCK_IP`, `DISABLE_ACCOUNT`) without an approval gate.
- **Role-Based Access Control**: Respect the 7 roles (`SUPER_ADMIN`, `SOC_MANAGER`, `INCIDENT_RESPONDER`, `SECURITY_ANALYST`, `THREAT_HUNTER`, `AUDITOR`, `READ_ONLY`).
- **Tenant Isolation**: Always enforce tenant boundary checks (`organization_id`) in queries and WebSocket broadcasts.
- **Cryptographic Audit**: Append all SOAR actions to the SHA-256 chained audit ledger.
- **Input Sanitization**: Always validate and sanitize user input against prompt injection and SSRF.
