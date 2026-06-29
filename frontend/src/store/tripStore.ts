import { create } from "zustand";
import type { PlanRouteResponse, ApiErrorResponse } from "@/types/trip";

const STORAGE_KEY = "logroute-session-trips";

export interface SessionTrip {
  id: string;
  label: string;
  cycleHoursUsed: number;
  drivingHours: number;
  totalMiles: number;
  plannedAt: string;
}

interface TripStore {
  result: PlanRouteResponse | null;
  isLoading: boolean;
  error: ApiErrorResponse | null;
  sessionTrips: SessionTrip[];
  setResult: (result: PlanRouteResponse) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: ApiErrorResponse | null) => void;
  clearError: () => void;
  clearResult: () => void;
  addSessionTrip: (trip: SessionTrip) => void;
  removeSessionTrip: (id: string) => void;
  clearSessionTrips: () => void;
  /** Total cycle hours consumed across all session trips (latest trip's cycleHoursUsed + all drivingHours) */
  sessionCycleTotal: () => number;
}

function loadSessionTrips(): SessionTrip[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveSessionTrips(trips: SessionTrip[]): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(trips));
  } catch { /* quota exceeded, ignore */ }
}

export const useTripStore = create<TripStore>()((set, get) => ({
  result: null,
  isLoading: false,
  error: null,
  sessionTrips: loadSessionTrips(),
  setResult: (result) => set({ result, error: null }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  clearError: () => set({ error: null }),
  clearResult: () => set({ result: null, error: null }),
  addSessionTrip: (trip) => set((s) => {
    const updated = [...s.sessionTrips, trip];
    saveSessionTrips(updated);
    return { sessionTrips: updated };
  }),
  removeSessionTrip: (id) => set((s) => {
    const updated = s.sessionTrips.filter((t) => t.id !== id);
    saveSessionTrips(updated);
    return { sessionTrips: updated };
  }),
  clearSessionTrips: () => {
    saveSessionTrips([]);
    set({ sessionTrips: [] });
  },
  sessionCycleTotal: () => {
    const trips = get().sessionTrips;
    if (trips.length === 0) return 0;
    const last = trips[trips.length - 1];
    return last.cycleHoursUsed + trips.reduce((sum, t) => sum + t.drivingHours, 0);
  },
}));
