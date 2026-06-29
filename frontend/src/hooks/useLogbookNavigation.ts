import { useState, useCallback } from 'react';

export interface UseLogbookNavigationReturn {
  activeDay: number;
  setActiveDay: (day: number) => void;
  nextDay: () => void;
  prevDay: () => void;
  hasNext: boolean;
  hasPrev: boolean;
}

export function useLogbookNavigation(totalDays: number): UseLogbookNavigationReturn {
  const [activeDay, setActiveDayState] = useState(0);

  const setActiveDay = useCallback(
    (day: number) => {
      if (day >= 0 && day < totalDays) setActiveDayState(day);
    },
    [totalDays]
  );

  const nextDay = useCallback(() => setActiveDay(activeDay + 1), [activeDay, setActiveDay]);
  const prevDay = useCallback(() => setActiveDay(activeDay - 1), [activeDay, setActiveDay]);

  return {
    activeDay,
    setActiveDay,
    nextDay,
    prevDay,
    hasNext: activeDay < totalDays - 1,
    hasPrev: activeDay > 0,
  };
}
