export type Severity = 'INFO' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type IncidentStatus = 'OPEN' | 'INVESTIGATING' | 'CONTAINED' | 'RESOLVED' | 'CLOSED';
export type ActionStatus = 'PENDING_APPROVAL' | 'APPROVED' | 'REJECTED' | 'EXECUTED';

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
}

export interface ChatMessage {
  id: string;
  sender: 'analyst' | 'assistant';
  text: string;
  timestamp: string;
  citations?: Array<{ source: string; entity: string }>;
}
