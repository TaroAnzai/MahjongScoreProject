import { beforeEach, describe, expect, it, vi } from 'vitest';
import { customFetch } from '@/api/customFetch';
import { customFetchAdmin } from '@/api/customFetchAdmin';
import { getApiGroupsGroupKey, getApiGroupsGroupKeyPlayerStats, postApiGroups } from '@/api/generated/mahjongApi';
import { getApiAdminGroups, postApiAdminLogin } from '@/api/generated/adminApi';

const env = vi.hoisted(() => ({ API_BASE_URL: 'http://localhost:6080' }));
vi.mock('@/api/loadEnv', () => env);

const fetchMock = vi.fn<typeof fetch>();
beforeEach(() => {
  fetchMock.mockReset();
  vi.stubGlobal('fetch', fetchMock);
  env.API_BASE_URL = 'http://localhost:6080';
});

describe.each([
  ['一般API', customFetch, undefined],
  ['管理API', customFetchAdmin, 'include'],
] as const)('%sの通信契約', (_name, request, credentials) => {
  it.each(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])('%sのRequestInitとJSONレスポンスを保持する', async (method) => {
    fetchMock.mockResolvedValue(Response.json({ id: 7 }));
    const signal = new AbortController().signal;
    const body = method === 'GET' ? undefined : JSON.stringify({ score: 0 });
    await expect(request('/games', { method, body, signal,
      headers: { 'X-Request-ID': 'test', Authorization: 'Bearer test-token' },
    })).resolves.toEqual({ id: 7 });
    const [url, options] = fetchMock.mock.calls[0];
    expect(url).toBe('http://localhost:6080/games');
    expect(options).toMatchObject({ method, body, signal });
    expect(options?.credentials).toBe(credentials);
    const headers = new Headers(options?.headers);
    expect(headers.get('Content-Type')).toBe('application/json');
    expect(headers.get('X-Request-ID')).toBe('test');
    expect(headers.get('Authorization')).toBe('Bearer test-token');
  });

  it.each([new Headers({ 'Content-Type': 'text/plain' }), [['Content-Type', 'text/plain']] as [string, string][]])('HeadersInitで既定ヘッダーを上書きできる', async (headers) => {
    fetchMock.mockResolvedValue(Response.json({}));
    await request('/games', { headers });
    expect(new Headers(fetchMock.mock.calls[0][1]?.headers).get('Content-Type')).toBe('text/plain');
  });

  it.each(['/api/groups/test-key', 'api/groups/test-key', '//api/groups/test-key'])('結合時にスラッシュが重複しない: %s', async (path) => {
    env.API_BASE_URL = 'http://localhost:6080/';
    fetchMock.mockResolvedValue(Response.json({}));
    await request(path);
    expect(fetchMock.mock.calls[0][0]).toBe('http://localhost:6080/api/groups/test-key');
  });

  it('絶対URLとエンコード済みクエリを保持する', async () => {
    fetchMock.mockResolvedValue(Response.json([]));
    const url = 'https://example.test/players?' + new URLSearchParams({ name: '東 & 南', page: '2' });
    await request(url, { method: 'GET' });
    expect(fetchMock.mock.calls[0][0]).toBe(url);
    expect(fetchMock.mock.calls[0][1]?.body).toBeUndefined();
  });

  it('JSON以外の本文を文字列として返す', async () => {
    fetchMock.mockResolvedValue(new Response('name,score', { headers: { 'Content-Type': 'text/csv' } }));
    await expect(request('/export')).resolves.toBe('name,score');
  });

  it('204ではJSON解析を行わずnullを返す', async () => {
    const response = new Response(null, { status: 204, headers: { 'Content-Type': 'application/json' } });
    const json = vi.spyOn(response, 'json');
    fetchMock.mockResolvedValue(response);
    await expect(request('/games', { method: 'DELETE' })).resolves.toBeNull();
    expect(json).not.toHaveBeenCalled();
  });

  it('HTTPエラーの詳細を保持する', async () => {
    const body = { errors: { score: ['invalid'] } };
    fetchMock.mockResolvedValue(Response.json(body, { status: 422, statusText: 'Unprocessable Entity' }));
    await expect(request('/games', { method: 'PUT' })).rejects.toEqual({
      status: 422, statusText: 'Unprocessable Entity', body, url: 'http://localhost:6080/games',
    });
  });

  it('HTMLエラーでもHTTPステータスを保持する', async () => {
    fetchMock.mockResolvedValue(new Response('<html>Bad Gateway</html>', { status: 502, statusText: 'Bad Gateway' }));
    await expect(request('/games')).rejects.toEqual({ status: 502, statusText: 'Bad Gateway', body: {}, url: 'http://localhost:6080/games' });
  });

  it('通信エラーをそのまま伝播する', async () => {
    const error = new TypeError('Failed to fetch');
    fetchMock.mockRejectedValue(error);
    await expect(request('/games')).rejects.toBe(error);
  });
});

describe('Orval生成関数から実mutatorへの回帰テスト', () => {
  it.each([
    ['一般API', (options: RequestInit) => getApiGroupsGroupKey('test-key', options), '/api/groups/test-key', undefined],
    ['管理API', (options: RequestInit) => getApiAdminGroups(options), '/api/admin/groups', 'include'],
  ] as const)('%sで正しいURLとRequestInitをfetchへ渡す', async (_name, call, path, credentials) => {
    fetchMock.mockResolvedValue(Response.json({ id: 7 }));
    const signal = new AbortController().signal;
    await expect(call({ signal, headers: { 'X-Request-ID': 'generated' } })).resolves.toEqual({ id: 7 });
    const [url, options] = fetchMock.mock.calls[0];
    expect(url).toBe(`http://localhost:6080${path}`);
    expect(String(url)).not.toContain('undefined');
    expect(options).toMatchObject({ method: 'GET', signal });
    expect(options?.body).toBeUndefined();
    expect(options?.credentials).toBe(credentials);
    expect(new Headers(options?.headers).get('X-Request-ID')).toBe('generated');
  });

  it('生成されたクエリ文字列をそのまま送信する', async () => {
    fetchMock.mockResolvedValue(Response.json([]));
    await getApiGroupsGroupKeyPlayerStats('test-key', { start_date: '2026-09-01', end_date: null });
    expect(fetchMock.mock.calls[0][0]).toBe('http://localhost:6080/api/groups/test-key/player_stats?start_date=2026-09-01&end_date=null');
  });

  it('一般APIの生成済みJSON本文を二重に文字列化しない', async () => {
    fetchMock.mockResolvedValue(Response.json({}));
    const body = { token: 'test-token' };
    await postApiGroups(body);
    expect(fetchMock.mock.calls[0][1]).toMatchObject({ method: 'POST', body: JSON.stringify(body) });
  });

  it('管理APIのJSON本文とCookie認証を保持する', async () => {
    fetchMock.mockResolvedValue(Response.json({}));
    const body = { username: 'admin', password: 'test' };
    await postApiAdminLogin(body, { credentials: 'omit' });
    expect(fetchMock.mock.calls[0][1]).toMatchObject({ method: 'POST', body: JSON.stringify(body), credentials: 'include' });
  });
});
