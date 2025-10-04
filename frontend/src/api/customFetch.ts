// src/api/customFetch.ts
export const customFetch = async <T>(
  config: {
    url: string;
    method: string;
    body?: any;
    data?: any;
    params?: Record<string, string | number | boolean | undefined>;
    headers?: Record<string, string>;
    signal?: AbortSignal;
  },
  options?: RequestInit
): Promise<T> => {
  const { url, method, body, data, params, headers, signal } = config;

  // クエリ文字列を構築
  const queryString = params
    ? '?' +
      Object.entries(params)
        .filter(([, v]) => v !== undefined)
        .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`)
        .join('&')
    : '';

  const response = await fetch(url + queryString, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(headers || {}),
      ...(options?.headers || {}),
    },
    body: body
      ? JSON.stringify(body)
      : data
      ? JSON.stringify(data)
      : undefined,
    signal,
    credentials: 'include',
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
};
