import type { LocalTask } from './types';

/** A task from the old TimeTracker: one `YYYY-MM-DD.json` file per day, times without a date. */
export interface LegacyRecord {
  date: string;
  description: string;
  category: string;
  start: string;
  finish: string;
}

interface LegacyFile {
  Tasks?: Array<{
    Action?: unknown;
    Category?: unknown;
    StartTimestamp?: unknown;
    EndTimestamp?: unknown;
  }>;
}

const TIME = /^\d{1,2}:\d{2}:\d{2}$/;
const DAY_FILE = /^(\d{4}-\d{2}-\d{2})\.json$/;

const normalizeTime = (value: string) => value.padStart(8, '0');

function nextDay(date: string): string {
  const [y, m, d] = date.split('-').map(Number);
  const next = new Date(Date.UTC(y, m - 1, d + 1));
  return next.toISOString().slice(0, 10);
}

/** Parses one day file; skips records without both times or a description. */
export function parseLegacyDay(fileName: string, text: string): LegacyRecord[] {
  const match = DAY_FILE.exec(fileName);
  if (!match) return [];
  const date = match[1];
  let data: LegacyFile;
  try {
    data = JSON.parse(text) as LegacyFile;
  } catch {
    return [];
  }
  const records: LegacyRecord[] = [];
  for (const item of data.Tasks ?? []) {
    const description = typeof item.Action === 'string' ? item.Action.trim() : '';
    const start = typeof item.StartTimestamp === 'string' ? item.StartTimestamp : '';
    const finish = typeof item.EndTimestamp === 'string' ? item.EndTimestamp : '';
    if (!description || !TIME.test(start) || !TIME.test(finish)) continue;
    const startTime = normalizeTime(start);
    const finishTime = normalizeTime(finish);
    // A finish earlier than the start means the task ran past midnight.
    const finishDate = finishTime < startTime ? nextDay(date) : date;
    records.push({
      date,
      description: description.slice(0, 50),
      category: typeof item.Category === 'string' ? item.Category.trim() : '',
      start: `${date} ${startTime}`,
      finish: `${finishDate} ${finishTime}`,
    });
  }
  return records;
}

// Fixed namespace: the same old record always gets the same id, so importing twice is harmless.
const NAMESPACE = 'b6f1c0a2-6a4e-4d0e-9a51-6f0f8f6c2d11';

function bytesFromUuid(uuid: string): Uint8Array {
  const hex = uuid.replace(/-/g, '');
  return Uint8Array.from({ length: 16 }, (_, i) => parseInt(hex.slice(i * 2, i * 2 + 2), 16));
}

/** RFC 4122 version 5 (SHA-1, name-based) UUID. */
export async function uuidV5(name: string, namespace = NAMESPACE): Promise<string> {
  const nameBytes = new TextEncoder().encode(name);
  const input = new Uint8Array(16 + nameBytes.length);
  input.set(bytesFromUuid(namespace));
  input.set(nameBytes, 16);
  const hash = new Uint8Array(await crypto.subtle.digest('SHA-1', input)).slice(0, 16);
  hash[6] = (hash[6] & 0x0f) | 0x50;
  hash[8] = (hash[8] & 0x3f) | 0x80;
  const hex = Array.from(hash, (b) => b.toString(16).padStart(2, '0')).join('');
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
}

/** Turns old records into queued tasks; category names must already map to server ids. */
export async function legacyToTasks(
  records: LegacyRecord[], categoryIds: Map<string, number>,
): Promise<LocalTask[]> {
  return Promise.all(records.map(async (record) => ({
    clientId: await uuidV5(
      [record.start, record.finish, record.description, record.category].join('|')),
    description: record.description,
    categoryId: record.category ? categoryIds.get(record.category.toLowerCase()) ?? null : null,
    start: record.start,
    finish: record.finish,
    synced: false,
  })));
}
