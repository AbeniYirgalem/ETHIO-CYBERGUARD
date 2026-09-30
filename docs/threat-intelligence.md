# ETHIO-CYBERGUARD - Threat Intelligence Architecture

## 1. IOC Management

ETHIO-CYBERGUARD tracks Indicators of Compromise (IOCs) across multiple categories:
- **IPv4 / IPv6**: Command & Control (C2) servers, botnet relays, brute-force exit nodes.
- **Domains & FQDNs**: Phishing infrastructure, fast-flux dynamic DNS, typosquatted brand portals.
- **File Hashes**: SHA256, SHA1, and MD5 hashes of known malware payloads (Mimikatz, Cobalt Strike, ransomware).
- **URLs**: Credential harvesting endpoints and malicious download scripts.

## 2. Integrated Intelligence Feeds

- **National Feed**: Ethio-CERT / INSA cyber advisories and national blocklists.
- **Commercial & Global Sources**: AbuseIPDB, AlienVault OTX, VirusTotal, and MISP indicators.
- **Active Brand Defense**: Dynamic openSquat typosquatted variations generated specifically for Ethiopian institutions.

## 3. Enrichment Pipeline

During event normalization, any extracted IP, domain, or process hash is checked against the in-memory Redis/PostgreSQL IOC database:
- Matching indicators append confidence scores (0–100%) and threat actor attribution directly to the incident record.
- Alerts enriched with high-confidence malicious IOCs automatically elevate the incident risk score and trigger high-priority SOAR recommendations.
