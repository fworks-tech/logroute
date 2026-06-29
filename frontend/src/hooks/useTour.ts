import { useState, useCallback } from 'react';
import type { EventData } from 'react-joyride';
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

export function useTour() {
  const [persisted, setPersisted] = useState<TourState>(loadState);
  const [run, setRun] = useState(false);
  const [stepIndex, setStepIndex] = useState(0);
  const [phase, setPhase] = useState<'form' | 'results' | null>(null);

  const steps = phase === 'results' ? RESULTS_STEPS : FORM_STEPS;

  const startFormTour = useCallback(() => {
    setPhase('form');
    setStepIndex(0);
    setRun(true);
  }, []);

  const startResultsTour = useCallback(() => {
    setPhase('results');
    setStepIndex(0);
    setRun(true);
  }, []);

  const stopTour = useCallback(() => {
    setRun(false);
    setPhase(null);
  }, []);

  const handleCallback = useCallback(
    (data: EventData) => {
      const { status, index, action } = data;

      if (status === 'finished' || status === 'skipped') {
        const next = { ...persisted };
        if (phase === 'form') next.formCompleted = true;
        if (phase === 'results') next.resultsCompleted = true;
        setPersisted(next);
        saveState(next);
        setRun(false);
        setPhase(null);
        return;
      }

      if (action === 'close' || action === 'skip') {
        const next = { ...persisted };
        if (phase === 'form') next.formCompleted = true;
        if (phase === 'results') next.resultsCompleted = true;
        setPersisted(next);
        saveState(next);
        setRun(false);
        setPhase(null);
        return;
      }

      setStepIndex(index);
    },
    [phase, persisted],
  );

  return {
    run,
    stepIndex,
    steps,
    phase,
    startFormTour,
    startResultsTour,
    stopTour,
    setStepIndex,
    handleCallback,
    hasCompletedFormTour: persisted.formCompleted,
    hasCompletedResultsTour: persisted.resultsCompleted,
  };
}
