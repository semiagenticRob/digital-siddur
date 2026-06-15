import { Service } from './types';
import shacharitData from './shacharit.json';

const SERVICES: Record<string, Service> = {
  shacharit: shacharitData as Service,
};

export function getService(id: string): Service | null {
  return SERVICES[id] ?? null;
}

export function listServices(): Array<{ id: string; heTitle: string; enTitle: string }> {
  return Object.values(SERVICES).map(({ id, heTitle, enTitle }) => ({ id, heTitle, enTitle }));
}
