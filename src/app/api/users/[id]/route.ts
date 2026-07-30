// ============================================================
// Route Handler — Single User (update + delete)
// ============================================================
// BFF pattern: forwards requests to the Python backend.
// ============================================================

import { proxyToPython } from '@/lib/python-proxy';
import { NextRequest, NextResponse } from 'next/server';

type Params = { params: Promise<{ id: string }> };

export async function PUT(request: NextRequest, { params }: Params) {
  try {
    const { id } = await params;
    const body = await request.json();
    const data = await proxyToPython<any>(`/api/users/${id}`, {
      method: 'PUT',
      body: JSON.stringify(body),
    });
    return NextResponse.json(data);
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Internal server error';
    return NextResponse.json({ success: false, message }, { status: 502 });
  }
}

export async function DELETE(request: NextRequest, { params }: Params) {
  try {
    const { id } = await params;
    const data = await proxyToPython<any>(`/api/users/${id}`, {
      method: 'DELETE',
    });
    return NextResponse.json(data);
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Internal server error';
    return NextResponse.json({ success: false, message }, { status: 502 });
  }
}
