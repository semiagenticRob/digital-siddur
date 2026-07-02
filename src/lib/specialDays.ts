// Diaspora special-day badge rules for the home screen. Pure over the civil
// Date -> Hebrew-date conversion in hebrewDate.ts; each rule below carries a
// one-line halachic source. Month numbering matches hebrewDate.ts:
// 1 = Nisan … 3 = Sivan … 7 = Tishrei … 9 = Kislev, 10 = Teves.
import { fromGregorian, lastDayOfHebrewMonth } from './hebrewDate';

export function specialDayBadges(civilDate: Date): Record<string, string> {
  const badges: Record<string, string> = {};
  const { year, month, day } = fromGregorian(civilDate);
  const isSaturday = civilDate.getDay() === 6;

  // Sefiras HaOmer is counted at the evening service, so "Tonight" tracks
  // *tomorrow's* Hebrew date: the count runs 16 Nisan (first night) through
  // 5 Sivan (the night before Shavuos) — Vayikra 23:15-16.
  const tomorrow = new Date(civilDate.getFullYear(), civilDate.getMonth(), civilDate.getDate() + 1);
  const t = fromGregorian(tomorrow);
  if ((t.month === 1 && t.day >= 16) || t.month === 2 || (t.month === 3 && t.day <= 5)) {
    badges['sefiras-haomer'] = 'Tonight';
  }

  // Rosh Chodesh mussaf: 30th of any month (first RC day when the outgoing
  // month is full) or 1st of any month, except 1 Tishrei — Bamidbar 28:11.
  const isRoshChodesh = day === 30 || (day === 1 && month !== 7);
  if (isRoshChodesh) badges['mussaf-rosh-chodesh'] = 'Today';

  // Chol Hamoed mussaf: the intermediate days of Pesach and Sukkos —
  // Orach Chaim 490:1, 653:1.
  const isCholHamoed =
    (month === 1 && day >= 17 && day <= 20) || (month === 7 && day >= 17 && day <= 21);
  if (isCholHamoed) badges['mussaf-chol-hamoed'] = 'Today';

  // Chanukah runs 25 Kislev for 8 days regardless of Kislev's length, so it
  // ends 2 Teves when Kislev has 30 days or 3 Teves when Kislev has 29 —
  // Shabbos 21b.
  const kislevLen = lastDayOfHebrewMonth(year, 9);
  const chanukahEndInTeves = kislevLen === 30 ? 2 : 3;
  const isChanukah = (month === 9 && day >= 25) || (month === 10 && day <= chanukahEndInTeves);

  // Hallel: Rosh Chodesh, Chol Hamoed, the Yom Tov days of Pesach/Sukkos and
  // Shavuos (6-7 Sivan in the diaspora), and Chanukah — Erchin 10a.
  const isYomTovHallel =
    (month === 1 && day >= 15 && day <= 21) ||
    (month === 3 && (day === 6 || day === 7)) ||
    (month === 7 && day >= 15 && day <= 23);
  if (isRoshChodesh || isCholHamoed || isYomTovHallel || isChanukah) {
    badges['hallel'] = 'Today';
  }

  // Netilas Lulav: 15-21 Tishrei, but never on Shabbos (the lulav is not
  // taken on Shabbos, even on the first day) — Sukkah 42b.
  if (month === 7 && day >= 15 && day <= 21 && !isSaturday) {
    badges['netilas-lulav'] = 'Today';
  }

  // The Motzaei Shabbos maariv insertion is said Saturday night.
  if (isSaturday) badges['maariv-motzaei-shabbos'] = 'Tonight';

  return badges;
}
