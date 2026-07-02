import { useCallback, useEffect, useState } from 'react';
import { AppState } from 'react-native';
import { useFocusEffect } from 'expo-router';

// Screens that show "now"-derived content (today's date, zmanim, special-day
// badges) can stay mounted across midnight — iOS keeps apps alive for days —
// so `now` must be refreshed rather than computed once at render: on screen
// focus, and when the app returns to the foreground.
export function useNow(): Date {
  const [now, setNow] = useState(() => new Date());

  useFocusEffect(
    useCallback(() => {
      setNow(new Date());
    }, [])
  );

  useEffect(() => {
    const subscription = AppState.addEventListener('change', (state) => {
      if (state === 'active') {
        setNow(new Date());
      }
    });
    return () => subscription.remove();
  }, []);

  return now;
}
