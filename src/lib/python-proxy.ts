/**
 * BFF Proxy Utility
 *
 * Forwards requests to the Python backend.
 * This is the bridge between Next.js route handlers and the Python API.
 */

const PYTHON_BACKEND_URL = process.env.PYTHON_BACKEND_URL || 'http://localhost:8000';

export async function proxyToPython<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${PYTHON_BACKEND_URL}${endpoint}`;

  const res = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Python API error: ${res.status}`);
  }

  return res.json() as Promise<T>;
}
