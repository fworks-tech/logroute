import { create } from "zustand";
import type { PlanRouteResponse, ApiErrorResponse } from "@/types/trip";

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
}

export const useTripStore = create<TripStore>()((set) => ({
  result: null,
  isLoading: false,
  error: null,
  sessionTrips: [],
  setResult: (result) => set({ result, error: null }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  clearError: () => set({ error: null }),
  clearResult: () => set({ result: null, error: null }),
  addSessionTrip: (trip) => set((s) => ({ sessionTrips: [...s.sessionTrips, trip] })),
  removeSessionTrip: (id) => set((s) => ({ sessionTrips: s.sessionTrips.filter((t) => t.id !== id) })),
  clearSessionTrips: () => set({ sessionTrips: [] }),
}));
