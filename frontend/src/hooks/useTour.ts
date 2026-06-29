import { useState, useCallback } from 'react';
import type { EventData, Status } from 'react-joyride';
import { FORM_STEPS, RESULTS_STEPS, STORAGE_KEY } from '@/lib/tourConfig';

interface TourState {
  formCompleted: boolean;
  resultsCompleted: boolean;
}

function loadState(): TourState {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch { /* ignore */ }
  return { formCompleted: false, resultsCompleted: false };
}

function saveState(state: TourState): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch { /* ignore */ }
}

function isTerminal(status: Status): boolean {
  return status === 'finished' || status === 'skipped';
}

export function useTour() {
  const [persisted, setPersisted] = useState<TourState>(loadState);
  const [run, setRun] = useState(false);
  const [phase, setPhase] = useState<'form' | 'results' | null>(null);

  const steps = phase === 'results' ? RESULTS_STEPS : FORM_STEPS;

  const startFormTour = useCallback(() => {
    setPhase('form');
    setRun(true);
  }, []);

  const startResultsTour = useCallback(() => {
    setPhase('results');
    setRun(true);
  }, []);

  const handleCallback = useCallback(
    (data: EventData) => {
      const { status, action } = data;

      if (isTerminal(status) || action === 'close' || action === 'skip') {
        const next = { ...persisted };
        if (phase === 'form') next.formCompleted = true;
        if (phase === 'results') next.resultsCompleted = true;
        setPersisted(next);
        saveState(next);
        setRun(false);
        setPhase(null);
      }
    },
    [phase, persisted],
  );

  return {
    run,
    steps,
    phase,
    startFormTour,
    startResultsTour,
    handleCallback,
    hasCompletedFormTour: persisted.formCompleted,
    hasCompletedResultsTour: persisted.resultsCompleted,
  };
}
