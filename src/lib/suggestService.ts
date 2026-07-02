/**
 * Suggests the appropriate prayer service based on time of day and zmanim.
 * @param now Current time
 * @param dayZmanim Zmanim for the location (sunset and optional minchaGedola as ISO strings)
 * @returns Service id ('shacharit', 'minchah', 'maariv', or 'maariv-motzaei-shabbos'),
 *   or `null` when there is no weekday-siddur suggestion to make: civil
 *   Friday past the evening boundary through civil Saturday before the
 *   evening boundary is Shabbos, which this weekday siddur doesn't cover.
 *   Saturday past the evening boundary resumes with Motzaei Shabbos Maariv.
 *
 * ASSUMPTION: Device timezone == location timezone (true except during travel).
 * Wall-clock comparison uses HH:MM from ISO string vs device clock HH:MM.
 */
export function suggestService(
  now: Date,
  dayZmanim: { sunset: string; minchaGedola?: string } | null
): string | null {
  // Extract device time as HH:MM (zero-padded) from device clock
  const hours = String(now.getHours()).padStart(2, '0');
  const minutes = String(now.getMinutes()).padStart(2, '0');
  const deviceTime = `${hours}:${minutes}`;

  // Determine if we're in evening (after shkiah or >= 19:30 fallback)
  let isEvening = false;

  if (dayZmanim) {
    // Extract sunset time from ISO string (chars 11–16 = HH:MM)
    const sunsetTime = dayZmanim.sunset.slice(11, 16);
    isEvening = deviceTime >= sunsetTime;
  } else {
    // No zmanim: use 19:30 fallback
    isEvening = deviceTime >= '19:30';
  }

  const day = now.getDay(); // 0=Sun ... 5=Fri, 6=Sat

  // Shabbos window: Friday evening through Saturday's evening boundary.
  // This is a weekday siddur, so there's no service to suggest here —
  // except Saturday evening, which is Motzaei Shabbos Maariv (below).
  if (day === 5 && isEvening) return null;
  if (day === 6 && !isEvening) return null;

  if (isEvening) {
    // After shkiah: check if Saturday for motzaei shabbos
    if (day === 6) {
      return 'maariv-motzaei-shabbos';
    } else {
      return 'maariv';
    }
  }

  // Before shkiah: use midday boundary to distinguish shacharit vs minchah
  let midday = '13:00';
  if (dayZmanim?.minchaGedola) {
    midday = dayZmanim.minchaGedola.slice(11, 16);
  }

  if (deviceTime < midday) {
    return 'shacharit';
  } else {
    return 'minchah';
  }
}
