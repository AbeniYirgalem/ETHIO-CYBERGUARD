import type {
  Incident, ResponseAction, AuthUser, ThreatIndicator, AuditLogEntry, AssistantReply,
  DashboardStats, SecurityEvent, Severity,
} from '../types';

/**
 * API client for the ETHIO-CYBERGUARD backend.
 * Base URL comes from VITE_API_URL (default: http://localhost:8000).
 * Tokens live in sessionStorage, so they are cleared when the tab closes.
 */
export const API_BASE: string =
  (import.meta.env.VITE_API_URL ?? '').replace(/\/+$/, '') || 'http://localhost:8000';

const SESSION_KEY = 'ecg_session';
const REQUEST_TIMEOUT_MS = 6000;

export interface Session {
  accessToken: string;
  refreshToken: string;
  user: AuthUser;
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

// ---------- session storage ----------

export function getSession(): Session | null {
  try {
    const raw = sessionStorage.getItem(SESSION_KEY);
    return raw ? (JSON.parse(raw) as Session) : null;
  } catch {
    return null;
  }
}

function saveSession(session: Session | null): void {
  try {
    if (session) sessionStorage.setItem(SESSION_KEY, JSON.stringify(session));
    else sessionStorage.removeItem(SESSION_KEY);
  } catch {
    /* storage unavailable: session lasts for this page view only */
  }
}

// ---------- low-level request ----------

function errorDetail(body: unknown, fallback: string): string {
  if (body && typeof body === 'object' && 'detail' in body) {
    const detail = (body as { detail: unknown }).detail;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail) && detail.length > 0) {
      const first = detail[0] as { msg?: string };
      if (first?.msg) return first.msg;
    }
  }
  return fallback;
}

async function rawRequest(path: string, init: RequestInit, token?: string): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  try {
    const headers = new Headers(init.headers);
    headers.set('Accept', 'application/json');
    if (init.body) headers.set('Content-Type', 'application/json');
    if (token) headers.set('Authorization', `Bearer ${token}`);
    return await fetch(`${API_BASE}${path}`, { ...init, headers, signal: controller.signal });
  } catch {
    throw new ApiError(0, 'Backend unreachable');
  } finally {
    clearTimeout(timer);
  }
}

async function refreshSession(session: Session): Promise<Session | null> {
  try {
    const res = await rawRequest('/api/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: session.refreshToken }),
    });
    if (!res.ok) return null;
    const data = (await res.json()) as { access_token: string; refresh_token: string };
    const next: Session = {
      ...session,
      accessToken: data.access_token,
      refreshToken: data.refresh_token,
    };
    saveSession(next);
    return next;
  } catch {
    return null;
  }
}

async function authedRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  let session = getSession();
  if (!session) throw new ApiError(401, 'Not signed in');

  let res = await rawRequest(path, init, session.accessToken);
  if (res.status === 401) {
    const refreshed = await refreshSession(session);
    if (!refreshed) {
      saveSession(null);
      throw new ApiError(401, 'Session expired. Please sign in again.');
    }
    session = refreshed;
    res = await rawRequest(path, init, session.accessToken);
  }

  const body: unknown = await res.json().catch(() => null);
  if (!res.ok) throw new ApiError(res.status, errorDetail(body, `Request failed (${res.status})`));
  return body as T;
}

// ---------- auth ----------

export async function login(email: string, password: string): Promise<Session> {
  const res = await rawRequest('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  const body: unknown = await res.json().catch(() => null);
  if (!res.ok) throw new ApiError(res.status, errorDetail(body, 'Sign-in failed'));
  const data = body as { access_token: string; refresh_token: string; user: AuthUser };
  const session: Session = {
    accessToken: data.access_token,
    refreshToken: data.refresh_token,
    user: data.user,
  };
  saveSession(session);
  return session;
}

export function logout(): void {
  const session = getSession();
  saveSession(null);
  if (!session) return;
  // Best effort: ask the server to revoke both tokens so a copied token stops working.
  void rawRequest(
    '/api/auth/logout',
    { method: 'POST', body: JSON.stringify({ refresh_token: session.refreshToken }) },
    session.accessToken,
  ).catch(() => undefined);
}

export interface NewUserPayload {
  email: string;
  password: string;
  full_name: string;
  role: string;
  department?: string;
  organization?: string;
}

/** Create a user account. The server only allows this for administrators. */
export async function createUser(payload: NewUserPayload): Promise<AuthUser> {
  const data = await authedRequest<{ user: AuthUser }>('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  return data.user;
}

export const FALLBACK_ROLES: string[] = [
  'SUPER_ADMIN', 'SOC_MANAGER', 'INCIDENT_COMMANDER', 'SECURITY_ANALYST',
  'INCIDENT_RESPONDER', 'THREAT_HUNTER', 'AUDITOR', 'READ_ONLY',
];

/** Roles the backend knows about (public endpoint); falls back to a built-in list when offline. */
export async function fetchRoles(): Promise<string[]> {
  try {
    const res = await rawRequest('/api/auth/roles', { method: 'GET' });
    if (!res.ok) return FALLBACK_ROLES;
    const body = (await res.json()) as { roles?: string[] };
    return Array.isArray(body.roles) && body.roles.length > 0 ? body.roles : FALLBACK_ROLES;
  } catch {
    return FALLBACK_ROLES;
  }
}

// ---------- data ----------

export async function fetchIncidents(): Promise<Incident[]> {
  const data = await authedRequest<{ incidents: Incident[] }>('/api/incidents');
  return data.incidents;
}

export async function fetchActions(): Promise<ResponseAction[]> {
  const data = await authedRequest<{ actions: ResponseAction[] }>('/api/response/actions');
  return data.actions;
}

export async function fetchThreatIntel(): Promise<ThreatIndicator[]> {
  const data = await authedRequest<{ indicators: Array<Partial<ThreatIndicator>> }>(
    '/api/threat-intelligence',
  );
  // The API record may omit optional fields, so fill safe defaults for the UI.
  return data.indicators.map((i) => ({
    indicator: i.indicator ?? 'unknown',
    type: i.type ?? 'IPV4',
    reputation: i.reputation ?? 'SUSPICIOUS',
    confidence: i.confidence ?? 0,
    first_seen: i.first_seen ?? '',
    threat_actor: i.threat_actor ?? 'Unknown',
    malware: i.malware ?? 'Unknown',
    country: i.country ?? 'Unknown',
    related_incidents: i.related_incidents ?? [],
  }));
}

export async function fetchAuditLog(): Promise<AuditLogEntry[]> {
  const data = await authedRequest<{ audit_logs: AuditLogEntry[] }>('/api/response/audit-log');
  return data.audit_logs;
}

export async function askAssistant(query: string, incidentNumber: string): Promise<AssistantReply> {
  const data = await authedRequest<{ reply: string; citations?: AssistantReply['citations'] }>(
    '/api/ai/chat',
    { method: 'POST', body: JSON.stringify({ query, incident_number: incidentNumber }) },
  );
  return { reply: data.reply, citations: data.citations ?? [] };
}

export async function fetchDashboardStats(): Promise<DashboardStats> {
  return authedRequest<DashboardStats>('/api/dashboard/stats');
}

// ---------- live event stream (WebSocket) ----------

interface RawStreamEvent {
  event_id: string;
  timestamp?: string;
  source?: { type?: string; hostname?: string; ip?: string; os?: string };
  event_type?: string;
  severity?: string;
  user?: string;
  process?: { name?: string | null; command_line?: string | null };
  network?: {
    source_ip?: string | null; source_port?: number | null;
    destination_ip?: string | null; destination_port?: number | null;
  } | null;
}

export interface StreamAlert {
  title?: string;
  severity?: string;
}

export interface StreamStats {
  events_per_second: number;
  events_processed_today: number;
}

export interface LiveStreamHandlers {
  onEvent: (event: SecurityEvent, stats: StreamStats | undefined, alerts: StreamAlert[]) => void;
  onStatus: (connected: boolean) => void;
}

const SEVERITIES: Severity[] = ['INFO', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];

function toSecurityEvent(raw: RawStreamEvent): SecurityEvent {
  const when = raw.timestamp ? new Date(raw.timestamp) : new Date();
  const net = raw.network ?? undefined;
  const hasNet = !!net && (net.source_ip || net.destination_ip);
  const severity = (raw.severity ?? 'INFO').toUpperCase() as Severity;
  return {
    event_id: raw.event_id,
    timestamp: Number.isNaN(when.getTime()) ? String(raw.timestamp) : when.toLocaleTimeString(),
    source: {
      type: raw.source?.type ?? 'endpoint',
      hostname: raw.source?.hostname ?? 'unknown',
      ip: raw.source?.ip ?? '',
      os: raw.source?.os,
    },
    event_type: raw.event_type ?? 'event',
    severity: SEVERITIES.includes(severity) ? severity : 'INFO',
    user: raw.user ?? 'SYSTEM',
    process: {
      name: raw.process?.name ?? undefined,
      command_line: raw.process?.command_line ?? undefined,
    },
    network: hasNet
      ? {
          source_ip: net?.source_ip ?? undefined,
          source_port: net?.source_port ?? undefined,
          destination_ip: net?.destination_ip ?? undefined,
          destination_port: net?.destination_port ?? undefined,
        }
      : undefined,
  };
}

/** Opens the authenticated live telemetry stream and reconnects with backoff.
 *  Returns a function that closes it. */
export function openLiveStream(handlers: LiveStreamHandlers): () => void {
  let socket: WebSocket | null = null;
  let closed = false;
  let retry = 0;
  let pingTimer: ReturnType<typeof setInterval> | undefined;
  let reconnectTimer: ReturnType<typeof setTimeout> | undefined;

  const scheduleReconnect = () => {
    if (closed) return;
    const delay = Math.min(15000, 1000 * 2 ** retry);
    retry += 1;
    reconnectTimer = setTimeout(() => { void connect(); }, delay);
  };

  const connect = async () => {
    if (closed) return;
    if (retry > 0) {
      // The stored access token may have expired while we were disconnected.
      try { await authedRequest('/api/auth/me'); } catch { /* handled by the next attempt */ }
    }
    const session = getSession();
    if (!session || closed) return;
    const url = `${API_BASE.replace(/^http/i, 'ws')}/ws/live-events?token=${encodeURIComponent(session.accessToken)}`;
    try {
      socket = new WebSocket(url);
    } catch {
      scheduleReconnect();
      return;
    }
    socket.onopen = () => {
      retry = 0;
      handlers.onStatus(true);
      pingTimer = setInterval(() => {
        if (socket && socket.readyState === WebSocket.OPEN) socket.send('ping');
      }, 25000);
    };
    socket.onmessage = (msg: MessageEvent) => {
      if (typeof msg.data !== 'string' || msg.data === 'pong') return;
      try {
        const data = JSON.parse(msg.data) as {
          type?: string; event?: RawStreamEvent; stats?: StreamStats; alerts?: StreamAlert[];
        };
        if (data.type === 'EVENT_INGESTED' && data.event) {
          handlers.onEvent(toSecurityEvent(data.event), data.stats, data.alerts ?? []);
        }
      } catch {
        /* ignore malformed frames */
      }
    };
    socket.onclose = () => {
      if (pingTimer) clearInterval(pingTimer);
      handlers.onStatus(false);
      scheduleReconnect();
    };
    socket.onerror = () => { socket?.close(); };
  };

  void connect();

  return () => {
    closed = true;
    if (reconnectTimer) clearTimeout(reconnectTimer);
    if (pingTimer) clearInterval(pingTimer);
    socket?.close();
  };
}

export async function decideAction(
  id: string,
  decision: 'approve' | 'reject',
  reason: string,
): Promise<ResponseAction> {
  const data = await authedRequest<{ action: ResponseAction }>(
    `/api/response/actions/${encodeURIComponent(id)}/${decision}`,
    { method: 'POST', body: JSON.stringify({ reason }) },
  );
  return data.action;
}
