import React, { useState } from 'react';
import { 
  GitMerge, 
  Play, 
  CheckCircle2, 
  ShieldAlert, 
  Binary, 
  Bot, 
  Lock, 
  FileText, 
  ArrowRight, 
  CheckSquare, 
  Fingerprint,
  RefreshCw,
  Sparkles,
  Server,
  UserCheck,
  Globe,
  Radio,
  HardDrive
} from 'lucide-react';

interface Scenario {
  id: string;
  name: string;
  category: string;
  badgeColor: string;
  targetUser: string;
  targetAsset: string;
  vector: string;
  c2OrDestination: string;
  riskScore: number;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM';
  sigmaRule: string;
  mitreTechnique: string;
  ecsData: Record<string, unknown>;
  evidence: Array<{
    id: string;
    title: string;
    confidence: string;
    description: string;
  }>;
  aiInsights: Array<{
    agent: string;
    analysis: string;
  }>;
  soarActions: Array<{
    id: string;
    action: string;
    risk: 'HIGH RISK' | 'LOW RISK';
    description: string;
  }>;
  auditRecord: {
    auditId: string;
    incidentId: string;
    analyst: string;
    approver: string;
    sha256: string;
  };
}

const PRESET_SCENARIOS: Scenario[] = [
  {
    id: 'phishing-telebirr',
    name: '1. Phishing Email with Malicious Link (Telebirr Impersonation)',
    category: 'Email Security',
    badgeColor: 'text-[#FF1744] bg-[#FF1744]/20',
    targetUser: 'dawit.mengistu (Finance Dept)',
    targetAsset: 'WORKSTATION-FIN-09 (10.10.1.24)',
    vector: 'telebirr-bonus.xyz (Hard SPF/DKIM Fail)',
    c2OrDestination: '185.220.101.5:443 (Cobalt Strike C2)',
    riskScore: 92,
    severity: 'CRITICAL',
    sigmaRule: 'SIGMA-EML-001 (Spearphishing Attachment/Link)',
    mitreTechnique: 'T1566.002 (Phishing: Spearphishing Link)',
    ecsData: {
      "@timestamp": "2026-09-30T10:42:00Z",
      "event": {
        "kind": "alert",
        "category": ["email", "threat_intel"],
        "type": ["phishing_email", "brand_impersonation"],
        "action": "blocked_by_gateway",
        "outcome": "failure"
      },
      "source": { "ip": "196.188.99.12", "port": 49210, "domain": "telebirr-bonus.xyz" },
      "destination": { "ip": "10.10.1.24", "port": 25, "user": "dawit.mengistu@cbe.com.et" },
      "email": {
        "from": "support@telebirr-bonus.xyz",
        "reply_to": "phisher-collector@gmail.com",
        "subject": "URGENT: ቴሌብር 10,000 ብር የሽልማት አሸናፊ - አሁኑኑ ያረጋግጡ",
        "spf": "fail",
        "dkim": "fail",
        "dmarc": "fail"
      },
      "observables": [
        { "type": "domain", "value": "telebirr-bonus.xyz", "reputation": "MALICIOUS" },
        { "type": "url", "value": "http://196.188.99.12/claim-prize/login.php", "risk_weight": 35 }
      ]
    },
    evidence: [
      {
        id: 'EV-001',
        title: 'Cryptographic SPF/DKIM Mismatch',
        confidence: '99.4%',
        description: 'RFC-822 header Authentication-Results returned hard failure for sender IP 196.188.99.12 against SPF record.'
      },
      {
        id: 'EV-002',
        title: 'Regional Financial Brand Abuse',
        confidence: '94.8%',
        description: 'Amharic NLP identified Telebirr brand name in Amharic (የቴሌብር ሽልማት) sent from unauthorized foreign domain.'
      },
      {
        id: 'EV-003',
        title: 'Raw IPv4 Egress Beaconing',
        confidence: '96.2%',
        description: 'Network socket telemetry confirmed outbound connection on port 443 to known Cobalt Strike C2 (185.220.101.5).'
      }
    ],
    aiInsights: [
      { agent: '1. Event Analysis Agent', analysis: 'Deconstructed initial inbound SMTP vector into MITRE ATT&CK technique T1566.002 (Spearphishing Link).' },
      { agent: '2. Threat Intelligence Agent', analysis: 'Cross-referenced extracted C2 IP 185.220.101.5 against Ethio-CERT blacklist (Confirmed 98% malicious).' },
      { agent: '3. Correlation Agent', analysis: 'Linked recipient user dawit.mengistu with WORKSTATION-FIN-09 PowerShell execution within a 4-minute time window.' },
      { agent: '4. Investigation Agent', analysis: 'Root cause established: Credential harvesting link clicked from email client, leading to secondary stage delivery.' },
      { agent: '5. Risk Assessment Agent', analysis: 'Asset Criticality (Core Banking +25) + Privileged User (+20) + Malicious IOC (+25) + Brand Spoof (+20) = 92/100 (CRITICAL).' }
    ],
    soarActions: [
      { id: 'act_isolate_ws', action: 'ISOLATE_HOST: WORKSTATION-FIN-09 (10.10.1.24)', risk: 'HIGH RISK', description: 'Cuts lateral network propagation while keeping SOC forensic connection alive.' },
      { id: 'act_block_c2', action: 'BLOCK_IP: 185.220.101.5 on Perimeter Gateways', risk: 'LOW RISK', description: 'Drops all outbound network beaconing to Cobalt Strike C2 server.' }
    ],
    auditRecord: {
      auditId: 'aud_7f19b2e8a1',
      incidentId: 'INC-00042',
      analyst: 'Dawit Mengistu (ID: SEC-ETH-04)',
      approver: 'Sara Yohannes (ID: SEC-ETH-09)',
      sha256: 'b74557f489f60126dca93785996abbe178b9cfbc3bd132b0351cbb22a978d183'
    }
  },
  {
    id: 'kerberoasting-ad',
    name: '2. Account Compromise & Kerberoasting (Active Directory)',
    category: 'Identity & Access',
    badgeColor: 'text-[#FF1744] bg-[#FF1744]/20',
    targetUser: 'svc_backup -> Escalated to DomainAdmin',
    targetAsset: 'DC-AD01.cbe.internal (10.10.0.5)',
    vector: 'Kerberos TGS-REQ with RC4 (0x17) Downgrade',
    c2OrDestination: '10.10.2.88 (Compromised Jumpbox)',
    riskScore: 96,
    severity: 'CRITICAL',
    sigmaRule: 'SIGMA-WIN-009 (Kerberoasting Service Ticket Request)',
    mitreTechnique: 'T1558.003 (Steal or Forge Kerberos Tickets: Kerberoasting)',
    ecsData: {
      "@timestamp": "2026-09-30T11:15:22Z",
      "event": {
        "kind": "alert",
        "category": ["iam", "authentication"],
        "type": ["privilege_escalation", "credential_theft"],
        "action": "kerberos_tgs_request",
        "outcome": "success"
      },
      "winlog": {
        "event_id": 4769,
        "service_name": "MSSQLSvc/db01.cbe.internal:1433",
        "ticket_encryption_type": "0x17",
        "ticket_options": "0x40810000"
      },
      "user": { "name": "svc_backup", "domain": "CBE", "id": "S-1-5-21-39281-500" },
      "source": { "ip": "10.10.2.88", "host": "MGMT-JUMPBOX-01" },
      "destination": { "ip": "10.10.0.5", "host": "DC-AD01" }
    },
    evidence: [
      {
        id: 'EV-101',
        title: 'RC4 Ticket Encryption Downgrade',
        confidence: '98.7%',
        description: 'Event 4769 requested service ticket with weak RC4-HMAC (0x17) cipher rather than modern AES-256.'
      },
      {
        id: 'EV-102',
        title: 'Anomalous High-Volume TGS Bursts',
        confidence: '95.1%',
        description: '14 unique High-Privilege Service Principal Names requested within 18 seconds from non-standard workstation.'
      },
      {
        id: 'EV-103',
        title: 'Shadow Copy Access via NTDS.dit',
        confidence: '99.0%',
        description: 'Volume shadow copy creation initiated by parent process powershell.exe targeting domain controller database.'
      }
    ],
    aiInsights: [
      { agent: '1. Event Analysis Agent', analysis: 'Detected classic Kerberoasting attack pattern mapped to MITRE ATT&CK T1558.003.' },
      { agent: '2. Threat Intelligence Agent', analysis: 'Jumpbox source IP 10.10.2.88 was previously flagged in lateral movement reconnaissance.' },
      { agent: '3. Correlation Agent', analysis: 'Correlated service ticket extraction with sudden admin group membership changes in Active Directory.' },
      { agent: '4. Investigation Agent', analysis: 'Backup service account was compromised via reused NTLM hash dumped from memory.' },
      { agent: '5. Risk Assessment Agent', analysis: 'Domain Controller Threat (+40) + DomainAdmin Escalation (+30) + Ticket Downgrade (+26) = 96/100 (CRITICAL).' }
    ],
    soarActions: [
      { id: 'act_reset_krbtgt', action: 'REVOKE_TICKETS: Reset KRBTGT Password & Force Ticket Invalidation', risk: 'HIGH RISK', description: 'Invalidates all golden/silver tickets across the CBE Active Directory forest.' },
      { id: 'act_lock_svc', action: 'LOCK_ACCOUNT: Disable Compromised svc_backup Account', risk: 'LOW RISK', description: 'Prevents ongoing credential reuse and shuts down lateral movement sessions.' }
    ],
    auditRecord: {
      auditId: 'aud_ad331902c9',
      incidentId: 'INC-00043',
      analyst: 'Abebe Kebede (ID: SEC-ETH-01)',
      approver: 'Dawit Mengistu (ID: SEC-ETH-04)',
      sha256: '9f81a7b45c23d091e8471b3e8a45f912cd3104e8b91929384756cba981023d84'
    }
  },
  {
    id: 'typosquat-brand',
    name: '3. Typosquatting & Look-Alike Brand Impersonation (openSquat Engine)',
    category: 'Brand Defense',
    badgeColor: 'text-[#F59E0B] bg-[#F59E0B]/20',
    targetUser: 'Public Ethio Telecom Customers & Agents',
    targetAsset: 'telebirr.et Brand Equity & User Trust',
    vector: 'telebiir-et.com (Double Character Insertion)',
    c2OrDestination: '103.224.212.222 (Bulletproof Offshore Host)',
    riskScore: 88,
    severity: 'HIGH',
    sigmaRule: 'SIGMA-DNS-004 (Look-Alike Domain Generation)',
    mitreTechnique: 'T1583.001 (Acquire Infrastructure: Domains)',
    ecsData: {
      "@timestamp": "2026-09-30T09:12:45Z",
      "event": {
        "kind": "alert",
        "category": ["dns", "threat_intel"],
        "type": ["typosquatting", "combosquatting"],
        "action": "sinkhole_recommended",
        "outcome": "detected"
      },
      "target_domain": "telebirr.et",
      "squatted_domain": "telebiir-et.com",
      "algorithm": "double_character_insertion",
      "levenshtein_distance": 1,
      "dns": {
        "resolved_ip": "103.224.212.222",
        "mx_records": ["mail.telebiir-et.com"],
        "asn": "AS45102 Bulletproof Network",
        "country": "Offshore"
      },
      "tls": {
        "issuer": "Let's Encrypt Authority X3",
        "valid_from": "2026-09-30T06:00:00Z"
      }
    },
    evidence: [
      {
        id: 'EV-201',
        title: 'Levenshtein Distance 1 from telebirr.et',
        confidence: '99.9%',
        description: 'Algorithmic string distance of 1 with identical phonetic pronunciation targeting mobile banking users.'
      },
      {
        id: 'EV-202',
        title: 'Active MX Mail Exchanger Configured',
        confidence: '93.4%',
        description: 'DNS MX records active and accepting mail, indicating preparation for inbound phishing and CEO fraud.'
      },
      {
        id: 'EV-203',
        title: 'Fresh TLS Certificate Issued Today',
        confidence: '97.0%',
        description: 'Automated ACME Let\'s Encrypt certificate obtained under 3 hours ago to bypass browser warning badges.'
      }
    ],
    aiInsights: [
      { agent: '1. Event Analysis Agent', analysis: 'openSquat engine generated permutation matched live DNS resolution on high-risk bulletproof hosting.' },
      { agent: '2. Threat Intelligence Agent', analysis: 'Hosting IP 103.224.212.222 has 23 prior domain takedown notices filed with international registrars.' },
      { agent: '3. Correlation Agent', analysis: 'Linked to recent phishing campaign targeting Ethio Telecom retail franchise agents.' },
      { agent: '4. Investigation Agent', analysis: 'Site clone matches CBE/Telebirr portal login screen pixel-for-pixel with harvested credential POST endpoints.' },
      { agent: '5. Risk Assessment Agent', analysis: 'Brand Severity (+35) + Active Mail Servers (+30) + Offshore ASN (+23) = 88/100 (HIGH).' }
    ],
    soarActions: [
      { id: 'act_sinkhole_dns', action: 'DNS_SINKHOLE: Point telebiir-et.com to 127.0.0.1 on Internal Resolvers', risk: 'LOW RISK', description: 'Blocks all corporate endpoints from resolving or communicating with the spoofed domain.' },
      { id: 'act_registrar_takedown', action: 'SUBMIT_TAKEDOWN: Transmit Evidence Dossier to Registrar & Ethio-CERT', risk: 'LOW RISK', description: 'Initiates formal UDRP / abuse suspension process with registrar.' }
    ],
    auditRecord: {
      auditId: 'aud_sq91823ab4',
      incidentId: 'INC-00044',
      analyst: 'Tigist Haile (ID: SEC-ETH-07)',
      approver: 'Dawit Mengistu (ID: SEC-ETH-04)',
      sha256: 'a129d38402fbbcd9817293847aef928139401726354819203948571625341029'
    }
  },
  {
    id: 'impossible-travel',
    name: '4. Suspicious Off-Hours Multi-Geo Login (Impossible Travel)',
    category: 'Cloud Identity',
    badgeColor: 'text-[#F59E0B] bg-[#F59E0B]/20',
    targetUser: 'sara.yohannes (Cloud Infrastructure Admin)',
    targetAsset: 'AWS IAM / Azure Active Directory Tenant',
    vector: 'Addis Ababa (08:30) vs Frankfurt (08:37) (5,340 km in 7m)',
    c2OrDestination: '45.133.1.99 (Frankfurt Tor Exit Node)',
    riskScore: 85,
    severity: 'HIGH',
    sigmaRule: 'SIGMA-IAM-003 (Impossible Velocity Geolocation Anomaly)',
    mitreTechnique: 'T1078.004 (Valid Accounts: Cloud Accounts)',
    ecsData: {
      "@timestamp": "2026-09-30T08:37:12Z",
      "event": {
        "kind": "alert",
        "category": ["iam", "audit"],
        "type": ["anomalous_login", "impossible_travel"],
        "action": "session_created",
        "outcome": "flagged"
      },
      "user": { "name": "sara.yohannes@telecom.et", "roles": ["Global Admin", "Cloud Architect"] },
      "logins": [
        { "timestamp": "08:30:00Z", "ip": "196.188.12.4", "city": "Addis Ababa", "country": "ET", "asn": "AS24757" },
        { "timestamp": "08:37:12Z", "ip": "45.133.1.99", "city": "Frankfurt", "country": "DE", "asn": "AS9009" }
      ],
      "delta_minutes": 7.2,
      "calculated_speed_kmh": 44500
    },
    evidence: [
      {
        id: 'EV-301',
        title: 'Impossible Velocity of 44,500 km/h',
        confidence: '99.8%',
        description: 'Physical transit distance between Addis Ababa and Frankfurt cannot be covered in 7.2 minutes under any terrestrial flight speeds.'
      },
      {
        id: 'EV-302',
        title: 'High-Risk Anonymizing VPN / Tor Node',
        confidence: '96.5%',
        description: 'Foreign IP 45.133.1.99 matches known Tor exit node telemetry and bulletproof anonymizer feed.'
      },
      {
        id: 'EV-303',
        title: 'MFA Push Fatigue / Spam Anomaly',
        confidence: '92.0%',
        description: 'User prompt showed 6 rapid MFA push denials followed by an unexpected approval from Frankfurt.'
      }
    ],
    aiInsights: [
      { agent: '1. Event Analysis Agent', analysis: 'Impossible travel anomaly triggered by concurrent sessions in two disparate geographic continents.' },
      { agent: '2. Threat Intelligence Agent', analysis: 'Frankfurt source IP flagged on AbuseIPDB with 87% fraud score.' },
      { agent: '3. Correlation Agent', analysis: 'Session established directly after MFA push bombing pattern indicative of token theft.' },
      { agent: '4. Investigation Agent', analysis: 'Infostealer malware on personal contractor laptop leaked session cookie and primary refresh token (PRT).' },
      { agent: '5. Risk Assessment Agent', analysis: 'Privileged Role (Global Admin +35) + Tor Source (+30) + Velocity Anomaly (+20) = 85/100 (HIGH).' }
    ],
    soarActions: [
      { id: 'act_revoke_tokens', action: 'REVOKE_SESSIONS: Invalidate All Active OAuth Tokens & PRT Cookies', risk: 'HIGH RISK', description: 'Instantly terminates active cloud console sessions across AWS, Azure, and Google Cloud.' },
      { id: 'act_geofence_mfa', action: 'ENFORCE_GEOFENCE: Restrict Admin Logins to Ethiopian AS24757 IP Prefixes', risk: 'LOW RISK', description: 'Blocks foreign IP authentications until physical identity verification completes.' }
    ],
    auditRecord: {
      auditId: 'aud_geo0192837f',
      incidentId: 'INC-00045',
      analyst: 'Sara Yohannes (ID: SEC-ETH-09)',
      approver: 'Dawit Mengistu (ID: SEC-ETH-04)',
      sha256: 'c3b8192a01928384756192837465019283746510293847561928374650192837'
    }
  },
  {
    id: 'ransomware-lateral',
    name: '5. Ransomware / Cobalt Strike Lateral Movement (SERVER-04)',
    category: 'Endpoint EDR',
    badgeColor: 'text-[#FF1744] bg-[#FF1744]/20',
    targetUser: 'NT AUTHORITY\\SYSTEM',
    targetAsset: 'SERVER-04 (10.10.1.24 - Core DB)',
    vector: 'WMI Remote Exec + PowerShell Obfuscated Payload',
    c2OrDestination: 'vssadmin delete shadows /all /quiet',
    riskScore: 98,
    severity: 'CRITICAL',
    sigmaRule: 'SIGMA-EDR-012 (Volume Shadow Copy Deletion & In-Memory Injection)',
    mitreTechnique: 'T1490 (Inhibit System Recovery)',
    ecsData: {
      "@timestamp": "2026-09-30T12:04:19Z",
      "event": {
        "kind": "alert",
        "category": ["endpoint", "malware"],
        "type": ["ransomware_precursor", "lateral_movement"],
        "action": "process_spawn_blocked",
        "outcome": "containment_required"
      },
      "process": {
        "name": "powershell.exe",
        "pid": 4812,
        "parent_name": "wmic.exe",
        "command_line": "powershell.exe -enc SQBFAFgA... (Base64)",
        "child_command": "vssadmin.exe delete shadows /all /quiet"
      },
      "host": { "name": "SERVER-04", "ip": "10.10.1.24", "os": "Windows Server 2022" },
      "threat": { "framework": "MITRE ATT&CK", "tactic": "Impact", "technique": "T1490" }
    },
    evidence: [
      {
        id: 'EV-401',
        title: 'SIGMA-WIN-003 Obfuscated PowerShell Trigger',
        confidence: '99.6%',
        description: 'Decoded Base64 payload revealed in-memory reflection DLL injection invoking Cobalt Strike beacon.'
      },
      {
        id: 'EV-402',
        title: 'Shadow Copy Invalidation Command',
        confidence: '99.9%',
        description: 'Process telemetry captured invocation of `vssadmin.exe delete shadows /all /quiet` designed to prevent ransomware recovery.'
      },
      {
        id: 'EV-403',
        title: 'Rapid High-Frequency SMB File Renaming',
        confidence: '97.8%',
        description: 'File system driver reported 320 file extension alterations to `.locked` in 4 seconds.'
      }
    ],
    aiInsights: [
      { agent: '1. Event Analysis Agent', analysis: 'Ransomware deployment phase confirmed: Volume Shadow destruction followed by high-speed encryption loop.' },
      { agent: '2. Threat Intelligence Agent', analysis: 'Binary hash matched BlackCat / ALPHV ransomware variant tracked by international cybersecurity certs.' },
      { agent: '3. Correlation Agent', analysis: 'Execution originated from compromised workstation WORKSTATION-FIN-09 via administrative WMI shares.' },
      { agent: '4. Investigation Agent', analysis: 'Attacker possessed Domain Admin credentials acquired through Kerberoasting.' },
      { agent: '5. Risk Assessment Agent', analysis: 'Production Impact (+45) + System Recovery Invalidation (+30) + Ransomware (+23) = 98/100 (CRITICAL).' }
    ],
    soarActions: [
      { id: 'act_kill_process', action: 'TERMINATE_PROCESS: Kill PID 4812 & Freeze Memory Dump for Forensics', risk: 'HIGH RISK', description: 'Stops the ransomware encryption thread instantly and preserves RAM for volatile analysis.' },
      { id: 'act_isolate_server', action: 'EDR_ISOLATE: Isolate SERVER-04 from Internal Subnet', risk: 'HIGH RISK', description: 'Severs SMB / RPC communication to prevent propagation across banking subnets.' }
    ],
    auditRecord: {
      auditId: 'aud_edr9928123c',
      incidentId: 'INC-00046',
      analyst: 'Abebe Kebede (ID: SEC-ETH-01)',
      approver: 'Sara Yohannes (ID: SEC-ETH-09)',
      sha256: 'ee44918237465019283746501928374650192837465019283746501928374651'
    }
  },
  {
    id: 'osint-surface',
    name: '6. External Attack Surface Exposure (SpiderFoot / OSINT Recon)',
    category: 'Perimeter Defense',
    badgeColor: 'text-[#00D9FF] bg-[#00D9FF]/20',
    targetUser: 'SecOps Infrastructure Team',
    targetAsset: 'infratest.telecom.et (196.188.45.10)',
    vector: 'Exposed Port 3389 (RDP) & Unauthenticated Jenkins (8080)',
    c2OrDestination: 'Ethio Telecom ASN AS24757',
    riskScore: 90,
    severity: 'HIGH',
    sigmaRule: 'SIGMA-EXT-007 (Public Administrative Interface Exposure)',
    mitreTechnique: 'T1190 (Exploit Public-Facing Application)',
    ecsData: {
      "@timestamp": "2026-09-30T07:22:15Z",
      "event": {
        "kind": "alert",
        "category": ["osint", "surface_recon"],
        "type": ["port_exposure", "credential_leak"],
        "action": "acl_remediation_required",
        "outcome": "exposed"
      },
      "target": { "domain": "infratest.telecom.et", "ip": "196.188.45.10", "asn": "AS24757" },
      "ports_open": [
        { "port": 3389, "service": "ms-wbt-server", "state": "open", "vulnerability": "CVE-2019-0708 (BlueKeep susceptible)" },
        { "port": 8080, "service": "http-jenkins", "state": "open", "anonymous_exec": true }
      ],
      "tls": {
        "version": "TLS 1.0 (Deprecated)",
        "cipher": "DES-CBC3-SHA (Weak)"
      }
    },
    evidence: [
      {
        id: 'EV-501',
        title: 'Publicly Exposed RDP Port 3389 without NLA',
        confidence: '99.5%',
        description: 'Direct internet reachable Remote Desktop service on Ethio Telecom IP prefix lacking Network Level Authentication.'
      },
      {
        id: 'EV-502',
        title: 'Unauthenticated Jenkins CI/CD Dashboard',
        confidence: '98.9%',
        description: 'Public HTTP 8080 endpoint permits unauthenticated script execution (/script) leading to instant remote code execution.'
      },
      {
        id: 'EV-503',
        title: 'Exposed Git Environment Variables',
        confidence: '94.2%',
        description: 'Web root contains accessible .env file referencing production database connection strings.'
      }
    ],
    aiInsights: [
      { agent: '1. Event Analysis Agent', analysis: 'Surface reconnaissance uncovered two critical internet-facing footholds directly into the perimeter.' },
      { agent: '2. Threat Intelligence Agent', analysis: 'Shodan and Censys crawlers already have recorded this IP as active and vulnerable.' },
      { agent: '3. Correlation Agent', analysis: 'Subdomain belongs to internal staging environment accidentally mapped to public ASN IP range.' },
      { agent: '4. Investigation Agent', analysis: 'DevOps deployment misconfigured firewall security group during weekend maintenance.' },
      { agent: '5. Risk Assessment Agent', analysis: 'Critical Foothold Potential (+40) + Public Exposure (+30) + Weak Ciphers (+20) = 90/100 (HIGH).' }
    ],
    soarActions: [
      { id: 'act_firewall_drop', action: 'FIREWALL_DROP: Deploy Edge ACL Dropping Ports 3389 & 8080 from WAN', risk: 'LOW RISK', description: 'Blocks global internet access while keeping management accessible via internal VPN.' },
      { id: 'act_notify_devops', action: 'DISPATCH_ALERT: Rotate Exposed CI/CD DB Credentials & Revoke Tokens', risk: 'LOW RISK', description: 'Notifies SecOps and resets credentials found inside .env file.' }
    ],
    auditRecord: {
      auditId: 'aud_sur9082310b',
      incidentId: 'INC-00047',
      analyst: 'Tigist Haile (ID: SEC-ETH-07)',
      approver: 'Abebe Kebede (ID: SEC-ETH-01)',
      sha256: '778811223344556677889900aabbccddeeff00112233445566778899aabbccdd'
    }
  }
];

interface UnifiedPipelineViewProps {
  onNotify?: (msg: string) => void;
}

export const UnifiedPipelineView: React.FC<UnifiedPipelineViewProps> = ({ onNotify }) => {
  const [selectedScenarioIndex, setSelectedScenarioIndex] = useState<number>(0);
  const [activeStep, setActiveStep] = useState<number>(0);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [selectedSubTab, setSelectedSubTab] = useState<'graph' | 'ecs' | 'evidence' | 'ai' | 'soar' | 'audit'>('graph');
  const [approvedActions, setApprovedActions] = useState<Record<string, boolean>>({});

  const scenario = PRESET_SCENARIOS[selectedScenarioIndex];

  const PIPELINE_STEPS = [
    { id: 1, title: 'Event Ingestion', desc: `${scenario.category} telemetry received`, icon: FileText, color: 'text-[#00D9FF]' },
    { id: 2, title: 'ECS Normalization', desc: 'Mapped to canonical Elastic Common Schema', icon: Binary, color: 'text-[#22C55E]' },
    { id: 3, title: 'SIGMA Detection', desc: `Matched ${scenario.sigmaRule.split(' ')[0]}`, icon: ShieldAlert, color: 'text-[#F59E0B]' },
    { id: 4, title: 'Graph Correlation', desc: 'Correlated User + Asset + IOC nodes', icon: GitMerge, color: 'text-[#00D9FF]' },
    { id: 5, title: '7 AI Agents Layer', desc: 'Root cause analysis with Evidence Grounding', icon: Bot, color: 'text-[#FF1744]' },
    { id: 6, title: 'Dual-Custody SOAR', desc: 'Containment actions pending analyst review', icon: CheckSquare, color: 'text-[#F59E0B]' },
    { id: 7, title: 'Immutable Audit', desc: 'Cryptographic SHA-256 block recorded', icon: Lock, color: 'text-[#22C55E]' }
  ];

  const handleSelectScenario = (index: number) => {
    setSelectedScenarioIndex(index);
    setActiveStep(0);
    setApprovedActions({});
    if (onNotify) {
      onNotify(`Loaded Preset Scenario: ${PRESET_SCENARIOS[index].name}`);
    }
  };

  const handleRunFullChain = () => {
    setIsRunning(true);
    setActiveStep(1);
    const interval = setInterval(() => {
      setActiveStep(prev => {
        if (prev >= 7) {
          clearInterval(interval);
          setIsRunning(false);
          if (onNotify) {
            onNotify(`Unified 7-Stage Pipeline completed successfully for ${scenario.auditRecord.incidentId}`);
          }
          return 7;
        }
        return prev + 1;
      });
    }, 600);
  };

  const handleApproveAction = (actionId: string, actionName: string) => {
    setApprovedActions(prev => ({ ...prev, [actionId]: true }));
    if (onNotify) {
      onNotify(`Dual-Custody Authorization: Approved "${actionName}"`);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-3 border-b border-[#1E2A38] gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-[#00D9FF]/20 text-[#00D9FF] uppercase tracking-wider">
              Common Security Graph Engine
            </span>
            <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-[#22C55E]/20 text-[#22C55E] uppercase tracking-wider">
              Unified Vertical Slice
            </span>
            <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-purple-500/20 text-purple-400 uppercase tracking-wider flex items-center space-x-1">
              <Sparkles className="w-3 h-3 mr-0.5" />
              <span>Interactive Scenarios</span>
            </span>
          </div>
          <h1 className="text-xl font-bold text-white mt-1">Unified Security Pipeline & Attack Graph</h1>
          <p className="text-xs text-[#7D8A99]">
            The complete end-to-end workflow where every capability feeds the same: Event → Evidence → Alert → Incident → 7 AI Agents → SOAR Response → Audit Trail
          </p>
        </div>

        <button
          onClick={handleRunFullChain}
          disabled={isRunning}
          className="flex items-center space-x-2 px-5 py-2.5 bg-[#00D9FF] hover:bg-[#00B8D9] text-black font-bold text-xs rounded-lg transition-all shadow-lg shadow-[#00D9FF]/10 cursor-pointer disabled:opacity-50"
        >
          {isRunning ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span>Executing Pipeline Step {activeStep}/7...</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4 fill-current" />
              <span>Execute End-to-End Vertical Slice</span>
            </>
          )}
        </button>
      </div>

      {/* Scenario Preset Selector Cards */}
      <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="text-xs font-bold text-white flex items-center space-x-2">
            <Radio className="w-3.5 h-3.5 text-[#00D9FF]" />
            <span>Select Demonstration Attack Scenario (6 Comprehensive Presets):</span>
          </div>
          <span className="text-[10px] text-[#7D8A99]">Click any scenario to load its graph & telemetry</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
          {PRESET_SCENARIOS.map((sc, idx) => {
            const isSelected = idx === selectedScenarioIndex;
            return (
              <button
                key={sc.id}
                onClick={() => handleSelectScenario(idx)}
                className={`p-3 rounded-lg border text-left transition-all cursor-pointer ${
                  isSelected 
                    ? 'border-[#00D9FF] bg-[#00D9FF]/10 ring-1 ring-[#00D9FF]' 
                    : 'border-[#1E2A38] bg-[#070B12] hover:border-[#7D8A99]/50'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${sc.badgeColor}`}>
                    {sc.category}
                  </span>
                  <span className="text-[10px] font-mono text-[#7D8A99]">
                    Risk: <strong className="text-white">{sc.riskScore}/100</strong>
                  </span>
                </div>
                <div className="text-xs font-bold text-white truncate">{sc.name}</div>
                <div className="text-[10px] text-[#7D8A99] truncate mt-0.5 font-mono">{sc.mitreTechnique}</div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Pipeline Stepper Progression Banner */}
      <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-5">
        <div className="text-xs font-bold text-white mb-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span>7-Stage Pipeline Lifecycle Progression:</span>
            <span className="text-white font-mono text-[11px] px-2 py-0.5 rounded bg-[#1E2A38]">
              {scenario.auditRecord.incidentId} • {scenario.severity} ({scenario.riskScore}/100)
            </span>
          </div>
          <span className="text-[11px] text-[#00D9FF] font-mono">
            {activeStep === 0 ? 'Ready to execute' : activeStep === 7 ? 'Pipeline Completed (100%)' : `Executing Stage ${activeStep} of 7...`}
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-7 gap-3">
          {PIPELINE_STEPS.map((step) => {
            const Icon = step.icon;
            const isCompleted = activeStep >= step.id;
            const isCurrent = activeStep === step.id;

            return (
              <div 
                key={step.id} 
                className={`p-3 rounded-lg border text-left transition-all ${
                  isCurrent 
                    ? 'border-[#00D9FF] bg-[#00D9FF]/10 ring-1 ring-[#00D9FF]' 
                    : isCompleted 
                    ? 'border-[#22C55E]/40 bg-[#0D131C]' 
                    : 'border-[#1E2A38] bg-[#070B12] opacity-60'
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[10px] font-mono font-bold text-[#7D8A99]">STEP 0{step.id}</span>
                  {isCompleted ? (
                    <CheckCircle2 className="w-3.5 h-3.5 text-[#22C55E]" />
                  ) : (
                    <Icon className={`w-3.5 h-3.5 ${step.color}`} />
                  )}
                </div>
                <div className="font-bold text-white text-[12px] truncate">{step.title}</div>
                <div className="text-[10px] text-[#7D8A99] line-clamp-2 mt-0.5">{step.desc}</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Sub-Tabs: Graph, ECS Event, Evidence Trail, AI Investigation, SOAR, Audit */}
      <div className="flex items-center space-x-1 border-b border-[#1E2A38] pb-1 overflow-x-auto text-xs">
        <button
          onClick={() => setSelectedSubTab('graph')}
          className={`px-3 py-2 rounded-t-lg font-bold transition-all cursor-pointer ${
            selectedSubTab === 'graph' ? 'bg-[#111923] text-[#00D9FF] border-b-2 border-[#00D9FF]' : 'text-[#7D8A99] hover:text-white'
          }`}
        >
          Common Security Graph
        </button>
        <button
          onClick={() => setSelectedSubTab('ecs')}
          className={`px-3 py-2 rounded-t-lg font-bold transition-all cursor-pointer ${
            selectedSubTab === 'ecs' ? 'bg-[#111923] text-[#00D9FF] border-b-2 border-[#00D9FF]' : 'text-[#7D8A99] hover:text-white'
          }`}
        >
          Canonical ECS Event
        </button>
        <button
          onClick={() => setSelectedSubTab('evidence')}
          className={`px-3 py-2 rounded-t-lg font-bold transition-all cursor-pointer ${
            selectedSubTab === 'evidence' ? 'bg-[#111923] text-[#00D9FF] border-b-2 border-[#00D9FF]' : 'text-[#7D8A99] hover:text-white'
          }`}
        >
          Evidence Grounding ({scenario.evidence[0].id})
        </button>
        <button
          onClick={() => setSelectedSubTab('ai')}
          className={`px-3 py-2 rounded-t-lg font-bold transition-all cursor-pointer ${
            selectedSubTab === 'ai' ? 'bg-[#111923] text-[#00D9FF] border-b-2 border-[#00D9FF]' : 'text-[#7D8A99] hover:text-white'
          }`}
        >
          7 AI Agents Synthesis
        </button>
        <button
          onClick={() => setSelectedSubTab('soar')}
          className={`px-3 py-2 rounded-t-lg font-bold transition-all cursor-pointer ${
            selectedSubTab === 'soar' ? 'bg-[#111923] text-[#00D9FF] border-b-2 border-[#00D9FF]' : 'text-[#7D8A99] hover:text-white'
          }`}
        >
          Dual-Custody SOAR Response
        </button>
        <button
          onClick={() => setSelectedSubTab('audit')}
          className={`px-3 py-2 rounded-t-lg font-bold transition-all cursor-pointer ${
            selectedSubTab === 'audit' ? 'bg-[#111923] text-[#00D9FF] border-b-2 border-[#00D9FF]' : 'text-[#7D8A99] hover:text-white'
          }`}
        >
          Tamper-Proof Audit Record
        </button>
      </div>

      {/* Tab 1: Common Security Graph */}
      {selectedSubTab === 'graph' && (
        <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-5 space-y-4">
          <div className="flex justify-between items-center">
            <div>
              <div className="text-sm font-bold text-white">Unified Attack Correlation Graph ({scenario.auditRecord.incidentId})</div>
              <div className="text-xs text-[#7D8A99]">Correlating entities across Vector → Targeted User → Impacted Asset → Destination IOC</div>
            </div>
            <span className={`text-[10px] px-2 py-0.5 rounded font-bold ${
              scenario.severity === 'CRITICAL' ? 'bg-[#FF1744]/20 text-[#FF1744]' : 'bg-[#F59E0B]/20 text-[#F59E0B]'
            }`}>
              {scenario.severity} Incident
            </span>
          </div>

          {/* ASCII / Visual Graph Map */}
          <div className="p-6 bg-[#070B12] border border-[#1E2A38] rounded-xl flex flex-col md:flex-row items-center justify-between gap-4 font-mono text-xs overflow-x-auto">
            <div className="p-3 bg-[#0D131C] border border-[#FF1744]/50 rounded-lg text-center w-full md:w-52">
              <div className="flex items-center justify-center space-x-1 text-[10px] text-[#FF1744] font-bold uppercase mb-1">
                <Globe className="w-3 h-3" />
                <span>ATTACK VECTOR</span>
              </div>
              <span className="text-white font-bold block truncate">{scenario.vector}</span>
              <span className="text-[#7D8A99] text-[10px] block mt-0.5">{scenario.category}</span>
            </div>

            <ArrowRight className="w-5 h-5 text-[#00D9FF] shrink-0 hidden md:block" />

            <div className="p-3 bg-[#0D131C] border border-[#F59E0B]/50 rounded-lg text-center w-full md:w-52">
              <div className="flex items-center justify-center space-x-1 text-[10px] text-[#F59E0B] font-bold uppercase mb-1">
                <UserCheck className="w-3 h-3" />
                <span>TARGETED IDENTITY</span>
              </div>
              <span className="text-white font-bold block truncate">{scenario.targetUser}</span>
              <span className="text-[#7D8A99] text-[10px] block mt-0.5">Account / Role</span>
            </div>

            <ArrowRight className="w-5 h-5 text-[#00D9FF] shrink-0 hidden md:block" />

            <div className="p-3 bg-[#0D131C] border border-[#00D9FF]/50 rounded-lg text-center w-full md:w-52">
              <div className="flex items-center justify-center space-x-1 text-[10px] text-[#00D9FF] font-bold uppercase mb-1">
                <Server className="w-3 h-3" />
                <span>PRIMARY ASSET</span>
              </div>
              <span className="text-white font-bold block truncate">{scenario.targetAsset}</span>
              <span className="text-[#7D8A99] text-[10px] block mt-0.5">Critical Infrastructure</span>
            </div>

            <ArrowRight className="w-5 h-5 text-[#00D9FF] shrink-0 hidden md:block" />

            <div className="p-3 bg-[#0D131C] border border-[#FF1744]/50 rounded-lg text-center w-full md:w-52">
              <div className="flex items-center justify-center space-x-1 text-[10px] text-[#FF1744] font-bold uppercase mb-1">
                <HardDrive className="w-3 h-3" />
                <span>C2 / TARGET IOC</span>
              </div>
              <span className="text-[#FF1744] font-bold block truncate">{scenario.c2OrDestination}</span>
              <span className="text-[#7D8A99] text-[10px] block mt-0.5">{scenario.mitreTechnique}</span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-2 text-xs">
            <div className="p-3 bg-[#0D131C] border border-[#1E2A38] rounded-lg">
              <span className="text-[#7D8A99] text-[11px] block">SIGMA Detection Rule:</span>
              <span className="text-white font-mono font-bold">{scenario.sigmaRule}</span>
            </div>
            <div className="p-3 bg-[#0D131C] border border-[#1E2A38] rounded-lg">
              <span className="text-[#7D8A99] text-[11px] block">MITRE ATT&CK Matrix:</span>
              <span className="text-[#00D9FF] font-mono font-bold">{scenario.mitreTechnique}</span>
            </div>
            <div className="p-3 bg-[#0D131C] border border-[#1E2A38] rounded-lg">
              <span className="text-[#7D8A99] text-[11px] block">Deterministic Risk Score:</span>
              <span className="text-[#FF1744] font-mono font-bold">{scenario.riskScore}/100 ({scenario.severity})</span>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Canonical ECS Event */}
      {selectedSubTab === 'ecs' && (
        <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-5 space-y-3">
          <div className="flex items-center justify-between">
            <div className="text-sm font-bold text-white">Canonical Elastic Common Schema (ECS) Representation</div>
            <span className="text-[10px] font-mono text-[#00D9FF]">Standardized Ingestion Schema</span>
          </div>
          <pre className="p-4 bg-[#070B12] border border-[#1E2A38] rounded-lg text-xs font-mono text-[#00D9FF] overflow-x-auto leading-relaxed">
            {JSON.stringify(scenario.ecsData, null, 2)}
          </pre>
        </div>
      )}

      {/* Tab 3: Evidence Grounding */}
      {selectedSubTab === 'evidence' && (
        <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-bold text-white">Traceable Evidence Grounding (Zero Hallucination Guarantee)</div>
              <div className="text-xs text-[#7D8A99]">Every AI conclusion must cite at least one explicit EV-* evidence identifier</div>
            </div>
            <span className="text-[10px] px-2 py-0.5 rounded bg-[#22C55E]/20 text-[#22C55E] font-bold">
              100% Grounded
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {scenario.evidence.map((ev) => (
              <div key={ev.id} className="p-4 bg-[#0D131C] border border-[#1E2A38] rounded-lg text-xs space-y-2">
                <div className="flex justify-between items-center">
                  <span className="font-mono font-bold text-[#00D9FF]">{ev.id}</span>
                  <span className="text-[10px] text-[#22C55E] font-bold">Conf: {ev.confidence}</span>
                </div>
                <div className="font-bold text-white">{ev.title}</div>
                <p className="text-[#7D8A99] text-[11px] leading-relaxed">
                  {ev.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 4: 7 AI Agents Synthesis */}
      {selectedSubTab === 'ai' && (
        <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-5 space-y-3">
          <div className="flex items-center justify-between">
            <div className="text-sm font-bold text-white">7 Specialized AI Agents Output Synthesis</div>
            <span className="text-[10px] font-mono text-[#00D9FF]">Multi-Agent Consensus</span>
          </div>
          <div className="space-y-2 text-xs">
            {scenario.aiInsights.map((insight, idx) => (
              <div key={idx} className="p-3 bg-[#0D131C] border border-[#1E2A38] rounded-lg">
                <strong className="text-[#00D9FF]">{insight.agent}:</strong> {insight.analysis}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 5: Dual-Custody SOAR Response */}
      {selectedSubTab === 'soar' && (
        <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-5 space-y-4">
          <div className="flex justify-between items-center">
            <div>
              <div className="text-sm font-bold text-white">Dual-Custody SOAR Playbook Execution</div>
              <div className="text-xs text-[#7D8A99]">High-impact containment actions require explicit Tier-2 SOC Analyst authorization</div>
            </div>
            <span className="text-[10px] px-2 py-0.5 rounded bg-[#F59E0B]/20 text-[#F59E0B] font-bold">
              Human-In-The-Loop Enforced
            </span>
          </div>

          <div className="space-y-3">
            {scenario.soarActions.map((act) => (
              <div key={act.id} className="p-4 bg-[#0D131C] border border-[#1E2A38] rounded-lg flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-bold text-white text-xs">{act.action}</span>
                    <span className={`text-[10px] px-1.5 py-0.2 rounded font-bold ${
                      act.risk === 'HIGH RISK' ? 'bg-[#FF1744]/20 text-[#FF1744]' : 'bg-[#00D9FF]/20 text-[#00D9FF]'
                    }`}>
                      {act.risk}
                    </span>
                  </div>
                  <div className="text-[11px] text-[#7D8A99] mt-0.5">
                    {act.description}
                  </div>
                </div>

                {approvedActions[act.id] ? (
                  <span className="px-3 py-1.5 rounded bg-[#22C55E]/20 text-[#22C55E] font-bold text-xs flex items-center space-x-1 shrink-0">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Approved & Enforced</span>
                  </span>
                ) : (
                  <button
                    onClick={() => handleApproveAction(act.id, act.action)}
                    className="px-4 py-2 bg-[#22C55E] hover:bg-[#16A34A] text-black font-bold text-xs rounded-lg transition-all cursor-pointer shrink-0"
                  >
                    Approve Action
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 6: Tamper-Proof Audit */}
      {selectedSubTab === 'audit' && (
        <div className="bg-[#111923] border border-[#1E2A38] rounded-xl p-5 space-y-3 font-mono text-xs">
          <div className="text-sm font-bold text-white font-sans flex items-center space-x-2">
            <Fingerprint className="w-4 h-4 text-[#22C55E]" />
            <span>Cryptographic Immutable Audit Log Entry</span>
          </div>
          <div className="p-4 bg-[#070B12] border border-[#1E2A38] rounded-lg space-y-2 text-[#E6EDF3]">
            <div><strong>Audit ID:</strong> {scenario.auditRecord.auditId}</div>
            <div><strong>Timestamp:</strong> 2026-09-30T10:42:15.892Z</div>
            <div><strong>Incident Promoted:</strong> {scenario.auditRecord.incidentId} ({scenario.severity})</div>
            <div><strong>Duty Analyst:</strong> {scenario.auditRecord.analyst}</div>
            <div><strong>Dual-Custody Approver:</strong> {scenario.auditRecord.approver}</div>
            <div>
              <strong>SHA256 Checksum:</strong> <span className="text-[#00D9FF] break-all">{scenario.auditRecord.sha256}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
