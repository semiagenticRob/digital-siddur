import { Redirect } from 'expo-router';
import { usePreferencesStore } from '../src/store/preferences';

export default function Root() {
  const { hasCompletedOnboarding } = usePreferencesStore();
  return <Redirect href={hasCompletedOnboarding ? '/daven' : '/onboarding'} />;
}
