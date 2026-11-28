import { describe, expect, it } from 'vitest';
import { TrackerApi, type Fetch } from './api';
import { recordWithoutStart, startTask, stopTask } from './queue';
import { syncPending } from './sync';
import { EMPTY_STATE, type LocalState } from './types';

const input = { description: 'task', categoryId: null };

function store(initial: LocalState) {
  let state = initial;
  return { get: () => state, set: (next: LocalState) => { state = next; } };
}

function server(answer: (url: string, body: unknown) => Response | Error) {
  const calls: Array<{ url: string; body: unknown }> = [];
  const fetchImpl: Fetch = async (url, init) => {
    const body = init?.body ? JSON.parse(String(init.body)) : undefined;
    calls.push({ url, body });
    const result = answer(url, body);
    if (result instanceof Error) throw result;
    return result;
  };
  return { api: new TrackerApi('http://host:8080/', fetchImpl, 'secret'), calls };
}

const ok = () => new Response(JSON.stringify({ id: 1 }), { status: 200 });

describe('syncPending', () => {
  it('sends pending tasks oldest first through /api', async () => {
    let state = recordWithoutStart(EMPTY_STATE, input, '2026-11-27 10:00:00', 'b');
    state = recordWithoutStart(state, input, '2026-11-27 09:00:00', 'a');
    const s = store(state);
    const { api, calls } = server(ok);

    const result = await syncPending(api, s.get, s.set);

    expect(result).toEqual({ sent: 2, rejected: 0, offline: false, unauthorized: false });
    expect(calls.map((c) => c.url)).toEqual([
      'http://host:8080/api/tasks/by-client-id/a', 'http://host:8080/api/tasks/by-client-id/b']);
    expect(calls[0].body).toEqual({
      description: 'task', category_id: null,
      start_timestamp: '2026-11-27 09:00:00', finish_timestamp: '2026-11-27 09:00:00' });
    expect(s.get().tasks.every((t) => t.synced)).toBe(true);
  });

  it('stops at the first connection failure and keeps the queue', async () => {
    let state = recordWithoutStart(EMPTY_STATE, input, '2026-11-27 09:00:00', 'a');
    state = recordWithoutStart(state, input, '2026-11-27 10:00:00', 'b');
    const s = store(state);
    const { api, calls } = server(() => new TypeError('network down'));

    const result = await syncPending(api, s.get, s.set);

    expect(result.offline).toBe(true);
    expect(calls).toHaveLength(1);
    expect(s.get().tasks.some((t) => t.synced)).toBe(false);
  });

  it('treats 5xx as offline and 4xx as rejected', async () => {
    let state = recordWithoutStart(EMPTY_STATE, input, '2026-11-27 09:00:00', 'a');
    state = recordWithoutStart(state, input, '2026-11-27 10:00:00', 'b');
    const s = store(state);
    const { api } = server((url) => url.endsWith('/a')
      ? new Response('{"detail":"bad"}', { status: 422 }) : ok());

    expect(await syncPending(api, s.get, s.set))
      .toEqual({ sent: 1, rejected: 1, offline: false, unauthorized: false });
    expect(s.get().tasks.find((t) => t.clientId === 'a')?.rejected).toContain('bad');

    const again = server(() => new Response('', { status: 503 }));
    expect((await syncPending(again.api, s.get, s.set)).sent).toBe(0);
    expect(again.calls).toHaveLength(0);
    expect((await syncPending(again.api, s.get, s.set, true)).offline).toBe(true);
  });

  it('keeps a task pending when it was stopped during the request', async () => {
    const s = store(startTask(EMPTY_STATE, input, '2026-11-27 10:00:00', 'a'));
    const { api } = server(() => {
      s.set(stopTask(s.get(), '2026-11-27 10:01:00'));
      return ok();
    });

    await syncPending(api, s.get, s.set);

    expect(s.get().tasks[0]).toMatchObject({ synced: false, finish: '2026-11-27 10:01:00' });
  });

  it('reports a missing server address as offline', async () => {
    const s = store(recordWithoutStart(EMPTY_STATE, input, '2026-11-27 10:00:00', 'a'));
    const api = new TrackerApi('', async () => ok(), 'secret');
    expect((await syncPending(api, s.get, s.set)).offline).toBe(true);
  });

  it.each([401, 403])('stops on HTTP %i and keeps tasks pending and unflagged', async (status) => {
    let state = recordWithoutStart(EMPTY_STATE, input, '2026-11-27 09:00:00', 'a');
    state = recordWithoutStart(state, input, '2026-11-27 10:00:00', 'b');
    const s = store(state);
    const { api, calls } = server(() =>
      new Response('{"detail":"Invalid token"}', { status }));

    for (const retryRejected of [false, true]) {
      expect(await syncPending(api, s.get, s.set, retryRejected))
        .toEqual({ sent: 0, rejected: 0, offline: false, unauthorized: true });
    }

    expect(calls).toHaveLength(2);
    expect(s.get().tasks).toHaveLength(2);
    expect(s.get().tasks.every((t) => !t.synced && t.rejected === undefined)).toBe(true);
  });

  it('stops without a request when the token is not set', async () => {
    const s = store(recordWithoutStart(EMPTY_STATE, input, '2026-11-27 10:00:00', 'a'));
    const calls: string[] = [];
    const api = new TrackerApi('http://host:8080', async (url) => { calls.push(url); return ok(); });

    expect((await syncPending(api, s.get, s.set)).unauthorized).toBe(true);
    expect(calls).toEqual([]);
    expect(s.get().tasks[0]).toMatchObject({ synced: false });
    expect(s.get().tasks[0].rejected).toBeUndefined();
  });
});
