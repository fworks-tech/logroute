import type { LogbookEvent } from './LogbookEvent';
import type { RowTotals } from './RowTotals';

export type LogbookDay = {
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
  events: Array<LogbookEvent>;
};
