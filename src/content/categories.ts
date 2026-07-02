import { listServices } from './loader';

// The home screen's grouping (approved design, Variant A). A service must
// live in exactly one category — the unit test fails the build if a newly
// registered service isn't categorized here.
export interface HomeCategory {
  key: string;
  title: string;
  compact: boolean; // compact rows for the less-frequent sections
  serviceIds: string[];
}

export const HOME_CATEGORIES: HomeCategory[] = [
  { key: 'tefillos', title: 'Tefillos', compact: false, serviceIds: ['shacharit', 'minchah', 'maariv'] },
  {
    key: 'special', title: 'Special Days', compact: true,
    serviceIds: ['sefiras-haomer', 'maariv-motzaei-shabbos', 'mussaf-rosh-chodesh', 'mussaf-chol-hamoed', 'hallel', 'netilas-lulav'],
  },
  { key: 'after-eating', title: 'After Eating', compact: true, serviceIds: ['birkas-hamazon', 'al-hamichyah', 'borei-nefashos'] },
  { key: 'anytime', title: 'Anytime', compact: true, serviceIds: ['tefillas-haderech', 'krias-shema-al-hamitah'] },
];

export interface HomeSection {
  key: string;
  title: string;
  compact: boolean;
  data: Array<{ id: string; heTitle: string; enTitle: string }>;
}

export function homeSections(): HomeSection[] {
  const byId = new Map(listServices().map((s) => [s.id, s]));
  return HOME_CATEGORIES.map((c) => ({
    key: c.key,
    title: c.title,
    compact: c.compact,
    data: c.serviceIds.map((id) => {
      const svc = byId.get(id);
      if (!svc) throw new Error(`home category '${c.key}' references unknown service '${id}'`);
      return svc;
    }),
  }));
}
