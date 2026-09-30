import type { Incident, SecurityEvent, ThreatIndicator, ResponseAction, TimelineEntry } from './types';

export const INITIAL_INCIDENTS: Incident[] = [
  {
    id: "e0000000-0000-0000-0000-000000000001",
    incident_number: "INC-00042",
    title: "Suspicious Obfuscated PowerShell Activity & C2 Beaconing",
    severity: "CRITICAL",
    status: "INVESTIGATING",
    risk_score: 92,
    affected_asset: "SERVER-04",
    asset_ip: "10.10.1.24",
    department: "Core Banking Infrastructure",
    first_seen: "2026-09-30 10:42:00 EAT",
    last_activity: "2026-09-30 11:18:00 EAT",
    assigned_analyst: "Dawit Mengistu",
    summary: "Privileged administrator session executed base64-encoded PowerShell payload with memory download cradle, followed by high-frequency beaconing to external C2 node 185.220.101.5."
  },
  {
    id: "e0000000-0000-0000-0000-000000000002",
    incident_number: "INC-00021",
    title: "Perimeter Gateway Distributed SSH & RDP Brute Force",
    severity: "HIGH",
    status: "OPEN",
    risk_score: 78,
    affected_asset: "FW-PERIMETER-01",
    asset_ip: "197.156.70.1",
    department: "Perimeter Network",
    first_seen: "2026-09-30 09:15:00 EAT",
    last_activity: "2026-09-30 09:22:00 EAT",
    assigned_analyst: "Sara Yohannes",
    summary: "Over 1,200 failed authentication sweeps targeting perimeter firewall management ingress within a 4-minute window."
  },
  {
    id: "e0000000-0000-0000-0000-000000000003",
    incident_number: "INC-00019",
    title: "Unusual Off-Hours Privileged SWIFT Access from Remote Subnet",
    severity: "MEDIUM",
    status: "INVESTIGATING",
    risk_score: 64,
    affected_asset: "LAPTOP-FINANCE-22",
    asset_ip: "10.10.4.88",
    department: "Treasury Operations",
    first_seen: "2026-09-30 03:14:00 EAT",
    last_activity: "2026-09-30 03:45:00 EAT",
    assigned_analyst: "Dawit Mengistu",
    summary: "Treasury workstation logged in at 03:14 AM EAT from unmanaged residential IP subnet, accessing SWIFT payment file transfer directory."
  }
];

export const INITIAL_TIMELINE: TimelineEntry[] = [
  { time: "10:42:03", event: "User 'administrator' interactive logon to SERVER-04", type: "auth", severity: "INFO" },
  { time: "10:42:19", event: "PowerShell process spawned (PID 4812) by explorer.exe", type: "process", severity: "MEDIUM" },
  { time: "10:42:21", event: "Suspicious base64 encoded command detected (-Enc SQBFAFgA...)", type: "alert", severity: "CRITICAL" },
  { time: "10:43:02", event: "Outbound TLS socket connection established to 185.220.101.5:443", type: "network", severity: "HIGH" },
  { time: "10:43:08", event: "Threat intelligence match: Cobalt Strike C2 Node (Ethio-CERT Feed)", type: "threat_intel", severity: "CRITICAL" },
  { time: "10:43:11", event: "AI multi-agent investigation pipeline triggered", type: "ai", severity: "INFO" },
  { time: "10:43:14", event: "Incident promoted to CRITICAL severity (Risk Score: 92/100)", type: "incident", severity: "CRITICAL" }
];

export const INITIAL_EVENTS: SecurityEvent[] = [
  {
    event_id: "evt_104821",
    timestamp: "11:31:21 EAT",
    source: { type: "endpoint", hostname: "SERVER-04", ip: "10.10.1.24", os: "Windows" },
    event_type: "process_execution",
    severity: "CRITICAL",
    user: "administrator",
    process: { name: "powershell.exe", command_line: "powershell.exe -NoP -NonI -W Hidden -Exec Bypass -Enc SQBFA...", pid: 4812 },
    network: { destination_ip: "185.220.101.5", destination_port: 443 }
  },
  {
    event_id: "evt_104818",
    timestamp: "11:31:18 EAT",
    source: { type: "firewall", hostname: "FW-PERIMETER-01", ip: "197.156.70.1" },
    event_type: "port_scan_sweep",
    severity: "HIGH",
    user: "anonymous",
    network: { source_ip: "45.154.255.89", destination_ip: "197.156.70.1", destination_port: 22 }
  },
  {
    event_id: "evt_104813",
    timestamp: "11:31:13 EAT",
    source: { type: "endpoint", hostname: "LAPTOP-FINANCE-22", ip: "10.10.4.88", os: "Windows" },
    event_type: "file_modification",
    severity: "CRITICAL",
    user: "finance_clerk",
    process: { name: "mimikatz.exe", command_line: "mimikatz.exe \"privilege::debug\" \"sekurlsa::logonpasswords\"", pid: 3102 }
  },
  {
    event_id: "evt_104809",
    timestamp: "11:30:58 EAT",
    source: { type: "syslog", hostname: "ROUTER-GATEWAY-AAU", ip: "10.200.0.1" },
    event_type: "bgp_route_anomaly",
    severity: "MEDIUM",
    user: "netadmin",
    network: { source_ip: "10.200.0.1", destination_ip: "197.156.0.1" }
  },
  {
    event_id: "evt_104802",
    timestamp: "11:30:44 EAT",
    source: { type: "endpoint", hostname: "DB-ORACLE-CORE", ip: "10.10.2.15", os: "Linux" },
    event_type: "privilege_escalation",
    severity: "HIGH",
    user: "oracle_agent",
    process: { name: "sudo", command_line: "sudo su - postgres" }
  }
];

export const INITIAL_INDICATORS: ThreatIndicator[] = [
  {
    indicator: "185.220.101.5",
    type: "IPV4",
    reputation: "MALICIOUS",
    confidence: 96,
    first_seen: "2026-04-12",
    threat_actor: "APT-CobaltStrike-Actor",
    malware: "Cobalt Strike Beacon",
    country: "Germany (Tor Exit)",
    related_incidents: ["INC-00042", "INC-00021"]
  },
  {
    indicator: "update-winsec-cloud.com",
    type: "DOMAIN",
    reputation: "MALICIOUS",
    confidence: 92,
    first_seen: "2026-08-19",
    threat_actor: "Fin-Threat Cluster",
    malware: "Empire C2 Stager",
    country: "Russia",
    related_incidents: ["INC-00019"]
  },
  {
    indicator: "7d4b29c9103a89e924a2734ef0350d24fb4b3e6480c55ffc06a928db6928e469",
    type: "SHA256",
    reputation: "MALICIOUS",
    confidence: 99,
    first_seen: "2026-01-10",
    threat_actor: "Lazarus Group",
    malware: "Mimikatz LSASS Infiltrator",
    country: "North Korea",
    related_incidents: ["INC-00042"]
  },
  {
    indicator: "45.154.255.89",
    type: "IPV4",
    reputation: "SUSPICIOUS",
    confidence: 84,
    first_seen: "2026-09-15",
    threat_actor: "Mirai Botnet Affiliate",
    malware: "SSH Scanner",
    country: "Netherlands",
    related_incidents: ["INC-00021"]
  }
];

export const INITIAL_ACTIONS: ResponseAction[] = [
  {
    id: "ACT-001",
    incident_number: "INC-00042",
    action_type: "ISOLATE_HOST",
    target_entity: "SERVER-04 (10.10.1.24)",
    recommended_by: "AI_RISK_AGENT",
    reasoning: "Potential active malware / C2 beaconing. Host network isolation cuts lateral traversal while keeping management socket active for forensic acquisition.",
    confidence: 94,
    status: "PENDING_APPROVAL",
    created_at: "2026-09-30 10:45:00 EAT"
  },
  {
    id: "ACT-002",
    incident_number: "INC-00042",
    action_type: "BLOCK_IP",
    target_entity: "185.220.101.5",
    recommended_by: "AI_THREAT_INTEL_AGENT",
    reasoning: "Confirmed Cobalt Strike C2 server on Ethio-CERT blacklist. Egress and ingress drop recommended across perimeter gateways.",
    confidence: 98,
    status: "PENDING_APPROVAL",
    created_at: "2026-09-30 10:46:00 EAT"
  },
  {
    id: "ACT-003",
    incident_number: "INC-00042",
    action_type: "REVOKE_TOKEN",
    target_entity: "Account: administrator",
    recommended_by: "AI_EVENT_ANALYSIS_AGENT",
    reasoning: "High likelihood of interactive credential compromise; invalidate all active Kerberos and OAuth tickets.",
    confidence: 91,
    status: "PENDING_APPROVAL",
    created_at: "2026-09-30 10:48:00 EAT"
  }
];
