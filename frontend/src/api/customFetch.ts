/**
 * customFetch.ts
 * Orvalのmutator用fetchラッパー
 */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL; // ← .envから読み込む

interface CustomFetchConfig {
  url: string;
  method: string;
  data?: any;
  params?: Record<string, string | number>;
  headers?: Record<string, string>;
  signal?: AbortSignal;
}

/**
 * Orvalが自動生成したfetch呼び出しを共通化
 */
export const customFetch = async <T>(
  config: CustomFetchConfig,
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
    },
    body: config.data && config.method !== 'GET' ? JSON.stringify(config.data) : undefined,
    signal: config.signal,
    ...options,
  });

  if (!response.ok) {
    console.error(`[customFetch2] ${response.status} ${response.statusText}`);
    throw response;
  }

  // JSON以外のレスポンスにも対応
  const contentType = response.headers.get('content-type');
  if (contentType?.includes('application/json')) {
    return (await response.json()) as T;
  }
  return (await response.text()) as T;
};
