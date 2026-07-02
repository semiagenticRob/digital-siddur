// Hebrew calendar conversion — the classic Dershowitz & Reingold algorithms
// ("Calendrical Calculations"). Hand-rolled: the npm Hebrew-calendar packages
// are GPL/LGPL, which this app cannot bundle, and Hermes Intl calendar
// support can't be verified under jest. Maps the civil day as printed on a
// wall calendar; "after sunset it's tomorrow" refinement belongs to the
// future zmanim round.

export interface HebrewDate {
  year: number;
  month: number; // 1 = Nisan … 7 = Tishrei … 12 = Adar (Adar I in leap years), 13 = Adar II
  day: number;
}

const HEBREW_EPOCH = -1373427; // Rata Die of 1 Tishrei, AM 1

function gregorianLeap(y: number): boolean {
  return (y % 4 === 0 && y % 100 !== 0) || y % 400 === 0;
}

const G_MONTH_DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];

// Rata Die: day 1 = Gregorian 0001-01-01.
function gregorianToRd(y: number, m: number, d: number): number {
  const p = y - 1;
  let days = 365 * p + Math.floor(p / 4) - Math.floor(p / 100) + Math.floor(p / 400);
  for (let i = 0; i < m - 1; i++) days += G_MONTH_DAYS[i];
  if (m > 2 && gregorianLeap(y)) days += 1;
  return days + d;
}

export function isHebrewLeapYear(year: number): boolean {
  return (7 * year + 1) % 19 < 7;
}

function elapsedDays(year: number): number {
  const monthsElapsed = Math.floor((235 * year - 234) / 19);
  const partsElapsed = 12084 + 13753 * monthsElapsed;
  let days = monthsElapsed * 29 + Math.floor(partsElapsed / 25920);
  if ((3 * (days + 1)) % 7 < 3) days += 1;
  return days;
}

function newYearDelay(year: number): number {
  const ny1 = elapsedDays(year);
  if (elapsedDays(year + 1) - ny1 === 356) return 2;
  if (ny1 - elapsedDays(year - 1) === 382) return 1;
  return 0;
}

function hebrewNewYearRd(year: number): number {
  return HEBREW_EPOCH + elapsedDays(year) + newYearDelay(year);
}

function daysInHebrewYear(year: number): number {
  return hebrewNewYearRd(year + 1) - hebrewNewYearRd(year);
}

function lastMonthOfHebrewYear(year: number): number {
  return isHebrewLeapYear(year) ? 13 : 12;
}

function lastDayOfHebrewMonth(year: number, month: number): number {
  if (month === 2 || month === 4 || month === 6 || month === 10 || month === 13) return 29;
  if (month === 12 && !isHebrewLeapYear(year)) return 29;
  if (month === 8 && daysInHebrewYear(year) % 10 !== 5) return 29; // regular/deficient Cheshvan
  if (month === 9 && daysInHebrewYear(year) % 10 === 3) return 29; // deficient Kislev
  return 30;
}

function hebrewToRd(year: number, month: number, day: number): number {
  let rd = hebrewNewYearRd(year) + day - 1;
  if (month < 7) {
    for (let m = 7; m <= lastMonthOfHebrewYear(year); m++) rd += lastDayOfHebrewMonth(year, m);
    for (let m = 1; m < month; m++) rd += lastDayOfHebrewMonth(year, m);
  } else {
    for (let m = 7; m < month; m++) rd += lastDayOfHebrewMonth(year, m);
  }
  return rd;
}

function rdToHebrew(rd: number): HebrewDate {
  let year = Math.floor((rd - HEBREW_EPOCH) / 366) + 1;
  while (hebrewNewYearRd(year + 1) <= rd) year++;
  // Months in civil order: Tishrei..(Adar/Adar II), then Nisan..Elul.
  const order: number[] = [];
  for (let m = 7; m <= lastMonthOfHebrewYear(year); m++) order.push(m);
  for (let m = 1; m <= 6; m++) order.push(m);
  let month = 7;
  for (const m of order) {
    if (rd <= hebrewToRd(year, m, lastDayOfHebrewMonth(year, m))) { month = m; break; }
  }
  return { year, month, day: rd - hebrewToRd(year, month, 1) + 1 };
}

export function fromGregorian(date: Date): HebrewDate {
  return rdToHebrew(gregorianToRd(date.getFullYear(), date.getMonth() + 1, date.getDate()));
}

const G_VALUES: Array<[number, string]> = [
  [400, 'ת'], [300, 'ש'], [200, 'ר'], [100, 'ק'], [90, 'צ'], [80, 'פ'], [70, 'ע'],
  [60, 'ס'], [50, 'נ'], [40, 'מ'], [30, 'ל'], [20, 'כ'], [10, 'י'], [9, 'ט'],
  [8, 'ח'], [7, 'ז'], [6, 'ו'], [5, 'ה'], [4, 'ד'], [3, 'ג'], [2, 'ב'], [1, 'א'],
];

export function gematriya(n: number): string {
  let rest = n;
  let out = '';
  for (const [v, ch] of G_VALUES) {
    if (v < 100 && rest === 15) { out += 'טו'; rest = 0; }
    if (v < 100 && rest === 16) { out += 'טז'; rest = 0; }
    while (rest >= v) { out += ch; rest -= v; }
  }
  if (out.length === 1) return out + '׳';
  return out.slice(0, -1) + '״' + out.slice(-1);
}

// Display names (unvocalized — these are UI labels, not liturgical text).
const HE_MONTHS = ['ניסן', 'אייר', 'סיון', 'תמוז', 'אב', 'אלול', 'תשרי', 'חשון', 'כסלו', 'טבת', 'שבט', 'אדר', 'אדר ב׳'];

export function formatHebrewDate(h: HebrewDate): string {
  const month = h.month === 12 && isHebrewLeapYear(h.year) ? 'אדר א׳' : HE_MONTHS[h.month - 1];
  return `${gematriya(h.day)} ${month} ${gematriya(h.year % 1000)}`;
}

// No Intl: Hermes Intl coverage differs by platform; static tables are exact.
const WEEKDAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

export function formatEnDate(date: Date): string {
  return `${WEEKDAYS[date.getDay()]} · ${MONTHS[date.getMonth()]} ${date.getDate()}`;
}
