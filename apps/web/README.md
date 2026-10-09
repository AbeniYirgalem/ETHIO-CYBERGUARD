# 🛡️ ETHIO-CYBERGUARD — SOC Web HUD Console

The **ETHIO-CYBERGUARD Web HUD** is a mission-critical, high-performance web interface designed for Security Operations Centers (SOC) defending national infrastructure, commercial banks, telecommunications, and government perimeters in Ethiopia.

---

## ⚡ Key Highlights & Technologies

- **React 19**: Modern functional architecture utilizing `useState`, `useEffect`, `useRef`, and `useCallback` with strict Fast Refresh compliance and zero cascading renders.
- **Vite 8 & Rolldown**: Ultra-fast build times (~1.2s) with custom functional `manualChunks` splitting React/ReactDOM vendor and Lucide chunks (each bundle under 270 kB).
- **Tailwind CSS v4**: Tactical dark theme interface (`#070B12`, `#0D131C`, `#111923`, `#00D9FF`, `#FF1744`, `#22C55E`, `#F59E0B`).
- **Web Audio API Acoustic Synthesizer**: Custom real-time audio alerts for Critical (880 Hz dual-beep), High (440 Hz pulse), and Info (220 Hz chime) events with persistent mute toggle.
- **Ethiopia Cyber Radar**: Real-time canvas radar visualizer mapping national critical infrastructure nodes (Commercial Bank of Ethiopia, Ethio Telecom, INSA, National Grid) with ping arcs, sweeps, and status pulses.
- **Dual-Custody SOAR Gate**: Cryptographic authorization modals requiring human analyst confirmation before destructive containment execution.
- **Amharic NLP & Telebirr Shield**: Interactive phishing and brand impersonation analyzer supporting Ge'ez script SMS and email lures.
- **Code Quality**: Clean build with `oxlint` (0 errors, 0 warnings).

---

## 📂 Component Directory Breakdown

```text
apps/web/src/
├── components/
│   ├── ActionApprovalModal.tsx      # Dual-custody SOAR approval dialog
│   ├── AssistantView.tsx            # Grounded AI SOC Copilot chat with citation links
│   ├── CommandPalette.tsx           # Quick navigation HUD (Ctrl/Cmd + K)
│   ├── EthiopiaCyberRadar.tsx       # Live canvas radar for national critical nodes
│   ├── IncidentDossierModal.tsx     # Deep-dive forensic dossier & attack graph
│   ├── PhishingDetectorView.tsx     # Telebirr & Amharic SMS/email phishing inspector
│   ├── RoleSwitcher.tsx             # 7-tier RBAC simulator for testing role policies
│   ├── TelemetryStream.tsx          # Real-time ECS log ingestion stream
│   ├── ThreatIntelligenceView.tsx   # IOC feeds, MISP indicators & reputation
│   └── ...
├── utils/
│   └── soundSynthesizer.ts          # Web Audio API procedural sound engine
├── types.ts                         # Complete TypeScript domain interfaces
├── App.tsx                          # Root layout, navigation tabs & state machine
└── main.tsx                         # React 19 entrypoint
```

---

## 🚀 Development Quickstart

### Prerequisites
- Node.js 20+ (Node.js 22 LTS recommended)
- `npm` 10+

### Installation
```bash
# From apps/web directory
npm install
```

### Run Local Development Server
```bash
npm run dev
```
The application will launch at `http://localhost:5173`.

### Type-Check & Production Build
```bash
npm run build
```
Build output is generated into `dist/` with relative asset links (`base: './'`), ready for direct static hosting, Docker Nginx containers, or GitHub Pages.

### Fast Linting with Oxlint
```bash
npm run lint
```

---

## 🎮 Keyboard Shortcuts & HUD Navigation

- <kbd>Ctrl</kbd> + <kbd>K</kbd> / <kbd>Cmd</kbd> + <kbd>K</kbd>: Open Command Palette for quick search and action dispatch.
- <kbd>Esc</kbd>: Close open modals (Dossier, Dual-Custody Approval, Command Palette).
- <kbd>M</kbd>: Mute / unmute Web Audio API audio synthesizer alarms.

---

## 🔒 Security Invariants for Web Development

1. **Dual-Custody Gate**: Never automatically invoke containment action endpoints (`/api/v1/response/actions/.../approve`) from UI components without rendering the `ActionApprovalModal`.
2. **Relative Asset Base**: Always preserve `base: './'` in `vite.config.ts` to ensure compatibility with subpath deployments and GitHub Pages.
3. **Fast Refresh Purity**: Do not export non-component constants or helper functions from `.tsx` component files. Keep all data structures in dedicated types or utility files.
