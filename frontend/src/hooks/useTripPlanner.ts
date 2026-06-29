import { useMutation } from '@tanstack/react-query';
import { AxiosError } from 'axios';
import { planRoute } from '@/lib/api';
import { useTripStore } from '@/store/tripStore';
import type { TripFormValues } from '@/lib/schema';
import type { TripInput } from '@/lib/api-client/models/TripInput';
import type { PlanRouteResponse, ApiErrorResponse } from '@/types/trip';

export interface UseTripPlannerReturn {
  submit: (data: TripFormValues) => void;
  isLoading: boolean;
  error: ApiErrorResponse | null;
  reset: () => void;
  result: PlanRouteResponse | null;
}

function toTripInput(data: TripFormValues): TripInput {
  return {
    current_location: data.currentLocation,
    pickup_location: data.pickupLocation,
    dropoff_location: data.dropoffLocation,
    cycle_hours_used: data.cycleHoursUsed,
    cycle_schedule: data.cycleSchedule,
  };
}

export function useTripPlanner(): UseTripPlannerReturn {
  const { setResult, setLoading, setError, clearResult, result } = useTripStore();

  const mutation = useMutation({
    mutationFn: planRoute,
    onMutate: () => {
      setLoading(true);
      setError(null);
    },
    onSuccess: (data) => {
      setError(null);
      setResult(data);
      setLoading(false);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    },
    onError: (err: Error) => {
      clearResult();

      const axiosError = err as AxiosError<{ error?: string; detail?: string }>;
      const statusCode = axiosError.response?.status;
      const errorData = axiosError.response?.data;

      if (statusCode === 502 || statusCode === 503) {
        setError({
          code: 'upstream_error',
          message: 'Service unavailable',
          detail: 'The routing or geocoding service is temporarily unavailable. Please try again.',
          statusCode,
          isRetryable: true,
        });
      } else if (statusCode === 504) {
        setError({
          code: 'timeout',
          message: 'Request timed out',
          detail: 'The external service did not respond in time. Please try again.',
          statusCode,
          isRetryable: true,
        });
      } else if (statusCode === 400) {
        setError({
          code: 'validation_error',
          message: errorData?.error || 'Invalid request',
          detail: errorData?.detail || 'Please check that all locations are valid and try again.',
          statusCode,
          isRetryable: false,
        });
      } else {
        setError({
          code: 'unknown_error',
          message: 'Something went wrong',
          detail: err.message,
          statusCode: statusCode ?? 0,
          isRetryable: true,
        });
      }

      setLoading(false);
    },
  });

  const reset = () => {
    mutation.reset();
    clearResult();
  };

  const { error: storeError } = useTripStore();

  return {
    submit: (data: TripFormValues) => mutation.mutate(toTripInput(data)),
    isLoading: mutation.isPending,
    error: storeError,
    reset,
    result,
  };
}
