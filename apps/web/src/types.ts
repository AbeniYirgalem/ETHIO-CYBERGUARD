export type Severity = 'INFO' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type IncidentStatus =
  | 'OPEN' | 'NEW' | 'TRIAGED' | 'ASSIGNED' | 'INVESTIGATING' | 'CONTAINMENT_PENDING'
  | 'CONTAINED' | 'ERADICATION' | 'RECOVERY' | 'RESOLVED' | 'CLOSED' | 'REOPENED';
export type ActionStatus =
  | 'PENDING_APPROVAL' | 'APPROVED' | 'REJECTED' | 'EXECUTED'
  | 'EXPIRED' | 'ROLLED_BACK' | 'DRY_RUN_SIMULATED';

export interface AuthUser {
  id: string;
  email: string;
  name: string;
  role: string;
  department?: string;
}

export interface SecurityEvent {
  event_id: string;
  timestamp: string;
  source: {
    type: string;
    hostname: string;
    ip: string;
    os?: string;
  };
  event_type: string;
  severity: Severity;
  user: string;
  process?: {
    name?: string;
    command_line?: string;
    pid?: number;
  };
  network?: {
    source_ip?: string;
    source_port?: number;
    destination_ip?: string;
    destination_port?: number;
  };
  enrichment?: {
    geo_location?: { country: string; city?: string; reputation?: string };
    is_internal_network?: boolean;
  };
  raw_data?: Record<string, any>;
}

export interface Incident {
  id: string;
  incident_number: string;
  title: string;
  severity: Severity;
  status: IncidentStatus;
  risk_score: number;
  affected_asset: string;
  asset_ip: string;
  department: string;
  first_seen: string;
  last_activity: string;
  assigned_analyst: string;
  summary: string;
}

export interface TimelineEntry {
  time: string;
  event: string;
  type: 'auth' | 'process' | 'alert' | 'network' | 'threat_intel' | 'ai' | 'incident';
  severity: Severity;
}

export interface ThreatIndicator {
  indicator: string;
  type: 'IPV4' | 'DOMAIN' | 'SHA256' | 'URL';
  reputation: 'MALICIOUS' | 'SUSPICIOUS' | 'BENIGN';
  confidence: number;
  first_seen: string;
  threat_actor: string;
  malware: string;
  country: string;
  related_incidents: string[];
}

export interface TimelineBucket {
  hour: string; // ISO, start of the UTC hour
  events: number;
  critical: number;
  alerts: number;
}

export interface SectorProfile {
  active_alerts: number;
  critical: number;
  high: number;
  max_severity: string;
}

export interface DashboardStats {
  metrics: {
    events_per_second: number;
    events_processed_today: number;
    active_incidents: number;
    critical_alerts: number;
    high_risk_alerts: number;
    medium_risk_alerts: number;
    pending_approvals: number;
    audit_entries: number;
    assets_monitored: number;
    mean_time_to_detect_minutes: number | null;
    mean_time_to_respond_minutes: number | null;
  };
  /** How many incidents the MTTD / MTTR averages were measured from. */
  response_metrics?: { mttd_samples: number; mttr_samples: number };
  top_threats: Array<{ name: string; count: number; severity: string; tactic?: string | null; source: string }>;
  /** Hourly event history, last 24 UTC hours, oldest first. */
  timeline?: TimelineBucket[];
  /** Active incidents per sector (Banking, Telecom, ...). */
  sector_profiles?: Record<string, SectorProfile>;
  system_health: { ingestion_pipeline: string; live_stream_clients: number };
}

export interface AuditLogEntry {
  id: string;
  timestamp: string;
  operator: string;
  action: string;
  target: string;
  result: string;
  details: string;
  prev_hash: string;
  integrity_hash: string;
}

export interface AssistantReply {
  reply: string;
  citations: Array<{ source: string; entity: string }>;
}

export interface ResponseAction {
  id: string;
  incident_number: string;
  action_type: string;
  target_entity: string;
  recommended_by: string;
  reasoning: string;
  confidence: number;
  status: ActionStatus;
  created_at: string;
  rejection_reason?: string;
  reviewed_by?: string;
  requested_by_id?: string;
  dry_run?: boolean;
  expires_at?: string;
}

export interface ChatMessage {
  id: string;
  sender: 'analyst' | 'assistant';
  text: string;
  timestamp: string;
  citations?: Array<{ source: string; entity: string }>;
}
