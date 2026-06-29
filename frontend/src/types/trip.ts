export interface RouteCoordinate {
  latitude: number;
  longitude: number;
}

export interface Marker {
  id: string;
  type: "start" | "pickup" | "dropoff" | "fuel" | "rest";
  position: RouteCoordinate;
  label: string;
  time?: string;
}

export type DutyStatus = "OFF_DUTY" | "SLEEPER_BERTH" | "DRIVING" | "ON_DUTY_NOT_DRIVING";

export interface LogbookEvent {
  status: DutyStatus;
  start_time: string;
  end_time: string;
  duration_hours: number;
  label?: string;
  location?: string;
}

export interface RowTotals {
  off_duty_hours: number;
  sleeper_berth_hours: number;
  driving_hours: number;
  on_duty_not_driving_hours: number;
}

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

export interface TripSummary {
  total_distance_miles: number;
  total_trip_hours: number;
  total_driving_hours: number;
  num_fuel_stops: number;
  num_rest_stops: number;
  leg_1_miles: number;
  leg_2_miles: number;
}

export interface ELDMetadata {
  trip_date?: string;
  tractor_number?: string;
  trailer_number?: string;
  shipper_name?: string;
}

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

export type ApiErrorCode =
  | "timeout"
  | "upstream_error"
  | "validation_error"
  | "network_error"
  | "server_error"
  | "unknown_error";

export interface ApiErrorResponse {
  code: ApiErrorCode;
  message: string;
  detail?: string;
  statusCode: number;
  isRetryable: boolean;
}
