-- ==============================================================================
-- ETHIO-CYBERGUARD: Seed Data
-- Realistic Ethiopian Security Operations Center Simulation Data
-- ==============================================================================

-- 1. Organizations
INSERT INTO organizations (id, name, slug, sector, country) VALUES
('a0000000-0000-0000-0000-000000000001', 'Commercial Bank of Ethiopia (CBE)', 'cbe-et', 'Banking', 'Ethiopia'),
('a0000000-0000-0000-0000-000000000002', 'Ethio Telecom Enterprise', 'ethio-telecom', 'Telecom', 'Ethiopia'),
('a0000000-0000-0000-0000-000000000003', 'Addis Ababa University (AAU)', 'aau-edu', 'Education', 'Ethiopia');

-- 2. Users (Passwords hashed for demonstration)
INSERT INTO users (id, org_id, email, password_hash, full_name, role) VALUES
('b0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001', 'admin@cbe.com.et', '$2b$12$e8rO...simulated_hash', 'Abebe Bikila', 'SUPER_ADMIN'),
('b0000000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-000000000001', 'soc.lead@cbe.com.et', '$2b$12$e8rO...simulated_hash', 'Sara Yohannes', 'SOC_MANAGER'),
('b0000000-0000-0000-0000-000000000003', 'a0000000-0000-0000-0000-000000000001', 'analyst1@cbe.com.et', '$2b$12$e8rO...simulated_hash', 'Dawit Mengistu', 'SECURITY_ANALYST');

-- 3. Assets
INSERT INTO assets (id, org_id, hostname, ip_address, mac_address, os_type, os_version, criticality, department, physical_location) VALUES
('c0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001', 'SERVER-04', '10.10.1.24', '00:1A:2B:3C:4D:5E', 'WINDOWS', 'Windows Server 2022', 'CRITICAL', 'Core Banking Infrastructure', 'Addis Ababa HQ - Data Center Room 3'),
('c0000000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-000000000001', 'FW-PERIMETER-01', '197.156.70.1', '00:1A:2B:3C:4D:5F', 'NETWORK_DEVICE', 'Palo Alto PAN-OS 11', 'CRITICAL', 'Network Security', 'Addis Ababa Gateway Hub'),
('c0000000-0000-0000-0000-000000000003', 'a0000000-0000-0000-0000-000000000001', 'LAPTOP-FINANCE-22', '10.10.4.88', '00:1A:2B:3C:4D:60', 'WINDOWS', 'Windows 11 Enterprise', 'HIGH', 'Treasury & SWIFT Processing', 'Bole Branch Office');

-- 4. Threat Indicators
INSERT INTO threat_indicators (id, indicator_type, indicator_value, reputation, confidence_score, threat_actor, malware_family, campaign_name, source_feed, mitre_attack_id, tags) VALUES
('d0000000-0000-0000-0000-000000000001', 'IPV4', '185.220.101.5', 'MALICIOUS', 96, 'APT-CobaltStrike-Actor', 'Cobalt Strike Beacon', 'Operation Red Nile', 'Ethio-CERT Threat Intel', 'T1071.001', ARRAY['c2', 'tor-exit', 'banking-threat']),
('d0000000-0000-0000-0000-000000000002', 'DOMAIN', 'update-winsec-cloud.com', 'MALICIOUS', 92, 'Unknown Fin-Threat', 'Empire C2', 'Phishing Campaign Q3', 'AlienVault OTX', 'T1566.002', ARRAY['phishing', 'typosquatting']),
('d0000000-0000-0000-0000-000000000003', 'SHA256', '7d4b29c9103a89e924a2734ef0350d24fb4b3e6480c55ffc06a928db6928e469', 'MALICIOUS', 99, 'Lazarus Group', 'Mimikatz / LSASS Dumper', 'African Banking Sector Recon', 'VirusTotal Enterprise', 'T1003.001', ARRAY['credential-dumping', 'lsass']);

-- 5. Incidents
INSERT INTO incidents (id, incident_number, org_id, title, description, severity, status, risk_score, affected_asset_id, assigned_to, first_seen, last_activity) VALUES
('e0000000-0000-0000-0000-000000000001', 'INC-00042', 'a0000000-0000-0000-0000-000000000001', 'Suspicious Obfuscated PowerShell Activity & C2 Beaconing', 'Privileged service account initiated hidden PowerShell process with base64 encoded command, followed by outbound beaconing to known malicious C2 IP 185.220.101.5.', 'CRITICAL', 'INVESTIGATING', 92, 'c0000000-0000-0000-0000-000000000001', 'b0000000-0000-0000-0000-000000000003', '2026-09-30 10:42:00+03', '2026-09-30 11:18:00+03'),
('e0000000-0000-0000-0000-000000000002', 'INC-00021', 'a0000000-0000-0000-0000-000000000001', 'Perimeter Gateway Distributed SSH & RDP Brute Force', 'Over 1,200 failed authentication attempts detected within 4 minutes originating from distributed IP ranges targeting perimeter firewall management interface.', 'HIGH', 'OPEN', 78, 'c0000000-0000-0000-0000-000000000002', 'b0000000-0000-0000-0000-000000000003', '2026-09-30 09:15:00+03', '2026-09-30 09:22:00+03'),
('e0000000-0000-0000-0000-000000000003', 'INC-00019', 'a0000000-0000-0000-0000-000000000001', 'Unusual Off-Hours Privileged SWIFT Access from Remote IP', 'Treasury workstation user logged in at 03:14 AM EAT from unmanaged residential IP subnet, accessing SWIFT payment file transfer directory.', 'MEDIUM', 'INVESTIGATING', 64, 'c0000000-0000-0000-0000-000000000003', 'b0000000-0000-0000-0000-000000000002', '2026-09-30 03:14:00+03', '2026-09-30 03:45:00+03');

-- 6. Response Actions (Human-Approval Queue)
INSERT INTO response_actions (id, incident_id, action_type, target_entity, action_parameters, recommended_by, reasoning, confidence_score, status) VALUES
('f0000000-0000-0000-0000-000000000001', 'e0000000-0000-0000-0000-000000000001', 'ISOLATE_HOST', 'SERVER-04 (10.10.1.24)', '{"method": "firewall_drop_all_except_soc", "asset_id": "c0000000-0000-0000-0000-000000000001"}'::jsonb, 'AI_RISK_AGENT', 'Potential active malware / C2 beaconing. Host isolation is recommended immediately to prevent lateral traversal to core banking settlement switches.', 94, 'PENDING_APPROVAL'),
('f0000000-0000-0000-0000-000000000002', 'e0000000-0000-0000-0000-000000000001', 'BLOCK_IP', '185.220.101.5', '{"direction": "egress_and_ingress", "duration_hours": 72}'::jsonb, 'AI_THREAT_INTEL_AGENT', 'Match with high-confidence Cobalt Strike C2 infrastructure on Ethio-CERT blacklist. Block at perimeter edge.', 98, 'PENDING_APPROVAL');
