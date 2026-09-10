import { API_BASE_URL } from '@/api/loadEnv';

/** Orval 8 supplies a URL (including query parameters) and a serialized RequestInit. */
export const customFetchAdmin = async <T>(
  url: string,
  options?: RequestInit
): Promise<T> => {
  const fullUrl = /^[a-z][a-z\d+.-]*:/i.test(url)
    ? url
    : `${API_BASE_URL.replace(/\/+$/, '')}/${url.replace(/^\/+/, '')}`;
  const headers = new Headers({ 'Content-Type': 'application/json' });
  new Headers(options?.headers).forEach((value, key) => headers.set(key, value));

  const response = await fetch(fullUrl, {
    ...options,
    credentials: 'include',
    headers,
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw {
      status: response.status,
      statusText: response.statusText,
      body: errorBody,
      url: fullUrl,
    };
  }

  if (response.status === 204) {
    return null as T;
  }
  const contentType = response.headers.get('content-type');
  if (contentType?.includes('application/json')) {
    return (await response.json()) as T;
  }
  return (await response.text()) as T;
};
