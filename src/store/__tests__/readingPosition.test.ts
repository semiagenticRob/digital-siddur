import { useReadingPositionStore } from '../readingPosition';

beforeEach(() => {
  useReadingPositionStore.setState({ offsets: {}, lastServiceId: null });
});

test('lastServiceId is null initially', () => {
  expect(useReadingPositionStore.getState().lastServiceId).toBeNull();
});

test('setLastService records the most recent service', () => {
  useReadingPositionStore.getState().setLastService('shacharit');
  useReadingPositionStore.getState().setLastService('minchah');
  expect(useReadingPositionStore.getState().lastServiceId).toBe('minchah');
});

test('setOffset still stores per-service offsets', () => {
  useReadingPositionStore.getState().setOffset('maariv', 1234);
  expect(useReadingPositionStore.getState().offsets['maariv']).toBe(1234);
});
