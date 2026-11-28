/** Server timestamps are naive local times: "YYYY-MM-DD HH:MM:SS". */
export type Stamp = string;

const pad = (n: number) => String(n).padStart(2, '0');

export function toStamp(date: Date): Stamp {
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ` +
    `${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
}

/**
 * The server answers with ISO times ("YYYY-MM-DDTHH:MM:SS", maybe with fractions);
 * the window keeps "YYYY-MM-DD HH:MM:SS" so stamps compare correctly as strings.
 */
export function stampFromServer(value: string): Stamp {
  return value.replace('T', ' ').slice(0, 19);
}

export function fromStamp(stamp: Stamp): Date {
  // Also accepts the ISO "T" separator, so a stamp saved by an older build still works.
  const [d, t = '00:00:00'] = stamp.split(/[ T]/);
  const [y, mo, day] = d.split('-').map(Number);
  const [h, mi, s] = t.split(':').map(Number);
  return new Date(y, mo - 1, day, h, mi, s);
}

/** Elapsed time as HH:MM:SS; hours may exceed 24. */
export function formatElapsed(ms: number): string {
  const total = Math.max(0, Math.floor(ms / 1000));
  return `${pad(Math.floor(total / 3600))}:${pad(Math.floor(total / 60) % 60)}:${pad(total % 60)}`;
}
