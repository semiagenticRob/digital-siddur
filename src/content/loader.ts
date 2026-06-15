import { Service } from './types';
import shacharitData from './shacharit.json';
import minchahData from './minchah.json';
import maarivData from './maariv.json';
import birkasMazonData from './birkas-hamazon.json';

const SERVICES: Record<string, Service> = {
  shacharit: shacharitData as Service,
  minchah: minchahData as Service,
  maariv: maarivData as Service,
  'birkas-hamazon': birkasMazonData as Service,
};

export function getService(id: string): Service | null {
  return SERVICES[id] ?? null;
}

export function listServices(): Array<{ id: string; heTitle: string; enTitle: string }> {
  return Object.values(SERVICES).map(({ id, heTitle, enTitle }) => ({ id, heTitle, enTitle }));
}
