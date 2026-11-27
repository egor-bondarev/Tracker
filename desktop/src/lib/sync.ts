import { OfflineError, RejectedError, type TrackerApi } from './api';
import { markSent, pendingTasks } from './queue';
import type { LocalState } from './types';

export interface SyncResult {
  sent: number;
  rejected: number;
  offline: boolean;
}

/**
 * Sends pending tasks oldest first. Stops at the first connection failure so the order is
 * kept; tasks the server rejects are flagged and skipped unless `retryRejected` is set
 * (manual sync). `getState`/`setState` let the window keep working (and stop a task)
 * while requests are in flight.
 */
export async function syncPending(
  api: TrackerApi,
  getState: () => LocalState,
  setState: (state: LocalState) => void,
  retryRejected = false,
): Promise<SyncResult> {
  const result: SyncResult = { sent: 0, rejected: 0, offline: false };
  for (const task of pendingTasks(getState())) {
    if (task.rejected && !retryRejected) continue;
    try {
      await api.putTask(task);
      setState(markSent(getState(), task));
      result.sent += 1;
    } catch (error) {
      if (error instanceof RejectedError) {
        setState(markSent(getState(), task, error.message || 'Rejected by server'));
        result.rejected += 1;
      } else if (error instanceof OfflineError) {
        result.offline = true;
        break;
      } else {
        throw error;
      }
    }
  }
  return result;
}
