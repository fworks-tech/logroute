export type TripInput = {
  current_location: string;
  pickup_location: string;
  dropoff_location: string;
  cycle_hours_used: number;
  cycle_schedule?: string;
  trip_date?: string | null;
  tractor_number?: string;
  trailer_number?: string;
  shipper_name?: string;
};
