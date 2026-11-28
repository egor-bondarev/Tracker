import type { Stamp } from './time';

export interface Category {
  id: number;
  name: string;
  archived: boolean;
}

/** A task as the window keeps it until the server has confirmed its latest state. */
export interface LocalTask {
  clientId: string;
  description: string;
  categoryId: number | null;
  start: Stamp;
  finish: Stamp | null;
  synced: boolean;
  /** Server refused this state (HTTP 4xx); it is not retried automatically. */
  rejected?: string;
}

export interface LocalState {
  version: 1;
  tasks: LocalTask[];
  /** End of the latest finished task: the start of a task recorded without pressing start. */
  lastFinish: Stamp | null;
  /** Last known categories, so the list works offline. */
  categories: Category[];
  lastSyncAt: Stamp | null;
}

export interface Settings {
  serverUrl: string;
  /** Personal API token issued by the server admin; empty until the user enters it. */
  token: string;
  /** 0 means sync only manually and after actions. */
  syncIntervalMinutes: number;
}

export const DEFAULT_SETTINGS: Settings = { serverUrl: '', token: '', syncIntervalMinutes: 60 };

export const EMPTY_STATE: LocalState = {
  version: 1, tasks: [], lastFinish: null, categories: [], lastSyncAt: null,
};
