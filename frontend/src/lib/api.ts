import axios from 'axios';
import type { TripInput } from './api-client/models/TripInput';
import { Logger } from './logger';
import { redactPII } from './redaction';
import type { PlanRouteResponse } from '@/types/trip';

const logger = new Logger('api');

export function formatApiError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status;
    const detail = (error.response?.data as any)?.detail;
    if (status === 422) return `Validation error: ${detail || 'Invalid input'}`;
    if (status === 404) return 'Route not found';
    if (status === 500) return 'Server error. Please try again.';
    if (error.message) return redactPII(error.message);
    return 'An unexpected error occurred';
  }
  if (error instanceof Error) return redactPII(error.message);
  return String(error);
}

export const apiClient = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
});

export function setupApiLogging(): void {
  apiClient.interceptors.request.use(
    (config) => {
      const correlationId = logger.getCorrelationId();
      config.headers['X-Correlation-ID'] = correlationId;
      logger.info('API Request', { method: config.method, url: config.url });
      return config;
    },
    (error) => {
      logger.error('API Request Error', error);
      return Promise.reject(error);
    }
  );

  apiClient.interceptors.response.use(
    (response) => {
      logger.info('API Response', { status: response.status, url: response.config.url });
      return response;
    },
    (error) => {
      const status = error.response?.status;
      const detail = error.response?.data?.detail;
      logger.error('API Response Error', error, { status, detail: redactPII(detail) });
      return Promise.reject(error);
    }
  );
}

export function adaptTripOutputToResponse(data: Record<string, unknown>): PlanRouteResponse {
  const rc = data.route_coordinates as Array<[number, number]> | undefined;
  const rawMarkers = (data.markers || []) as Array<Record<string, unknown>>;
  return {
    route_coordinates: (rc || []).map(([lng, lat]) => ({ latitude: lat, longitude: lng })),
    markers: rawMarkers.map((m: Record<string, unknown>, i: number) => ({
      id: String(m.id ?? `marker-${i}`),
      type: m.type as PlanRouteResponse['markers'][number]['type'],
      position: { latitude: (m as any).lat ?? (m as any).position?.latitude ?? 0, longitude: (m as any).lon ?? (m as any).position?.longitude ?? 0 },
      label: String(m.label ?? ''),
      time: m.time as string | undefined,
    })),
    logbook_days: (data.logbook_days || []) as PlanRouteResponse['logbook_days'],
    trip_summary: (data.trip_summary || {}) as PlanRouteResponse['trip_summary'],
    trip_date: data.trip_date as string | undefined,
    tractor_number: data.tractor_number as string | undefined,
    trailer_number: data.trailer_number as string | undefined,
    shipper_name: data.shipper_name as string | undefined,
    cycle_schedule: data.cycle_schedule as string | undefined,
    cycle_max_hours: data.cycle_max_hours as number | undefined,
  };
}

export async function planRoute(input: TripInput): Promise<PlanRouteResponse> {
  logger.info('Planning route', {
    current_location: redactPII(input.current_location),
    pickup_location: redactPII(input.pickup_location),
    dropoff_location: redactPII(input.dropoff_location),
  });

  try {
    const { data } = await apiClient.post('/plan-route/', input);
    logger.info('Route planned successfully', {
      total_distance: data.trip_summary?.total_distance_miles,
      legs: data.trip_summary?.legs,
    });
    return adaptTripOutputToResponse(data);
  } catch (error) {
    logger.error('Route planning failed', error instanceof Error ? error : undefined);
    throw error;
  }
}
