/** A geographic coordinate pair (latitude/longitude). */
export interface RouteCoordinate {
  latitude: number;
  longitude: number;
}

/** A point-of-interest marker along the route (start, pickup, dropoff, fuel, rest). */
export interface Marker {
  id: string;
  type: "start" | "pickup" | "dropoff" | "fuel" | "rest";
  position: RouteCoordinate;
  label: string;
  time?: string;
}

/** FMCSA duty status values for ELD logbook events. */
export type DutyStatus = "OFF_DUTY" | "SLEEPER_BERTH" | "DRIVING" | "ON_DUTY_NOT_DRIVING";

/** A single logbook event with a duty status, time range, and optional location. */
export interface LogbookEvent {
  status: DutyStatus;
  start_time: string;
  end_time: string;
  duration_hours: number;
  label?: string;
  location?: string;
}

/** Aggregate hours for each duty status in a single logbook day. */
export interface RowTotals {
  off_duty_hours: number;
  sleeper_berth_hours: number;
  driving_hours: number;
  on_duty_not_driving_hours: number;
}

/** A single day in the ELD logbook with events, miles, and cumulative cycle data. */
export interface LogbookDay {
  day: number;
  date_offset: number;
  date: string;
  from_location: string;
  to_location: string;
  daily_miles: number;
  cumulative_miles: number;
  total_driving_hours: number;
  total_on_duty_hours: number;
  cycle_hours_after_day: number;
  row_totals: RowTotals;
  events: LogbookEvent[];
}

/** High-level summary of the planned trip: distance, hours, stops. */
export interface TripSummary {
  total_distance_miles: number;
  total_trip_hours: number;
  total_driving_hours: number;
  num_fuel_stops: number;
  num_rest_stops: number;
  leg_1_miles: number;
  leg_2_miles: number;
}

/** Optional metadata fields for the ELD logbook. */
export interface ELDMetadata {
  trip_date?: string;
  tractor_number?: string;
  trailer_number?: string;
  shipper_name?: string;
}

/** Full response from the plan-route API: coordinates, markers, logbook, summary. */
export interface PlanRouteResponse extends ELDMetadata {
  route_coordinates: RouteCoordinate[];
  markers: Marker[];
  logbook_days: LogbookDay[];
  trip_summary: TripSummary;
  current_location?: string;
  pickup_location?: string;
  dropoff_location?: string;
  cycle_schedule?: string;
  cycle_max_hours?: number;
}

/** Categorised error codes returned by the API. */
export type ApiErrorCode =
  | "timeout"
  | "upstream_error"
  | "validation_error"
  | "network_error"
  | "server_error"
  | "unknown_error";

/** Structured error response with code, message, and retryability. */
export interface ApiErrorResponse {
  code: ApiErrorCode;
  message: string;
  detail?: string;
  statusCode: number;
  isRetryable: boolean;
}
