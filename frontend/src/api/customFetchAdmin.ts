// src/api/customFetchAdmin.ts

export const customFetchAdmin = async <T>({
  url,
  method,
  params,
  data,
  headers,
  signal,
}: {
  url: string;
  method: string;
  params?: Record<string, any>;
  data?: any;
  headers?: Record<string, string>;
  signal?: AbortSignal;
}): Promise<T> => {
  let finalUrl = url;

  // --- クエリパラメータを付与 ---
  if (params && Object.keys(params).length > 0) {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, String(value));
      }
    });
    finalUrl += `?${searchParams.toString()}`;
  }

  const response = await fetch(finalUrl, {
    method,
    body: data ? JSON.stringify(data) : undefined,
    headers: {
      'Content-Type': 'application/json',
      ...(headers || {}),
    },
    credentials: 'include', // ← 管理者APIは Cookie 必須！
    signal,
  });

  const contentType = response.headers.get('content-type') || '';
  const isJson = contentType.includes('application/json');

  if (!response.ok) {
    const error = isJson ? await response.json() : await response.text();
    throw error;
  }

  return isJson ? response.json() : ({} as T);
};
