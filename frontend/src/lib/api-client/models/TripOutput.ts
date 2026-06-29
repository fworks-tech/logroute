import type { LogbookDay } from './LogbookDay';
import type { Marker } from './Marker';
import type { TripSummary } from './TripSummary';

export type TripOutput = {
  route_coordinates: Array<Array<number>>;
  markers: Array<Marker>;
  logbook_days: Array<LogbookDay>;
  trip_summary: TripSummary;
  trip_date?: string | null;
  tractor_number?: string;
  trailer_number?: string;
  shipper_name?: string;
};
