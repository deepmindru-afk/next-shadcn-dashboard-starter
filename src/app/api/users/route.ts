// ============================================================
// Route Handler — Users (list + create)
// ============================================================
// BFF pattern: forwards requests to the Python backend.
// ============================================================

import { proxyToPython } from '@/lib/python-proxy';
import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = request.nextUrl;
    const params = new URLSearchParams(searchParams);
    const data = await proxyToPython<any>(`/api/users?${params.toString()}`);
    return NextResponse.json(data);
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Internal server error';
    return NextResponse.json({ success: false, message }, { status: 502 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const data = await proxyToPython<any>('/api/users', {
      method: 'POST',
      body: JSON.stringify(body),
    });
    return NextResponse.json(data, { status: 201 });
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Internal server error';
    return NextResponse.json({ success: false, message }, { status: 502 });
  }
}
