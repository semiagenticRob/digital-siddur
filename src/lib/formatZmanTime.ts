/**
 * Formats an ISO datetime string's wall-clock time as 12-hour HH:MM with no
 * leading zero and no AM/PM (the zmanim strip labels already say which cell
 * is which). Slices chars 11-16 (HH:MM) rather than using Date/Intl so the
 * displayed time matches the ISO string's own offset, not the device's.
 */
export function formatZmanTime(iso: string): string {
  const hhmm = iso.slice(11, 16);
  const [hStr, mStr] = hhmm.split(':');
  let h = Number(hStr) % 12;
  if (h === 0) h = 12;
  return `${h}:${mStr}`;
}
