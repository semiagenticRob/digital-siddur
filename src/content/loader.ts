import { Service } from './types';
import shacharitData from './shacharit.json';
import minchahData from './minchah.json';
import maarivData from './maariv.json';
import maarivMotzaeiShabbosData from './maariv-motzaei-shabbos.json';
import birkasMazonData from './birkas-hamazon.json';
import alHamichyahData from './al-hamichyah.json';
import boreiNefashosData from './borei-nefashos.json';
import tefillasHaderechData from './tefillas-haderech.json';
import sefirasHaomerData from './sefiras-haomer.json';
import kriasShemaAlHamitahData from './krias-shema-al-hamitah.json';
import netilasLulavData from './netilas-lulav.json';
import hallelData from './hallel.json';
import mussafRoshChodeshData from './mussaf-rosh-chodesh.json';
import mussafCholHamoedData from './mussaf-chol-hamoed.json';

const SERVICES: Record<string, Service> = {
  shacharit: shacharitData as Service,
  minchah: minchahData as Service,
  maariv: maarivData as Service,
  'maariv-motzaei-shabbos': maarivMotzaeiShabbosData as Service,
  'birkas-hamazon': birkasMazonData as Service,
  'al-hamichyah': alHamichyahData as Service,
  'borei-nefashos': boreiNefashosData as Service,
  'tefillas-haderech': tefillasHaderechData as Service,
  'sefiras-haomer': sefirasHaomerData as Service,
  'krias-shema-al-hamitah': kriasShemaAlHamitahData as Service,
  'netilas-lulav': netilasLulavData as Service,
  hallel: hallelData as Service,
  'mussaf-rosh-chodesh': mussafRoshChodeshData as Service,
  'mussaf-chol-hamoed': mussafCholHamoedData as Service,
};

export function getService(id: string): Service | null {
  return SERVICES[id] ?? null;
}

export function listServices(): Array<{ id: string; heTitle: string; enTitle: string }> {
  return Object.values(SERVICES).map(({ id, heTitle, enTitle }) => ({ id, heTitle, enTitle }));
}
