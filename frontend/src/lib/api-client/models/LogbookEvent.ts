export type LogbookEvent = {
  status: string;
  start_time: string;
  end_time: string;
  duration_hours: number;
  label: string;
  location?: string;
};
