import { describe, expect, it } from 'vitest';
import { AuthError, OfflineError, RejectedError, TrackerApi, type Fetch } from './api';

function server(status = 200, body: unknown = {}) {
  const calls: Array<{ url: string; headers: Record<string, string> }> = [];
  const fetchImpl: Fetch = async (url, init) => {
    calls.push({ url, headers: { ...(init?.headers as Record<string, string>) } });
    return new Response(JSON.stringify(body), { status });
  };
  return { fetchImpl, calls };
}

const task = {
  clientId: 'a', description: 'task', categoryId: null,
  start: '2026-11-27 09:00:00', finish: null, synced: false,
};

describe('TrackerApi', () => {
  it('sends the token on every call except ready', async () => {
    const { fetchImpl, calls } = server(200, { status: 'ready' });
    const api = new TrackerApi('http://host:8080/', fetchImpl, ' secret ');

    await api.ready();
    await api.putTask(task);
    await api.activeTask();
    await api.categories();
    await api.createCategory('work');

    expect(calls.map((c) => c.url)).toEqual([
      'http://host:8080/api/ready',
      'http://host:8080/api/tasks/by-client-id/a',
      'http://host:8080/api/tasks/active',
      'http://host:8080/api/categories',
      'http://host:8080/api/categories',
    ]);
    expect(calls[0].headers.Authorization).toBeUndefined();
    for (const call of calls.slice(1)) {
      expect(call.headers.Authorization).toBe('Bearer secret');
    }
  });

  it('checks readiness without a token', async () => {
    const { fetchImpl, calls } = server(200, { status: 'ready' });
    expect(await new TrackerApi('http://host:8080', fetchImpl).ready()).toBe(true);
    expect(calls).toHaveLength(1);
  });

  it('raises AuthError without a request when the token is not set', async () => {
    const { fetchImpl, calls } = server();
    await expect(new TrackerApi('http://host:8080', fetchImpl, '  ').activeTask())
      .rejects.toBeInstanceOf(AuthError);
    expect(calls).toHaveLength(0);
  });

  it.each([401, 403])('turns HTTP %i into AuthError', async (status) => {
    const { fetchImpl } = server(status, { detail: 'Invalid token' });
    const error = await new TrackerApi('http://host:8080', fetchImpl, 'wrong')
      .categories().catch((e: unknown) => e);
    expect(error).toBeInstanceOf(AuthError);
    expect(error).not.toBeInstanceOf(RejectedError);
    expect((error as Error).message).toContain('Invalid token');
  });

  it('keeps other 4xx as RejectedError and 5xx as OfflineError', async () => {
    const rejected = new TrackerApi('http://host:8080', server(422).fetchImpl, 't');
    await expect(rejected.putTask(task)).rejects.toBeInstanceOf(RejectedError);
    const down = new TrackerApi('http://host:8080', server(503).fetchImpl, 't');
    await expect(down.putTask(task)).rejects.toBeInstanceOf(OfflineError);
  });
});
