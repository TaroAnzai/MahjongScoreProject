// src/api/customFetch.ts
export const customFetch = async <T>(
  url: string,
  config: RequestInit
): Promise<T> => {
  const response = await fetch(url, {
    ...config,
    credentials: 'include', // Cookie セッションを送信
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
};