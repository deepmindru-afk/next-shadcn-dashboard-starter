// ============================================================
// User Service — Data Access Layer
// ============================================================
// BFF pattern: calls Next.js route handlers which proxy to the
// Python backend (FastAPI). This is the ONLY file you modify.
// ============================================================

import { apiClient } from '@/lib/api-client';
import type { UserFilters, UsersResponse, UserMutationPayload } from './types';

function buildQuery(filters: UserFilters): string {
  const params = new URLSearchParams();
  if (filters.page) params.set('page', String(filters.page));
  if (filters.limit) params.set('limit', String(filters.limit));
  if (filters.search) params.set('search', filters.search);
  if (filters.roles) params.set('roles', filters.roles);
  if (filters.sort) params.set('sort', filters.sort);
  const qs = params.toString();
  return qs ? `/users?${qs}` : '/users';
}

export async function getUsers(filters: UserFilters): Promise<UsersResponse> {
  return apiClient<UsersResponse>(buildQuery(filters));
}

export async function getUserById(id: number): Promise<any> {
  return apiClient<any>(`/users/${id}`);
}

export async function createUser(data: UserMutationPayload) {
  return apiClient<any>('/users', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateUser(id: number, data: UserMutationPayload) {
  return apiClient<any>(`/users/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function deleteUser(id: number) {
  return apiClient<any>(`/users/${id}`, {
    method: 'DELETE',
  });
}
