import type { LocalState, LocalTask } from './types';
import type { Stamp } from './time';

export interface TaskInput {
  description: string;
  categoryId: number | null;
}

export function activeTask(state: LocalState): LocalTask | undefined {
  return state.tasks.find((task) => task.finish === null);
}

/** Tasks the server does not have in their latest state yet, oldest first. */
export function pendingTasks(state: LocalState): LocalTask[] {
  return state.tasks.filter((task) => !task.synced).sort((a, b) => a.start.localeCompare(b.start));
}

export function startTask(state: LocalState, input: TaskInput, now: Stamp, clientId: string): LocalState {
  if (activeTask(state)) throw new Error('A task is already running');
  const task: LocalTask = { clientId, ...input, start: now, finish: null, synced: false };
  return { ...state, tasks: [...state.tasks, task] };
}

export function stopTask(state: LocalState, now: Stamp): LocalState {
  const running = activeTask(state);
  if (!running) throw new Error('No task is running');
  const finish = now < running.start ? running.start : now;
  return {
    ...state,
    lastFinish: finish,
    tasks: state.tasks.map((task) =>
      task === running ? { ...task, finish, synced: false, rejected: undefined } : task),
  };
}

/** "Forgot to press start": the task starts where the previous one finished. */
export function recordWithoutStart(
  state: LocalState, input: TaskInput, now: Stamp, clientId: string,
): LocalState {
  if (activeTask(state)) throw new Error('A task is already running');
  const start = state.lastFinish && state.lastFinish <= now ? state.lastFinish : now;
  const task: LocalTask = { clientId, ...input, start, finish: now, synced: false };
  return { ...state, lastFinish: now, tasks: [...state.tasks, task] };
}

/** Adds tasks unless a task with the same client id is already known. */
export function addTasks(state: LocalState, tasks: LocalTask[]): LocalState {
  const known = new Set(state.tasks.map((task) => task.clientId));
  const fresh = tasks.filter((task) => !known.has(task.clientId));
  return { ...state, tasks: [...state.tasks, ...fresh] };
}

const sameState = (a: LocalTask, b: LocalTask) =>
  a.description === b.description && a.categoryId === b.categoryId &&
  a.start === b.start && a.finish === b.finish;

/**
 * Records the server's answer for the state that was sent. If the task changed meanwhile
 * (for example it was stopped during the request), it stays pending.
 */
export function markSent(state: LocalState, sent: LocalTask, rejected?: string): LocalState {
  return {
    ...state,
    tasks: state.tasks.map((task) => {
      if (task.clientId !== sent.clientId || !sameState(task, sent)) return task;
      return rejected ? { ...task, rejected } : { ...task, synced: true, rejected: undefined };
    }),
  };
}

/** Drops finished tasks the server already has; the running task always stays. */
export function compact(state: LocalState): LocalState {
  return { ...state, tasks: state.tasks.filter((task) => !task.synced || task.finish === null) };
}
