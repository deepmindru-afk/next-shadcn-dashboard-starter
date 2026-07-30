// ============================================================
// Product Service — Data Access Layer
// ============================================================
// BFF pattern: calls Next.js route handlers which proxy to the
// Python backend (FastAPI). This is the ONLY file you modify.
// ============================================================

import { apiClient } from '@/lib/api-client';
import type {
  ProductFilters,
  ProductsResponse,
  ProductByIdResponse,
  ProductMutationPayload
} from './types';

function buildQuery(filters: ProductFilters): string {
  const params = new URLSearchParams();
  if (filters.page) params.set('page', String(filters.page));
  if (filters.limit) params.set('limit', String(filters.limit));
  if (filters.search) params.set('search', filters.search);
  if (filters.categories) params.set('categories', filters.categories);
  if (filters.sort) params.set('sort', filters.sort);
  const qs = params.toString();
  return qs ? `/products?${qs}` : '/products';
}

export async function getProducts(filters: ProductFilters): Promise<ProductsResponse> {
  return apiClient<ProductsResponse>(buildQuery(filters));
}

export async function getProductById(id: number): Promise<ProductByIdResponse> {
  return apiClient<ProductByIdResponse>(`/products/${id}`);
}

export async function createProduct(data: ProductMutationPayload) {
  return apiClient<any>('/products', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateProduct(id: number, data: ProductMutationPayload) {
  return apiClient<any>(`/products/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function deleteProduct(id: number) {
  return apiClient<any>(`/products/${id}`, {
    method: 'DELETE',
  });
}
