import type { Category, LocalTask } from './types';

export type Fetch = (input: string, init?: RequestInit) => Promise<Response>;

/** Raised when the server could not be reached or did not answer in time. */
export class OfflineError extends Error {}

/** Raised when the server answered with 4xx: resending the same data will not help. */
export class RejectedError extends Error {}

/**
 * Raised when the token is missing or the server refused it (HTTP 401/403). The data is
 * fine, so callers keep it queued until the token is fixed.
 */
export class AuthError extends Error {}

export interface ServerTask {
  id: number;
  client_id: string | null;
  description: string;
  category_id: number | null;
  start_timestamp: string | null;
  finish_timestamp: string | null;
}

/**
 * Talks to the record API through the web address (nginx proxies it under /api). Every
 * call except `ready()` sends the user's token as `Authorization: Bearer <token>`.
 */
export class TrackerApi {
  constructor(
    private readonly serverUrl: string,
    private readonly fetchImpl: Fetch,
    private readonly token = '',
    private readonly timeoutMs = 4000,
  ) {}

  get analyticsUrl(): string {
    return this.base();
  }

  private base(): string {
    return this.serverUrl.trim().replace(/\/+$/, '');
  }

  private async call<T>(path: string, init: RequestInit = {}, auth = true): Promise<T> {
    if (!this.base()) throw new OfflineError('Server address is not set');
    const token = this.token.trim();
    if (auth && !token) throw new AuthError('Token is not set');
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.timeoutMs);
    let response: Response;
    try {
      response = await this.fetchImpl(`${this.base()}/api${path}`, {
        ...init,
        headers: {
          'Content-Type': 'application/json',
          ...(auth ? { Authorization: `Bearer ${token}` } : {}),
          ...(init.headers ?? {}),
        },
        signal: controller.signal,
      });
    } catch (error) {
      throw new OfflineError(String(error));
    } finally {
      clearTimeout(timer);
    }
    if (response.status === 401 || response.status === 403) {
      throw new AuthError(await response.text());
    }
    if (response.status >= 400 && response.status < 500) {
      throw new RejectedError(await response.text());
    }
    if (!response.ok) throw new OfflineError(`HTTP ${response.status}`);
    return response.status === 204 ? (undefined as T) : (response.json() as Promise<T>);
  }

  async ready(): Promise<boolean> {
    const body = await this.call<{ status: string }>('/ready', {}, false);
    return body?.status === 'ready';
  }

  putTask(task: LocalTask): Promise<ServerTask> {
    return this.call(`/tasks/by-client-id/${task.clientId}`, {
      method: 'PUT',
      body: JSON.stringify({
        description: task.description,
        category_id: task.categoryId,
        start_timestamp: task.start,
        finish_timestamp: task.finish,
      }),
    });
  }

  activeTask(): Promise<ServerTask | null> {
    return this.call('/tasks/active');
  }

  categories(): Promise<Category[]> {
    return this.call('/categories');
  }

  createCategory(name: string): Promise<Category> {
    return this.call('/categories', { method: 'POST', body: JSON.stringify({ name }) });
  }
}
