import { describe, expect, it } from 'vitest';
import { formatElapsed, fromStamp, stampFromServer, toStamp } from './time';

describe('time', () => {
  it('turns server ISO times into window stamps', () => {
    expect(stampFromServer('2999-01-01T09:00:00')).toBe('2999-01-01 09:00:00');
    expect(stampFromServer('2026-11-28T10:20:30.123456')).toBe('2026-11-28 10:20:30');
    expect(stampFromServer('2026-11-28 10:20:30')).toBe('2026-11-28 10:20:30');
  });

  it('reads stamps with either separator', () => {
    const expected = new Date(2026, 10, 28, 10, 20, 30).getTime();
    expect(fromStamp('2026-11-28 10:20:30').getTime()).toBe(expected);
    expect(fromStamp('2026-11-28T10:20:30').getTime()).toBe(expected);
  });

  it('round-trips local dates', () => {
    const date = new Date(2026, 0, 2, 3, 4, 5);
    expect(fromStamp(toStamp(date)).getTime()).toBe(date.getTime());
    expect(formatElapsed(25 * 3600_000 + 61_000)).toBe('25:01:01');
  });
});
