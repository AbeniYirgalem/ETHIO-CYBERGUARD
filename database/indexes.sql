-- ==============================================================================
-- ETHIO-CYBERGUARD: High-Performance Database Indexes
-- Optimized for 50,000+ EPS ingestion, fast alert correlation, and analytical queries
-- ==============================================================================

-- 1. Events Ingestion & Time-Series Lookup
CREATE INDEX IF NOT EXISTS idx_events_timestamp_desc ON events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_events_event_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_source_ip ON events(source_ip);
CREATE INDEX IF NOT EXISTS idx_events_destination_ip ON events(destination_ip);
CREATE INDEX IF NOT EXISTS idx_events_user_name ON events(user_name);
CREATE INDEX IF NOT EXISTS idx_events_process_name ON events(process_name);
CREATE INDEX IF NOT EXISTS idx_events_org_time ON events(org_id, timestamp DESC);

-- 2. Alerts & Detections
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_rule_id ON alerts(rule_id);
CREATE INDEX IF NOT EXISTS idx_alerts_incident_id ON alerts(incident_id);
CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at DESC);

-- 3. Incidents & Case Management
CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidents(status);
CREATE INDEX IF NOT EXISTS idx_incidents_severity ON incidents(severity);
CREATE INDEX IF NOT EXISTS idx_incidents_assigned_user ON incidents(assigned_user_id);
CREATE INDEX IF NOT EXISTS idx_incidents_org_status ON incidents(org_id, status);
CREATE INDEX IF NOT EXISTS idx_incidents_risk_score ON incidents(risk_score DESC);

-- 4. Threat Intelligence & Observables
CREATE INDEX IF NOT EXISTS idx_iocs_indicator ON iocs(indicator);
CREATE INDEX IF NOT EXISTS idx_iocs_type_reputation ON iocs(ioc_type, reputation);
CREATE INDEX IF NOT EXISTS idx_iocs_confidence ON iocs(confidence DESC);

-- 5. SOAR Response Actions & Approvals
CREATE INDEX IF NOT EXISTS idx_actions_status ON actions(status);
CREATE INDEX IF NOT EXISTS idx_actions_incident ON actions(incident_id);
CREATE INDEX IF NOT EXISTS idx_approvals_action_id ON action_approvals(action_id);
CREATE INDEX IF NOT EXISTS idx_approvals_approver ON action_approvals(approver_id);

-- 6. Immutable Audit Trail
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_hash ON audit_logs(record_hash);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action_type);

-- 7. Phishing & Awareness
CREATE INDEX IF NOT EXISTS idx_phishing_campaigns_org ON phishing_campaigns(org_id);
CREATE INDEX IF NOT EXISTS idx_phishing_results_user ON phishing_results(user_email);

-- 8. Attack Surface OSINT
CREATE INDEX IF NOT EXISTS idx_domains_target ON domains(domain_name);
CREATE INDEX IF NOT EXISTS idx_subdomains_domain ON subdomains(domain_id);
CREATE INDEX IF NOT EXISTS idx_scans_target ON scans(target_input);
