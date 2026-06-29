import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useTour } from './useTour';
import { STORAGE_KEY } from '@/lib/tourConfig';

const store = new Map<string, string>();

beforeEach(() => {
  store.clear();
  vi.stubGlobal('localStorage', {
    getItem: (key: string) => store.get(key) ?? null,
    setItem: (key: string, value: string) => store.set(key, value),
    removeItem: (key: string) => store.delete(key),
    clear: () => store.clear(),
    get length() { return store.size; },
    key: (i: number) => [...store.keys()][i] ?? null,
  });
});

afterEach(() => {
  vi.unstubAllGlobals();
});

function getPersisted() {
  const raw = localStorage.getItem(STORAGE_KEY);
  return raw ? JSON.parse(raw) : null;
}

describe('useTour', () => {
  describe('localStorage persistence', () => {
    it('loads default state when nothing is stored', () => {
      const { result } = renderHook(() => useTour());
      expect(result.current.hasCompletedFormTour).toBe(false);
      expect(result.current.hasCompletedResultsTour).toBe(false);
    });

    it('loads previously persisted completion state', () => {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({ formCompleted: true, resultsCompleted: false }),
      );
      const { result } = renderHook(() => useTour());
      expect(result.current.hasCompletedFormTour).toBe(true);
      expect(result.current.hasCompletedResultsTour).toBe(false);
    });

    it('survives malformed localStorage gracefully', () => {
      localStorage.setItem(STORAGE_KEY, '{bad json');
      const { result } = renderHook(() => useTour());
      expect(result.current.hasCompletedFormTour).toBe(false);
      expect(result.current.hasCompletedResultsTour).toBe(false);
    });
  });

  describe('startFormTour / startResultsTour', () => {
    it('startFormTour sets run to true and phase to form', () => {
      const { result } = renderHook(() => useTour());

      act(() => result.current.startFormTour());

      expect(result.current.run).toBe(true);
      expect(result.current.phase).toBe('form');
    });

    it('startResultsTour sets run to true and phase to results', () => {
      const { result } = renderHook(() => useTour());

      act(() => result.current.startResultsTour());

      expect(result.current.run).toBe(true);
      expect(result.current.phase).toBe('results');
    });
  });

  describe('steps selection', () => {
    it('returns FORM_STEPS when phase is form', () => {
      const { result } = renderHook(() => useTour());
      act(() => result.current.startFormTour());
      expect(result.current.steps.length).toBe(9);
    });

    it('returns RESULTS_STEPS when phase is results', () => {
      const { result } = renderHook(() => useTour());
      act(() => result.current.startResultsTour());
      expect(result.current.steps.length).toBe(7);
    });
  });

  describe('handleCallback — completion', () => {
    function makeData(overrides: Record<string, unknown> = {}) {
      return {
        type: 'step:after',
        action: 'next',
        index: 1,
        lifecycle: 'complete',
        status: 'running',
        step: { target: 'body' } as any,
        controlled: false,
        size: 9,
        origin: null,
        scrolling: false,
        waiting: false,
        ...overrides,
      } as any;
    }

    it('marks form completed on finished status', () => {
      const { result } = renderHook(() => useTour());
      act(() => result.current.startFormTour());

      act(() => {
        result.current.handleCallback(makeData({ status: 'finished' }));
      });

      expect(result.current.run).toBe(false);
      expect(result.current.phase).toBe(null);
      expect(result.current.hasCompletedFormTour).toBe(true);
      const stored = getPersisted();
      expect(stored.formCompleted).toBe(true);
    });

    it('marks results completed on finished status', () => {
      const { result } = renderHook(() => useTour());
      act(() => result.current.startResultsTour());

      act(() => {
        result.current.handleCallback(makeData({ status: 'finished' }));
      });

      expect(result.current.hasCompletedResultsTour).toBe(true);
      const stored = getPersisted();
      expect(stored.resultsCompleted).toBe(true);
    });

    it('marks completed on skipped status', () => {
      const { result } = renderHook(() => useTour());
      act(() => result.current.startFormTour());

      act(() => {
        result.current.handleCallback(makeData({ status: 'skipped' }));
      });

      expect(result.current.hasCompletedFormTour).toBe(true);
    });

    it('marks completed on close action', () => {
      const { result } = renderHook(() => useTour());
      act(() => result.current.startFormTour());

      act(() => {
        result.current.handleCallback(makeData({ action: 'close', status: 'running' }));
      });

      expect(result.current.hasCompletedFormTour).toBe(true);
      expect(result.current.run).toBe(false);
    });

    it('marks completed on skip action', () => {
      const { result } = renderHook(() => useTour());
      act(() => result.current.startFormTour());

      act(() => {
        result.current.handleCallback(makeData({ action: 'skip', status: 'running' }));
      });

      expect(result.current.hasCompletedFormTour).toBe(true);
    });
  });

  describe('handleCallback — non-terminal events', () => {
    it('does not stop the tour for step:after navigation events', () => {
      const { result } = renderHook(() => useTour());
      act(() => result.current.startFormTour());

      act(() => {
        result.current.handleCallback({
          type: 'step:after',
          action: 'next',
          index: 1,
          lifecycle: 'complete',
          status: 'running',
          step: { target: 'body' } as any,
          controlled: false,
          size: 9,
          origin: null,
          scrolling: false,
          waiting: false,
        } as any);
      });

      expect(result.current.run).toBe(true);
      expect(result.current.hasCompletedFormTour).toBe(false);
    });
  });
});
