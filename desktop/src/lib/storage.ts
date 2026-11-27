import { invoke } from '@tauri-apps/api/core';
import { DEFAULT_SETTINGS, EMPTY_STATE, type LocalState, type Settings } from './types';

async function readJson<T>(name: string, fallback: T): Promise<T> {
  const text = await invoke<string | null>('read_app_file', { name });
  if (!text) return fallback;
  try {
    return { ...fallback, ...JSON.parse(text) } as T;
  } catch {
    // Keep a damaged file aside instead of overwriting it with a fresh one.
    await invoke('write_app_file', { name: name.replace('.json', '.broken.json'), content: text });
    return fallback;
  }
}

const writeJson = (name: string, value: unknown) =>
  invoke('write_app_file', { name, content: JSON.stringify(value, null, 2) });

export const loadSettings = () => readJson<Settings>('settings.json', DEFAULT_SETTINGS);
export const saveSettings = (settings: Settings) => writeJson('settings.json', settings);
export const loadState = () => readJson<LocalState>('tasks.json', EMPTY_STATE);
export const saveState = (state: LocalState) => writeJson('tasks.json', state);

export const readLegacyDir = (path: string) =>
  invoke<Array<[string, string]>>('read_legacy_dir', { path });
