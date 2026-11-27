import { describe, expect, it } from 'vitest';
import { legacyToTasks, parseLegacyDay, uuidV5 } from './legacy';

const day = JSON.stringify({
  Tasks: [
    { Action: 'Report', Category: 'Work', StartTimestamp: '10:00:00', EndTimestamp: '10:30:00', Duration: '0:30:00' },
    { Action: 'Late', Category: '', StartTimestamp: '23:50:00', EndTimestamp: '0:10:00', Duration: '0:20:00' },
    { Action: '', StartTimestamp: '11:00:00', EndTimestamp: '11:05:00' },
    { Action: 'Unfinished', StartTimestamp: '12:00:00' },
  ],
});

describe('legacy import', () => {
  it('reads day files and moves past-midnight finishes to the next day', () => {
    expect(parseLegacyDay('2024-06-30.json', day)).toEqual([
      { date: '2024-06-30', description: 'Report', category: 'Work',
        start: '2024-06-30 10:00:00', finish: '2024-06-30 10:30:00' },
      { date: '2024-06-30', description: 'Late', category: '',
        start: '2024-06-30 23:50:00', finish: '2024-07-01 00:10:00' },
    ]);
  });

  it('ignores other files and broken JSON', () => {
    expect(parseLegacyDay('user_settings.json', day)).toEqual([]);
    expect(parseLegacyDay('2024-06-30.json', '{not json')).toEqual([]);
  });

  it('produces RFC 4122 v5 ids', async () => {
    // Reference value from Python: uuid.uuid5(uuid.NAMESPACE_DNS, 'python.org')
    expect(await uuidV5('python.org', '6ba7b810-9dad-11d1-80b4-00c04fd430c8'))
      .toBe('886313e1-3b8a-5372-9b90-0c9aee199e5d');
  });

  it('gives the same record the same id, so a repeated import adds nothing', async () => {
    const records = parseLegacyDay('2024-06-30.json', day);
    const ids = new Map([['work', 7]]);
    const first = await legacyToTasks(records, ids);
    const second = await legacyToTasks(records, ids);
    expect(first.map((t) => t.clientId)).toEqual(second.map((t) => t.clientId));
    expect(new Set(first.map((t) => t.clientId)).size).toBe(2);
    expect(first.map((t) => t.categoryId)).toEqual([7, null]);
  });
});
