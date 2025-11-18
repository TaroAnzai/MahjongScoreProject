// src/api/customFetchAdmin.ts
import { API_BASE_URL } from '@/api/loadEnv';

interface CustomFetchAdminConfig {
  url: string;
  method: string;
  data?: any;
  params?: Record<string, string | number | null>;
  headers?: Record<string, string>;
  signal?: AbortSignal;
}
export const customFetchAdmin = async <T>(
  config: CustomFetchAdminConfig,
  options?: RequestInit
): Promise<T> => {
  // ✅ ベースURLを組み込む
  const fullUrl = `${API_BASE_URL}${config.url}`;

  // クエリパラメータ処理
  let urlWithParams = fullUrl;
  if (config.params) {
    const query = new URLSearchParams(
      Object.entries(config.params).map(([k, v]) => [k, String(v)])
    );
    urlWithParams += `?${query}`;
  }

  const response = await fetch(urlWithParams, {
    method: config.method,
    headers: {
      'Content-Type': 'application/json',
      ...(config.headers || {}),
      ...(options?.headers || {}),
    },
    body: config.data && config.method !== 'GET' ? JSON.stringify(config.data) : undefined,
    signal: config.signal,
    credentials: 'include',
    ...options,
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw {
      status: response.status,
      statusText: response.statusText,
      body: errorBody,
      url: urlWithParams,
    };
  }

  // JSON以外のレスポンスにも対応
  const contentType = response.headers.get('content-type');
  if (contentType?.includes('application/json')) {
    return (await response.json()) as T;
  }
  return (await response.text()) as T;
};
