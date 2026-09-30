-- Migration 002: Advanced RBAC, SOAR Approvals, and Multi-Tenancy Tables

-- 1. Threat Intelligence Indicators
CREATE TABLE IF NOT EXISTS iocs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    indicator VARCHAR(512) UNIQUE NOT NULL,
    ioc_type VARCHAR(50) NOT NULL,
    reputation VARCHAR(50) DEFAULT 'MALICIOUS',
    confidence INTEGER DEFAULT 90,
    threat_actor VARCHAR(255),
    malware_family VARCHAR(255),
    source_feed VARCHAR(255) DEFAULT 'Ethio-CERT',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. SOAR Response Actions & Dual-Custody Approvals
CREATE TABLE IF NOT EXISTS actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID REFERENCES incidents(id) ON DELETE CASCADE,
    action_type VARCHAR(100) NOT NULL,
    target_entity VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'PENDING_APPROVAL',
    recommended_by VARCHAR(100),
    confidence INTEGER,
    reasoning TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS action_approvals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action_id UUID REFERENCES actions(id) ON DELETE CASCADE,
    approver_id UUID REFERENCES users(id),
    decision VARCHAR(50) NOT NULL, -- APPROVED, REJECTED
    decision_reason TEXT,
    decided_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Immutable Audit Logs
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action_type VARCHAR(100) NOT NULL,
    target VARCHAR(255),
    reason TEXT,
    result VARCHAR(50) DEFAULT 'SUCCESS',
    record_hash VARCHAR(64) NOT NULL,
    prev_hash VARCHAR(64) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Phishing Campaigns & Training Modules
CREATE TABLE IF NOT EXISTS phishing_campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    campaign_name VARCHAR(255) NOT NULL,
    template_id VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'ACTIVE',
    sent_count INTEGER DEFAULT 0,
    clicked_count INTEGER DEFAULT 0,
    reported_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS phishing_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES phishing_campaigns(id) ON DELETE CASCADE,
    user_email VARCHAR(255) NOT NULL,
    clicked_link BOOLEAN DEFAULT FALSE,
    submitted_credentials BOOLEAN DEFAULT FALSE,
    reported_phish BOOLEAN DEFAULT FALSE,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Attack Surface OSINT Scans
CREATE TABLE IF NOT EXISTS domains (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    domain_name VARCHAR(255) UNIQUE NOT NULL,
    is_authorized BOOLEAN DEFAULT TRUE,
    risk_score INTEGER DEFAULT 20,
    last_scanned TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS subdomains (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain_id UUID REFERENCES domains(id) ON DELETE CASCADE,
    subdomain_name VARCHAR(255) NOT NULL,
    ip_address INET,
    is_live BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS scans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    target_input VARCHAR(255) NOT NULL,
    scan_type VARCHAR(50) DEFAULT 'OSINT_RECON',
    raw_results JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. AI Investigations
CREATE TABLE IF NOT EXISTS ai_investigations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID REFERENCES incidents(id) ON DELETE CASCADE,
    agents_executed INTEGER DEFAULT 7,
    summary TEXT,
    confidence INTEGER,
    pipeline_output JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. Notifications
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    recipient_user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    channel VARCHAR(50) DEFAULT 'IN_APP',
    severity VARCHAR(20) DEFAULT 'HIGH',
    title VARCHAR(255) NOT NULL,
    body TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
