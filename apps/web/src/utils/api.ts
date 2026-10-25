/**
 * ETHIO-CYBERGUARD API Client
 * Provides resilient communication with the FastAPI backend (/api/v1).
 * Supports automatic fallback to mock/demo data when backend is offline or on static GitHub Pages.
 */

import type { Incident, ResponseAction } from '../types';

export const API_BASE_URL = (() => {
  if (typeof window !== 'undefined' && (window as any).__ECG_API_URL__) {
    return (window as any).__ECG_API_URL__;
  }
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  // If hosted on localhost, default to FastAPI port 8000
  if (typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')) {
    return 'http://localhost:8000';
  }
  // Otherwise use relative paths for containerized reverse proxy
  return '';
})();

export interface ApiStatus {
  connected: boolean;
  demoMode: boolean;
  version?: string;
  database?: string;
  details?: any;
}

/**
 * Checks connection health against FastAPI backend.
 */
export async function checkBackendHealth(): Promise<ApiStatus> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 2500);

    const res = await fetch(`${API_BASE_URL}/health/live`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
      signal: controller.signal
    });
    clearTimeout(timeoutId);

    if (res.ok) {
      const data = await res.json();
      return {
        connected: true,
        demoMode: Boolean(data.demo_mode ?? true),
        version: data.version || '1.1.0',
        database: data.database || 'active',
        details: data
      };
    }
    return { connected: false, demoMode: true };
  } catch {
    return { connected: false, demoMode: true };
  }
}

/**
 * Fetches active incidents from backend.
 */
export async function fetchIncidents(): Promise<{ success: boolean; data?: Incident[]; isLive: boolean }> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3000);

    const res = await fetch(`${API_BASE_URL}/api/v1/incidents`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
      signal: controller.signal
    });
    clearTimeout(timeoutId);

    if (res.ok) {
      const data = await res.json();
      const items = Array.isArray(data) ? data : (data.incidents || []);
      return { success: true, data: items, isLive: true };
    }
  } catch {
    // Offline or unreachable
  }
  return { success: false, isLive: false };
}

/**
 * Fetches SOAR response actions from backend.
 */
export async function fetchResponseActions(): Promise<{ success: boolean; data?: ResponseAction[]; isLive: boolean }> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3000);

    const res = await fetch(`${API_BASE_URL}/api/v1/response/actions`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
      signal: controller.signal
    });
    clearTimeout(timeoutId);

    if (res.ok) {
      const data = await res.json();
      const actions = data.actions || (Array.isArray(data) ? data : []);
      return { success: true, data: actions, isLive: true };
    }
  } catch {
    // Offline
  }
  return { success: false, isLive: false };
}

/**
 * Approves a SOAR containment action on the FastAPI backend.
 */
export async function approveResponseAction(actionId: string, reason?: string): Promise<{ success: boolean; isLive: boolean; message: string }> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/response/actions/${encodeURIComponent(actionId)}/approve`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        reason: reason || 'Approved by certified Incident Commander',
        operator: 'analyst@cbe.com.et'
      })
    });
    if (res.ok) {
      const data = await res.json();
      return { success: true, isLive: true, message: data.message || `Action ${actionId} approved and executed.` };
    }
  } catch {
    // Fall back to simulated execution
  }
  return { 
    success: true, 
    isLive: false, 
    message: `[Simulated] Action ${actionId} approved locally in mock mode.` 
  };
}

/**
 * Rejects a SOAR containment action on the FastAPI backend.
 */
export async function rejectResponseAction(actionId: string, reason?: string): Promise<{ success: boolean; isLive: boolean; message: string }> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/response/actions/${encodeURIComponent(actionId)}/reject`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        reason: reason || 'Action dismissed by analyst evaluation',
        operator: 'analyst@cbe.com.et'
      })
    });
    if (res.ok) {
      const data = await res.json();
      return { success: true, isLive: true, message: data.message || `Action ${actionId} rejected.` };
    }
  } catch {
    // Fallback
  }
  return { 
    success: true, 
    isLive: false, 
    message: `[Simulated] Action ${actionId} rejected locally in mock mode.` 
  };
}
