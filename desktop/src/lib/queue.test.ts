import { describe, expect, it } from 'vitest';
import {
  activeTask, addTasks, compact, markSent, pendingTasks, recordWithoutStart, startTask, stopTask,
} from './queue';
import { EMPTY_STATE } from './types';

const input = { description: 'report', categoryId: 3 };

describe('queue', () => {
  it('starts and stops a task, keeping both changes pending', () => {
    let state = startTask(EMPTY_STATE, input, '2026-11-27 10:00:00', 'a');
    expect(activeTask(state)?.clientId).toBe('a');
    state = stopTask(state, '2026-11-27 10:30:00');
    expect(activeTask(state)).toBeUndefined();
    expect(state.lastFinish).toBe('2026-11-27 10:30:00');
    expect(pendingTasks(state)).toHaveLength(1);
  });

  it('refuses a second running task', () => {
    const state = startTask(EMPTY_STATE, input, '2026-11-27 10:00:00', 'a');
    expect(() => startTask(state, input, '2026-11-27 10:01:00', 'b')).toThrow();
  });

  it('never stops before the start', () => {
    const state = stopTask(startTask(EMPTY_STATE, input, '2026-11-27 10:00:00', 'a'),
      '2026-11-27 09:59:00');
    expect(state.tasks[0].finish).toBe('2026-11-27 10:00:00');
  });

  it('records without start from the previous finish, or from now', () => {
    const first = recordWithoutStart(EMPTY_STATE, input, '2026-11-27 10:00:00', 'a');
    expect(first.tasks[0].start).toBe('2026-11-27 10:00:00');
    const second = recordWithoutStart(first, input, '2026-11-27 11:00:00', 'b');
    expect(second.tasks[1]).toMatchObject({ start: '2026-11-27 10:00:00', finish: '2026-11-27 11:00:00' });
  });

  it('marks only the state that was sent', () => {
    const started = startTask(EMPTY_STATE, input, '2026-11-27 10:00:00', 'a');
    const sent = started.tasks[0];
    const stopped = stopTask(started, '2026-11-27 10:05:00');
    expect(markSent(stopped, sent).tasks[0].synced).toBe(false);
    expect(markSent(stopped, stopped.tasks[0]).tasks[0].synced).toBe(true);
  });

  it('flags rejected tasks without marking them synced', () => {
    const state = startTask(EMPTY_STATE, input, '2026-11-27 10:00:00', 'a');
    const rejected = markSent(state, state.tasks[0], 'bad category');
    expect(rejected.tasks[0]).toMatchObject({ synced: false, rejected: 'bad category' });
  });

  it('compacts synced finished tasks but keeps the running one', () => {
    let state = recordWithoutStart(EMPTY_STATE, input, '2026-11-27 10:00:00', 'a');
    state = markSent(state, state.tasks[0]);
    state = startTask(state, input, '2026-11-27 10:10:00', 'b');
    state = markSent(state, state.tasks[1]);
    expect(compact(state).tasks.map((t) => t.clientId)).toEqual(['b']);
  });

  it('does not add a task twice', () => {
    const state = recordWithoutStart(EMPTY_STATE, input, '2026-11-27 10:00:00', 'a');
    expect(addTasks(state, state.tasks).tasks).toHaveLength(1);
  });
});
