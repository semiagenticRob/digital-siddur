import { specialDayBadges } from '../specialDays';
import { HOME_CATEGORIES } from '../../content/categories';

const SPECIAL_DAY_IDS = HOME_CATEGORIES.find((c) => c.key === 'special')!.serviceIds;

test('plain weekday has no badges', () => {
  expect(specialDayBadges(new Date(2026, 6, 1))).toEqual({}); // Wed 1 Jul 2026 = 16 Tammuz 5786
});

test('Saturday gets motzaei-shabbos Tonight', () => {
  expect(specialDayBadges(new Date(2026, 6, 4))['maariv-motzaei-shabbos']).toBe('Tonight');
});

test('Rosh Chodesh gets mussaf + hallel', () => {
  // 1 Av 5786 = 15 Jul 2026 (verified via hebcal converter)
  const badges = specialDayBadges(new Date(2026, 6, 15));
  expect(badges['mussaf-rosh-chodesh']).toBe('Today');
  expect(badges['hallel']).toBe('Today');
});

test('Shabbos Rosh Chodesh keeps hallel but not the weekday mussaf', () => {
  // 1 Iyar 5786 = Sat 18 Apr 2026
  const badges = specialDayBadges(new Date(2026, 3, 18));
  expect(badges['mussaf-rosh-chodesh']).toBeUndefined();
  expect(badges['hallel']).toBe('Today');
});

test('1 Tishrei (Rosh Hashanah) does not get mussaf-rosh-chodesh', () => {
  // 1 Tishrei 5787 = 12 Sep 2026 (verified via hebcal converter)
  const badges = specialDayBadges(new Date(2026, 8, 12));
  expect(badges['mussaf-rosh-chodesh']).toBeUndefined();
});

test('Omer period gets sefirah Tonight (evening begins next Hebrew day)', () => {
  // 30 Apr 2026 = 13 Iyar 5786 → tonight begins 14 Iyar, within the Omer
  expect(specialDayBadges(new Date(2026, 3, 30))['sefiras-haomer']).toBe('Tonight');
  // 24 May 2026 = 8 Sivan → Omer over
  expect(specialDayBadges(new Date(2026, 4, 24))['sefiras-haomer']).toBeUndefined();
});

test('Pesach hallel runs 15-22 Nisan (diaspora); 23 Nisan does not', () => {
  // All verified via hebcal converter for 5786:
  // 15 Nisan = 2 Apr 2026 ("Pesach I"); 17 Nisan = 4 Apr ("Pesach III (CH''M)");
  // 22 Nisan = 9 Apr ("Pesach VIII", Acharon Shel Pesach); 23 Nisan = 10 Apr (plain day).
  expect(specialDayBadges(new Date(2026, 3, 2))['hallel']).toBe('Today'); // 15 Nisan, Yom Tov I
  const cholHamoed = specialDayBadges(new Date(2026, 3, 5)); // 18 Nisan (Sunday), Chol Hamoed
  expect(cholHamoed['mussaf-chol-hamoed']).toBe('Today');
  expect(cholHamoed['hallel']).toBe('Today');
  // 17 Nisan = 4 Apr 2026 is Shabbos Chol Hamoed: Shabbos Mussaf, not the weekday one.
  const shabbosCholHamoed = specialDayBadges(new Date(2026, 3, 4));
  expect(shabbosCholHamoed['mussaf-chol-hamoed']).toBeUndefined();
  expect(shabbosCholHamoed['hallel']).toBe('Today');
  expect(specialDayBadges(new Date(2026, 3, 9))['hallel']).toBe('Today'); // 22 Nisan, Acharon Shel Pesach
  expect(specialDayBadges(new Date(2026, 3, 10))['hallel']).toBeUndefined(); // 23 Nisan — Pesach over
});

test('Shavuos (6-7 Sivan, diaspora) gets hallel; 8 Sivan does not', () => {
  // 6 Sivan 5786 = 22 May 2026, "Shavuot I"; 7 Sivan = 23 May, "Shavuot II";
  // 8 Sivan = 24 May, plain day (all verified via hebcal converter).
  expect(specialDayBadges(new Date(2026, 4, 22))['hallel']).toBe('Today');
  expect(specialDayBadges(new Date(2026, 4, 23))['hallel']).toBe('Today');
  expect(specialDayBadges(new Date(2026, 4, 24))['hallel']).toBeUndefined();
});

test('Chol Hamoed Sukkos gets mussaf-chol-hamoed + hallel + lulav', () => {
  // 17 Tishrei 5787 = 28 Sep 2026, Monday (verified via hebcal converter)
  const badges = specialDayBadges(new Date(2026, 8, 28));
  expect(badges['mussaf-chol-hamoed']).toBe('Today');
  expect(badges['hallel']).toBe('Today');
  expect(badges['netilas-lulav']).toBe('Today');
});

test('no lulav on Shabbos even during Sukkos', () => {
  // 15 Tishrei 5787 (Sukkos I) = 26 Sep 2026, which is a Saturday this year
  // (verified via hebcal converter: falls within the 15-21 Tishrei lulav
  // window, so it is the "Shabbos during Sukkos" case the rule excludes).
  const shabbosSukkos = new Date(2026, 8, 26);
  const badges = specialDayBadges(shabbosSukkos);
  expect(badges['netilas-lulav']).toBeUndefined();
  expect(badges['hallel']).toBe('Today');
});

describe('Chanukah (8 days, end date depends on Kislev length)', () => {
  test('30-day-Kislev year: Chanukah runs 25 Kislev - 2 Teves', () => {
    // 5786 has a 30-day Kislev (verified: 30 Kislev 5786 = 20 Dec 2025 exists).
    // Day 1 = 25 Kislev = 15 Dec 2025 ... day 8 = 2 Teves = 22 Dec 2025.
    expect(specialDayBadges(new Date(2025, 11, 15))['hallel']).toBe('Today'); // 25 Kislev, day 1
    expect(specialDayBadges(new Date(2025, 11, 20))['hallel']).toBe('Today'); // 30 Kislev, day 6
    expect(specialDayBadges(new Date(2025, 11, 21))['hallel']).toBe('Today'); // 1 Teves, day 7
    expect(specialDayBadges(new Date(2025, 11, 22))['hallel']).toBe('Today'); // 2 Teves, day 8 (last)
    expect(specialDayBadges(new Date(2025, 11, 23))['hallel']).toBeUndefined(); // 3 Teves — Chanukah over
  });

  test('29-day-Kislev year: Chanukah runs 25 Kislev - 3 Teves', () => {
    // 5784 has a 29-day Kislev (verified: 30 Kislev 5784 does not exist).
    // Day 1 = 25 Kislev = 8 Dec 2023 ... day 8 = 3 Teves = 15 Dec 2023.
    expect(specialDayBadges(new Date(2023, 11, 8))['hallel']).toBe('Today'); // 25 Kislev, day 1
    expect(specialDayBadges(new Date(2023, 11, 12))['hallel']).toBe('Today'); // 29 Kislev, day 5
    expect(specialDayBadges(new Date(2023, 11, 13))['hallel']).toBe('Today'); // 1 Teves, day 6
    expect(specialDayBadges(new Date(2023, 11, 15))['hallel']).toBe('Today'); // 3 Teves, day 8 (last)
    expect(specialDayBadges(new Date(2023, 11, 16))['hallel']).toBeUndefined(); // 4 Teves — Chanukah over
  });
});

test('every badge key produced is a registered Special Days service id', () => {
  // Sweep a full civil year so every rule branch (RC, Chol Hamoed, Chanukah,
  // Omer, lulav, motzaei Shabbos) gets exercised at least once.
  const start = new Date(2026, 0, 1);
  const seen = new Set<string>();
  for (let i = 0; i < 400; i++) {
    const d = new Date(start.getFullYear(), start.getMonth(), start.getDate() + i);
    Object.keys(specialDayBadges(d)).forEach((k) => seen.add(k));
  }
  expect(seen.size).toBeGreaterThan(0);
  for (const id of seen) {
    expect(SPECIAL_DAY_IDS).toContain(id);
  }
});
