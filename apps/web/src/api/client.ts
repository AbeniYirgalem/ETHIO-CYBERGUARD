import type { Incident, ResponseAction, AuthUser } from '../types';

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
  saveSession(null);
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
