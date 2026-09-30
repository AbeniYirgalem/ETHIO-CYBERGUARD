-- ==============================================================================
-- ETHIO-CYBERGUARD: PostgreSQL Core Production Schema
-- AI-Assisted Cybersecurity Platform for Threat Detection, Investigation & Response
-- Designed for enterprise SOC/SIEM operations with human-in-the-loop response
-- ==============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 1. Organizations & Multi-tenancy
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    sector VARCHAR(100) DEFAULT 'Education', -- Banking, Telecom, Government, Healthcare, Education
    country VARCHAR(100) DEFAULT 'Ethiopia',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. User Accounts & RBAC
CREATE TYPE user_role AS ENUM ('SUPER_ADMIN', 'SOC_MANAGER', 'SECURITY_ANALYST', 'VIEWER');

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role user_role DEFAULT 'SECURITY_ANALYST',
    is_active BOOLEAN DEFAULT TRUE,
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret VARCHAR(255),
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Assets & Inventory
CREATE TYPE asset_criticality AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL');
CREATE TYPE asset_os AS ENUM ('WINDOWS', 'LINUX', 'MACOS', 'NETWORK_DEVICE', 'CLOUD');

CREATE TABLE assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    hostname VARCHAR(255) NOT NULL,
    ip_address INET NOT NULL,
    mac_address MACADDR,
    os_type asset_os NOT NULL,
    os_version VARCHAR(100),
    criticality asset_criticality DEFAULT 'MEDIUM',
    department VARCHAR(100),
    physical_location VARCHAR(255) DEFAULT 'Addis Ababa HQ',
    is_isolated BOOLEAN DEFAULT FALSE,
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_assets_ip ON assets(ip_address);
CREATE INDEX idx_assets_hostname ON assets(hostname);

-- 4. Data Sources & Collectors
CREATE TYPE data_source_type AS ENUM ('SYSLOG', 'WINDOWS_EVENT', 'NETFLOW', 'ZEEK_SURICATA', 'CLOUD_API', 'AUDITD');
CREATE TYPE source_health AS ENUM ('HEALTHY', 'DEGRADED', 'OFFLINE');

CREATE TABLE data_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    source_type data_source_type NOT NULL,
    ip_address INET,
    status source_health DEFAULT 'HEALTHY',
    events_per_sec INTEGER DEFAULT 0,
    last_heartbeat TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    configuration JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Normalized Security Events
CREATE TYPE event_severity AS ENUM ('INFO', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL');

CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_uid VARCHAR(64) UNIQUE NOT NULL,
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    asset_id UUID REFERENCES assets(id) ON DELETE SET NULL,
    source_type VARCHAR(50) NOT NULL,
    event_type VARCHAR(100) NOT NULL, -- process_execution, user_login, network_connection, etc.
    severity event_severity DEFAULT 'INFO',
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    user_name VARCHAR(150),
    source_ip INET,
    source_port INTEGER,
    destination_ip INET,
    destination_port INTEGER,
    protocol VARCHAR(20),
    process_name VARCHAR(255),
    command_line TEXT,
    file_hash VARCHAR(128),
    raw_payload JSONB DEFAULT '{}'::jsonb,
    normalized_data JSONB NOT NULL,
    is_correlated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_events_timestamp ON events(timestamp DESC);
CREATE INDEX idx_events_event_type ON events(event_type);
CREATE INDEX idx_events_src_ip ON events(source_ip);
CREATE INDEX idx_events_dst_ip ON events(destination_ip);

-- 6. Threat Intelligence Indicators
CREATE TYPE indicator_type AS ENUM ('IPV4', 'IPV6', 'DOMAIN', 'URL', 'SHA256', 'MD5', 'EMAIL');
CREATE TYPE reputation_grade AS ENUM ('MALICIOUS', 'SUSPICIOUS', 'BENIGN', 'UNKNOWN');

CREATE TABLE threat_indicators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    indicator_type indicator_type NOT NULL,
    indicator_value VARCHAR(512) UNIQUE NOT NULL,
    reputation reputation_grade DEFAULT 'SUSPICIOUS',
    confidence_score INTEGER CHECK (confidence_score BETWEEN 0 AND 100),
    threat_actor VARCHAR(255),
    malware_family VARCHAR(255),
    campaign_name VARCHAR(255),
    source_feed VARCHAR(255) DEFAULT 'Ethio-CERT Threat Intel',
    mitre_attack_id VARCHAR(50),
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],
    first_seen TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_indicators_value ON threat_indicators(indicator_value);

-- 7. Detection Rules
CREATE TYPE rule_engine AS ENUM ('SIGMA', 'BEHAVIORAL_BASELINE', 'THRESHOLD', 'ANOMALY');

CREATE TABLE detection_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    rule_name VARCHAR(255) NOT NULL,
    description TEXT,
    engine rule_engine DEFAULT 'SIGMA',
    severity event_severity DEFAULT 'HIGH',
    mitre_tactic VARCHAR(100),
    mitre_technique VARCHAR(100),
    query_condition JSONB NOT NULL,
    window_seconds INTEGER DEFAULT 300,
    threshold_count INTEGER DEFAULT 1,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 8. Alerts
CREATE TYPE alert_status AS ENUM ('NEW', 'ACKNOWLEDGED', 'IN_INCIDENT', 'SUPPRESSED', 'CLOSED');

CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_number VARCHAR(50) UNIQUE NOT NULL,
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    rule_id UUID REFERENCES detection_rules(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    severity event_severity NOT NULL,
    status alert_status DEFAULT 'NEW',
    trigger_event_id UUID REFERENCES events(id) ON DELETE SET NULL,
    confidence_score INTEGER DEFAULT 80,
    mitre_tactics TEXT[] DEFAULT ARRAY[]::TEXT[],
    mitre_techniques TEXT[] DEFAULT ARRAY[]::TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_status ON alerts(status);

-- 9. Incidents (Central SOC Object)
CREATE TYPE incident_status AS ENUM ('OPEN', 'INVESTIGATING', 'CONTAINED', 'RESOLVED', 'CLOSED');

CREATE TABLE incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_number VARCHAR(50) UNIQUE NOT NULL, -- e.g. INC-00042
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    severity event_severity NOT NULL,
    status incident_status DEFAULT 'OPEN',
    risk_score INTEGER CHECK (risk_score BETWEEN 0 AND 100) DEFAULT 50,
    affected_asset_id UUID REFERENCES assets(id) ON DELETE SET NULL,
    assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
    first_seen TIMESTAMP WITH TIME ZONE NOT NULL,
    last_activity TIMESTAMP WITH TIME ZONE NOT NULL,
    root_cause TEXT,
    resolution_summary TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_incidents_number ON incidents(incident_number);
CREATE INDEX idx_incidents_status ON incidents(status);
CREATE INDEX idx_incidents_risk ON incidents(risk_score DESC);

-- 10. Incident Relational Links
CREATE TABLE incident_events (
    incident_id UUID REFERENCES incidents(id) ON DELETE CASCADE,
    event_id UUID REFERENCES events(id) ON DELETE CASCADE,
    sequence_order INTEGER DEFAULT 0,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (incident_id, event_id)
);

CREATE TABLE incident_indicators (
    incident_id UUID REFERENCES incidents(id) ON DELETE CASCADE,
    indicator_id UUID REFERENCES threat_indicators(id) ON DELETE CASCADE,
    matched_value VARCHAR(512),
    matched_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (incident_id, indicator_id)
);

-- 11. Evidence Locker
CREATE TYPE evidence_type AS ENUM ('LOG_SNIPPET', 'FILE_HASH', 'PCAP_SAMPLE', 'MEMORY_DUMP', 'COMMAND_TRACE', 'SCREENSHOT');

CREATE TABLE incident_evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID REFERENCES incidents(id) ON DELETE CASCADE,
    evidence_type evidence_type NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    content_data JSONB NOT NULL,
    sha256_fingerprint VARCHAR(64) NOT NULL,
    collected_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 12. Multi-Agent AI Analysis Runs
CREATE TYPE ai_agent_type AS ENUM (
    'EVENT_ANALYSIS',
    'THREAT_INTEL',
    'CORRELATION',
    'INVESTIGATION',
    'RISK_ASSESSMENT',
    'REPORT_GENERATOR',
    'SECURITY_ASSISTANT'
);

CREATE TABLE ai_agent_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID REFERENCES incidents(id) ON DELETE CASCADE,
    agent_type ai_agent_type NOT NULL,
    model_version VARCHAR(100) DEFAULT 'gemini-1.5-pro / local-sec-llm',
    prompt_context JSONB NOT NULL,
    raw_response TEXT NOT NULL,
    structured_output JSONB NOT NULL,
    confidence_score NUMERIC(5,2),
    execution_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ai_agent_incident ON ai_agent_runs(incident_id);

-- 13. Risk Assessment Breakdown
CREATE TABLE risk_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID REFERENCES incidents(id) ON DELETE CASCADE,
    overall_score INTEGER CHECK (overall_score BETWEEN 0 AND 100),
    impact_score INTEGER CHECK (impact_score BETWEEN 0 AND 100),
    likelihood_score INTEGER CHECK (likelihood_score BETWEEN 0 AND 100),
    exposure_score INTEGER CHECK (exposure_score BETWEEN 0 AND 100),
    confidence_score INTEGER CHECK (confidence_score BETWEEN 0 AND 100),
    contributing_factors JSONB NOT NULL, -- e.g. [{"factor": "privileged account", "weight": 25}]
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 14. Response Actions with Human Approval Workflow
CREATE TYPE response_action_type AS ENUM (
    'ISOLATE_HOST',
    'BLOCK_IP',
    'KILL_PROCESS',
    'REVOKE_TOKEN',
    'RESET_PASSWORD',
    'QUARANTINE_FILE',
    'UPDATE_FIREWALL_RULE',
    'NOTIFY_ETHIO_CERT'
);

CREATE TYPE approval_status AS ENUM ('PENDING_APPROVAL', 'APPROVED', 'REJECTED', 'EXECUTED', 'FAILED');

CREATE TABLE response_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID REFERENCES incidents(id) ON DELETE CASCADE,
    action_type response_action_type NOT NULL,
    target_entity VARCHAR(255) NOT NULL, -- IP, hostname, username, hash
    action_parameters JSONB DEFAULT '{}'::jsonb,
    recommended_by VARCHAR(50) DEFAULT 'AI_RISK_AGENT',
    reasoning TEXT NOT NULL,
    confidence_score INTEGER DEFAULT 90,
    status approval_status DEFAULT 'PENDING_APPROVAL',
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    rejection_reason TEXT,
    execution_log TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_response_status ON response_actions(status);

-- 15. Reports (Executive & Technical)
CREATE TYPE report_type AS ENUM ('TECHNICAL_FORENSIC', 'EXECUTIVE_SUMMARY', 'COMPLIANCE_AUDIT');

CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID REFERENCES incidents(id) ON DELETE CASCADE,
    report_type report_type NOT NULL,
    title VARCHAR(255) NOT NULL,
    summary TEXT,
    markdown_content TEXT NOT NULL,
    generated_by VARCHAR(50) DEFAULT 'AI_REPORT_AGENT',
    reviewed_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 16. Immutable Audit Trail
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id VARCHAR(100),
    details JSONB DEFAULT '{}'::jsonb,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_created ON audit_logs(created_at DESC);
