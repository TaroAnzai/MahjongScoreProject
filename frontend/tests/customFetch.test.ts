import { beforeEach, describe, expect, it, vi } from 'vitest';
import { customFetch } from '@/api/customFetch';
import { customFetchAdmin } from '@/api/customFetchAdmin';

vi.mock('@/api/loadEnv', () => ({ API_BASE_URL: 'https://api.example.test' }));

describe.each([
  ['一般API', customFetch, undefined],
  ['管理API', customFetchAdmin, 'include'],
] as const)('%sの通信契約', (_name, request, credentials) => {
  const fetchMock = vi.fn<typeof fetch>();
  beforeEach(() => vi.stubGlobal('fetch', fetchMock));

  it('URL・JSON本文・ヘッダー・中断シグナルを渡し、JSONを返す', async () => {
    fetchMock.mockResolvedValue(Response.json({ id: 7 }));
    const signal = new AbortController().signal;
    const data = { scores: [{ player_id: 1, score: 0 }] };
    await expect(request({ url: '/games', method: 'POST', data, signal,
      headers: { 'X-Request-ID': 'test' } })).resolves.toEqual({ id: 7 });
    const [url, options] = fetchMock.mock.calls[0];
    expect(url).toBe('https://api.example.test/games');
    expect(options).toMatchObject({ method: 'POST', body: JSON.stringify(data), signal });
    const headers = new Headers(options?.headers);
    expect(headers.get('Content-Type')).toBe('application/json');
    expect(headers.get('X-Request-ID')).toBe('test');
    expect(options?.credentials).toBe(credentials);
  });

  it('HeadersInitの統合と他のoptionsの優先順位を保持する', async () => {
    fetchMock.mockResolvedValue(Response.json({}));
    const signal = new AbortController().signal;
    await request({ url: '/games', method: 'POST', data: {},
      headers: new Headers({ 'Content-Type': 'config/type', 'X-Keep': 'yes' }) },
      { headers: [['content-type', 'options/type']], method: 'PUT', body: 'override', signal, credentials: 'omit' });
    const options = fetchMock.mock.calls[0][1];
    expect(options).toMatchObject({ method: 'PUT', body: 'override', signal, credentials: 'omit' });
    expect(new Headers(options?.headers).get('Content-Type')).toBe('options/type');
    expect(new Headers(options?.headers).get('X-Keep')).toBe('yes');
  });

  it('検索条件をURLエンコードし、GETでは本文を送らない', async () => {
    fetchMock.mockResolvedValue(Response.json([]));
    await request({ url: '/players', method: 'GET', data: { ignored: true },
      params: { name: '東 & 南', page: 2 } });
    const [url, options] = fetchMock.mock.calls[0];
    const parsed = new URL(String(url));
    expect(parsed.searchParams.get('name')).toBe('東 & 南');
    expect(parsed.searchParams.get('page')).toBe('2');
    expect(options?.body).toBeUndefined();
  });

  it('JSON以外のエクスポート内容を文字列として返す', async () => {
    fetchMock.mockResolvedValue(new Response('name,score\n東,10', {
      headers: { 'Content-Type': 'text/csv' },
    }));
    await expect(request({ url: '/export', method: 'GET' })).resolves.toBe('name,score\n東,10');
  });

  it('APIのバリデーションエラーを失わずに呼び出し元へ渡す', async () => {
    const body = { errors: { json: { scores: ['合計が0ではありません'] } } };
    fetchMock.mockResolvedValue(Response.json(body, { status: 422, statusText: 'Unprocessable Entity' }));
    await expect(request({ url: '/games', method: 'PUT' })).rejects.toEqual({
      status: 422, statusText: 'Unprocessable Entity', body, url: 'https://api.example.test/games',
    });
  });

  it('プロキシがHTMLエラーを返してもHTTPステータスを保持する', async () => {
    fetchMock.mockResolvedValue(new Response('<html>Bad Gateway</html>', { status: 502, statusText: 'Bad Gateway' }));
    await expect(request({ url: '/games', method: 'GET' })).rejects.toMatchObject({ status: 502, body: {} });
  });

  it('通信切断のエラーを呼び出し元へ伝える', async () => {
    const error = new TypeError('Failed to fetch');
    fetchMock.mockRejectedValue(error);
    await expect(request({ url: '/games', method: 'GET' })).rejects.toBe(error);
  });

  it('[BUG-04] 追加ヘッダーを指定してもJSONのContent-Typeと既存ヘッダーを保持する', async () => {
    fetchMock.mockResolvedValue(Response.json({}));
    await request({ url: '/games', method: 'POST', data: { scores: [] },
      headers: { 'X-Request-ID': 'test' } }, { headers: { Authorization: 'Bearer test-token' } });
    const headers = new Headers(fetchMock.mock.calls[0][1]?.headers);
    expect(headers.get('Content-Type')).toBe('application/json');
    expect(headers.get('X-Request-ID')).toBe('test');
    expect(headers.get('Authorization')).toBe('Bearer test-token');
    expect(fetchMock.mock.calls[0][1]?.credentials).toBe(credentials);
  });
});

it('管理APIの削除成功（204）は空のJSONを解析せずnullを返す', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(null, {
    status: 204, headers: { 'Content-Type': 'application/json' },
  })));
  await expect(customFetchAdmin({ url: '/groups/test', method: 'DELETE' })).resolves.toBeNull();
});
